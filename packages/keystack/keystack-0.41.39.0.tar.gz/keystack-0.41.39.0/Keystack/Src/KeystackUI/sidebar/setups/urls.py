from django.urls import include, path, re_path
from sidebar.setups.views import Setups, EnvLoadBalancer

# GetSetupTableData, EnvGroups, , EnvGroupsTableForDelete, CreateEnv, ViewEditEnv,  GetWaitList, GetActiveUsersList, RemoveFromWaitList, ReserveEnv, ReleaseEnv, RemoveFromActiveUsersList,  ReleaseEnvOnFailure, ResetEnv, 

urlpatterns = [
    path(r'', Setups.as_view(), name='setups'),
    #path(r'getSetupTableData', GetSetupTableData.as_view(), name='getSetupTableData'),
    #path(r'envGroups', EnvGroups.as_view(), name='envGroups'),
    #path(r'createEnv', CreateEnv.as_view(), name='createEnv'),
    #path(r'viewEditEnv', ViewEditEnv.as_view(), name='viewEditEnv'),
    #path(r'envWaitList', GetWaitList.as_view(), name='envWaitList'),
    #path(r'getActiveUsersList', GetActiveUsersList.as_view(), name='getActiveUsersList'),
    #path(r'reserveEnv', ReserveEnv.as_view(), name='reserveEnv'),
    #path(r'releaseEnv', ReleaseEnv.as_view(), name='releaseEnv'),
    #path(r'removeEnvFromWaitList', RemoveFromWaitList.as_view(), name='removeEnvFromWaitList'),
    #path(r'removeEnvFromActiveUsersList', RemoveFromActiveUsersList.as_view(), name='removeEnvFromActiveUsersList'),
    # path(r'releaseEnvOnFailure', ReleaseEnvOnFailure.as_view(), name='releaseEnvOnFailure'),
    # path(r'resetEnv', ResetEnv.as_view(), name='resetEnv'),
    
    #path(r'envGroupsTableForDelete', EnvGroupsTableForDelete.as_view(), name='envGroupsTableForDelete'),
    
    path(r'envLoadBalancer', EnvLoadBalancer.as_view(), name='envLoadBalancer'),
    
    #path(r'manualLockEnv', ManualLockEnv.as_view(), name='manualLockEnv'),
    #path(r'unlockEnv', UnlockEnv.as_view(), name='unlockEnv'),
]
