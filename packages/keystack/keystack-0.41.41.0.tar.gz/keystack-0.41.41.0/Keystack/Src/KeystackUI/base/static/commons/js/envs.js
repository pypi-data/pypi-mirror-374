import * as commons from './commons.js';

var refreshPageInterval = 10000;
var env = null;
var selectAllEnvGroupsToDeleteIsChecked = false;
var intervalId = null;

// Pagination
var devicesPerPage = 50;
// Set default page number = 1
var getCurrentPageNumber = 1;
// For previous/next button calculation
var startPageIndex = 0;
var totalPages = 0;


intervalId = setTimeout(() => {
    getSetupTableData();
}, refreshPageInterval);

document.addEventListener("DOMContentLoaded", function() { 
    let isUserSysAdmin = document.querySelector("#user").getAttribute('sysAdmin');
    let domainUserRole = document.querySelector("#domainUserRole").getAttribute('role');

    if (domainUserRole == 'engineer') {
        let divs = ["#envNavbar", "#envModifyButton", "#removeFromActiveUsersButton",
                    "#removeFromWaitListButton"]
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

    var remoteController = sessionStorage.getItem("remoteController");
    document.querySelector("#setDevicesPerPageDropdown").innerHTML = devicesPerPage;
    updateActiveUsersAndWaitList();     
    getSetupTableData();
    getEnvSchedulerCount();
    getEnvGroupsForDelete();
    commons.getInstantMessages('envs');
    commons.getServerTime();
})

const getEnvGroupsForDelete = async () => {
    let response = await commons.postData("/api/v1/env/envGroupsTableForDelete",  
                                            {remoteController: sessionStorage.getItem("remoteController")})
    commons.getInstantMessages('envs');
    if (response.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertDeleteEnvGroup").innerHTML = response.envGroupsHtml;
    }
}

document.querySelector("#setDevicesPerPage").addEventListener('click', event => {
    devicesPerPage = event.target.innerText;
    document.querySelector("#setDevicesPerPageDropdown").innerHTML = devicesPerPage;
    getSetupTableData();
})

const isDropdownOpened = (dropdownId) => {
    if (dropdownId) {
        return dropdownId.classList.contains('show');
    }
}

const getSetupTableData = async (getPageNumberButton=null, previousNextPage=null) => {
    // Verify if any checkbox is checked. If yes, don't update the tableData
    var checkboxListener = document.querySelectorAll('input[name=envCheckboxes]:checked');
    if (checkboxListener.length > 0) {
        return
    }

    let portGroupDropdownId = document.querySelector("#envPortGroupDropdownId");
    if (isDropdownOpened(portGroupDropdownId)) {
        return
    }

    let isEnvSharedDropdownId = document.querySelector("#isEnvSharedDropdownId");
    if (isDropdownOpened(isEnvSharedDropdownId)) {
        return
    }

    let autoSetup1 = document.querySelector("#autoSetupModal").style.display;
    if (document.querySelector("#autoSetupModal").style.display == 'block') {
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

    let domain = document.querySelector('#pageAttributes').getAttribute('domain');
    let envGroupPath = document.querySelector('#envPageAttributes').getAttribute('envGroupPath');
    let topbarDisplayDomain = document.querySelector('#envPageAttributes').getAttribute('topbarDisplayDomain');
    let topbarDisplayGroup = document.querySelector('#envPageAttributes').getAttribute('topbarDisplayGroup');

    const data = await commons.postData("/api/v1/env/getEnvTableData",  
                                                {remoteController: sessionStorage.getItem("remoteController"),
                                                 envGroup: envGroupPath, 
                                                 domain:domain,
                                                 pageIndexRange: pageIndexRange,
                                                 getCurrentPageNumber: getCurrentPageNumber,
                                                 devicesPerPage: Number(devicesPerPage)})
    commons.getInstantMessages('envs');
    if (data.name == "TypeError") {
        clearTimeout(intervalId);
    } else {
        document.querySelector('#setupTableData').innerHTML = data.tableData;
        document.querySelector('#topbarTitlePage').innerHTML = `Env Mgmt&emsp;|&emsp;${topbarDisplayDomain} &ensp;&ensp;${topbarDisplayGroup}` ;
        commons.sortTable({tableId: "#envTable", columnIndex:1});
        getEnvSchedulerCount();

        getCurrentPageNumber = data.getCurrentPageNumber;
        totalPages = data.totalPages;
        document.querySelector("#insertPagination").innerHTML = data.pagination;
        document.querySelector("#previousPage").addEventListener('click', event => {
            getSetupTableData(getPageNumberButton=null, previousNextPage='decr');
        })
        
        document.querySelector("#nextPage").addEventListener('click', event => {
            getSetupTableData(getPageNumberButton=null, previousNextPage='incr');
        })

        let shareableClasses = document.querySelectorAll('.shareableDropdown');
        for (var x=0; x < shareableClasses.length; x++) {
            shareableClasses[x].addEventListener('click', shareableClassesEvent => {
                setShareableEnv(shareableClassesEvent);
            })
        }

        let envAutoSetup = document.querySelectorAll('.envAutoSetup');
        for (var z=0; z < envAutoSetup.length; z++) {
            envAutoSetup[z].addEventListener('click', event => {
                autoSetup(event);
            })
        }

        /*
        if (intervalId !== "") {
            intervalId = setTimeout(getSetupTableData, refreshPageInterval);
        }
        */
        intervalId = setTimeout(getSetupTableData, refreshPageInterval);
    } 
}

const setShareableEnv = async (event) => {
    // env: shareable
    let env = event.target.getAttribute('env');
    let shareable = event.target.getAttribute('shareable');
    const data = await commons.postData("/api/v1/env/setShareable",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 env: env,
                                 shareable: shareable});

    commons.getInstantMessages('envs');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getSetupTableData();
    }
}

// Get all delete-env checkboxes
let deleteSetupButton = document.querySelector('#deleteSetupButton');
let deleteEnvList = new Array(); 

deleteSetupButton.addEventListener('click', event => {
    let envCheckboxes = document.querySelectorAll('input[name="envCheckboxes"]:checked');
    envCheckboxes.forEach((checkbox) => {
        deleteEnvList.push(checkbox.value);
        checkbox.checked = false;
    })

    deleteEnvs(deleteEnvList);
})

const deleteEnvs = async (envList) => {
    const data = await commons.postData("/api/v1/env/delete", 
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 envs: envList});

    commons.getInstantMessages('envs');
    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        //window.location.reload();
        commons.blinkSuccess();
        getSetupTableData();
    }
}

const disableEnvGroupCheckboxes = (object) => {
    // SelectAll checkbox is checked.  Comes in here.
    // If checked, disabled all env checkboxes in the group. 
    // If unchecked, enable all env checkboxes in the group.
    
    let isChecked = object.checked;
    if (isChecked) {
        selectAllEnvGroupsToDeleteIsChecked = true;
    } else {
        selectAllEnvGroupsToDeleteIsChecked = false;
    }

    let checkboxes = document.querySelectorAll(`input[name="deleteEnvGroups"]`);
    for (let x = 0; x < checkboxes.length; x++) {
        if (isChecked) {
            checkboxes[x].checked = false;
            checkboxes[x].disabled = true;
        } else {
            checkboxes[x].checked = false;
            checkboxes[x].disabled = false;
        }
    }
}

const getSelectedEnvGroupsToDelete = () => {
    // Collect all the selected checkboxes and delete them all in one shot
    var checkboxArray = document.querySelectorAll('input[name=deleteEnvGroups]:checked');
    var envGroupsToDelete = [];

    for (let x=0; x < checkboxArray.length; x++) {
        let envGroupFullPath = checkboxArray[x].getAttribute('value');
        envGroupsToDelete.push(envGroupFullPath);
    }
    return envGroupsToDelete;
}

const deleteEnvGroups = async () => {
    if (selectAllEnvGroupsToDeleteIsChecked) {
        var selectAll = true;
        var selectedEnvGroups = [];
    } else {
        var selectAll = false;
        selectAllEnvGroupsToDeleteIsChecked = false;
        var selectedEnvGroups = getSelectedEnvGroupsToDelete();
    }

    const response = await commons.postData("/api/v1/env/deleteEnvGroups",  
                {remoteController: sessionStorage.getItem("remoteController"),
                 selectedEnvGroups:selectedEnvGroups, selectAll:selectAll});

    commons.getInstantMessages('envs');	
    if (response.status == 'success') {
        commons.blinkSuccess();
        getEnvGroupsForDelete();
    } else {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';  
    }
    
    closeDeleteEnvGroups();
}

const closeDeleteEnvGroups = () => {
    selectAllEnvGroupsToDeleteIsChecked = false;

    let checkboxes = document.querySelectorAll(`input[name="deleteEnvGroups"]`);
    for (let x = 0; x < checkboxes.length; x++) {
        checkboxes[x].checked = false;
        checkboxes[x].disabled = false;
    }
    document.querySelector('input[name=deleteAllEnvGroups]').checked = false;
}

const getFileContents = async (filePath) => {
    try {
        // getFileContents calls sidebar/views
        const data = await commons.postData("/api/v1/fileMgmt/getFileContents",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         filePath: filePath.value})
        
        // Text area. Set the name attr with the task preferences file path.
        document.querySelector("#insertFileContents").innerHTML =
        `<textarea id="textareaId" name="${data.fullPath}" cols="123" rows="25">${data.fileContents}</textarea><br><br>`;
        
        const toggle = document.querySelector("#insertFileContents");
        // Toggle to show text 
        //toggle.style.display = toggle.style.display == "block" ? "none" : "block";
        // toggle.style.display = toggle.style.display == "block";
        if (toggle) {
            toggle.style.display = "block";
        }

        document.querySelector("#currentOpenedFile").innerHTML = '<h7>' + 'Envs:&emsp;' + data.fullPath.split("/Envs/").slice(1) + '</h7>';
        document.querySelector('#modifyButton').style.display = "block";

        // close modal button
        document.querySelector('#textAreaButton').style.display = "block";
    } catch (error) {
        console.error(`Envs getFileContents: ${error.message}`);
    }
    commons.getInstantMessages('envs');	  
}

const closeText = () => {
    let toggle = document.querySelector("#textareaId");
    if (toggle) {
        toggle.value = '';
    }

    // Toggle to hide buttons
    //toggle.style.display = toggle.style.display == "none" ? "block" : "none";
    document.querySelector("#insertFileContents").style.display = "none";
    document.querySelector('#modifyButton').style.display = "none";
    document.querySelector('#textAreaButton').style.display = "none";
    document.querySelector("#currentOpenedFile").innerHTML = "";
    document.querySelector("#modifyEnvStatus").innerHTML = "";
}

const createEnv = async () => {
    try {
        const domain = document.querySelector('#envPageAttributes').getAttribute('topbarDisplayDomain');
        const textArea = document.querySelector('#insertEnvTemplate').value;
        const newEnv = document.querySelector('#newEnv').value;
        var envGroup = document.querySelector('#envGroup').value;

        if (envGroup === '') {
            let resourceGroup = document.querySelector('#envPageAttributes').getAttribute('topbarDisplayGroup');
            envGroup = resourceGroup.split("=")[1];
        }
        
        const data = await commons.postData("/api/v1/env/create",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             textArea: textArea, 
                                             newEnv: newEnv, 
                                             envGroup: envGroup,
                                             domain: domain})

        commons.getInstantMessages('envs');

        if (data.status == "success") {
            // Close the BS modal
            //document.querySelector('#createEnvModal').style.display = "none";
            //document.querySelector('.modal-backdrop').remove();
            //getSetupTableData();
            closeCreateEnv();
            commons.blinkSuccess();
            window.location.reload();

        } else {
            let status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`
            document.querySelector("#createEnvStatus").innerHTML = status;
        }
    } catch (error) {  
        console.error(`!createEnv: ${error}`);
    }

    // Have to refresh the page. If calling getSetupTable(), view env modal won't open
}

const closeCreateEnv = () => {
    document.querySelector("#newEnv").value = "";
    document.querySelector('#envGroup').value = "";
    document.querySelector("#createEnvStatus").innerHTML = "";
    document.querySelector("#insertEnvTemplate").value = "";

    // Close the modal
    document.querySelector('#createEnvModal').style.display = "none";
    // Close the modal all the way through.
    document.querySelector('.modal-backdrop').remove();
}

const filterSetup = () => {
    // Call search in commons.js
    const taskFilter = document.querySelector('#filterSetup').value
    commons.search({searchInputId:"#filterSetup", tableId:'#setupTableData', columnIndex:2})
}

const waitList = async (obj) => {
    // User clicked on waitList link
    const env = obj.getAttribute('env');
    const data = await commons.postData("/api/v1/env/envWaitList",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             env: env})
    document.querySelector('#insertWaitList').innerHTML = data.tableData;
}

const getWaitList = async (env) => {
    /* Used internally only by removeFromWaitList for refreshing the modal table data immediately */
    const data = await commons.postData("/api/v1/env/envWaitList",  
                                            {remoteController: sessionStorage.getItem("remoteController"), 
                                             env: env})
    document.querySelector('#insertWaitList').innerHTML = data.tableData;
}

const activeUsersList = async (obj) => {
    // User clicked on activeUser link

    env = obj.getAttribute('env');
    const data = await commons.postData("/api/v1/env/getActiveUsersList",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             env: env})
    document.querySelector('#insertActiveUsers').innerHTML = data.tableData;
    document.querySelector('#userMgmt').innerHTML = `Env: &ensp;${env}`
    getWaitList(env);
}

const getActiveUsersList = async (env) => {
    const data = await commons.postData("/api/v1/env/getActiveUsersList",  
                                            {remoteController: sessionStorage.getItem("remoteController"), 
                                             env: env})
    document.querySelector('#insertActiveUsers').innerHTML = data.tableData;
}

const reserveEnv = async (obj) => {
    /* Manually reserve env */
    const env = obj.getAttribute('env');
    const data = await commons.postData("/api/v1/env/reserveEnv",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             env: env})
    commons.getInstantMessages('envs');

    if (data.status == "failed") {
        const status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getSetupTableData();
    }
}

const releaseEnv = async (obj) => {
    /* Release an individual env when an env goes into holdEnvsIfFailed or release
       a manually reserved env. */

    const env = obj.getAttribute('env');
    const data = await commons.postData("/api/v1/env/releaseEnv",  
                                                {remoteController: sessionStorage.getItem("remoteController"),
                                                 env: env})   
    commons.getInstantMessages('envs');

    if (data.status == "failed") {
        let status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getSetupTableData();
    }
}

const resetEnv = async (obj) => {
    const env = obj.getAttribute('env');

    const data = await commons.postData("/api/v1/env/resetEnv",  
                                            {remoteController: sessionStorage.getItem("remoteController"), 
                                             env: env});
    commons.getInstantMessages('envs');
    if (data.status == "failed") {
        let status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        window.location.reload();
    }
}

// Get all remove checkboxes from remove wait-list
let removeFromWaitListButton = document.querySelector('#removeFromWaitListButton');
let removeFromWaitListArray = new Array(); 

removeFromWaitListButton.addEventListener('click', event => {
    let removeFromWaitListCheckboxes = document.querySelectorAll('input[name="envWaitListCheckboxes"]:checked');
    removeFromWaitListCheckboxes.forEach((checkbox) => {
        var env =       checkbox.getAttribute("env");
        var sessionId = checkbox.getAttribute("sessionId");
        var user =      checkbox.getAttribute("user");
        var stage =     checkbox.getAttribute("stage");
        var task =    checkbox.getAttribute("task");
        removeFromWaitListArray.push({env:env, user:user, sessionId:sessionId, stage:stage, task:task});
    });

    removeEnvFromWaitList(env, removeFromWaitListArray);
})

const removeEnvFromWaitList = async (env, removeList) => {
    // checkboxes: envWaitListCheckboxes
    const data = await commons.postData("/api/v1/env/removeEnvFromWaitList",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             env:env, removeList: removeList})
    commons.getInstantMessages('envs');       
    if (data.status == 'failed') {
        const status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
        document.querySelector("#releaseStatus").innerHTML = status;        
    } else {
        // Get the env from global var
        getWaitList(env);
        getActiveUsersList(env);
    }
}

// Get all remove checkboxes from activeUsers
let removeActiveUsersButton = document.querySelector('#removeFromActiveUsersButton');
let removeFromActiveUsersArray = new Array(); 

removeActiveUsersButton.addEventListener('click', event => {
    let removeFromActiveUsersCheckboxes = document.querySelectorAll('input[name="envActiveUsersCheckboxes"]:checked');
    removeFromActiveUsersCheckboxes.forEach((checkbox) => {
        removeFromActiveUsersArray.push({env:checkbox.getAttribute("env"),
                                         sessionId: checkbox.getAttribute("sessionId"),
                                         overallSummaryFile: checkbox.getAttribute("overallSummaryFile"),
                                         user: checkbox.getAttribute("user"), 
                                         stage: checkbox.getAttribute("stage"), 
                                         task: checkbox.getAttribute("task")});
    })
    removeEnvFromActiveUsersList(env, removeFromActiveUsersArray);
})

const removeEnvFromActiveUsersList = async (env, removeList) => {
    const data = await commons.postData("/api/v1/env/removeEnvFromActiveUsersList",  
                                                {remoteController: sessionStorage.getItem("remoteController"),
                                                 env: env, removeList: removeList})

    commons.getInstantMessages('envs');
    if (data.status == "failed") {
        const status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
        document.querySelector("#releaseStatus").innerHTML = status;
    } else {
        // Get the env from global var
        getActiveUsersList(env);
        getWaitList(env);
    }
}  

const updateActiveUsersAndWaitList = async () => {
    // User clicked on waitList link
    const data = await commons.postData("/api/v1/env/updateActiveUsersAndWaitList",  
                                            {remoteController: sessionStorage.getItem("remoteController")})
    commons.getInstantMessages('envs');
}

const getEnvCronScheduler = async (object) => {
    /*  Get dropdown selections for minute, hour, day, month and dayOfWeek.
    At the same time, show the env row the user clicked on */

    document.querySelector("#createEnvSchedulerModal").style.display = 'block';
    document.querySelector("#envSchedulerStatus").innerHTML = '';
    let env = object.getAttribute('env');
    if (env != "all") {
        document.querySelector("#insertEnvName").innerHTML = env;
    }

    const data = await commons.postData("/api/v1/env/scheduler/getCronScheduler",  
                                        {remoteController: sessionStorage.getItem("remoteController")})
    commons.getInstantMessages('envs');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertSchedulerDatetimePicker').innerHTML = data.schedulerDateTimePicker;
        document.querySelector('#insertSchedulerExpiresDatetimePicker').innerHTML = data.schedulerExpiresDateTimePicker;
        viewEnvScheduler(env);
    }
}

const saveScheduledEnv = async () => {
    /* Submit button to save a scheduled env */

    var selectedEnvs = [];
    let envCheckboxes = document.querySelectorAll('input[name="envCheckboxes"]:checked');
    for (let x=0; x < envCheckboxes.length; x++) {
        selectedEnvs.push(envCheckboxes[x].value);
        envCheckboxes[x].checked = false;
    }

    if (selectedEnvs.length == 0) {
        var envFullPath = document.querySelector("#insertEnvName").innerHTML;

        // User clicked on the env row "On-Scheduler" total cron. This ia a singular env selectioin
        if (envFullPath != "all") {
            selectedEnvs = [envFullPath];
        }
    }

    if (selectedEnvs.length == 0 || selectedEnvs == "") {
        alert("Please select one or more envs to schedule a reservation")
        return
    }

    if (selectedEnvs.length == 0 && env == null) {
        // env = all, means that the user did not click on an env row
        // So coming in here means the user did not select any env to reserve.
        alert('Please select one or more Envs to reserve')
        return
    }

    let minute = document.querySelector("#reserve-minute").value;
    let hour = document.querySelector("#reserve-hour").value;
    let dayOfMonth = document.querySelector("#reserve-dayOfMonth").value;
    let month = document.querySelector("#reserve-month").value;
    let dayOfWeek = document.querySelector("#reserve-dayOfWeek").value;
    let removeJobAfterRunning = document.querySelector('#removeEnvAfterRunning').checked;
    let reservationUser = document.querySelector("#reservationDomainUserSelections").value;

    let release_minute = document.querySelector("#release-minute").value;
    let release_hour = document.querySelector("#release-hour").value;
    let release_dayOfMonth = document.querySelector("#release-dayOfMonth").value;
    let release_month = document.querySelector("#release-month").value;
    let release_dayOfWeek = document.querySelector("#release-dayOfWeek").value;
    let reservationNotes = document.querySelector("#reservationNotesId").value;

    if (reservationNotes.trim().length > 100) {
        alert('Reservation notes must be up to 100 characters')
        return
    }

    const response = await commons.postData("/api/v1/env/scheduler/add",  
                            Object.assign({remoteController: sessionStorage.getItem("remoteController"),
                                            minute: minute, hour:hour, dayOfMonth: dayOfMonth,
                                            month: month, dayOfWeek: dayOfWeek,
                                            removeJobAfterRunning: removeJobAfterRunning,
                                            envs: selectedEnvs,
                                            reservationUser: reservationUser,
                                            reservationNotes: reservationNotes,
                                            release_minute: release_minute,
                                            release_hour: release_hour,
                                            release_dayOfMonth: release_dayOfMonth,
                                            release_month: release_month,
                                            release_dayOfWeek: release_dayOfWeek}) 
                                            );

    commons.getInstantMessages('envs');

    if (response.status == 'success') {
        document.querySelector('#envSchedulerStatus').style.color = 'green';
        document.querySelector("#envSchedulerStatus").innerHTML = 'Success';
    } else {
        document.querySelector('#envSchedulerStatus').style.color = 'red';
        document.querySelector("#envSchedulerStatus").innerHTML = response.errorMsg;
        //document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }

    document.querySelector('#removeEnvAfterRunning').checked = false;
    document.querySelector("#reservationNotesId").value = '';

    if (envFullPath == "all") {
        setTimeout(() => {
            viewEnvScheduler(env="all");
        }, 3000);
    } else {
        setTimeout(() => {
            viewEnvScheduler(envFullPath);
        }, 3000);
    }

    getSetupTableData();
    getEnvSchedulerCount();
}

const viewEnvScheduler = async (env) => {
    const data = await commons.postData("/api/v1/env/scheduler/scheduledEnvs",  
                                          {remoteController: sessionStorage.getItem("remoteController"),
                                           env: env
                                          });

    commons.getInstantMessages('envs');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertEnvSchedules').innerHTML = data.envSchedules;

        if (data.areThereJobs == false) {
            document.querySelector("#removeScheduledEnvsButton").style.display = 'none';
        } else {
            document.querySelector("#removeScheduledEnvsButton").style.display = 'block';
        }

        getDomainUserDropdown();
    }
}

const getEnvSchedulerCount = async () => {
    const data = await commons.postData("/api/v1/scheduler/getSchedulerCount",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                            searchPattern: "env="});
    commons.getInstantMessages('envs');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertEnvSchedulerCount').innerHTML = data.totalScheduledCronJobs;
    }
} 

const getDomainUserDropdown = async () => {
    let domain = document.querySelector('#pageAttributes').getAttribute('domain');

    const data = await commons.postData("/api/v1/scheduler/getDomainUsers",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         domain:domain});

    if (data.status == 'failed') {
        commons.getInstantMessages('scheduler');
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertDomainUserSelection').innerHTML = data.domainUsersDropdown;
    }
} 

const removeScheduledEnvsButton = async () => {
    /* <input type="checkbox" name="envSchedulerMgmt" env={env} month={month} day={day} hour={hour} minute={min}/> */

    // Collect the selected checkboxes and delete them all in one shot
    let scheduledJobsArray = document.querySelectorAll('input[name=envSchedulerMgmt]:checked');
    let removeScheduledJobsArray = [];

    // jobSearchPattern: Defined in pipelineViews:ScheduleJobs() <input jobSearchPattern="env={env}">
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
    
    const data = await commons.postData("/api/v1/env/scheduler/delete",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 removeScheduledEnvs: removeScheduledJobsArray});

    commons.getInstantMessages('envs'); 
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }

    // Wait a few seconds because kestackScheduler updates cron every 1 second
    intervalId = setTimeout(() => {
        viewEnvScheduler(env='all');
        getSetupTableData();
        getEnvSchedulerCount();
    }, 3000);
}

document.querySelector("#closeEnvSchedulerModal").addEventListener('click', event => {
    document.querySelector("#createEnvSchedulerModal").style.display = "none";
    document.querySelector('.modal-backdrop').remove()
    getSetupTableData();
    getEnvSchedulerCount();

    let envCheckboxes = document.querySelectorAll('input[name="envCheckboxes"]:checked');
    for (let x=0; x < envCheckboxes.length; x++) {
        if (envCheckboxes[x].checked) {
            envCheckboxes[x].checked = false;
        }
    }
})

const autoSetupTaskCreatorTemplate = async () => {
    /* A task creator. Create a task with a name.
       Connects to a device and enter commands.
       In Env Yaml files, use key-list: autoSetup: -taskName1, -taskName2
    */
    const data = await commons.postData("/api/v1/env/autoSetupTaskCreatorTemplate",  
                              {remoteController: sessionStorage.getItem("remoteController")});

    commons.getInstantMessages('envs'); 
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertAutoSetupTaskCreatorTemplate").innerHTML = data.autoSetupTaskCreatorTemplate;
    }
}

const autoSetup = (event) => {
    /* List of commands to run on the controller */
    let env = event.target.getAttribute('env');
    console.log(`--- autoSetup: ${env} ---`)
    document.querySelector("#insertAutoSetupEnv").innerHTML = `<strong>Auto-Setup Env:</strong>&ensp;&ensp;${env}`;
    document.querySelector("#autoSetupModal").style.display = 'block';
}

const autoTeardown = () => {
    /* List of commands to run on the controller */
    console.log(`---- auto teardown ----`)
}

document.querySelector("#closeEnvAutoSetupModal").addEventListener('click', event => {
    document.querySelector("#autoSetupModal").style.display = 'none';
})

window.getSetupTableData = getSetupTableData;
window.createEnv = createEnv;
window.closeCreateEnv = closeCreateEnv;
window.closeText = closeText;
window.deleteEnvGroups = deleteEnvGroups;
window.closeDeleteEnvGroups = closeDeleteEnvGroups;
window.filterSetup = filterSetup;
window.getFileContents = getFileContents;
window.modifyFile = commons.modifyFile;
window.reserveEnv = reserveEnv;
window.releaseEnv = releaseEnv;
window.resetEnv = resetEnv;
window.activeUsersList = activeUsersList;
window.getEnvCronScheduler = getEnvCronScheduler;
window.getEnvSchedulerCount = getEnvSchedulerCount;
window.saveScheduledEnv = saveScheduledEnv;
window.removeScheduledEnvsButton = removeScheduledEnvsButton;







