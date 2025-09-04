import click 
import traceback

"""
Env management: 
   show active-users
   make reservatioins
   release reservation
   reset
   releaseOnFailure

Usage:
   keystack env list -domain <domain>
   keystack env show_active_users -domain <domain> -env <env> 
   keystack env reserve -domain <domain> -env <env>
   keystack env release -domain <domain> -env <env>
   keystack env reset -domain <domain> -env <env>
   keystack env release_on_failure -session_id <session ID>
"""


@click.command()
@click.argument('list',
                 required=False)

@click.argument('show_active_users',
                 required=False)

@click.argument('reserve',
                 required=False)

@click.argument('release',
                 required=False)

@click.argument('reset',
                 required=False)

@click.argument('release_on_failure',
                 required=False)

@click.option('-domain',
              required=False, default=False, type=str,
              help='Install Keystack docker container. Must include param -dockerFile <docker tar file>')

@click.option('-env',   
              required=False, default=False, type=str,  
              help='The saved pipeline name to run')

@click.option('-session_id',
              required=False, type=str, 
              help='Keystack docker tar file')


# kwargs: all the above click.options in a dict
def manage(**kwargs):
    """ 
    Manage Envs
    """
    try:
        click.echo(f'Manage Envs: {kwargs}')
        
    except KeyboardInterrupt:
        pass
    
    except Exception as errMsg:
        pass


'''
#kwargs: all the above click.options in a dict
@click.command()
def upgrade(**kwargs):
    """ 
    Upgrade existing Keystack
    """
    try:
        click.echo(f'upgrade: {kwargs}')
        
    except KeyboardInterrupt:
        pass
    
    except Exception as errMsg:
        pass
'''
