from commonLib import showVersion

from django.urls import include, path, re_path
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from topbar.docs.restApi.views import RestAPI
from topbar.docs.restApi.userGuides import UserGuidesMenu, UserGuide

from topbar.docs.restApi.redis import UpdateOverallSummaryData, UpdateEnvMgmt, ReadEnvMgmt

from topbar.docs.restApi.system import GetSystemSettings, ModifySystemSettings, GetSystemPaths, GetServerTime, GetInstantMessages, Ping, VerifyVersion, GetUserAllowedDomainsAndRoles, SystemBackup, SystemRestore, GetBackupFilesTable, DownloadBackupFile, UploadBackupFile, DeleteBackupFiles, WebsocketDemo
from topbar.docs.restApi.systemLogs import GetLogMessageTopics, GetLogMessages, DeleteLogs
from topbar.docs.restApi.fileMgmtViews import GetFileContents, ModifyFile
from topbar.docs.restApi.loginCredentials  import LoginCredentials
from topbar.docs.restApi.controllers import AddController, DeleteControllers, GetControllers, GetControllerList, RegisterRemoteAccessKey, GetAccessKeys, RemoveAccessKeys, GenerateAccessKey

from topbar.docs.restApi.reservations import GetDomainUsers, GetSchedulerCount

from topbar.docs.restApi.domains import GetDomains, CreateDomain, DeleteDomains, GetAllUsersTableData, GetDomainsDropdown, AddUserGroupsToDomain, RemoveUserGroupsFromDomain, GetDomainUserGroups, IsUserAllowedInDomain, AddUsersToDomains, RemoveUsersFromDomains

from topbar.docs.restApi.accountMgr import GetDomainSelectionForUserAccount, RemoveDomainsFromUserAccount, AddUser, DeleteUser, GetUserAccountTableData, GetUserDetails, ModifyUserAccount, GetApiKey, GetPassword, RegenerateApiKey, GetApiKeyFromRestApi, IsApiKeyValid
from topbar.docs.restApi.userGroup import GetUserAccountDataTable, CreateUserGroup, DeleteUserGroups, GetUserGroupsDropdown, AddUsersToUserGroup, RemoveUsersFromUserGroup, GetUserGroupUsers, GetUserGroupTable

from topbar.docs.restApi.pipelineViews import GetSessions, GetSessionDomains, GetSessionDetails, GetPipelines, GetPipelineTableData, GetPipelinesDropdown, SavePipeline,  DeletePipelineSessions, DeletePipelines, GetTestReport, GetTestLogs, TerminateProcessId, ResumePausedOnFailure, ScheduledJobs, AddJobSchedule,  DeleteScheduledJob, GetJobSchedulerCount, GetCronScheduler, GetTestcasesInProgress, GetTestConfigsDropdownForPipeline, GetTestConfigsList, DeleteTestConfigs, GetTestConfigParams, SaveNewTestConfigsToFile

from topbar.docs.restApi.playbookViews import GetPlaybooks, CreatePlaybook, DeletePlaybooks, IsExists, RunPlaybook, GetPlaybookDetails, GetPlaybookEnvDetails, GetPlaybookPlaylist, PlaybookTemplate, PlaybookGroups, GetPlaybookNames, AddPlaybookSchedule, DeleteScheduledPlaybook, ScheduledPlaybooks, GetPlaybookCronScheduler  

from topbar.docs.restApi.pipelineStatusViews import GetPipelineStatus, Pipelines, Report

from topbar.docs.restApi.envViews import GetEnvTableData, CreateEnv, DeleteEnvs, GetEnvs, EnvGroups, GetEnvGroups, DeleteEnvGroups, ViewEditEnv, EnvGroupsTableForDelete, IsEnvAvailableRest, GetActiveUsers, ReserveEnvUI, GetWaitList, AmINext, Reset, ForceRemoveFromActiveUsersList, RemoveFromActiveUsersListUI, RemoveEnvFromWaitList, GetActiveUsersList, RemoveFromActiveUsersList, ReserveEnv, ReleaseEnv, ReleaseEnvOnFailure, ResetEnv, GetEnvGroupsDropdownForUserGroupMgmt, AddEnvSchedule, DeleteScheduledEnv, ScheduledEnvs, GetEnvCronScheduler, GetAutoSetupTaskCreatorTemplate, UpdateEnv, UpdateEnvActiveUsersAndWaitList, SetShareable

from topbar.docs.restApi.portMgmt import GetSidebarMenu, GetPortConnections, SelectPortGroupToAddPorts, SelectPortGroupToRemovePorts, AddPortsToPortGroup, RemovePortsFromPortGroup, GetConnectPortsToLinkDeviceDropdown, ConnectToLinkDevice, DisconnectPorts, SetRemotePortConnection, TestConnection, SetPortMultiTenant, SetOpticMode, SetPortType, SetPortSpeed, SetVlanId, PortConnectionAddKey, PortConnectionGetRemoveKeysTable, PortConnectionRemoveKeys, ModifyPortAdditionalKeyValue, PortMgmtAddFieldOption, PortMgmtRemoveFieldOptions

from topbar.docs.restApi.labInventory import GetInventoryDomains, CreateInitialDeviceFilters, GetDeviceTypeFilterOptions, GetDeviceTypeOptions, GetDeviceTypeDropdownForEditing, GetDeviceTypeFilterMgmtTable, AddDeviceType, RemoveDeviceType, GetDeviceLocationFilterOptions, GetDeviceLocationOptions, GetDeviceLocationDropdownForEditing, GetDeviceLocationFilterMgmtTable, AddDeviceLocation, RemoveDeviceLocation, GetDeviceVendorFilterOptions, GetDeviceVendorOptions, GetDeviceVendorDropdownForEditing, GetDeviceVendorFilterMgmtTable, AddDeviceVendor, RemoveDeviceVendor, AddDevice, DeleteDevices, EditDevice, GetDevices, AddPorts, RemovePorts, ExportCSV, ImportCSV, GetDevicePassword, GetDomainEnvsDropdownMenu, GetDeviceNames, InventoryAddKey, RemoveKeysTable, RemoveKeys, ChangeDeviceAdditionalFieldValue, AddFieldOption, RemoveFieldOptions, TestConnection

from topbar.docs.restApi.portGroup import GetPortGroupDomains, CreatePortGroup,  GetPortGroupTableData, DeletePortGroups, GetPortsConfigurationTable,ReservePortGroupButton, ReservePortGroupUI, ReleasePortGroupButton, IsPortGroupAvailable, AmINextPortGroup, RemoveFromActiveUserListPortGroup, RemoveFromActiveUserListPortGroup2, RemoveFromWaitListPortGroup, ResetPortGroup, GetPortGroupActiveUsersMgmtTable, GetPortGroupWaitListTable, AddPortGroupSchedule, DeleteScheduledPortGroup, ScheduledPortGroups, GetPortGroupCronScheduler, UpdatePortGroupActiveUsersAndWaitList

from topbar.docs.restApi.linkLayer import ConfigureLinkLayer

from topbar.docs.restApi.loadBalanceEnvs import  CreateNewLoadBalanceGroup, DeleteLoadBalanceGroup, AddEnvsToLoadBalancGroup, GetLoadBalanceGroups, GetAllEnvs, GetLoadBalanceGroupEnvs, GetLoadBalanceGroupEnvsUI, RemoveAllEnvsFromLoadBalanceGroup, RemoveSelectedEnvsRest, ResetLoadBalanceGroupRest

from topbar.docs.restApi.testcaseViews import GetTestcaseDetails, GetTestcasesInternal

from topbar.docs.restApi.modules import GetModules, GetModuleDetails
from topbar.docs.restApi.testcases import GetTestcaseGroupFolders, GetTestcaseDetails

from topbar.docs.restApi.appsViews import GetApps, RemoveApps, GetAvailableApps, GetAppDescription, GetAppStoreAppDescription, UpdateApps, InstallApps

from topbar.docs.restApi.testResults import SidebarTestResults, GetNestedFolderFiles, GetTestResultPages, ArchiveResults, DeleteAllInDomain, DeleteAllInPlaybook, DeleteResults, DownloadResults

from topbar.docs.restApi.awsS3 import GetAwsS3Uploads, DeleteAwsS3Uploads, RestartAwsS3Service, StopAwsS3Service, IsAwsS3ServiceRunning, GetAwsS3Logs, ClearAwsS3Logs, DisableAwsS3DebugLogs, EnableAwsS3DebugLogs, IsAwsS3DebugEnabled, GetPipelineAwsS3LogFiles

from topbar.docs.restApi.utilitilizations import GetEnvBarChart, GetUserUsageBarChart

from django.views.generic import RedirectView

schemaView = get_schema_view(
    openapi.Info(
        basePath='/api/v1/restAPI',
        title="Keystack ReST APIs",
        default_version=showVersion(),
        #description="Automating test and lab management",
        #terms_of_service="https://www.keysight.com",
        contact=openapi.Contact(email="hubert.gee@keysight.com"),
        #license=openapi.License(name="Hubert Gee"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
    
# REST APIs
urlpatterns = [
    path('v1/modules',                            GetModules.as_view(),                    name='getModules'),
    path('v1/modules/details',                    GetModuleDetails.as_view(),              name='getModuleDetails'),
    
    path('v1/testcases',                          GetTestcaseGroupFolders.as_view(),       name='hetTestcaseGroupFolders'),
    path('v1/testcases/details',                  GetTestcaseDetails.as_view(),            name='getTestcaseDetails'),
       
    path('v1/fileMgmt/getFileContents',           GetFileContents.as_view(),               name='getFileContents'),
    path('v1/fileMgmt/modifyFile',                ModifyFile.as_view(),                    name='modifyFile'),

    path('v1/redis/updateOverallSummaryData',     UpdateOverallSummaryData.as_view(),      name='updateOverallSummaryData'),
    path('v1/redis/updateEnvMgmt',                UpdateEnvMgmt.as_view(),                 name='updateEnvMgmt'),
    path('v1/redis/readEnvMgmt',                  ReadEnvMgmt.as_view(),                   name='readEnvMgmt'),
        
    path('v1/results/pages',                      GetTestResultPages.as_view(),            name='getTestResultPages'),
    path('v1/results/nestedFolderFiles',          GetNestedFolderFiles.as_view(),          name='getNestedFolderFiles'),
    path('v1/results/sidebarMenu',                SidebarTestResults.as_view(),            name='sidebarTestResults'),
    path('v1/results/archive',                    ArchiveResults.as_view(),                name='archiveResults'),
    path('v1/results/deleteAllInDomain',          DeleteAllInDomain.as_view(),             name='testResultsDeleteAllInDomain'),
    path('v1/results/deleteAllInPlaybook',        DeleteAllInPlaybook.as_view(),           name='testResultsDeleteAllInPlaybook'),
    path('v1/results/delete',                     DeleteResults.as_view(),                 name='deleteResults'),
    path('v1/results/downloadResults',            DownloadResults.as_view(),               name='downloadResults'),
       
    #path('v1/playbook/login',                    RedirectView.as_view(url='http://192.168.28.7:8000')),        
    path('v1/playbook/groups',                    PlaybookGroups.as_view(),                name='playbookGroups'),
    path('v1/playbook/template',                  PlaybookTemplate.as_view(),              name='getPlaybookTemplate'),
    path('v1/playbook/isExists',                  IsExists.as_view(),                      name='isPlaybookExists'),
    path('v1/playbook/details',                   GetPlaybookDetails.as_view(),            name='getPlaybookDetails'),
    path('v1/playbook/playlist',                  GetPlaybookPlaylist.as_view(),           name='getPlaybookPlaylist'),   
    path('v1/playbook/env/details',               GetPlaybookEnvDetails.as_view(),         name='getPlaybookEnvDetails'), 
    path('v1/playbook/runPlaybook',               RunPlaybook.as_view(),                   name='runPlaybook'),
    path('v1/playbook/names',                     GetPlaybookNames.as_view(),              name='getPlaybookNames'),
    path('v1/playbook/get',                       GetPlaybooks.as_view(),                  name='getPlaybooks'),
    path('v1/playbook/create',                    CreatePlaybook.as_view(),                name='createPlaybook'),
    path('v1/playbook/delete',                    DeletePlaybooks.as_view(),               name='deletePlaybooks'),  
    
    path('v1/playbook/scheduler/add',                AddPlaybookSchedule.as_view(),        name='addPlaybookSchedule'), 
    path('v1/playbook/scheduler/delete',             DeleteScheduledPlaybook.as_view(),    name='deleteScheduledPlaybook'), 
    path('v1/playbook/scheduler/scheduledPlaybooks', ScheduledPlaybooks.as_view(),         name='scheduledPlaybooks'), 
    path('v1/playbook/scheduler/getCronScheduler',   GetPlaybookCronScheduler.as_view(),   name='getPlaybookCronScheduler'), 
           
    path('v1/pipeline/status',                    GetPipelineStatus.as_view(),             name='getPipelineStatus'),
    path('v1/pipeline/report',                    Report.as_view(),                        name='report'),
    path('v1/pipelines',                          Pipelines.as_view(),                     name='pipelines'),
    path('v1/pipeline/getPipelines',              GetSessions.as_view(),                   name='getSessions'),
    path('v1/pipeline/getSessionDetails',         GetSessionDetails.as_view(),             name='getSessionDetails'),     
    path('v1/pipelinesUI',                        GetPipelines.as_view(),                  name='getPipelines'),
    path('v1/pipelines/tableData',                GetPipelineTableData.as_view(),          name='getPipelineTableData'),
    path('v1/pipelines/dropdown',                 GetPipelinesDropdown.as_view(),          name='getPipelinesDropdown'),
    path('v1/pipelines/deletePipelineSessions',   DeletePipelineSessions.as_view(),        name='deletePipelineSessions'),
    path('v1/pipelines/delete',                   DeletePipelines.as_view(),               name='deletePipelines'),
    path('v1/pipelines/getTestReport',            GetTestReport.as_view(),                 name='getTestReport'),
    path('v1/pipelines/getTestLogs',              GetTestLogs.as_view(),                   name='getTestLogs'),
    path('v1/pipelines/terminateProcessId',       TerminateProcessId.as_view(),            name='terminateProcessId'),
    path('v1/pipelines/save',                     SavePipeline.as_view(),                  name='savePipeline'),    
    path('v1/pipelines/resumePausedOnFailure',    ResumePausedOnFailure.as_view(),         name='resumePausedOnFailure'),
    path('v1/pipelines/getSessionDomains',        GetSessionDomains.as_view(),             name='getSessionDomains'),
    path('v1/pipelines/getTestcasesInProgress',   GetTestcasesInProgress.as_view(),        name='getTestcasesInProgress'),
    path('v1/pipelines/testConfigs/getTestConfigsDropdownForPipeline',  GetTestConfigsDropdownForPipeline.as_view(),    name='getTestConfigsDropdownForPipeline'),
    path('v1/pipelines/testConfigs/getTestConfigsList',                 GetTestConfigsList.as_view(),                   name='getTestConfigsList'),
    path('v1/pipelines/testConfigs/delete',                             DeleteTestConfigs.as_view(),                    name='deleteTestConfigs'),
    path('v1/pipelines/testConfigs/getParams',                          GetTestConfigParams.as_view(),                  name='getTestConfigParams'),
    path('v1/pipelines/testConfigs/saveNewTestConfigsToFile',           SaveNewTestConfigsToFile.as_view(),             name='saveNewTestConfigsToFile'),
            
    path('v1/pipelines/jobScheduler/getCronScheduler',     GetCronScheduler.as_view(),     name='getCronScheduler'),
    path('v1/pipelines/jobScheduler/getJobSchedulerCount', GetJobSchedulerCount.as_view(), name='getJobSchedulerCount'),
    path('v1/pipelines/jobScheduler/scheduledJobs',        ScheduledJobs.as_view(),        name='scheduledJobs'),
    path('v1/pipelines/jobScheduler/add',                  AddJobSchedule.as_view(),       name='addJobSchedule'),
    path('v1/pipelines/jobScheduler/delete',               DeleteScheduledJob.as_view(),   name='deleteScheduledJob'), 
             
    path('v1/testcase/details',                            GetTestcaseDetails.as_view(),   name='getTestcaseDetails'),
    path('v1/testcase/get',                                GetTestcasesInternal.as_view(), name='getTestcasesInternal'),
        
    path('v1/env/getEnvGroupsDropdownForUserGroupMgmt', GetEnvGroupsDropdownForUserGroupMgmt.as_view(), name='getEnvGroupsDropdownForUserGroupMgmt'),        
    path('v1/env/getEnvTableData',                      GetEnvTableData.as_view(),                      name='getEnvTableData'),
    path('v1/env/create',                               CreateEnv.as_view(),                            name='createEnv'),     
    path('v1/env/delete',                               DeleteEnvs.as_view(),                           name='deleteEnvs'),    
    path('v1/env/groups',                               GetEnvGroups.as_view(),                         name='getEnvGroups'),
    path('v1/env/envGroups',                            EnvGroups.as_view(),                            name='envGroups'),
    path('v1/env/deleteEnvGroups',                      DeleteEnvGroups.as_view(),                      name='deleteEnvGroups'),
    path('v1/env/viewEditEnv',                          ViewEditEnv.as_view(),                          name='viewEditEnv'),
    path('v1/env/envGroupsTableForDelete',              EnvGroupsTableForDelete.as_view(),              name='envGroupsTableForDelete'),
    path('v1/env/list',                                 GetEnvs.as_view(),                              name='getEnvs'),
    path('v1/env/envWaitList',                          GetWaitList.as_view(),                          name='envWaitList'),
    path('v1/env/amINext',                              AmINext.as_view(),                              name='amINext'),
    path('v1/env/isEnvAvailable',                       IsEnvAvailableRest.as_view(),                   name='isEnvAvailableRest'),
    path('v1/env/removeEnvFromWaitList',                RemoveEnvFromWaitList.as_view(),                name='removeEnvFromWaitList'),
    path('v1/env/getActiveUsersList',                   GetActiveUsersList.as_view(),                   name='getActiveUsersList'),
    path('v1/env/removeEnvFromActiveUsersList',         RemoveFromActiveUsersList.as_view(),            name='removeEnvFromActiveUsersList'),
    path('v1/env/reserveEnv',                           ReserveEnv.as_view(),                           name='reserveEnv'),
    path('v1/env/releaseEnv',                           ReleaseEnv.as_view(),                           name='releaseEnv'),
    path('v1/env/releaseEnvOnFailure',                  ReleaseEnvOnFailure.as_view(),                  name='releaseEnvOnFailure'),
    path('v1/env/resetEnv',                             ResetEnv.as_view(),                             name='resetEnv'),
    path('v1/env/reserve',                              ReserveEnvUI.as_view(),                         name='reserve'),
    path('v1/env/reset',                                Reset.as_view(),                                name='reset'),
    path('v1/env/activeUsers',                          GetActiveUsers.as_view(),                       name='activeUsers'),
    path('v1/env/removeFromActiveUsersListUI',          RemoveFromActiveUsersListUI.as_view(),          name='removeFromActiveUsersList'),
    path('v1/env/forceRemoveFromActiveUsersList',       ForceRemoveFromActiveUsersList.as_view(),       name='forceRemoveFromActiveUsersList'),
    path('v1/env/getAutoSetupTaskCreatorTemplate',      GetAutoSetupTaskCreatorTemplate.as_view(),      name='getAutoSetupTaskCreatorTemplate'),
    path('v1/env/setShareable',                         SetShareable.as_view(),                         name='setShareable'),
    path('v1/env/updateActiveUsersAndWaitList',         UpdateEnvActiveUsersAndWaitList.as_view(),      name='updateEnvActiveUsersAndWaitList'),
    path('v1/env/loadBalanceGroup/create',              CreateNewLoadBalanceGroup.as_view(),            name='createNewLoadBalanceGroup'),    
    path('v1/env/loadBalanceGroup/delete',              DeleteLoadBalanceGroup.as_view(),               name='deleteLoadBalanceGroup'),
    path('v1/env/loadBalanceGroup/addEnvs',             AddEnvsToLoadBalancGroup.as_view(),             name='addEnvsToLoadBalanceGroup'), 
    path('v1/env/loadBalanceGroup/get',                 GetLoadBalanceGroups.as_view(),                 name='getLoadBalanceGroups'),
    path('v1/env/loadBalanceGroup/getAllEnvs',          GetAllEnvs.as_view(),                           name='getAllEnvs'),  
    path('v1/env/loadBalanceGroup/getEnvsUI',           GetLoadBalanceGroupEnvsUI.as_view(),            name='getLoadBalanceGroupEnvsUI'),
    path('v1/env/loadBalanceGroup/getEnvs',             GetLoadBalanceGroupEnvs.as_view(),              name='getLoadBalanceGroupEnvs'),
    path('v1/env/loadBalanceGroup/removeAllEnvs',       RemoveAllEnvsFromLoadBalanceGroup.as_view(),    name='removeAllEnvsFromLoadBalanceGroup'),
    path('v1/env/loadBalanceGroup/removeEnvs',          RemoveSelectedEnvsRest.as_view(),               name='removeSelectedEnvs'),
    path('v1/env/loadBalanceGroup/reset',               ResetLoadBalanceGroupRest.as_view(),            name='resetLoadBalanceGroup'),
    path('v1/env/scheduler/add',                        AddEnvSchedule.as_view(),                       name='addEnvSchedule'),
    path('v1/env/scheduler/delete',                     DeleteScheduledEnv.as_view(),                   name='deleteScheduledEnv'),
    path('v1/env/scheduler/scheduledEnvs',              ScheduledEnvs.as_view(),                        name='scheduledEnvs'),
    path('v1/env/scheduler/getCronScheduler',           GetEnvCronScheduler.as_view(),                  name='getEnvCronScheduler'),
    path('v1/env/update',                               UpdateEnv.as_view(),                            name='updateEnv'),
        
    path('v1/scheduler/getDomainUsers',                 GetDomainUsers.as_view(),                       name='getDomainUsers'),
    path('v1/scheduler/getSchedulerCount',              GetSchedulerCount.as_view(),                    name='gGetSchedulerCount'),
                              
    path('v1/lab/inventory/domains',                             GetInventoryDomains.as_view(),                 name='getInventoryDomains'),
    path('v1/lab/inventory/createInitialDeviceFilters',          CreateInitialDeviceFilters.as_view(),          name='createInitialDeviceFilters'),
    path('v1/lab/inventory/getDevicePassword',                   GetDevicePassword.as_view(),                   name='getDevicePassword'),
    path('v1/lab/inventory/addPorts',                            AddPorts.as_view(),                            name='addPorts'),
    path('v1/lab/inventory/removePorts',                         RemovePorts.as_view(),                         name='removePorts'),

    path('v1/lab/inventory/addDeviceType',                       AddDeviceType.as_view(),                       name='addDeviceType'),
    path('v1/lab/inventory/removeDeviceType',                    RemoveDeviceType.as_view(),                    name='removeDeviceType'),
    path('v1/lab/inventory/getDeviceTypeOptions',                GetDeviceTypeOptions.as_view(),                name='getDeviceTypeOptions'),
    path('v1/lab/inventory/getDeviceTypeDropdownForEditing',     GetDeviceTypeDropdownForEditing.as_view(),     name='getDeviceTypeDropdownForEditing'), 
    path('v1/lab/inventory/getDeviceTypeFilterOptions',          GetDeviceTypeFilterOptions.as_view(),          name='getDeviceTypeFilterOptions'),
    path('v1/lab/inventory/getDeviceTypeFilterMgmtTable',        GetDeviceTypeFilterMgmtTable.as_view(),        name='getDeviceTypeFilterMgmtTable'),
        
    path('v1/lab/inventory/addDeviceLocation',                   AddDeviceLocation.as_view(),                   name='addDeviceLocation'),
    path('v1/lab/inventory/removeDeviceLocation',                RemoveDeviceLocation.as_view(),                name='removeDeviceLocation'),
    path('v1/lab/inventory/getDeviceLocationOptions',            GetDeviceLocationOptions.as_view(),            name='getDeviceLocationOptions'),
    path('v1/lab/inventory/getDeviceLocationDropdownForEditing', GetDeviceLocationDropdownForEditing.as_view(), name='getDeviceLocationDropdownForEditing'),   
    path('v1/lab/inventory/getDeviceLocationFilterOptions',      GetDeviceLocationFilterOptions.as_view(),      name='getDeviceLocationFilterOptions'),
    path('v1/lab/inventory/getDeviceLocationFilterMgmtTable',    GetDeviceLocationFilterMgmtTable.as_view(),    name='getDeviceLocationFilterMgmtTable'),
    
    path('v1/lab/inventory/addDeviceVendor',                     AddDeviceVendor.as_view(),                     name='addDeviceVendor'),
    path('v1/lab/inventory/removeDeviceVendor',                  RemoveDeviceVendor.as_view(),                  name='removeDeviceVendor'),
    path('v1/lab/inventory/getDeviceVendorOptions',              GetDeviceVendorOptions.as_view(),              name='getDeviceVendorOptions'),
    path('v1/lab/inventory/getDeviceVendorDropdownForEditing',   GetDeviceVendorDropdownForEditing.as_view(),   name='getDeviceVendorDropdownForEditing'), 
    path('v1/lab/inventory/getDeviceVendorFilterOptions',        GetDeviceVendorFilterOptions.as_view(),        name='getDeviceVendorFilterOptions'),
    path('v1/lab/inventory/getDeviceVendorFilterMgmtTable',      GetDeviceVendorFilterMgmtTable.as_view(),      name='getDeviceVendorFilterMgmtTable'),    
    
    path('v1/lab/inventory/addDevice',                           AddDevice.as_view(),                           name='addDevice'),
    path('v1/lab/inventory/deleteDevices',                       DeleteDevices.as_view(),                       name='deleteDevices'),
    path('v1/lab/inventory/editDevice',                          EditDevice.as_view(),                          name='editDevice'),
    path('v1/lab/inventory/testConnection',                      TestConnection.as_view(),                      name='testConnection'),
    path('v1/lab/inventory/getDevices',                          GetDevices.as_view(),                          name='getDevices'),
    path('v1/lab/inventory/exportCSV',                           ExportCSV.as_view(),                           name='exportCSV'),
    path('v1/lab/inventory/importCSV',                           ImportCSV.as_view(),                           name='importCSV'),
    path('v1/lab/inventory/getDomainEnvsDropdownMenu',           GetDomainEnvsDropdownMenu.as_view(),           name='getDomainEnvsDropdownMenu'),
    path('v1/lab/inventory/getDeviceNames',                      GetDeviceNames.as_view(),                      name='getDeviceNames'),
    path('v1/lab/inventory/addKey',                              InventoryAddKey.as_view(),                     name='InventoryAddKey'),
    path('v1/lab/inventory/removeKeysTable',                     RemoveKeysTable.as_view(),                     name='removeKeysTable'),
    path('v1/lab/inventory/removeKeys',                          RemoveKeys.as_view(),                          name='removeKeys'),    
    path('v1/lab/inventory/changeDeviceAdditionalFieldValue',    ChangeDeviceAdditionalFieldValue.as_view(),    name='changeDeviceAdditionalFieldValue'), 
    path('v1/lab/inventory/addFieldOption',                      AddFieldOption.as_view(),                      name='addFieldOption'),      
    path('v1/lab/inventory/removeFieldOptions',                  RemoveFieldOptions.as_view(),                  name='removeFieldOptions'), 
           
    path('v1/portMgmt/getSidebarMenu',                       GetSidebarMenu.as_view(),                      name='getSidebarMenu'),
    path('v1/portMgmt/getPortConnections',                   GetPortConnections.as_view(),                  name='getPortConnections'),
    path('v1/portMgmt/setRemotePortConnection',              SetRemotePortConnection.as_view(),             name='setRemotePortConnection'),
    path('v1/portMgmt/selectPortGroupToAddPorts',            SelectPortGroupToAddPorts.as_view(),           name='SelectPortGroupToAddPorts'),
    path('v1/portMgmt/selectPortGroupToRemovePorts',         SelectPortGroupToRemovePorts.as_view(),        name='SelectPortGroupToRemovePorts'),
    path('v1/portMgmt/setPortMultiTenant',                   SetPortMultiTenant.as_view(),                  name='setPortMultiTenant'),
    path('v1/portMgmt/setOpticMode',                         SetOpticMode.as_view(),                        name='setOpticMode'),
    path('v1/portMgmt/setPortType',                          SetPortType.as_view(),                         name='setPortType'),
    path('v1/portMgmt/setPortSpeed',                         SetPortSpeed.as_view(),                        name='setPortSpeed'),
    path('v1/portMgmt/setVlanId',                            SetVlanId.as_view(),                           name='setVlanId'),           
    path('v1/portMgmt/addPortsToPortGroup',                  AddPortsToPortGroup.as_view(),                 name='addPortsToPortGroup'),
    path('v1/portMgmt/removePortsFromPortGroup',             RemovePortsFromPortGroup.as_view(),            name='removePortsFromPortGroup'),
    path('v1/portMgmt/getConnectPortsToLinkDeviceDropdown',  GetConnectPortsToLinkDeviceDropdown.as_view(), name='getConnectPortsToLinkDeviceDropdown'),
    path('v1/portMgmt/connectToLinkDevice',                  ConnectToLinkDevice.as_view(),                 name='connectToLinkDevice'),
    path('v1/portMgmt/disconnectPorts',                      DisconnectPorts.as_view(),                     name='disconnectPorts'),
    path('v1/portMgmt/testConnection',                       TestConnection.as_view(),                      name='testConnection'),
    path('v1/portMgmt/portConnection/addKey',                PortConnectionAddKey.as_view(),                name='portConnectionAddKey'),
    path('v1/portMgmt/portConnection/removeKeysTable',       PortConnectionGetRemoveKeysTable.as_view(),    name='portConnectionGetRemoveKeysTable'),
    path('v1/portMgmt/portConnection/removeKeys',            PortConnectionRemoveKeys.as_view(),            name='portConnectionRemoveKeys'),
    path('v1/portMgmt/portConnection/modifyPortAdditionalKeyValue', ModifyPortAdditionalKeyValue.as_view(), name='modifyPortAdditionalKeyValue'),
    path('v1/portMgmt/portConnection/removeFieldOptions',    PortMgmtRemoveFieldOptions.as_view(),          name='PortMgmtRemoveFieldOptions'),
    path('v1/portMgmt/portConnection/addFieldOption',        PortMgmtAddFieldOption.as_view(),              name='PortMgmtAddFieldOption'),

    path('v1/portGroup/domains',                           GetPortGroupDomains.as_view(),                name='getPortGroupDomains'),           
    path('v1/portGroup/create',                            CreatePortGroup.as_view(),                    name='createPortGroup'),
    path('v1/portGroup/getTableData',                      GetPortGroupTableData.as_view(),              name='getPortGroupTableData'),
    path('v1/portGroup/delete',                            DeletePortGroups.as_view(),                   name='deletePortGroups'),
    path('v1/portGroup/portsTable',                        GetPortsConfigurationTable.as_view(),         name='portsTable'),
    path('v1/portGroup/reserveUI',                         ReservePortGroupUI.as_view(),                 name='reservePortGroupUI'),
    path('v1/portGroup/reserve',                           ReservePortGroupButton.as_view(),             name='reservePortGroup'),
    path('v1/portGroup/removeFromActiveUsersListUI',       RemoveFromActiveUserListPortGroup.as_view(),  name='removeFromActiveUserListPortGroup'),
    path('v1/portGroup/removeFromActiveUsersListManually', RemoveFromActiveUserListPortGroup2.as_view(), name='removeFromActiveUserListPortGroup2'),
    path('v1/portGroup/removeFromWaitList',                RemoveFromWaitListPortGroup.as_view(),        name='removeFromWaitListPortGroup'),
    path('v1/portGroup/release',                           ReleasePortGroupButton.as_view(),             name='releasePortGroup'),
    path('v1/portGroup/amINext',                           AmINextPortGroup.as_view(),                   name='amINextPortGroup'),
    path('v1/portGroup/isPortGroupAvailable',              IsPortGroupAvailable.as_view(),               name='isPortGroupAvailable'),
    path('v1/portGroup/reset',                             ResetPortGroup.as_view(),                     name='resetPortGroup'),
    path('v1/portGroup/activeUsersTable',                  GetPortGroupActiveUsersMgmtTable.as_view(),   name='getPortGroupActiveUsersMgmtTable'),
    path('v1/portGroup/waitListTable',                     GetPortGroupWaitListTable.as_view(),          name='getPortGroupWaitListTable'),
    path('v1/portGroup/updateActiveUsersAndWaitList',      UpdatePortGroupActiveUsersAndWaitList.as_view(), name='UpdatePortGroupActiveUsersAndWaitList'),
    path('v1/portGroup/scheduler/add',                     AddPortGroupSchedule.as_view(),               name='addPortGroupSchedule'),
    path('v1/portGroup/scheduler/delete',                  DeleteScheduledPortGroup.as_view(),           name='deleteScheduledPortGroup'),
    path('v1/portGroup/scheduler/scheduledPortGroups',     ScheduledPortGroups.as_view(),                name='scheduledPortGroups'),
    path('v1/portGroup/scheduler/getCronScheduler',        GetPortGroupCronScheduler.as_view(),          name='getPortGroupCronScheduler'),
    
    path('v1/linkLayer/configure',                         ConfigureLinkLayer.as_view(),                 name='configureLinkLayer'),
        
    path('v1/apps',                               GetApps.as_view(),                       name='getApps'),
    path('v1/apps/remove',                        RemoveApps.as_view(),                    name='removeApps'),
    path('v1/apps/getAvailableApps',              GetAvailableApps.as_view(),              name='getAvailableApps'),
    path('v1/apps/description',                   GetAppDescription.as_view(),             name='getAppDescription'),
    path('v1/apps/getAppStoreAppDescription',     GetAppStoreAppDescription.as_view(),     name='getAppStoreAppDescription'),
    path('v1/apps/update',                        UpdateApps.as_view(),                    name='updateApps'),
    path('v1/apps/install',                       InstallApps.as_view(),                   name='installApps'),

    path('v1/debug/awsS3/getUploads',             GetAwsS3Uploads.as_view(),               name='getAwsS3Uploads'),
    path('v1/debug/awsS3/deleteUploads',          DeleteAwsS3Uploads.as_view(),            name='deleteAwsS3Uploads'),
    path('v1/debug/awsS3/restartService',         RestartAwsS3Service.as_view(),           name='restartAwsS3Service'),
    path('v1/debug/awsS3/stopService',            StopAwsS3Service.as_view(),              name='stopAwsS3Service'),
    path('v1/debug/awsS3/isServiceRunning',       IsAwsS3ServiceRunning.as_view(),         name='isAwsS3ServiceRunning'),
    path('v1/debug/awsS3/getLogs',                GetAwsS3Logs.as_view(),                  name='getAwsS3Logs'),
    path('v1/debug/awsS3/clearLogs',              ClearAwsS3Logs.as_view(),                name='clearAwsS3Logs'),
    path('v1/debug/awsS3/enableDebugLogs',        EnableAwsS3DebugLogs.as_view(),          name='enableAwsS3DebugLogs'),
    path('v1/debug/awsS3/disableDebugLogs',       DisableAwsS3DebugLogs.as_view(),         name='disableAwsS3DebugLogs'),
    path('v1/debug/awsS3/isDebugEnabled',         IsAwsS3DebugEnabled.as_view(),           name='isAwsS3DebugEnabled'),
    path('v1/debug/awsS3/getPipelineLogFiles',    GetPipelineAwsS3LogFiles.as_view(),      name='getPipelineAwsS3LogFiles'),

    path('v1/system/paths',                       GetSystemPaths.as_view(),                name='getSystemPaths'),
    path('v1/system/systemBackup',                SystemBackup.as_view(),                  name='systemBackup'),
    path('v1/system/systemRestore',               SystemRestore.as_view(),                 name='systemRestore'),
    path('v1/system/downloadBackupFile',          DownloadBackupFile.as_view(),            name='downloadBackupFile'),
    path('v1/system/uploadBackupFile',            UploadBackupFile.as_view(),              name='uploadBackupFile'),
    path('v1/system/deleteBackupFiles',           DeleteBackupFiles.as_view(),             name='deleteBackupFiles'),
    path('v1/system/getBackupFilesTable',         GetBackupFilesTable.as_view(),           name='getBackupFilesTable'),
    path('v1/system/getSystemSettings',           GetSystemSettings.as_view(),             name='getSystemSettings'),
    path('v1/system/modifySystemSettings',        ModifySystemSettings.as_view(),          name='modifySystemSettings'),        
    path('v1/system/getInstantMessages',          GetInstantMessages.as_view(),            name='getInstantMessages'),
    path('v1/system/ping',                        Ping.as_view(),                          name='ping'),
    path('v1/system/serverTime',                  GetServerTime.as_view(),                 name='getServerTime'),
    path('v1/system/websocketDemo',               WebsocketDemo.as_view(),                 name='websocketDemo') ,
    path('v1/system/getLogMessages',              GetLogMessages.as_view(),                name='getLogMessages'),
    path('v1/system/getLogMessageTopics',         GetLogMessageTopics.as_view(),           name='getLogMessageTopics'),
    path('v1/system/deleteLogs',                  DeleteLogs.as_view(),                    name='deleteLogs'),
    path('v1/system/getUserAllowedDomainsAndRoles', GetUserAllowedDomainsAndRoles.as_view(), name='getUserAllowedDomainsAndRoles'),

    path('v1/system/domain/create',               CreateDomain.as_view(),                  name='createDomain'),
    path('v1/system/domain/delete',               DeleteDomains.as_view(),                 name='deleteDomains'),
    path('v1/system/domain/getDomainsDropdown',   GetDomainsDropdown.as_view(),            name='getDomainsDropdown'),
    path('v1/system/domain/getAllUsersTableData', GetAllUsersTableData.as_view(),          name='getAllUsersTableData'),
    path('v1/system/domain/addUserGroups',        AddUserGroupsToDomain.as_view(),         name='addUserGroupsToDomain'),
    path('v1/system/domain/removeUserGroups',     RemoveUserGroupsFromDomain.as_view(),    name='removeUserGroupsFromDomain'),
    path('v1/system/domain/getUserGroups',        GetDomainUserGroups.as_view(),           name='getDomainUserGroups'),
    path('v1/system/domain/get',                  GetDomains.as_view(),                    name='getDomains'),
    path('v1/system/domain/isUserAllowedInDomain', IsUserAllowedInDomain.as_view(),        name='isUserAllowedInDomain'),
    path('v1/system/domain/addUsersToDomains',     AddUsersToDomains.as_view(),            name="addUsersToDomains"),
    path('v1/system/domain/removeUsersFromDomains', RemoveUsersFromDomains.as_view(),      name="removeUsersFromDomains"),
                      
    path('v1/system/account/getDomainSelectionForUserAccount', GetDomainSelectionForUserAccount.as_view(), name='getDomainSelectionForUserAccount'),
    path('v1/system/account/removeDomainsFromUserAccount',     RemoveDomainsFromUserAccount.as_view(),     name='removeDomainsFromUserAccount') ,          
    path('v1/system/account/add',                  AddUser.as_view(),                       name='addUser'),
    path('v1/system/account/delete',               DeleteUser.as_view(),                    name='deleteUser'),
    path('v1/system/account/modify',               ModifyUserAccount.as_view(),             name='modifyUserAccount'),
    path('v1/system/account/tableData',            GetUserAccountTableData.as_view(),       name='getUserAccountTableData'),
    path('v1/system/account/getUserDetails',       GetUserDetails.as_view(),                name='getUserDetails'),
    path('v1/system/account/getApiKey',            GetApiKey.as_view(),                     name='getApiKey'),
    path('v1/system/account/getPassword',          GetPassword.as_view(),                   name='getPassword'),
    path('v1/system/account/regenerateApiKey',     RegenerateApiKey.as_view(),              name='regenerateApiKey'),
    path('v1/system/account/getApiKeyFromRestApi', GetApiKeyFromRestApi.as_view(),          name='getApiKeyFromRestApi'),
    path('v1/system/accountMgmt/apiKey',           GetApiKeyFromRestApi.as_view(),          name='getApiKeyForRestApi'),
    path('v1/system/account/isApiKeyValid',        IsApiKeyValid.as_view(),                 name='isApiKeyValid'),
    
    path('v1/system/userGroup/getUserAccountDataTable',  GetUserAccountDataTable.as_view(),  name='getUserAccountDataTable'),
    path('v1/system/userGroup/create',                   CreateUserGroup.as_view(),          name='createUserGroup'),
    path('v1/system/userGroup/delete',                   DeleteUserGroups.as_view(),         name='deleteUserGroups'),
    path('v1/system/userGroup/addUsersToUserGroup',      AddUsersToUserGroup.as_view(),      name='addUsersToUserGroup'),
    path('v1/system/userGroup/users',                    GetUserGroupUsers.as_view(),        name='getUserGroupUsers'),
    path('v1/system/userGroup/removeUsersFromUserGroup', RemoveUsersFromUserGroup.as_view(), name='removeUsersFromUserGroup'),
    path('v1/system/userGroup/getUserGroupsDropdown',    GetUserGroupsDropdown.as_view(),    name='getUserGroupsDropdown'),
    path('v1/system/userGroup/getUserGroupTable',        GetUserGroupTable.as_view(),        name='getUserGroupTable'),
    
    path('v1/system/loginCredentials',                   LoginCredentials.as_view(),        name='loginCredentialsRest'),
    path('v1/system/verifyVersion',                      VerifyVersion.as_view(),           name='verifyVersion'),
        
    path('v1/system/controller/add',                     AddController.as_view(),           name='addController'),
    path('v1/system/controller/delete',                  DeleteControllers.as_view(),       name='deleteControllers'),
    path('v1/system/controller/getControllers',          GetControllers.as_view(),          name='getControllers'),
    path('v1/system/controller/getControllerList',       GetControllerList.as_view(),       name='getControllerList'),
    path('v1/system/controller/generateAccessKey',       GenerateAccessKey.as_view(),       name='generateAccessKey'),
    path('v1/system/controller/registerRemoteAccessKey', RegisterRemoteAccessKey.as_view(), name='registerRemoteAccessKey'),
    path('v1/system/controller/getAccessKeys',           GetAccessKeys.as_view(),           name='getAccessKeys'),
    path('v1/system/controller/removeAccessKeys',        RemoveAccessKeys.as_view(),        name='removeAccessKeys'),    
          
    path('v1/utilization/envsBarChart',                  GetEnvBarChart.as_view(),          name='getEnvBarChart'),
    path('v1/utilization/usersBarChart',                 GetUserUsageBarChart.as_view(),    name='getUserUsageBarChart'),
      
    path('v1/userGuides/getMenu',                        UserGuidesMenu.as_view(),          name='userGuidesMenu'),
    path('v1/userGuides/getUserGuide',                   UserGuide.as_view(),               name='userGuide'),
        
    # Swagger-UI in keystack vie
    re_path('^v1/restAPI$',                       RestAPI.as_view(),                        name='restAPI'),

    # Backdoor to the rest api
    re_path(r'v1/restAPI/docs/$', schemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
            
    # default renderers are swagger, redoc, redoc-old
    #re_path(r'^swagger(?P<format>\.json|\.yaml)$', schemaView.without_ui(cache_timeout=0), name='schema-json'),
    #re_path(r'^redoc/$', schemaView.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
