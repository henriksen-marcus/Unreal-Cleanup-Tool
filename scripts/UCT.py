# Unreal Cleanup Tool (UCT) by Marcus Henriksen
# This program deletes unreal engine temporary files with one click. 
# You can also customize the list of files to delete.
# Use 'UCT.py -h' in cmd for available commands.

import argparse
from argparse import RawTextHelpFormatter
import subprocess
import shutil
import json
import glob
import sys
import os
from os.path import exists
import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
import winreg

defaultFolders = ['.vs', 'Binaries', 'DerivedDataCache', 'Intermediate']
defaultExtensions = ['.sln']
defaultConfig = {
    'fileManagement':
    {
        'files':[],
        'folders':defaultFolders,
        'extensions':defaultExtensions
    },
    'settings':
    {
        'generateProjectFiles':False,
        'compile':False,
        'disableCompileMessage':False
    }
}
config = {}

# JSON data in uproject file
uprojectData = {}

# We save the UnrealBuildTool directory in localappdata
# so that we don't have to search for it every time
defaultAppdataSavedVars = {
    'ubtPath':None,
    'devenvPath':None
}
appdataSavedVars = {}
appdataSavedVarsPath = os.environ['LOCALAPPDATA']

# Current file path
path = os.path.dirname(os.path.abspath(__file__))

# Unreal project name (.uproject)
uprojectPath = None


def initArgs():
    # Program description
    parser = argparse.ArgumentParser(usage=argparse.SUPPRESS, description = '''
    ### Unreal Cleanup Tool ###\n\n
    Deletes specified files and folders with one click
    ''', formatter_class=RawTextHelpFormatter)

    parser.error = lambda message: print(f'Error: {message}\nUse -h or --help for help.')

    # Arguments
    parser.add_argument('-a', help='Add a file to delete list', type=str, metavar='[filename].[ext]')
    parser.add_argument('-r', help='Remove a file from delete list', type=str, metavar='[filename].[ext]')
    parser.add_argument('-af', help='Add a folder to delete list', type=str, metavar='[foldername]')
    parser.add_argument('-rf', help='Remove a folder from delete list', type=str, metavar='[foldername]')
    parser.add_argument('-ae', help='Add a file extension to the delete list', type=str, metavar='[ext]')
    parser.add_argument('-re', help='Remove a file extension from the delete list', type=str, metavar='[ext]')
    parser.add_argument('-gpf', help="Toggle automatic generation of VS project files after deletion", action='store_true')
    parser.add_argument('-compile', help="Toggle automatic compilation of project after deletion", action='store_true')
    parser.add_argument('-msg', help="Toggle the popup message when the project was succesfully compiled", action='store_true')
    parser.add_argument('-show', help='Show the current file/folder delete configuration', action='store_true')
    parser.add_argument('-reset', help='Reset delete list to default', action='store_true')

    # For user to manually specify the unreal engine directory and visual studio directory
    parser.add_argument('-uedir', help=argparse.SUPPRESS, action='store_true')
    parser.add_argument('-vsdir', help=argparse.SUPPRESS, action='store_true')

    # Check user's arguments and add them to array
    return parser.parse_args()


def askWarningPrompt(message):
    "Prompt the user for a yes/no answer"

    # Show popup
    answer = tk.messagebox.askokcancel("Unreal Cleanup Tool", message, icon=tk.messagebox.WARNING)
    return answer


def infoPrompt(message):
    "Show a message prompt"

    # Show popup
    tk.messagebox.showinfo("Unreal Cleanup Tool", message)

def errorPrompt(message):
    "Show an error prompt"

    # Show popup
    tk.messagebox.showerror("Unreal Cleanup Tool", message)


def folderPrompt():
    "Prompt the user to select a folder"

    # Open a new tkinter main window
    root = tk.Tk()
    root.title('Main')
    root.geometry('0x0')

    # Hide main window
    root.withdraw()

    # Show popup
    return tk.filedialog.askdirectory()


def checkDirectory():
    "Check if we are in an unreal project directory and save the uproject path"

    if uprojectPath is None:
        return askWarningPrompt("You are not in an unreal engine project folder. This program deletes files. Continue?")


def checkArgs():
    "Check if there are any arguments, except the script call"

    return False if len(sys.argv) < 2 else True


def processArgs(args):
    "Decide what to do depending on the arguments given"

    global config
    localconfig = config['fileManagement']

    # Reset list
    if args.reset is not None:
        if args.reset:
            config = defaultConfig
            print("List reset to default.")
            saveData()
            return

    # Add
    if args.a is not None:
        if args.a not in localconfig['files']: # Avoid duplicates
            localconfig['files'].append(args.a)
            print(f'Added file {args.a}')
        else:
            print(f'{args.a} is already in the list.')

    # Remove
    if args.r is not None:
        try:
            i = localconfig['files'].index(args.r)
            try:  
                localconfig['files'].pop(i)
                print(f'Removed file {args.r}')
            except IndexError:
                print(f"'{args.r}' does not exists in the list!'")
        except ValueError:
            print(f"'{args.r}' does not exists in the list!'")
    
    # Add folder
    if args.af is not None:
        if args.af not in localconfig['folders']: # Avoid dupliates
            # Check for symbolised default argument
            if ('/' + args.af) in localconfig['folders']:
                try:
                    i = localconfig['folders'].index('/' + args.af)
                    # Rename
                    localconfig['folders'][i] = args.af
                except ValueError:
                    pass
            else:
                localconfig['folders'].append(args.af)
            print(f'Added folder {args.af}')
        else:
            print(f'{args.af} is already in the list.')

    # Remove folder
    if args.rf is not None:
        try:
            i = localconfig['folders'].index(args.rf)
            try:
                # Replace with symboled version, so we don't lose defaults
                if args.rf in defaultFolders:
                    localconfig['folders'][i] = '/' + localconfig['folders'][i]
                else:
                    localconfig['folders'].pop(i)
                print(f'Removed folder {args.rf}')
            except IndexError:
                print(f"'{args.rf}' does not exists in the list!'")
        except ValueError:
            print(f"'{args.rf}' does not exists in the list!'")

    # Add extension
    if args.ae is not None:
        # Add . at the start and prevent user error
        mod = '.' + args.ae.replace('.', '')
        # Avoid duplicates
        if mod not in localconfig['extensions']: 
            # Check for symbolised default argument
            if ('/' + mod) in localconfig['extensions']:
                try:
                    i = localconfig['extensions'].index('/' + mod)
                    localconfig['extensions'][i] = mod
                except ValueError:
                    pass
            else:
                localconfig['extensions'].append(mod)
            print(f'Added extension {mod}')
        else:
            print(f'{args.ae} is already in the list.')

    # Remove extension
    if args.re is not None:
        mod = '.' + args.re.replace('.', '')
        try:
            i = localconfig['extensions'].index(mod)
            try:
                localconfig['extensions'].pop(i)
                if args.r in defaultExtensions:
                    # Add a '/' to mark it as disabled, also this 
                    # symbol cannot be used in folder names
                    localconfig['extensions'].append('/' + args.re)
                print(f'Removed extension {mod}')
            except IndexError:
                print(f"'{mod}' does not exists in the list!'")
        except ValueError:
            print(f"'{mod}' does not exists in the list!'")

    # Toggle generate project files
    if args.gpf:
        if config['settings']['generateProjectFiles'] == False: # Enable
            val = checkgpf()
            if val['success']:
                config['settings']['generateProjectFiles'] = True 
            else:
                print(f"Error activating gpf: {val['message']}")
                config['settings']['generateProjectFiles'] = False
        else: # Disable
            config['settings']['generateProjectFiles'] = False
        
        print(f"Generate project files set to {config['settings']['generateProjectFiles']}")

    # Toggle automatic compilation
    if args.compile:
        if config['settings']['compile'] == False: # Enable
            if config['settings']['generateProjectFiles'] == True:
                config['settings']['compile'] = True
            else:
                print("Generate project files must be active to enable automatic compilaton. Use -gpf to enable it.")
        else:
            config['settings']['compile'] = False
        print(f"Automatic compilation set to {config['settings']['compile']}")

    if args.msg:
        config['settings']['disableCompileMessage'] = not config['settings']['disableCompileMessage']
        print(f"Compile success popup message {'turned off' if config['settings']['disableCompileMessage'] else 'turned on'}.")

    # Show delete list
    if args.show:
        indent = "    "
        # Don't print disabled default arguments (marked with '/')
        for key in localconfig:
            print(f'{key.capitalize()}:')
            valueCount = 0
            for value in localconfig[key]:
                if value[0] != '/':
                    print(indent + value)
                    valueCount += 1
            # If there were no active values, print empty
            if valueCount == 0:
                print(indent + '(empty)')

        print(f"\nGenerate project files set to {config['settings']['generateProjectFiles']}")
        print(f"Automatic compilation set to {config['settings']['compile']}")

    # Opens folder select dialog and saves the path
    if args.uedir is not None:
        if args.uedir:
            givenPath = folderPrompt()
            path = findFile(givenPath, "UnrealBuildTool.exe")
            if path is not None and os.path.exists(path):
                appdataSavedVars['ubtPath'] = path
                print("Successfully found Unreal Engine installation.")
            else:
                print(f"Could not find UnrealBuildTool.exe in {givenPath}.")
                return
            
    if args.vsdir is not None:
        if args.vsdir:
            givenPath = folderPrompt()
            path = findFile(givenPath, "devenv.exe")
            if path is not None and os.path.exists(path):
                appdataSavedVars['vsPath'] = path
                print("Successfully found Visual Studio installation.")
            else:
                print(f"Could not find devenv.exe in {givenPath}.")
                return

    config['fileManagement'] = localconfig
    saveData()


def delete():
    "Perform delete operation on all listed items"

    localconfig = config['fileManagement']
    num_deleted = 0
    for i, val in enumerate(localconfig['files']):
        if val[0] == '/': continue
        try:
            os.remove(localconfig['files'][i])
            num_deleted += 1
        except PermissionError:
            errorPrompt(f"Operation aborted: Permission was denied on a file or folder. Did you close unreal engine and you IDE?")
            sys.exit()
        except FileNotFoundError:
            pass

    for i, val in enumerate(localconfig['folders']):
        if val[0] == '/': continue
        try:
            shutil.rmtree(localconfig['folders'][i])
            num_deleted += 1
        except PermissionError:
            errorPrompt(f"Operation aborted: Permission was denied on a file or folder. Did you close unreal engine and you IDE?")
            sys.exit()
        except FileNotFoundError:
            pass

    for i, val in enumerate(localconfig['extensions']):
        if val[0] == '/': continue
        for file in glob.glob('*' + localconfig['extensions'][i], root_dir = path, include_hidden = True):
            try:
                os.remove(file)
                num_deleted += 1
            except PermissionError:
                errorPrompt(f"Operation aborted: Permission was denied on a file or folder. Did you close unreal engine and you IDE?")
                sys.exit()
            except FileNotFoundError:
                pass
        

    s = "s" if num_deleted > 1 or num_deleted == 0 else ""
    print(f'Deleted {num_deleted} file{s}/folder{s}.')


def loadData():
    "Load config"

    # Local configuration file
    global config
    if os.path.exists('uct_config.json'):
        with open('uct_config.json', 'r') as openfile:
            # Reading from json file
            config = json.load(openfile)
    else:
        config = defaultConfig

    # Localappdata configuration file
    global appdataSavedVars
    if os.path.exists(os.path.join(appdataSavedVarsPath, "UnrealCleanupTool/saved_data.json")):
        with open(os.path.join(appdataSavedVarsPath, "UnrealCleanupTool/saved_data.json"), 'r') as openfile:
            # Reading from json file
            appdataSavedVars = json.load(openfile)
    else:
        appdataSavedVars = defaultAppdataSavedVars

    global uprojectPath
    for file in os.listdir("."):
        if file.endswith(".uproject"):
            uprojectPath = os.path.abspath(file)

    # Load uproject file into memory
    global uprojectData
    if uprojectPath is not None:
        with open(uprojectPath, 'r') as openfile:
                    uprojectData = json.load(openfile)


def saveData():
    # Local configuration file
    json_object = json.dumps(config, indent = 4)

    # Delete old file
    if exists("uct_config.json"):
        os.remove("uct_config.json")

    # Create new file
    fileMode = 'w'

    with open("uct_config.json", fileMode) as outfile:
        outfile.write(json_object)
        try:
            # Make file hidden
            subprocess.check_call(["attrib","+H","uct_config.json"])
        except PermissionError:
            pass


    # Localappdata configuration file
    folder = os.path.join(appdataSavedVarsPath, "UnrealCleanupTool")
    file = os.path.join(folder, "saved_data.json")
    json_object = json.dumps(appdataSavedVars, indent = 4)

    if not exists(folder):
        os.mkdir(folder)

    # Delete old file
    if exists(file):
        os.remove(file)

    # Create new file
    fileMode = 'w'
    with open(file, fileMode) as outfile:
        outfile.write(json_object)


def findUnrealBuildTool():
    "Returns the path of the unreal build tool"

    # Check if we have it saved first
    if appdataSavedVars["ubtPath"] is not None:
        if os.path.exists(appdataSavedVars["ubtPath"]):
            return appdataSavedVars["ubtPath"]

    # Get engine version from uproject file
    if uprojectPath is not None:
        with open(uprojectPath, 'r') as openfile:
                    uprojectData = json.load(openfile)
    else:
        print("Could not find uproject file.")
        return None

    # Get the specific engine version install directory
    key_path = r"SOFTWARE\EpicGames\Unreal Engine"
    key_path = os.path.join(key_path, uprojectData['EngineAssociation'])
    installed_directory = None

    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
        installed_directory = winreg.QueryValueEx(key, "InstalledDirectory")[0]
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass

    if installed_directory is not None:
        path = findFile(installed_directory, "UnrealBuildTool.exe")
        if path is not None and os.path.exists(path) and os.path.basename(path) == "UnrealBuildTool.exe":
            appdataSavedVars['ubtPath'] = path
            saveData()
            return path
        else: 
            return None
    else:
        print("Could not find Unreal Engine install directory with correct version. Please use -uedir to select the directory.")
        return None    


def findFile(root, filename):
    for dirpath, dirnames, filenames in os.walk(root):
        if filename in filenames:
            file_path = os.path.join(dirpath, filename)
            return os.path.abspath(file_path)
    return None


def findExtension(root, ext):
    for dirpath, dirnames, filenames in os.walk(root):
        for file in filenames:
            if file.endswith(ext):
                file_path = os.path.join(dirpath, file)
                return os.path.abspath(file_path)
    return None


def generateProjectFiles():
    ubtPath = findUnrealBuildTool()
    if ubtPath is None:
        errorPrompt("Could not generate project files.")
        return False

    command = [ubtPath, "-projectfiles", uprojectPath]
    try:
        # Call UBT
        subprocess.run(command, check=True)
        #messagePrompt("Finished generating project files.")
    except subprocess.CalledProcessError as e:
        errorPrompt("Error generating project files.")
        return False

# devenv BowlingGame.sln /Build "Development Editor|Win64"
def compile():
    try:
        projectName = uprojectData['Modules'][0]['Name']
    except:
        projectName = None

    path = findDevenv()
    slnPath = findExtension(".", ".sln")

    if path is None or slnPath is None:
        errorPrompt("Could not compile.")
        print("Path: " + str(path))
        print("slnPath: " + str(slnPath))
        return False
    
    # Remove .exe from path, idk why it doesn't work with it
    if path.endswith(".exe"):
        path = path[:-4]
    print(path)
    command = [path, slnPath, "/Build", "Development Editor|Win64"]
    try:
        # Call devenv (visual studio)
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Command output:", result.stdout)
        print("Command error:", result.stderr)
        if not config['settings']['disableCompileMessage']: 
            infoPrompt(f"'{projectName}' rebuilt successfully.")
    except subprocess.CalledProcessError as e:
        errorPrompt("Could not compile.")
        print(e)
        return False

def findDevenv():
    "Returns the path of the visual studio executable"

    # Check if we have it saved first
    if appdataSavedVars.get("devenvPath") is not None:
        if os.path.exists(appdataSavedVars["devenvPath"]):
            return appdataSavedVars["devenvPath"]
    
    devenvPath = "C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE\devenv.exe"
    if os.path.exists(devenvPath):
        return devenvPath
    
    if os.path.exists("C:\Program Files\Microsoft Visual Studio"):
        vsPath = findHighestVersion("C:\Program Files\Microsoft Visual Studio")
        if vsPath is not None:
            devenvPath = findFile(vsPath, "devenv.exe")
            if devenvPath is not None:
                return devenvPath
            
    print("Could not find Visual Studio install directory. Please use -vsdir to select the directory.")
    return None


def findHighestVersion(root):
    "Returns the path to the folder with the higest number in the name"

    highest_version = 0
    highest_version_folder = ""

    for entry in os.scandir(root):
        if entry.is_dir():
            try:
                version_number = int(entry.name)
                if version_number > highest_version:
                    highest_version = version_number
                    highest_version_folder = entry.path
            except ValueError:
                continue

    return highest_version_folder


# if it works it ain't stupid
def checkgpf():
    "Check if we can generate project files"

    # Check if we have a uproject file
    if uprojectPath is None:
        return {'success': False, 'message': 'Could not find uproject file.'}

    if appdataSavedVars["ubtPath"] is not None:
        if os.path.exists(appdataSavedVars["ubtPath"]):
            return {'success': True, 'message': ''}

    # Get engine version from uproject file
    uprojectData = None
    if uprojectPath is not None:
        with open(uprojectPath, 'r') as openfile:
                    uprojectData = json.load(openfile)
    else:
        return {'success': False, 'message': 'Could not find uproject file.'}

    # Get the specific engine version install directory
    key_path = r"SOFTWARE\EpicGames\Unreal Engine"
    key_path = os.path.join(key_path, uprojectData['EngineAssociation'])
    installed_directory = None

    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
        installed_directory = winreg.QueryValueEx(key, "InstalledDirectory")[0]
        winreg.CloseKey(key)
    except FileNotFoundError:
        pass
    if installed_directory is not None:
        if findFile(installed_directory, "UnrealBuildTool.exe") is not None:
            return {'success': True, 'message': ''}
    else:
        return {'success': False, 'message': 'Could not find Unreal Engine install directory. Please use -uedir to select the directory.'}


def main():
    loadData()
    if checkArgs():
        processArgs(initArgs())
    else:
        # Check if we are in an unreal directory
        if checkDirectory() == False: return
        delete()

        if config['settings']['generateProjectFiles'] == True:
            if generateProjectFiles() == False: return
            
        # We do an extra check in case the user modified the json file
        if config['settings']['compile'] == True and config['settings']['generateProjectFiles'] == True:
            if compile() == False: return
          
if __name__ == "__main__":
    main()