import os, sys, click, traceback

version = None
currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, currentDir)

try:
    from commonLib import showVersion
except Exception as errMsg:
    print(f'\nKeystack run error: {traceback.format_exc(None, errMsg)}')

try:
    from CLI.RunKeystack import commands as runKeystackParams
except Exception as errMsg:
    print(f'\nKeystack run error: {traceback.format_exc(None, errMsg)}')

try:
    version = showVersion(stdout=False)
except Exception as errMsg:
    print(f'\nKeystack run error: {traceback.format_exc(None, errMsg)}')


from CLI.InstallKeystack import commands as installKeystackParams
from CLI.Env import commands as Env
# from CLI.Env.Reserve import commands as ReserveEnv
# from CLI.Env.Release import commands as ReleaseEnv
# from CLI.Env.ReleaseOnFailure import commands as ReleaseEnvOnFailure
# from CLI.Env.Reset import commands as Reset

class Keystack:
    @click.version_option(version)
    @click.group(help="CLI commands to manage Keystack")    
    def run():    
        pass


try:
    if os.path.exists('/opt/KeystackTests'):
        Keystack().run.add_command(runKeystackParams.run, name='run')
except Exception as errMsg:
       print(f'\nKeystack run error: {traceback.format_exc(None, errMsg)}')


Keystack().run.add_command(installKeystackParams.setup, name='setup')
Keystack().run.add_command(installKeystackParams.upgrade, name='upgrade')
#Keystack().run.add_command(Env.manage, name='env')
#Keystack().run.add_command(Env.reserve, name='reserveEnv')
#Keystack().run.add_command(Env.release, name='releaseEnv')
#Keystack().run.add_command(Env.releaseOnFailure, name='releaseEnvOnFailure')
#Keystack().run.add_command(Env.reset, name='reset')

if __name__ == "__main__":
    Keystack().run()
    

        
