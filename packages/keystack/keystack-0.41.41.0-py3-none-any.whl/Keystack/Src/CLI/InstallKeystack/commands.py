import os
import sys
import click 
import traceback

currentDir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, currentDir.replace('/Src/CLI/InstallKeystack', ''))

# TODO: Need to move Setup to /Keystack folder
from BuildPackages.Setup import setupKeystack
from globalVars import GlobalVars

        
"""
Keystack setup|upgrade perform the followings on the local host:
   - pip install keystack
   - docker pull keystack:latest
   - docker pull mongo:4.6.2
   - docker compose up

Usage:
    keystack install setup -docker setup|upgrade
    keystack install setup -docker -docker_file <dockerKeystack tar file>
    keystack install upgrade -docker -docker_file <dockerKeystack tar file>
    keystack install setup -linux
    keystack install upgrade -linux
"""


@click.command()
@click.option('-docker',
              required=False, default=False, is_flag=True,
              help='Install Keystack docker container. Must include param -dockerFile <docker tar file>')

@click.option('-linux',   
              required=False, default=False, is_flag=True,  
              help='Installing or Upgrading Keystack on a local Linux host')

@click.option('-docker_file',
              required=False, 
              help='Keystack docker tar file. Obtained by the Keystack maintainer.')

@click.option('-version',   
              required=False, default=None, 
              help='The Keystack version to install')

# @click.argument('setup',
#                  required=False, default=False, type=bool)

# kwargs: All the above click.options in a dict
def setup(**kwargs):
    """ 
    Initial Keystack setup and installation.  Wipes out existing Keystack.
    """
    try:
        # setup: {'docker': False, 'linux': False, 'docker_file': None, 'version': None}
        click.echo(f'Install: {kwargs}')
        
        # docker pull hubertgee/keystack:0.41.1.0
        # docker pull mongo:{GlobalVars.mongoVersion}
        setupKeystack.Setup().setup(platform='docker', dockerBuildImagePath=None, version=kwargs['version'])
        
    except KeyboardInterrupt:
        pass
    
    except Exception as errMsg:
        pass


@click.command()
@click.option('-docker',
              required=False, default=False, is_flag=True,
              help='Install Keystack docker container. Must include param -dockerFile <docker tar file>')

@click.option('-linux',   
              required=False, default=False, is_flag=True,  
              help='The saved pipeline name to run')

@click.option('-docker_file',
              required=False, type=str, 
              help='Keystack docker tar file')

@click.option('-version',   
              required=False, default=None, 
              help='The Keystack version to install')

# @click.argument('upgrade',
#                  required=False, default=False, type=bool)

#kwargs: all the above click.options in a dict
def upgrade(**kwargs):
    """ 
    Upgrade existing Keystack
    """
    try:
        click.echo(f'upgrade: {kwargs}')
        
        setupKeystack.Setup().update(platform='docker', dockerBuildImagePath=None, version=kwargs['version'])
        
    except KeyboardInterrupt:
        pass
    
    except Exception as errMsg:
        pass
