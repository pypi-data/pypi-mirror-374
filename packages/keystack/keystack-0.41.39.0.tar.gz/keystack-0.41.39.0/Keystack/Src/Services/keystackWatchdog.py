import sys, os, time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

currentDir = os.path.abspath(os.path.dirname(__file__))
keystackRootPath = currentDir.replace('/Services', '')
sys.path.insert(0, keystackRootPath)

from keystackUtilities import chownChmodFolder, readYaml
from globalVars import GlobalVars

keystackObj = readYaml('/etc/keystack.yml')

# Ex: /opt/KeystackSystem
keystackSystemPath = keystackObj['keystackSystemPath']
keystackTestPath = keystackObj["keystackTestRootPath"]
    
# Define a custom event handler
class MyHandler(FileSystemEventHandler):
    def __init__(self, excluded_dirs):
        self.excluded_dirs = excluded_dirs

    def _is_excluded(self, path):
        # Check if the directory is in the excluded list
        for excluded in self.excluded_dirs:
            if excluded in path:
                return True
            
        return False

    def on_created(self, event):
        if event.is_directory:
            if self._is_excluded(event.src_path):
                return
            else:
                chownChmodFolder(f'{event.src_path}', user=GlobalVars.user, userGroup=GlobalVars.userGroup, permission=770)

    def on_deleted_deactived(self, event):
        if event.is_directory:
            if self._is_excluded(event.src_path):
                return
            else:
                print(f'Deleted Dir: {event.src_path}')
        else:
            if self._is_excluded(event.src_path) is False:
                print(f'Deleted file: {event.src_path}')    
    
    def on_closed(self, event):
        if self._is_excluded(event.src_path):
            return
        else:
            # if os.path.isdir(event.src_path):
            #     print(f'Dir on_closed: {event.src_path}')
                
            # if os.path.isfile(event.src_path):
            #     print(f'File on_closed: {event.src_path}')
            
            chownChmodFolder(f'{event.src_path}', user=GlobalVars.user, userGroup=GlobalVars.userGroup, permission=770)
                
    def on_modified_deactivated(self, event):
        if event.is_directory:
            if self._is_excluded(event.src_path):
                return
            else:
                chownChmodFolder(f'{event.src_path}', user=GlobalVars.user, userGroup=GlobalVars.userGroup, permission=770)
        else:
            if self._is_excluded(event.src_path) is False:
                chownChmodFolder(f'{event.src_path}', user=GlobalVars.user, userGroup=GlobalVars.userGroup, permission=770)
        
        
# List of directories to monitor
directories_to_watch = [keystackObj['keystackSystemPath'], 
                        keystackObj['keystackTestRootPath']]

excluded_dirs = [f'{keystackObj["keystackSystemPath"]}/Logs',
                 f'{keystackObj["keystackSystemPath"]}/MongoDB',
                 f'{keystackObj["keystackSystemPath"]}/ResultDataHistory',
                 f'{keystackObj["keystackSystemPath"]}/ServicesStagingArea'
                ]

# Initialize event handler with excluded directories
event_handler = MyHandler(excluded_dirs)

# Create an observer instance
observer = Observer()

# Schedule the observer to watch the directories
for directory in directories_to_watch:
    observer.schedule(event_handler, directory, recursive=True)
    
# Start the observer
observer.start()

try:
    while True:
        time.sleep(1)  # Keep the script running to monitor changes
except KeyboardInterrupt:
    observer.stop()
except Exception as e:
    print(f"Error: {e}")
    observer.stop()

observer.join()
