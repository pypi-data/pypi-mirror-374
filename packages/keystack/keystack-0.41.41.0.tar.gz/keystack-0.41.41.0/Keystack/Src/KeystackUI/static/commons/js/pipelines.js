import * as commons from './commons.js';

var selectedPlaybook = null;
var selectedPlaybookDomain = null;
var getSessionView = 'current';
var refreshTableData = true;
var enterPageLoadTableData = true;
var deleteSessionsArray = new Array();
var archiveResultsArray = new Array();
var getSessionsInterval = 5000;
var userFilter;
var resultsFilter;
var playbookFilter;
var statusFilter;
var groupFilter;
var sessionIdFilter;

var statusFilterCheckboxes = 'All';
var userSelectedAllStatusFilterCheckbox = false;
var userFilterCheckboxes = 'All';
var userSelectedAllUserFilterCheckbox = false;
var resultFilterCheckboxes = 'All';
var userSelectedAllResultFilterCheckbox = false;

//For modifying playbook
var playbookPath;
// For modifying env
var envPath;
var selectedTestConfigsForChanges = null;
var newTestConfigFileName = null;
var createNewTestConfigsDone = false;

var individualTestConfigsArray = [];

// Pagination
var devicesPerPage = 25;
// Set default page number = 1
var getCurrentPageNumber = 1;
// For previous/next button calculation
var startPageIndex = 0;
var totalPages = 0;

// Initiate an intervalId.  This will be set in getSessions()
var intervalId = null;

var isStatusFilterDropdownClicked = false;

/*
let hideInstantMessagesDiv = document.querySelector('.hideInstantMessages');
if (hideInstantMessagesDiv.classList.contains('hideInstantMessages')) {
    hideInstantMessagesDiv.classList.remove('hideInstantMessages');
}
*/

document.addEventListener("DOMContentLoaded", function() {
    let isUserSysAdmin = document.querySelector("#user").getAttribute('sysAdmin');
    let domainUserRole = document.querySelector("#domainUserRole").getAttribute('role');
    let domain = document.querySelector("#pageAttributes").getAttribute("domain");

    if (domain == 'None') {
        let divs = ["#hidePlayPipelineDropdown", "#testParameters",
                    "#modifyTestcases", "#managePipelines", "#playNow", "#testScheduler", "#insertJobSchedulerCount",
                    "#hideSideBar", "#messages", "#messagesIcon", "#debugDropdown", "#utilization", "#utilizationIcon",
                    "#systemSettingsDropdown", "#mainBodyDiv"]
        for (let x=0; x<divs.length; x++) {
            let currentDiv = divs[x]
            document.querySelector(currentDiv).classList.add('hideFromUser');
        }
    } else {
        if (domainUserRole == 'engineer') {
            // "#messages", "#messagesIcon", "#debugDropdown", "#utilization", "#utilizationIcon", 
            let divs = ["#modifyTestcases", "#managePipelines", "#testScheduler", "#insertJobSchedulerCount",
                        "#modifyPlaybookInPipelineButton", "#modifyEnvInPipelineButton"]
            for (let x=0; x<divs.length; x++) {
                let currentDiv = divs[x]
                document.querySelector(currentDiv).classList.add('hideFromUser');
            }            
        }

        if (['engineer', 'manager'].includes(domainUserRole) || isUserSysAdmin == "False") {
            let divs = ["#systemSettingsDropdown"]
            for (let x=0; x<divs.length; x++) {
                let currentDiv = divs[x]
                document.querySelector(currentDiv).classList.add('hideFromUser');
            }            
        }

        intervalId = setTimeout(() => {
            getSessions();
        }, 100);

        getPipelines();
        getJobSchedulerCount();
        getPlaybookNamesDropdown();
        getTestConfigsDropdownForPipeline();
        commons.getInstantMessages('pipelines');
        commons.getServerTime();
    }
})


// eventListerner: dropdown-menu with id selectPlaybook. Use click eventListener to detect the user selection.
const dropdownSuiteSelection = document.querySelector('#selectPlaybook');
if (dropdownSuiteSelection) {
    dropdownSuiteSelection.addEventListener('click', event => {
        event.preventDefault();
        selectedPlaybook = event.target.innerText;
        let searchPattern = /DOMAIN=(.+?)\/.*/;
        let foundDomain = searchPattern.exec(selectedPlaybook);
        selectedPlaybookDomain = foundDomain[1];
        document.querySelector('#objectTitle').innerHTML = `|&emsp;Selected Playbook: ${selectedPlaybook}`;
    })
}

const showPipelineDetails = () => {
    /*
        To default disable overallDetails, add class="showOverallPipelineDetails" to the <tr> in sessionMgmt.html
    */
    const pipelineOverallDetailsObj = document.querySelector("#pipelineDetails");

    if (pipelineOverallDetailsObj.classList.contains("showOverallPipelineDetails")) {
        pipelineOverallDetailsObj.classList.remove("showOverallPipelineDetails");
    } else {
        pipelineOverallDetailsObj.classList.add("showOverallPipelineDetails");
    }
}

const getPlaybookNamesDropdown = async () => {
    // For selecting which playbook to play
    const data = await commons.postData("/api/v1/playbook/names",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     domain: document.querySelector("#pageAttributes").getAttribute('domain')});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertPlaybookNames').innerHTML = data.playbookNames;
    }
}

const getSelectedSessions = () => {
    // Collect all the selected checkboxes and delete them all in one shot
    let checkboxArray = document.querySelectorAll('input[name=deleteSessionId]:checked');

    for (let x=0; x < checkboxArray.length; x++) {
        let testResultsPath = checkboxArray[x].getAttribute('testResultsPath');
        archiveResultsArray.push(testResultsPath);

        // Uncheck the checkbox because getSessionIds() will not refresh 
        // the page is any deleteSessionId checkbox is checked
        checkboxArray[x].checked = false;
    }
}

const closeTestParameters = () => {
    document.querySelector('#testParameters').click();
}

const archiveResults = async () => {
    getSelectedSessions();

    const data = await commons.postData("/api/v1/results/archive",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                     results: archiveResultsArray});
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getSessions();
        commons.blinkSuccess();
    }
}

const resetParams = () => {
    /* Reset the test parameteres to default */
    document.querySelector('#sessionId').value = '';
    document.querySelector('#runInDebugMode').checked = false;
    //document.querySelector('#emailResults').checked = false;
    document.querySelector('#awsS3Upload').checked = false;
    document.querySelector('#jira').checked = false;
    document.querySelector('#pauseOnFailure').checked = false;
    document.querySelector('#holdEnvsIfFailed').checked = false;
    document.querySelector('#abortTestOnFailure').checked = false;
    document.querySelector('#includeLoopTestPassedResults').checked = false;
    document.querySelector('#selectAllPipelineCheckbox').checked = false;
    //document.querySelector("#testConfigs").value = "Select";
    individualTestConfigsArray = [];
    document.querySelector('#objectTitle').innerHTML = '';
    selectedPlaybookDomain = null;
    selectedTestConfigsForChanges = null;
    
    // In job scheduler modal
    document.querySelector('#removeJobAfterRunning').checked = false;
    selectedPlaybook = null;
}

const getSelectedTestParameters = () => {
    /* All all the user selected test parameteres */

    getSelectedTestConfigs();
    
    // testConfigs: document.querySelector("#testConfigs").value,
    // emailResults: document.querySelector('#emailResults').checked,
    let selectedTestParameters = {remoteController: sessionStorage.getItem("remoteController"),
                                  playbook: selectedPlaybook,
                                  debug: document.querySelector('#runInDebugMode').checked,
                                  awsS3: document.querySelector('#awsS3Upload').checked,
                                  jira: document.querySelector('#jira').checked,
                                  pauseOnFailure: document.querySelector('#pauseOnFailure').checked,
                                  holdEnvsIfFailed: document.querySelector('#holdEnvsIfFailed').checked,
                                  abortTestOnFailure: document.querySelector('#abortTestOnFailure').checked,
                                  includeLoopTestPassedResults: document.querySelector('#includeLoopTestPassedResults').checked,
                                  sessionId: sessionId.value,
                                  testConfigs: individualTestConfigsArray,
                                  domain: selectedPlaybookDomain
                            };
                                
    return selectedTestParameters;
}

let playNow = document.querySelector("#playNow");
playNow.addEventListener("click", event => {
    runPlaybookNow();
})

const runPlaybookNow = async () => {
    /* When adding new parameters, must also add in job scheduler */

    if (selectedPlaybook == null) {
        alert('Select a Playbook to play')
        return
    }

    document.querySelector("#pageAttributes").setAttribute('domain', selectedPlaybookDomain);

    //console.info(`runPlaybook(): ${JSON.stringify(getSelectedTestParameters())}`);
    const result = await commons.postData("/api/v1/playbook/runPlaybook",  getSelectedTestParameters());

    resetParams();
    commons.getInstantMessages('pipelines');

    if (result.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else{
        commons.blinkSuccess();
        getSessions();
    }
}

// PIPELINE MODAL:  For saved/view pipelines to select and run 
const managePipelines = document.querySelector('#managePipelines');
if (managePipelines) {
    managePipelines.addEventListener('click', async event => {
        getPipelineTableData();
    })
}

const getPipelineTableData = async () => {
    /* For saved/view pipelines to select and run */

    const data = await commons.postData("/api/v1/pipelines/tableData",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                        });
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertPipelineTableData').innerHTML = data.pipelineTableData;
    }
}

const closePipelineModal = () => {
    document.querySelector('#showPipelineStatus').innerHTML = '';
    document.querySelector("#insertSelectedParameters").innerHTML = '';
    window.location.reload();
}

const getPipelines = async () => {
    // Dropdown menu for user to select a pipeline to run
    const data = await commons.postData("/api/v1/pipelines/dropdown",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain: document.querySelector("#pageAttributes").getAttribute('domain')});
 
    commons.getInstantMessages('pipelines');                                               
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertPipelines').innerHTML = data.pipelines;
    }
}

const playPipeline = async (object) => {
    const pipeline = object.getAttribute('pipeline');
    const data = await commons.postData("/api/v1/playbook/runPlaybook",  
            {remoteController: sessionStorage.getItem("remoteController"),
             pipeline: pipeline,
             domain: document.querySelector("#pageAttributes").getAttribute('domain')});

    if (data.status == 'success') {
        document.querySelector("#getSessionDomainToShow").setAttribute('domain', data.domain);

        // Have to include a window reload in case the session timedout, reload 
        // takes user to login page
        //window.location.reload();
        getSessions();
    } else {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }

    commons.getInstantMessages('pipelines');
}

let managePipelinesEvent = document.querySelector("#managePipelines");
managePipelinesEvent.addEventListener("click", event => {
    getUserSelectedTestParameters();
})

const getUserSelectedTestParameters = () => {
    /* These are user selecteted test parameters to show what user selected before saving.
        Used for showing test parametered in savePipeline()
    */ 
    let selectedTestParams = getSelectedTestParameters();

    document.querySelector("#insertSelectedParameters").innerHTML = 'Selected Test Parameters:<br><br>'
    for (let param in selectedTestParams) {
        if (param != 'remoteController') {
            document.querySelector("#insertSelectedParameters").innerHTML += `&emsp;&emsp; ${param}: ${selectedTestParams[param]}<br>`;
        }
    };
}

const savePipeline = async () => {
    /* Save a pipeline to a name 
        In parallel, getUserSelectedTestParameters() is called also 
    */

    const pipelineName = document.querySelector('#pipelineNameId').value;

    if (pipelineName.indexOf('/') > 0) {
        alert('Pipeline name cannot have slashes');
        return
    }

    if (pipelineName == '') {
        alert('You must give a name for the pipeline');
        return
    }

    if (pipelineName.indexOf(' ') > 0) {
        alert('Pipeline name cannot have spaces');
        return
    }

    let selectedTestParams = getSelectedTestParameters();
    const result = await commons.postData("/api/v1/pipelines/save",  
                Object.assign({'pipeline': pipelineName, 
                               remoteController: sessionStorage.getItem("remoteController"),
                               domain: document.querySelector("#pageAttributes").getAttribute('domain')}, 
                               selectedTestParams));

    if (result.status == 'failed') {
        document.querySelector('#showPipelineStatus').style.color = 'red';
        document.querySelector('#showPipelineStatus').innerHTML = result.errorMsg;
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';

    } else {
        document.querySelector("#insertSelectedParameters").innerHTML = '';
        document.querySelector('#showPipelineStatus').style.color = 'green';
        document.querySelector('#showPipelineStatus').innerHTML = `Pipeline added: ${pipelineName}`;
    }

    resetPipeline();
    resetParams();
    getPipelines();
    getPipelineTableData();
    commons.getInstantMessages('pipelines');
}

const resetPipeline = () => {
    let pipelineNameId = document.querySelector('#pipelineNameId').value = '';
}

const deletePipeline = async () => {
    // Collect all the selected checkboxes and delete them all in one shot
    var pipelineCheckboxesArray = document.querySelectorAll('input[name=deletePipeline]:checked');
    let deletePipelineArray = [];
    
    for (let x=0; x < pipelineCheckboxesArray.length; x++) {
        let pipelinePath = pipelineCheckboxesArray[x].getAttribute('pipelineFullPath');
        deletePipelineArray.push(pipelinePath)

        // Uncheck the checkbox because getSessionIds() will not refresh 
        // the page is any deleteSessionId checkbox is checked
        pipelineCheckboxesArray[x].checked = false;
    }

    const data = await commons.postData("/api/v1/pipelines/delete",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                     pipelines:deletePipelineArray});

    if (data.status == 'success') {
        document.querySelector('#showPipelineStatus').style.color = 'green';
        document.querySelector('#showPipelineStatus').innerHTML = `Successfuly deleted`;
    } else {
        document.querySelector('#showPipelineStatus').style.color = 'red';
        document.querySelector('#showPipelineStatus').innerHTML = `Failed to delete`;
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }

    getPipelines();
    getPipelineTableData();
    commons.getInstantMessages('pipelines');
}

/*
Removing this for now.  Setting with 25 pipelines per page. Anymore is sluggish
document.querySelector("#setDevicesPerPage").addEventListener('click', event => {
    devicesPerPage = event.target.innerText;
    document.querySelector("#setDevicesPerPageDropdown").innerHTML = devicesPerPage;
    getSessions();
})
*/


const getSessions = async (getPageNumberButton=null, previousNextPage=null, noTimeoutDelay=false) => {
    /* view: current | archive 
    If archive, archive result link will pass in view=archive

    getPageNumberButton:  null == default total devices per page
    previousNextPage:     null == start from page 1
    noTimeoutDelay:       Used by statusFiltersEventListener and resultFiltersEventListener to avoid
                          setTimeout(getSessions).  We want to get sessions immediately without a timeout.

    <div id='getSessionDomainToShow' group={{showGroupSessions}} view={{showGroupView}}></div>
    */

    // Verify if any checkbox is checked. If yes, don't update the tableData
    var checkboxListener = document.querySelectorAll('input[name=deleteSessionId]:checked');
    if (checkboxListener.length > 0) {
        return
    }

    let userFilterDropdown = document.querySelector('#selectUserFilter');
    if (isDropdownVisible(userFilterDropdown)) {
        intervalId = setTimeout(getSessions, getSessionsInterval);
        return
    }

    let statusFilterDropdown = document.querySelector('#selectStatusFilter');
    if (isDropdownVisible(statusFilterDropdown)) {
        intervalId = setTimeout(getSessions, getSessionsInterval);
        return
    }

    let resultFilterDropdown = document.querySelector('#selectResultFilter');
    if (isDropdownVisible(resultFilterDropdown)) {
        intervalId = setTimeout(getSessions, getSessionsInterval);
        return
    }
    //clearTimeout(intervalId);

    let pageIndexRange = [];
    if (getPageNumberButton == null) {
        // Default devices per page
        // Creating just a one item array
        if (previousNextPage === null) {
            pageIndexRange.push(`0:${devicesPerPage}`);
        } else {
            if (previousNextPage === 'incr') {
                if (getCurrentPageNumber != totalPages) {
                    startPageIndex = getCurrentPageNumber * devicesPerPage;
                    let endPageIndex = startPageIndex + devicesPerPage
                    pageIndexRange.push(`${startPageIndex}:${endPageIndex}`);
                    getCurrentPageNumber++;
                } else {
                    return
                }
            }

            if (previousNextPage === 'decr') {
                if (getCurrentPageNumber != 1) {
                    startPageIndex = startPageIndex - devicesPerPage;
                    let endPageIndex = startPageIndex + devicesPerPage
                    pageIndexRange.push(`${startPageIndex}:${endPageIndex}`);
                    getCurrentPageNumber--;
                } else {
                    return
                }
            }
        }
    } else {
        // Creating just an one-item array
        pageIndexRange.push(getPageNumberButton.getAttribute("pageIndexRange"));
        getCurrentPageNumber = getPageNumberButton.getAttribute("getCurrentPageNumber");
    }

    const splitIndexRange = pageIndexRange[0];
    const startingIndex   = Number(splitIndexRange.split(":")[0]);
    const total           = parseInt(startingIndex) + parseInt(devicesPerPage);

    // Update the global startPageIndex for previous/next button calculation
    startPageIndex = startingIndex;

    const selectedDomain = document.querySelector("#pageAttributes").getAttribute('domain');

    // current || archive
    getSessionView = document.querySelector("#pageAttributes").getAttribute('view');

    const scheduledJobsCheckboxes = document.querySelectorAll('input[name=jobSchedulerMgmt]:checked');
    if (scheduledJobsCheckboxes.length > 0) {
        return
    }

    const data = await commons.postData("/api/v1/pipeline/getPipelines",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                 view: getSessionView,
                                 domain: selectedDomain,
                                 pageIndexRange: pageIndexRange,
                                 getCurrentPageNumber: getCurrentPageNumber,
                                 devicesPerPage: Number(devicesPerPage),
                                 userFilterCheckboxes: userFilterCheckboxes,
                                 statusFilterCheckboxes: statusFilterCheckboxes,
                                 resultFilterCheckboxes: resultFilterCheckboxes
                                 });

    commons.getInstantMessages('pipelines');

    // if the intervalId is not set
    if (data.name != "TypeError") {
        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        } else {
            document.querySelector('#tableData').innerHTML = data.tableData;
            document.querySelector('#topbarTitlePage').innerHTML = `Pipelines &emsp; | &emsp;Domain: ${selectedDomain}`;
            document.querySelector('#overallDetails').innerHTML = data.overallDetails;
            getJobSchedulerCount();

            getCurrentPageNumber = data.getCurrentPageNumber;
            totalPages = data.totalPages;
            document.querySelector("#insertPagination").innerHTML = data.pagination;
            document.querySelector("#previousPage").addEventListener('click', event => {
                getSessions(getPageNumberButton=null, previousNextPage='decr');
            })
            
            document.querySelector("#nextPage").addEventListener('click', event => {
                getSessions(getPageNumberButton=null, previousNextPage='incr');
            })

            // User clicked on deleteAll checkbox. Below code checkbox all session IDs
            let selectAllPipelineCheckbox = document.querySelector('#selectAllPipelineCheckbox');
            selectAllPipelineCheckbox.addEventListener('click', selectAllPipelines => {
                var pipelineCheckboxes = document.querySelectorAll('input[name="deleteSessionId"]')
                if (selectAllPipelines.target.checked) {
                    for (var x=0; x < pipelineCheckboxes.length; x++) {
                        pipelineCheckboxes[x].checked = true;
                    }
                } else {
                    for (var x=0; x < pipelineCheckboxes.length; x++) {
                        pipelineCheckboxes[x].checked = false;
                    }        
                }
            })

            statusFiltersEventListener();
            resultFiltersEventListener();

            if (sessionIdFilter) {filterSessionId();}
            if (userFilter) {filterUser();}
            if (playbookFilter) {filterPlaybook();}

            //if (intervalId !== "") {
            //    intervalId = setTimeout(getSessions, getSessionsInterval);
            //}

            if (noTimeoutDelay == false) {
                intervalId = setTimeout(getSessions, getSessionsInterval);
            }
        }

    } else {
        clearTimeout(intervalId);
    }
}

const usersFiltersEventListener = () => {
    // User selected all "user"
    let selectedAllUserFilter = document.querySelector("#selectedAllUserFilter");
    selectedAllUserFilter.addEventListener('click', event => {
        let selectedAllUserFilter = document.querySelectorAll('input[name="selectedAllUserFilter"]');
        let selectedUserFilter = document.querySelectorAll('input[name="selectedUserFilter"]');
        userFilterCheckboxes = 'All';

        if (selectedAllUserFilter[0].checked) {
            userSelectedAllUserFilterCheckbox = true;
            // Disable individual checkboxes
            for (var x=0; x < selectedUserFilter.length; x++) {
                selectedUserFilter[x].disabled = true; 
                selectedUserFilter[x].checked = false;
            }
        } else {
            userSelectedAllUserFilterCheckbox = false;
            // User uncheckbed the 'All' checkbox.  Enable all individual checkboxes.
            for (var x=0; x < selectedUserFilter.length; x++) {
                selectedUserFilter[x].disabled = false; 
            }                
        }
    })

    // User selected individual users filter
    let selectUserFilterButton = document.querySelector('#selectUserFilterButton');
    selectUserFilterButton.addEventListener('click', event => {
        if (userSelectedAllUserFilterCheckbox) {
            getSessions(noTimeoutDelay=true);
        } else {
            let selectedUserFilter = document.querySelectorAll('input[name="selectedUserFilter"]');
            userFilterCheckboxes = [];

            for (var x=0; x < selectedUserFilter.length; x++) {
                if (selectedUserFilter[x].checked) {
                    userFilterCheckboxes.push(selectedUserFilter[x].getAttribute("user"));
                }
            }

            if (userFilterCheckboxes != 'All' && userFilterCheckboxes.length == 0) {
                // User might've unchecked the 'All' checkboxes and did not select any individual device type
                // So get all device locations
                userFilterCheckboxes = 'All';
            }
            getSessions(noTimeoutDelay=true)
        }
    })
}

const statusFiltersEventListener = () => {
    // User selected all "status"
    let selectedAllStatusFilter = document.querySelector("#selectedAllStatusFilter");
    selectedAllStatusFilter.addEventListener('click', event => {
        let selectedAllStatusFilter = document.querySelectorAll('input[name="selectedAllStatusFilter"]');
        let selectedStatusFilter = document.querySelectorAll('input[name="selectedStatusFilter"]');
        statusFilterCheckboxes = 'All';

        if (selectedAllStatusFilter[0].checked) {
            userSelectedAllStatusFilterCheckbox = true;
            // Disable individual checkboxes
            for (var x=0; x < selectedStatusFilter.length; x++) {
                selectedStatusFilter[x].disabled = true; 
                selectedStatusFilter[x].checked = false;
            }
        } else {
            userSelectedAllStatusFilterCheckbox = false;
            // User uncheckbed the 'All' checkbox.  Enable all individual checkboxes.
            for (var x=0; x < selectedStatusFilter.length; x++) {
                selectedStatusFilter[x].disabled = false; 
            }                
        }
    })

    // User selected individual status filter
    let selectStatusFilterButton = document.querySelector('#selectStatusFilterButton');
    selectStatusFilterButton.addEventListener('click', event => {
        if (userSelectedAllStatusFilterCheckbox) {
            getSessions(null, null, true);
        } else {
            let selectedStatusFilter = document.querySelectorAll('input[name="selectedStatusFilter"]');
            statusFilterCheckboxes = [];

            for (var x=0; x < selectedStatusFilter.length; x++) {
                if (selectedStatusFilter[x].checked) {
                    statusFilterCheckboxes.push(selectedStatusFilter[x].getAttribute("status"));
                }
            }

            if (statusFilterCheckboxes != 'All' && statusFilterCheckboxes.length == 0) {
                // User might've unchecked the 'All' checkboxes and did not select any individual device type
                // So get all device locations
                statusFilterCheckboxes = 'All';
            }
            getSessions(null, null, true)
        }
    })
}

const resultFiltersEventListener = () => {
    // User selected all "result" filter
    let selectedAllResultFilter = document.querySelector("#selectedAllResultFilter");
    selectedAllStatusFilter.addEventListener('click', event => {
        let selectedAllResultFilter = document.querySelectorAll('input[name="selectedAllResultFilter"]');
        let selectedResultFilter = document.querySelectorAll('input[name="selectedResultFilter"]');
        resultFilterCheckboxes = 'All';

        if (selectedAllResultFilter[0].checked) {
            userSelectedAllResultFilterCheckbox = true;
            // Disable individual checkboxes
            for (var x=0; x < selectedResultFilter.length; x++) {
                selectedResultFilter[x].disabled = true; 
                selectedResultFilter[x].checked = false;
            }
        } else {
            userSelectedAllResultFilterCheckbox = false;
            // User uncheckbed the 'All' checkbox.  Enable all individual checkboxes.
            for (var x=0; x < selectedResultFilter.length; x++) {
                selectedResultFilter[x].disabled = false; 
            }                
        }
    })

    // User selected individual result filter
    let selectResultFilterButton = document.querySelector('#selectResultFilterButton');
    selectResultFilterButton.addEventListener('click', event => {
        if (userSelectedAllResultFilterCheckbox) {
            getSessions(null, null, true);
        } else {
            let selectedResultFilter = document.querySelectorAll('input[name="selectedResultFilter"]');
            resultFilterCheckboxes = [];

            for (var x=0; x < selectedResultFilter.length; x++) {
                if (selectedResultFilter[x].checked) {
                    resultFilterCheckboxes.push(selectedResultFilter[x].getAttribute("result"));
                }
            }

            if (resultFilterCheckboxes != 'All' && resultFilterCheckboxes.length == 0) {
                // User might've unchecked the 'All' checkboxes and did not select any individual device type
                // So get all device locations
                resultFilterCheckboxes = 'All';
            }
            getSessions(null, null, true)
        }
    })
}

const isDropdownVisible = (dropdownId) => {
    /* Checks if the dropdown ID in <ul id="selectStatusFilter" class="dropdown-menu"> is opened */
    
    if (dropdownId) {
        return dropdownId.offsetWidth > 0 && dropdownId.offsetHeight > 0;
    }
}

document.querySelector("#deletePipelinesButton").addEventListener('click', event => {
    /* This is disabled.  Meant for confirming with users if they really want to delete all
       pipelines */

    
    deleteSessionButton();

    // bootstrap modal might close the modal the leaves the screen dimmed.
    // This will close the modal all the way.
    //document.querySelector('.modal-backdrop').remove();
})

document.querySelector("#deleteAllPipelinesConfirmed").addEventListener('click', async event => {
    let domain = document.querySelector("#pageAttributes").getAttribute('domain');
    const data = await commons.postData("/api/v1/pipelines/deletePipelineSessions",  
                {remoteController: sessionStorage.getItem("remoteController"),
                 domain: domain,
                 pipelines: 'all'});

    commons.getInstantMessages('pipelines');

    if (data.status == 'success') {
        console.log(`----delete all passed ----`)
        document.querySelector("#deleteAllPipelinesModal").style.display = 'none';
        document.querySelector('.modal-backdrop').remove();
        commons.blinkSuccess();
        getSessions();
    }

    if (data.status == 'failed') {
        console.log(`----delete all  failed ----`)
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }
})

const deleteSessionButton = async () => {
    /*
    Removes session from results/logs
    */

    // Verify if user wants to also delete results from results/logs
    // Delete the session's results from "results & logs"
    let deleteResultsCheckbox = document.querySelector('#deleteResults');
    let domain = document.querySelector("#pageAttributes").getAttribute('domain');

    // Collect all the selected checkboxes and delete them all in one shot
    var checkboxArray = document.querySelectorAll('input[name=deleteSessionId]:checked');
    
    for (let x=0; x < checkboxArray.length; x++) {
        let testResultsPath = checkboxArray[x].getAttribute('testResultsPath');
        deleteSessionsArray.push({testResultsPath:testResultsPath})

        // Uncheck the checkbox because getSessionIds() will not refresh 
        // the page is any deleteSessionId checkbox is 
        checkboxArray[x].checked = false;
    }

    if (deleteSessionsArray.length == 0) {
        document.querySelector("#deletePipelinesModal").style.display = 'none';
        document.querySelector('.modal-backdrop').remove();        
    }

    const data = await commons.postData("/api/v1/pipelines/deletePipelineSessions",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     pipelines: deleteSessionsArray,
                                     domain: domain});

    commons.getInstantMessages('pipelines');
    if (data.status == 'success') {
        commons.blinkSuccess();
    }

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }

    document.querySelector("#deletePipelinesModal").style.display = 'none';
    document.querySelector('.modal-backdrop').remove();
    getSessions();
}

const resumePausedOnFailure = async (object) => {
    let pausedOnFailureFile = object.getAttribute('pausedOnFailureFile');
    const data = await commons.postData("/api/v1/pipelines/resumePausedOnFailure",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                     pausedOnFailureFile: pausedOnFailureFile});
    if (data.status == 'success') {
        getSessions();
    }

    if (data.status == 'failed') {
        commons.getInstantMessages('pipelines');
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }
}

const terminateProcessId = async (object) => {
    let sessionId      = object.getAttribute('sessionId');
    let processId      = object.getAttribute('processId');
    let statusJsonFile = object.getAttribute('statusJsonFile');

    const data = await commons.postData("/api/v1/pipelines/terminateProcessId",  
                                     {remoteController: sessionStorage.getItem("remoteController"),
                                      domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                      sessionId: sessionId,
                                      processId: processId,
                                      statusJsonFile: statusJsonFile});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
    }

    getSessions();
}

const openTestResultModal = async (testReportPathObj) => {
    let testReportPath = testReportPathObj.getAttribute('testReportPath');
    const data = await commons.postData("/api/v1/pipelines/getTestReport",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                     testReportPath: testReportPath});
    document.querySelector("#modalShowTestReport").innerHTML = `<pre>${data.testReportInsert}</pre>`;
}

const openTestLogsModal = async (testLogObj) => {
    /* This function shows status exception errors */

    const exceptionErrors = testLogObj.getAttribute('exceptionError');
    if (exceptionErrors != "") {
        document.querySelector("#modalShowTestLogs").innerHTML = exceptionErrors;
    } else {
        const testLogResultPath = testLogObj.getAttribute('testLogResultPath');
        const data = await commons.postData("/api/v1/pipelines/getTestLogs",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                         testResultPath: testLogResultPath});

        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        }
        document.querySelector("#currentOpenedFile").innerHTML = `${data.test.split('_')[0]} &emsp;  ${data.test.split('_')[1]} &emsp;  ${data.test.split('_')[2]}`;
        document.querySelector("#modalShowTestLogs").innerHTML = data.testLogsHtml;
        await addListeners({caretName:"caret2"});
    }
    commons.getInstantMessages('pipelines');
}  


const addListeners = async ({caretName="caret2", newVarName='x'}) => {
    window[caretName] = document.getElementsByClassName(caretName);

    for (let x= 0; x < window[caretName].length; x++) {
        window[caretName][x].addEventListener("click", function() {
            this.parentElement.querySelector(".nested").classList.toggle("active");         
        });
    }
}

const getFileContents = async (object) => {
    try {
        //document.querySelector("#modalShowTestLogs");
        const filePath = object.getAttribute('filePath');
        const data = await commons.postData("/api/v1/fileMgmt/getFileContents",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain:  document.querySelector("#pageAttributes").getAttribute('domain'),
                                             filePath: filePath});
        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        }

        // Show file contents in a new tab
        const myWindow = window.open("", '_blank');
        myWindow.document.write(`<pre>${data.fileContents}</pre>`);

    } catch (error) {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } 
    commons.getInstantMessages('pipelines');
}

const releaseEnvOnFailure = async (envObj) => {
    // If test failed, envs are on hold for debugging. A Release Envs button is created and blinking.
    let resultTimestampPath = envObj.getAttribute('resultTimestampPath');
    let sessionId = envObj.getAttribute('sessionId');
    let user = envObj.getAttribute('user');
    let stage = envObj.getAttribute('stage');
    let task = envObj.getAttribute('task');
    let env = envObj.getAttribute('env');

    const data = await commons.postData("/api/v1/env/releaseEnvOnFailure",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                     resultTimestampPath: resultTimestampPath,
                                     sessionId: sessionId, 
                                     user: user, 
                                     stage: stage, 
                                     task: task, 
                                     env: env});
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
    }
    getSessions();
}

const releaseEnv = async (obj) => {
    const env = obj.getAttribute('env');
    const data = await commons.postData("/api/v1/env/releaseEnv",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                         env: env});
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
    }
    getSessions();
}

const showTestcasesInProgress = async (obj) => {
    const testcaseSortedOrderList = obj.getAttribute('testcasesSortedOrderList');
    const resultsPath = obj.getAttribute('resultsPath');

    const data = await commons.postData("/api/v1/pipelines/getTestcasesInProgress",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                         testcaseSortedOrderList: testcaseSortedOrderList,
                                         resultsPath: resultsPath});
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#openShowTestcasesInProgressModel').style.display = 'block';
        document.querySelector("#insertTestcasesInProgress").innerHTML = data.testcases;
    }    
}

const showTestcase = async (object) => {
    /* In conjuncrtion with showTestcasesinProgress
       User clicked on a testcase to view contents 
    */
    const testcasePath = object.getAttribute('testcasePath');
    const data = await commons.postData("/api/v1/fileMgmt/getFileContents",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                             filePath: testcasePath})

    document.querySelector('#insertTestcasePath').innerHTML = testcasePath;
    document.querySelector('#insertInProgressTestcaseContents').innerHTML = `<textarea id="testcaseTextareaId" cols="135" rows="30">${data.fileContents}</textarea><br><br>`;
    commons.getInstantMessages('pipelines');
}

document.addEventListener("DOMContentLoaded", function(){
    document.querySelectorAll('.keystackSidebar .nav-link').forEach(function(element){
        element.addEventListener('click', function (e) {
            let nextEl = element.nextElementSibling;
            let parentEl  = element.parentElement;	

            if(nextEl) {
                e.preventDefault();	
                let mycollapse = new bootstrap.Collapse(nextEl);

                if(nextEl.classList.contains('show')){
                    mycollapse.hide();
                } else {
                    mycollapse.show();
                    // find other submenus with class=show
                    var opened_submenu = parentEl.parentElement.querySelector('.submenu.show');
                    // if it exists, then close all of them
                    if(opened_submenu){
                        new bootstrap.Collapse(opened_submenu);
                    }
                }
            }
        });
    })
}); 
// DOMContentLoaded  end

const filterSessionId = () => {
    // Call search in common.js
    sessionIdFilter = document.querySelector('#filterSessionId').value;
    commons.search({searchInputId:"#filterSessionId", tableId:'#tableData', columnIndex:2});
}

const filterPlaybook = () => {
    // Call search in commons.js
    playbookFilter = document.querySelector('#filterPlaybook').value;
    commons.search({searchInputId:"#filterPlaybook", tableId:'#tableData', columnIndex:3});
}

const filterUser = () => {
    // Call search in commons.js
    userFilter = document.querySelector('#filterUser').value;
    commons.search({searchInputId:"#filterUser", tableId:'#tableData', columnIndex:1});
}

const getCronScheduler = async () => {
    // Get dropdown selections for minute, hour, day, month and dayOfWeek
    
    document.querySelector("#createJobSchedulerModal").style.display = 'block';
    document.querySelector("#jobSchedulerStatus").innerHTML = '';

    const data = await commons.postData("/api/v1/pipelines/jobScheduler/getCronScheduler",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         domain: document.querySelector("#pageAttributes").getAttribute('domain')})
    if (data.status == 'failed') {
        commons.getInstantMessages('pipelines');
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertSchedulerDatetimePicker').innerHTML = data.schedulerDateTimePicker;
        // split and get the last element, then get the first element which is the playbook name only
        //let playbookName = playbookValues.split('/').pop().split('.')[0];

        if (selectedPlaybook == null) {
            document.querySelector("#selectedPlaybookForScheduler").innerHTML = `Selected playbook: None`;
        } else {
            document.querySelector("#selectedPlaybookForScheduler").innerHTML = `Selected playbook: ${selectedPlaybook}`;
        }
        
        viewJobScheduler();
    }
}

const saveScheduledPlaybook = async () => {
    /* Submit button to save a scheduled job */

    let selectedTestParams = getSelectedTestParameters();

    if (selectedTestParams.playbook == null) {
        alert('Please select a Playbook to schedule a job')
        return
    }

    let domain = document.querySelector("#pageAttributes").getAttribute('domain');

    let minute = document.querySelector("#reserve-minute").value;
    let hour = document.querySelector("#reserve-hour").value;
    let dayOfMonth = document.querySelector("#reserve-dayOfMonth").value;
    let month = document.querySelector("#reserve-month").value;
    let dayOfWeek = document.querySelector("#reserve-dayOfWeek").value;
    let removeJobAfterRunning = document.querySelector('#removeJobAfterRunning').checked;
    let reservationUser = document.querySelector("#reservationDomainUserSelections").value;
    let reservationNotes = document.querySelector("#playbookReservationNotesId").value;

    //console.info(`runPlaybook(): ${JSON.stringify(selectedTestParams)}`);   
    const response = await commons.postData("/api/v1/pipelines/jobScheduler/add",  
                            Object.assign({remoteController: sessionStorage.getItem("remoteController"),
                                           minute: minute, hour:hour, dayOfMonth: dayOfMonth,
                                           month: month, dayOfWeek: dayOfWeek,
                                           removeJobAfterRunning: removeJobAfterRunning,
                                           domain: domain,
                                           playbook: selectedTestParams.playbook,
                                           reservationUser: reservationUser,
                                           reservationNotes: reservationNotes},
                                           selectedTestParams));

    commons.getInstantMessages('pipelines');
    if (response.status == 'success') {
        document.querySelector('#jobSchedulerStatus').style.color = 'green';
        document.querySelector("#jobSchedulerStatus").innerHTML = 'Success';
    } else {
        document.querySelector('#jobSchedulerStatus').style.color = 'red';
        document.querySelector("#jobSchedulerStatus").innerHTML = `<h7>${response.errorMsg}</h7>`;
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }

    await setTimeout(() => {
        viewJobScheduler();
    }, 6000);

    getJobSchedulerCount();
    resetParams();
    getSessions();
}

const viewJobScheduler = async () => {
    const data = await commons.postData("/api/v1/pipelines/jobScheduler/scheduledJobs",  
                                          {remoteController: sessionStorage.getItem("remoteController"),
                                           domain: document.querySelector("#pageAttributes").getAttribute('domain')});

    commons.getInstantMessages('pipelines');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertPlaybookSchedules').innerHTML = data.jobSchedules;

        if (data.areThereJobs == false) {
            document.querySelector("#removeScheduledPlaybooksButton").style.display = 'none';
        } else {
            document.querySelector("#removeScheduledPlaybooksButton").style.display = 'block';
        }

        getDomainUserDropdown();
    }
}

const getJobSchedulerCount = async () => {
    const data = await commons.postData("/api/v1/scheduler/getSchedulerCount",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                         searchPattern: "playbook="});

    if (data.status == 'failed') {
        commons.getInstantMessages('pipelines');
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertJobSchedulerCount').innerHTML = data.totalScheduledCronJobs;
    }
} 

const getDomainUserDropdown = async () => {
    let domain = document.querySelector('#pageAttributes').getAttribute('domain');

    const data = await commons.postData("/api/v1/scheduler/getDomainUsers",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         domain: domain});

    if (data.status == 'failed') {
        commons.getInstantMessages('scheduler');
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertDomainUserSelection').innerHTML = data.domainUsersDropdown;
    }
} 

const removeScheduledJobsButton = async () => {
    /* <input type="checkbox" name="jobSchedulerMgmt" playbook={playbook} month={month} day={day} hour={hour} minute={min}/> */

    // Collect all the selected checkboxes and delete them all in one shot
    let scheduledJobsArray = document.querySelectorAll('input[name=jobSchedulerMgmt]:checked');
    let removeScheduledJobsArray = new Array();

    // jobSearchPattern: Defined in pipelineViews:ScheduleJobs() <input jobSearchPattern="playbook={playbook}">
    for (let x=0; x < scheduledJobsArray.length; x++) {
        let jobSearchPattern = scheduledJobsArray[x].getAttribute('jobSearchPattern')
        let month            = scheduledJobsArray[x].getAttribute('month');
        let day              = scheduledJobsArray[x].getAttribute('day');
        let hour             = scheduledJobsArray[x].getAttribute('hour');
        let minute           = scheduledJobsArray[x].getAttribute('minute');
        let dayOfWeek        = scheduledJobsArray[x].getAttribute('dayOfWeek');

        if (minute == "*") {minute = "\\*"}
        if (hour == "*") {hour = "\\*"}
        if (day == "*") {day = "\\*"}
        if (month == "*") {month = "\\*"}
        if (dayOfWeek == "*") {dayOfWeek = "\\*"}

        removeScheduledJobsArray.push({jobSearchPattern:jobSearchPattern, month:month, dayOfMonth:day, hour:hour, minute:minute, dayOfWeek:dayOfWeek})

        // Uncheck the checkbox
        scheduledJobsArray[x].checked = false;
    }
    
    const data = await commons.postData("/api/v1/pipelines/jobScheduler/delete",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                 removeScheduledJobs:removeScheduledJobsArray});

    commons.getInstantMessages('pipelines'); 
    if (data.status == 'failed') {
        commons.getInstantMessages('pipelines');
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }
    viewJobScheduler();
    getJobSchedulerCount();
}

document.querySelector("#closePlaybookSchedulerModal").addEventListener('click', event => {
    document.querySelector("#createJobSchedulerModal").style.display = "none";
    selectedPlaybook = null;
    document.querySelector('#objectTitle').innerHTML = '';
    getJobSchedulerCount();
})

const modifyFilePlaybook = async () => {
    /* Modify existing playbook */
    try {
        const playbookPathTitle = document.querySelector('#showPlaybookPath').innerHTML;
        const playbookTitleSplit = playbookPathTitle.split("Playbook:\u2002");
        const playbookPath = playbookTitleSplit[1];
        let textarea = document.querySelector('#textareaId').value;

        const data = await commons.postData("/api/v1/fileMgmt/modifyFile",  
                                                {remoteController: sessionStorage.getItem("remoteController"),
                                                 domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                                 textarea: textarea,
                                                 filePath: playbookPath})

        commons.getInstantMessages('pipelines'); 
        if (data.status == "success") {
            const status = `<div style='color:green'>Successfully modified Playbook</div>`;
            document.querySelector("#modifyPlaybookFileStatus").innerHTML = status;
        } else {
            const status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
            document.querySelector("#modifyPlaybookFileStatus").innerHTML = status;
        }
    } catch (error) {    
        console.error(`modifyFilePlaybook error: ${error}`);
    }
}

const modifyFileEnv = async () => {
    /* Modify existing env */
    try {
        const envPathTitle = document.querySelector('#showEnv').innerHTML;
        const envTitleSplit = envPathTitle.split("Env:\u2002");
        const envPath = envTitleSplit[1];

        const textarea = document.querySelector('#envTextareaId').value;
        const data = await commons.postData("/api/v1/fileMgmt/modifyFile",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                             textarea: textarea,
                                             filePath: envPath})

        commons.getInstantMessages('pipelines'); 
        if (data.status == "success") {
            const status = `<div style='color:green'>Successfully modified Env</div>`;
            document.querySelector("#modifyEnvFileStatus").innerHTML = status;
        } else {
            const status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
            document.querySelector("#modifyEnvFileStatus").innerHTML = status;
        }
    } catch (error) {  
        console.error(`modifyFileEnv error: ${error}`);
    }
}

const showPlaybook = async (object) => {
    const playbookPath = object.getAttribute('playbookPath');
    const data = await commons.postData("/api/v1/fileMgmt/getFileContents",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                             filePath: playbookPath})
    document.querySelector('#showPlaybookPath').innerHTML += playbookPath;
    document.querySelector('#insertPlaybookContents').innerHTML = `<textarea id="textareaId"  cols="135" rows="30">${data.fileContents}</textarea><br><br>`;
    commons.getInstantMessages('pipelines');
}

const showEnv = async (object) => {
    const envPath = object.getAttribute('envPath');
    const data = await commons.postData("/api/v1/fileMgmt/getFileContents",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                             filePath: envPath})
    document.querySelector('#showEnv').innerHTML += envPath;
    document.querySelector('#insertEnvContents').innerHTML = `<textarea id="envTextareaId"  cols="135" rows="30">${data.fileContents}</textarea><br><br>`;
    commons.getInstantMessages('pipelines');
}

const getTestConfigsDropdownForPipeline = async () => {
    /* Get reconfig dropdown menu for pipeline test parameters */
    try {
        const data = await commons.postData("/api/v1/pipelines/testConfigs/getTestConfigsDropdownForPipeline",  
                                                {remoteController: sessionStorage.getItem("remoteController"),
                                                 domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                                })

        document.querySelector('#insertTestConfigs').innerHTML = data.testConfigs;
        await addListeners({caretName:"caret2"});

    } catch (error) {
        commons.getInstantMessages('pipelines');
        console.error(`getTestConfigsList(): ${error}`)
    }    
}

const getSelectedTestConfigs = () => {
    // Individial Envs
    const individualTestConfigCheckbox = document.querySelectorAll('input[name=individualTestConfigCheckbox]:checked');

    for (let x=0; x < individualTestConfigCheckbox.length; x++) {
        let reconfigPath = individualTestConfigCheckbox[x].getAttribute('value');
        individualTestConfigsArray.push(reconfigPath)
        individualTestConfigCheckbox[x].checked = false;
    }

    /*
    const reconfigGroupCheckboxes = document.querySelectorAll('input[name=groupTestConfigCheckbox]:checked');

    for (let x=0; x < reconfigGroupCheckboxes.length; x++) {
        let envPath = reconfigGroupCheckboxes[x].getAttribute('value');
        reconfigGroupArray.push(envPath)
        reconfigGroupCheckboxes[x].checked = false;
    }
    */
}

/*
let modifyTestcases = document.querySelector("#modifyTestcases");
modifyTestcases.addEventListener('click', event => {
    getTestcasesToModify();
})
*/

const getTestcasesToModify = async () => {
    /* User wants to modify testcases 
       Make user select a playbook first so
       Keystack knows which testcases to get from the playlist
    */
    if (selectedPlaybook == null) {
        alert('Please select a Playbook first.\nKeystack need to know the testcases from the playbook.')
        return
    }

    getTestConfigsList();

    try {
        const data = await commons.postData("/api/v1/testcase/get",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                             playbook: selectedPlaybook});

        if (data.status == 'failed') {
            commons.getInstantMessages('pipelines');
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        } else {
            // Open the modal
            document.querySelector('#showTestcasesForModifyingModal').style.display = 'block';
            document.querySelector('#insertViewingPlaybook').innerHTML += `Playlist From Playbook:&emsp;${selectedPlaybook}`;
            document.querySelector('#insertPlaybookPlaylist').innerHTML = data.testcases;

            document.querySelector('#insertTestcaseContents').innerHTML = `<textarea id="testcaseContentsTextareaId" cols="101" rows="15">Select a testcase from the left side to view as a reference for the below reconfig or modify the testcase yml file.\n\nIf you want to modify testcase configurations for your testing, it would be better to use "reconfig" below so your changes will not be static and affect other users with your new changes.</textarea>`
            
            document.querySelector('#insertTestConfigFileContents').innerHTML = `<textarea id="reconfigFileContentsTextareaId" cols="101" rows="13">How-To:  Modify testcase configurations\n\nSelect or create a reconfig file to modify individual testcase parameter values.\nIt's not ideal to change testcase param values in the above testcase yml file.\nAlthough you could do that and it will work, but that will affect everybody who runs the same testcases with your changes.\nIt would be better to make all param changes in a reconfig file. Then select the reconfig file to use for your testing.</textarea>`;
        }
    } catch (error) {
        console.error(`getTestcasesToModify(): ${error}`)
    }
}

const getTestConfigContents = async (selectedTestConfigFile) => {
    /* Get dropdown selected reconfig file contents */

    try {
        selectedTestConfigsForChanges = selectedTestConfigFile;

        const data = await commons.postData("/api/v1/fileMgmt/getFileContents",  
                 {remoteController: sessionStorage.getItem("remoteController"),
                  domain: document.querySelector("#pageAttributes").getAttribute('domain'), 
                  filePath: selectedTestConfigFile})

        commons.getInstantMessages('pipelines');

        if (data.status == "failed") {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        } else {
            document.querySelector('#insertTestConfigFileContents').innerHTML = `<textarea id="reconfigFileContentsTextareaId" cols="102" rows="13">${data.fileContents}</textarea><br><br>`;
        }
    } catch (error) {    
        alert("getTestcaseContents() error: " + error);
    }
}

const deleteTestConfig = async () => {
    /* Delete a reconfig file */
    if (selectedTestConfigsForChanges == null) {
        alert('Please select a reconfig from the dropdown menu first')
        return
    } 

    try {
        const data = await commons.postData("/api/v1/pipelines/testConfigs/delete",  
                                                {remoteController: sessionStorage.getItem("remoteController"),
                                                 domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                                 reconfigFullPath: selectedTestConfigsForChanges})

        commons.getInstantMessages('pipelines');
        if (data.status == "success") {
            const status = `<div style='color:green'>Successfully deleted reconfig: ${selectedTestConfigsForChanges}</div>`;
            document.querySelector("#modifyTestcaseFileStatus").innerHTML = status;
            getTestConfigsList();
            selectedTestConfigsForChanges = null;

            document.querySelector('#insertTestConfigFileContents').innerHTML = `<textarea id="reconfigFileContentsTextareaId" cols="101" rows="13"></textarea>`
        } else {
            const status = `<div style='color:red'>Delete reconfig failed: ${data.errorMsg}</div>`;
            document.querySelector("#modifyTestcaseFileStatus").innerHTML = status;
        }

    } catch (error) {
        console.error(`deleteTestConfig(): ${error}`)
    }   
}

const saveTestConfigChanges = async () => {
    /* Save reconfig changes */
    if (selectedTestConfigsForChanges == null) {
        alert('Please select a reconfig from the dropdown menu first')
        return
    } 

    try {
        const textarea = document.querySelector('#reconfigFileContentsTextareaId').value;

        const data = await commons.postData("/api/v1/fileMgmt/modifyFile",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                             textarea: textarea,
                                             filePath: selectedTestConfigsForChanges})

        commons.getInstantMessages('pipelines');

        if (data.status == "success") {
            const status = `<div style='color:green'>Successfully modified reconfig: ${selectedTestConfigsForChanges}</div>`;
            document.querySelector("#modifyTestcaseFileStatus").innerHTML = status;
        } else {
            const status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
            document.querySelector("#modifyTestcaseFileStatus").innerHTML = status;
        }
    } catch (error) {    
        console.error(`modifyFileTestcase error: ${error}`);
    }
}

const createNewTestConfigs = async () => {
    /* Create a new reconfig file.
       Provide a template of all the available parameters 
    */
    try {
        const data = await commons.postData("/api/v1/pipelines/testConfigs/getParams",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain: document.querySelector("#pageAttributes").getAttribute('domain')})

        commons.getInstantMessages('pipelines');
        if (data.status == "success") {
            //const status = `<div style='color:green'>Successfully modified reconfig: ${selectedTestConfigsForChanges}</div>`;
            document.querySelector("#modifyTestcaseFileStatus").innerHTML = 'Make your changes in the text area. Press save when done.';

            document.querySelector('#insertTestConfigFileContents').innerHTML = `<textarea id="reconfigFileContentsTextareaId" cols="101" rows="13">${data.reconfigParams}</textarea>`;

            // saveNewTestConfigs needs to know if user indeed gotten new reconfig params
            createNewTestConfigsDone = true;

        } else {
            const status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
            document.querySelector("#modifyTestcaseFileStatus").innerHTML = status;
        }
    } catch (error) {    
        console.error(`createNewTestConfig error: ${error}`);
    }
}

const saveNewTestConfigs = async () => {
    /* Save new reconfig param and values from the text area */

    try {
        if (createNewTestConfigsDone == false) {
            alert('Please press the "Create New" button and make your changes in the text area first')
            return
        }

        newTestConfigFileName = document.querySelector('#NewTestConfigFileName').value;

        if (newTestConfigFileName == null || newTestConfigFileName == '') {
            alert('Please enter a new reconfig filename in the input box first')
            return
        }

        let textarea = document.querySelector('#reconfigFileContentsTextareaId').value;

        const data = await commons.postData("/api/v1/pipelines/testConfigs/saveNewTestConfigsToFile",
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                             textarea: textarea,
                                             reconfigName: newTestConfigFileName})

        commons.getInstantMessages('pipelines');
        if (data.status == "success") {
            const status = `<div style='color:green'>Successfully saved new reconfig: ${newTestConfigFileName}</div>`;
            document.querySelector("#modifyTestcaseFileStatus").innerHTML = status;
            getTestConfigsList();
            newTestConfigFileName = document.querySelector('#NewTestConfigFileName').value = '';

        } else {
            const status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
            document.querySelector("#modifyTestcaseFileStatus").innerHTML = status;
        }
    } catch (error) {    
        console.error(`saveNewTestConfigs error: ${error}`);
    }
}

const getTestConfigsList = async () => {
    /* TestConfigurations: dropdown for reconfig files */
    try {
        const data = await commons.postData("/api/v1/pipelines/testConfigs/getTestConfigsList",  
                                                {remoteController: sessionStorage.getItem("remoteController"),
                                                 domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                                })

        document.querySelector('#insertTestConfigsDropdown').innerHTML = data.testConfigsList;
        commons.getInstantMessages('pipelines');
    } catch (error) {
        console.error(`getTestConfigsList(): ${error}`)
    }    
}

const getTestcaseContents = async (testcaseFullPath) => {
    /* User wants to modify a testcase
       Get the testcase yml file contents
    */
    try {
        const data = await commons.postData("/api/v1/fileMgmt/getFileContents",  
                 {remoteController: sessionStorage.getItem("remoteController"),
                  domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                  mainController: sessionStorage.getItem("mainControllerIp"),  
                  filePath: testcaseFullPath})

        if (data.status == "failed") {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        } else {
            document.querySelector("#testcaseFilePath").innerHTML = testcaseFullPath;
            document.querySelector('#insertTestcaseContents').innerHTML = `<textarea id="testcaseContentsTextareaId" cols="102" rows="15">${data.fileContents}</textarea>`;
        }
    } catch (error) {    
        alert("getTestcaseContents() error: " + error);
    }
}

const modifyFileTestcase = async () => {
    /* Modify a testcase */

    try {
        const testcasePath = document.querySelector('#testcaseFilePath').innerHTML;
        const textarea = document.querySelector('#testcaseContentsTextareaId').value;

        const data = await commons.postData("/api/v1/fileMgmt/modifyFile",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                             textarea: textarea,
                                             filePath: testcasePath})

        commons.getInstantMessages('pipelines');
        if (data.status == "success") {
            const status = `<div style='color:green'>Successfully modified testcase: ${testcasePath}</div>`;
            document.querySelector("#modifyTestcaseFileStatus").innerHTML = status;
        } else {
            const status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
            document.querySelector("#modifyTestcaseFileStatus").innerHTML = status;
        }
    } catch (error) {    
        console.error(`modifyFileTestcase error: ${error}`);
    }
}

const closeShowModifyTestcasesModal = () => {
    document.querySelector('#showTestcasesForModifyingModal').style.display = 'none';
    document.querySelector('#testcaseFilePath').innerHTML = '&lt;Select a testcase on the left column&gt;';
    document.querySelector("#insertTestcaseContents").innerHTML = '';
    document.querySelector('#insertViewingPlaybook').innerHTML = '';
    document.querySelector('#insertPlaybookPlaylist').innerHTML = '';
    document.querySelector("#modifyTestcaseFileStatus").innerHTML = '';
    document.querySelector("#testConfigsList").value = "Select TestConfig File";
    document.querySelector('#insertTestConfigFileContents').innerHTML = '';
    //document.querySelector("#newTestConfigFileName").value = '';
    newTestConfigFileName = null;
    createNewTestConfigsDone = false;
}

const closePlaybookText = () => {
    document.querySelector('#insertPlaybookContents').innerHTML = '';
    document.querySelector('#showPlaybookPath').innerHTML = 'Playbook:&ensp;';
    document.querySelector('#modifyPlaybookFileStatus').innerHTML = '';
}

const closeEnvText = () => {
    document.querySelector('#insertEnvContents').innerHTML = '';
    document.querySelector('#showEnv').innerHTML = 'Env:&ensp;';
    document.querySelector('#modifyEnvFileStatus').innerHTML = '';
}

const closeGetTestcasesInternalModal = () => {
    document.querySelector('#getTestcasesInternalModal').style.display = 'none';
}

const closeTestcasesInProgressModal = () => {
    document.querySelector('#openShowTestcasesInProgressModel').style.display = 'none';
}


/* 
pipelines.js:1252 Mixed Content: The page at 'https://192.168.28.10/sessionMgmt/#' was loaded over HTTPS, but attempted to connect to the insecure WebSocket endpoint 'ws://192.168.28.10/ws/room/pipelineId'. This request has been blocked; this endpoint must be available over WSS.
(anonymous) @ pipelines.js:1252
sessionMgmt/#:1 Uncaught DOMException: Failed to construct 'WebSocket': An insecure WebSocket connection may not be initiated from a page loaded over HTTPS.
    at https://192.168.28.10/static/commons/js/pipelines.js:1252:17

var wsProtocol = 'ws'
if (window.location.protocol === 'https') {
    wsProtocol = 'wss'
}

var webSocket = new WebSocket(
    `${wsProtocol}://${window.location.host}/ws/room/pipelineId`
);

const wsSubmitButton = () => {
    console.log('---- pipeline.js: got to wsSubmit ---')
    console.log(`---- pipeline.js: websocket protocol: ${window.location.protocol}  -> ${wsProtocol} ---`)

    webSocket.onmessage = function (e) {
        // Recieved messages from server

        const data = JSON.parse(e.data);
        console.log(`----- pipeline.js: websocket Rx onmessage data: ${data.tester} ----`)
    }

    const messageInput = document.querySelector('#inputMessage');
    const message = messageInput.value;
    console.log(`----- pipeline.js: wsSubmitButton: ${message} ---`)

    webSocket.send(JSON.stringify({
        'messageFromTemplateJS': message,
    }));

    messageInput.value = '';
}
window.wsSubmitButton = wsSubmitButton;
*/

window.getSessions = getSessions;
window.createNewTestConfigs = createNewTestConfigs;
window.saveNewTestConfigs = saveNewTestConfigs;
window.saveTestConfigChanges = saveTestConfigChanges;
window.deleteTestConfig = deleteTestConfig;
window.deleteSessionButton = deleteSessionButton;
window.runPlaybookNow = runPlaybookNow;
window.getSelectedTestParameters = getSelectedTestParameters;
window.showEnv = showEnv;
window.closeEnvText = closeEnvText;
window.openTestResultModal = openTestResultModal;
window.openTestLogsModal = openTestLogsModal;
window.showPlaybook = showPlaybook;
window.showTestcase = showTestcase;
window.modifyFileEnv = modifyFileEnv;
window.modifyFilePlaybook = modifyFilePlaybook;
window.modifyFileTestcase = modifyFileTestcase;
window.closePlaybookText = closePlaybookText;
window.closeEnvText = closeEnvText;
window.closeTestParameters = closeTestParameters;
window.filterSessionId = filterSessionId;
window.filterPlaybook = filterPlaybook;
window.filterUser = filterUser;
window.terminateProcessId = terminateProcessId;
window.showPipelineDetails = showPipelineDetails;
window.archiveResults = archiveResults;
window.playPipeline = playPipeline;
window.resumePausedOnFailure = resumePausedOnFailure;
window.resetParams = resetParams;
window.getCronScheduler = getCronScheduler;
window.getJobSchedulerCount = getJobSchedulerCount;
window.saveScheduledPlaybook = saveScheduledPlaybook;
window.removeScheduledJobsButton = removeScheduledJobsButton;
window.closePipelineModal = closePipelineModal;
window.savePipeline = savePipeline;
window.deletePipeline = deletePipeline;
window.getUserSelectedTestParameters = getUserSelectedTestParameters;
window.releaseEnvOnFailure = releaseEnvOnFailure;
window.getTestConfigContents = getTestConfigContents;
window.getTestcaseContents = getTestcaseContents;
window.getTestcasesToModify = getTestcasesToModify;
window.modifyFileTestcase = modifyFileTestcase;
window.closeShowModifyTestcasesModal = closeShowModifyTestcasesModal;
window.closeGetTestcasesInternalModal = closeGetTestcasesInternalModal;
window.showTestcasesInProgress = showTestcasesInProgress;
window.closeTestcasesInProgressModal = closeTestcasesInProgressModal;
window.getTestConfigsDropdownForPipeline = getTestConfigsDropdownForPipeline;
window.getFileContents = getFileContents;












