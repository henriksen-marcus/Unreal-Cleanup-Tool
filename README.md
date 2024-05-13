# Unreal Cleanup Tool

⚠ This program is superseded by [unreal-utility](https://github.com/henriksen-marcus/unreal-utility). It's not worked on anymore and might not work like expected.

## What is it?
It's a python script with the purpose of quickly deleting unreal engine temporary files for C++ projects such as `Binaries`, `Intermediate` etc.

## What can it do?
Delete the default temporary files in your project, and any additional files, folders or file extensions you add.

## What do I need for it to work?
You need to have [Python](https://www.python.org/downloads/) installed to run the script, and a Windows system.
Other than that, it's configured out of the box. You don't need to change any settings for it to work like expected.

## :zap: How do I use it? 
Download `UCT.py` file from [Releases](https://github.com/henriksen-marcus/Unreal-Cleanup-Tool/releases) and copy it to your unreal engine project directory. It should be on the same level as your `.uproject` file. **Make sure unreal engine and visual studio is closed before running the script.** Then double click on the `UCT.py` file to clean the project.

## ⚙️ Changing settings 
To change the settings and define additional files/folders to delete, open the command line in the directory of the script.
To do this, navigate to the folder where your unreal project and script is, click on the address bar and type in `cmd`. <br>
![Pasted image](https://github.com/henriksen-marcus/Unreal-Cleanup-Tool/assets/89453098/4f2ae872-aafa-4bd3-94ea-cf5fcec8818d) <br>
With the command prompt open, call on the script by typing
```
UCT.py -h
```
This will display a help message with all available commands and settings.

## Additional information
It's possible to compress the script into a single exe file making it run on PCs without Python, but due to the heavy compression of all the needed python source code, the program takes over 10 seconds to open. This takes away the main purpose of the script which is to save time.
~~I have plans to rewrite this program in a compiled language once I get time, which will allow for execution without a Python installation.~~ New version here: [unreal-utility](https://github.com/henriksen-marcus/unreal-utility)
