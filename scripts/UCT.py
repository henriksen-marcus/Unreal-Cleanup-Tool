# Unreal Cleanup Tool (UCT) by Marcus Henriksen

# This program is designed to delete unreal engine
# temporary files with only one click. List of files to 
# delete is also customizable.

import argparse
from argparse import RawTextHelpFormatter
import subprocess
import shutil
import json
import glob
import sys
import os
from os.path import exists


config = {
    'files':[],
    'folders':['.vs', 'Binaries', 'DerivedDataCache', 'Intermediate'],
    'extensions':['.sln']
}

defaultFolders = ['.vs', 'Binaries', 'DerivedDataCache', 'Intermediate']
defaultExtensions = ['.sln']

path = os.path.dirname(os.path.abspath(__file__))


def initArgs():
    # Program description
    parser = argparse.ArgumentParser(description = '''
    ### Unreal Cleanup Tool ###\n\n
    Deletes specified files and folders with one click
    ''', formatter_class=RawTextHelpFormatter)

    # Arguments
    parser.add_argument('-a', help='Add a file to delete list', type=str, metavar='[filename].[ext]')
    parser.add_argument('-r', help='Remove a file from delete list', type=str, metavar='[filename].[ext]')
    parser.add_argument('-af', help='Add a folder to delete list', type=str, metavar='[foldername]')
    parser.add_argument('-rf', help='Remove a folder from delete list', type=str, metavar='[foldername]')
    parser.add_argument('-ae', help='Add a file extension to the delete list', type=str, metavar='[ext]')
    parser.add_argument('-re', help='Remove a file extension from the delete list', type=str, metavar='[ext]')
    parser.add_argument('-list', help='Show the list of files and folders', action='store_true')
    parser.add_argument('-reset', help='Reset delete list to default', action='store_true')

    # Check user's arguments and add them to array
    return parser.parse_args()


# Check if there are any arguments, except the script call
def checkArgs():
    return True if len(sys.argv) < 2 else False


# Decide what to do depending on the arguments given
def processArgs(args):
    global config

    # Reset list
    if args.reset is not None:
        if args.reset:
            config.clear()

    # Add
    if args.a is not None:
        if args.a not in config['files']: # Avoid duplicates
            config['files'].append(args.a)
            print(f'Added {args.a}')
        else:
            print(f'{args.a} is already in the list.')

    # Remove
    if args.r is not None:
        try:
            i = config['files'].index(args.r)
            try:  
                config['files'].pop(i)
                print(f'Removed {args.r}')
            except IndexError:
                print(f"'{args.r}' does not exists in the list!'")
        except ValueError:
            print(f"'{args.r}' does not exists in the list!'")
    
    # Add folder
    if args.af is not None:
        if args.af not in config['folders']: # Avoid dupliates
            # Check for symbolised default argument
            if ('/' + args.af) in config['folders']:
                try:
                    i = config['folders'].index('/' + args.af)
                    # Rename
                    config['folders'][i] = args.af
                except ValueError:
                    pass
            else:
                config['folders'].append(args.af)
            print(f'Added {args.af}')
        else:
            print(f'{args.af} is already in the list.')

    # Remove folder
    if args.rf is not None:
        try:
            i = config['folders'].index(args.rf)
            try:
                # Replace with symboled version, so we don't lose defaults
                if args.rf in defaultFolders:
                    config['folders'][i] = '/' + config['folders'][i]
                else:
                    config['folders'].pop(i)
                print(f'Removed {args.rf}')
            except IndexError:
                print(f"'{args.rf}' does not exists in the list!'")
        except ValueError:
            print(f"'{args.rf}' does not exists in the list!'")


    # Add extension
    if args.ae is not None:
        # Add . at the start and prevent user error
        mod = '.' + args.ae.replace('.', '')
        # Avoid duplicates
        if mod not in config['extensions']: 
            # Check for symbolised default argument
            if ('/' + mod) in config['extensions']:
                try:
                    i = config['extensions'].index('/' + mod)
                    config['extensions'][i] = mod
                except ValueError:
                    pass
            else:
                config['extensions'].append(mod)
            print(f'Added {mod}')
        else:
            print(f'{args.a} is already in the list.')

    # Remove extension
    if args.re is not None:
        mod = '.' + args.re.replace('.', '')
        try:
            i = config['extensions'].index(mod)
            try:
                config['extensions'].pop(i)
                if args.r in defaultExtensions:
                    # Add a '/' to mark it as disabled, also this 
                    # symbol cannot be used in folder names
                    config['extensions'].append('/' + args.re)
                print(f'Removed {mod}')
            except IndexError:
                print(f"'{mod}' does not exists in the list!'")
        except ValueError:
            print(f"'{mod}' does not exists in the list!'")

    # Show list
    if args.list is not None:
        if args.list:
            tmp = config
            indent = "    "
            # Remove disabled default arguments
            for key in tmp:
                print(f'{key.capitalize()}:')
                for value in tmp[key]:
                    if value[0] != '/':
                        print(indent + value)

    saveData()


# Perform delete operation on all listed items
def delete():
    num_deleted = 0
    for i, val in enumerate(config['files']):
        if val[0] == '/': continue
        try:
            os.remove(config['files'][i])
            num_deleted += 1
        except FileNotFoundError:
            pass

    for i, val in enumerate(config['folders']):
        if val[0] == '/': continue
        try:
            shutil.rmtree(config['folders'][i])
            num_deleted += 1
        except FileNotFoundError:
            pass

    for i, val in enumerate(config['extensions']):
        if val[0] == '/': continue
        for file in glob.glob('*' + config['extensions'][i], root_dir = path, include_hidden = True):
            try:
                os.remove(file)
                num_deleted += 1
            except FileNotFoundError:
                pass
        

    s = "s" if num_deleted > 1 or num_deleted == 0 else ""
    print(f'Deleted {num_deleted} file{s}/folder{s}.')
    

# Load config
def loadData():
    global config
    # Load saves files and folders
    if os.path.exists('uct_config.json'):
        with open('uct_config.json', 'r') as openfile:
            # Reading from json file
            config = json.load(openfile)


def saveData():
    # Serialize
    json_object = json.dumps(config, indent=4)

    if exists("uct_config.json"):
        # NOTE: PermissionError if opening mode is not 'r+'. 
        # Python cannot open hidden files that way.
        fileMode = 'r+'
    else:
        # Create new file
        fileMode = 'w'

    with open("uct_config.json", fileMode) as outfile:
        outfile.write(json_object)
        try:
            # Make file hidden
            subprocess.check_call(["attrib","+H","uct_config.json"])
        except PermissionError:
            pass
    


def main():
    loadData()
    delete() if checkArgs() else processArgs(initArgs())

        
if __name__ == "__main__":
    main()