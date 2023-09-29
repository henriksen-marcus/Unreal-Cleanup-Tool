# Unreal Cleanup Tool

## What is it?
It's a small script with the purpose of quickly deleting unreal engine temporary files for C++ projects such as `Binaries`, `Intermediate` etc.

## What can it do?
It is configured to delete the temp files out of the box. You don't need to change any settings for it to work like expected.
However, the script allows you to modify what files, folders and extensions to delete. Additionally it can generate the visual studio project files for you.

## What do I need for it to work?
You need to have [Python](https://www.python.org/downloads/) installed to run the script, and a Windows system.

## :zap: How do I use it? 
Download the `UCT.py` file from [Releases](https://github.com/henriksen-marcus/Unreal-Cleanup-Tool/releases) and copy it to your unreal engine project directory. It should be on the same level as your `.uproject` file. Make sure unreal engine and visual studio is closed before running the script. Then double click on the `UCT.py` file to clean the project.

## ⚙️ Changing settings 
To change the settings you need to open the command line in the directory of the script.
To do this, navigate to the folder where your unreal project and script is, click on the address bar and type in `cmd`. <br>
![Pasted image](https://github.com/henriksen-marcus/Unreal-Cleanup-Tool/assets/89453098/4f2ae872-aafa-4bd3-94ea-cf5fcec8818d) <br>
Once the command prompt is open, you can now call on the script by typing
```
UCT.py -h
```
This will show a help message with all available commands and settings.

## Additional information
It's possible to compress the script into a single exe file making it run on PCs without Python, however due to the heavy compression of all the needed python source code it takes over 10 seconds to open. This takes away the main purpose of the script which is to save time.
I have plans to rewrite this program in a compiled language once I get time, which will allow for execution without a Python installation.
