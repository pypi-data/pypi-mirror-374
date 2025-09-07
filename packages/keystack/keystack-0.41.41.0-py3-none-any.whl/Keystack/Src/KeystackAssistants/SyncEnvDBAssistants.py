import os, sys
from pydantic import Field, dataclasses
from globalVars import GlobalVars
from db import DB
from commonLib import getDockerInternalMongoDBIpAddress, getHttpIpAndPort
from keystackUtilities import readYaml
from execRestApi import ExecRestApi


@dataclasses.dataclass
class SyncEnvMgmtDBAssistant:
    """ 
    Env DB is synced in EnvMgmt:getEnvDetails() if the env has no data in MongoDB
    """
    def __post_init__(self):
        from EnvMgmt import ManageEnv
        keystackVersion = readYaml(GlobalVars.versionFile)['keystackVersion']
        keystackVersion = keystackVersion.replace('.', '')
        # keystacksetup_0200_keystack-net
        dockerNetworkLS = f'keystacksetup_{keystackVersion}_.*'
        mongoDockerInternalIp = getDockerInternalMongoDBIpAddress(searchPattern=dockerNetworkLS)
        
        self.envMgmtObj = ManageEnv(mongoDBDockerInternalIp=mongoDockerInternalIp)
        keystackHttpIpAddress, keystackIpPort = getHttpIpAndPort()
        self.execRestApiObj = ExecRestApi(ip=keystackHttpIpAddress, port=keystackIpPort)
        
    def syncEnvMgmtDB(self):
        """ 
        Check if all the envs in EnvMgmt MongoDB exists in
        yml files.  If any env yaml files don't exists in MongoDB, remove the
        env in the EnvMgmt MongoDB
        """
        self.envMgmtObj.syncEnvMgmtDBWithEnvYamlFiles()
        
    def syncEnvYmlFilesToEnvmgmtDB(self):
        """ 
        Check if all the env yaml files exists in the EnvMgmt MongoDB.
        If not, add the envs in MongoDB.
        """
        for root, dirs, files in os.walk(f'{GlobalVars.envPath}'):
            for file in files:
                envDomainPath = f'{root}/{file}'.split(f'{GlobalVars.envPath}/')[-1]
                
                self.envMgmtObj.setenv = envDomainPath
                if self.envMgmtObj.isEnvExists() == False:
                    self.envMgmtObj.addEnv()
                    
    def syncLoadBalanceGroup(self):
        """ 
        Verify if all the envs in each Load Balance Group still exist.
        Remove the envs from the LBGs if they don't exist
        """
        loadBalancers = DB.name.getDocuments(collectionName='envLoadBalanceGroups',
                                             fields={}, 
                                             includeFields={'_id':0}, 
                                             sortBy=[('name', 1)])
                
        for index, eachLoadBalancer in enumerate(loadBalancers):
            # {'_id': ObjectId('645d60a27c534d5996dc8d0b'), 'name': 'Qa'}
            loadBalanceGroupName = eachLoadBalancer['name']
            envs = eachLoadBalancer['envs']
            removeSelectedEnvs = []
            
            for env in envs:
                envFullPath = f'{GlobalVars.envPath}/{env}.yml'
                if os.path.exists(envFullPath) is False:
                    removeSelectedEnvs.append(env)
            
            if len(removeSelectedEnvs) > 0:        
                params = {'loadBalanceGroup': loadBalanceGroupName, 
                          'removeSelectedEnvs': removeSelectedEnvs, 'webhook': True}
                restApi = '/api/v1/env/loadBalanceGroup/removeEnvs'
                response = self.execRestApiObj.post(restApi=restApi, params=params, showApiOnly=True) 

    def syncAll(self):
        self.syncEnvMgmtDB()
        self.syncEnvYmlFilesToEnvmgmtDB()
        self.syncLoadBalanceGroup()    