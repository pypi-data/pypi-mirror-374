Title: Run PyTest Sample
Description: Run any app using CLI command 
objective: sample
topology: L3
requirements:
   - List of requirements here

# The CLI that you would enter on the server to execute a script or app
cliCommands:
   - python3.10 /opt/KeystackTests/Modules/Demo/Scripts/plainPythonScript.py

# This is an optional way to include CLI args with the app
scriptCmdlineArgs:
   - -build1 image1.yml
   - -build2 image2.yml


