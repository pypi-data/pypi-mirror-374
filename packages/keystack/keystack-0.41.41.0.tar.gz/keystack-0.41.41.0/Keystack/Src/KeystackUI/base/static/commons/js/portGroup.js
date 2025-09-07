import * as commons from './commons.js';

var portGroup = null;
var refreshPageInterval = 5000;
var intervalId = null;


document.addEventListener("DOMContentLoaded", (event) => {
    let isUserSysAdmin = document.querySelector("#user").getAttribute('sysAdmin');
    let domainUserRole = document.querySelector("#domainUserRole").getAttribute('role');

    if (domainUserRole == 'engineer') {
        let divs = ["#removePortGroups", "#createPortGroupLabelId", "#createPortGroupInput", 
                    "#createPortGroupButton", "#portGroupNotesRow",
                    "#portGroupRemoveFromActiveUsersButton", "#portGroupRemoveFromWaitListButton"]
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

    commons.getInstantMessages('portGroup');
    commons.getServerTime();
    //getPortGroupSchedulerCount();

    intervalId = setTimeout(() => {
        getPortGroupTable();
    }, 100);
})

const isDropdownOpened = (dropdownId) => {
    if (dropdownId) {
        return dropdownId.classList.contains('show');
    }
}

const getPortGroupTable = async () => {
    var portGroupCheckboxListener = document.querySelectorAll('input[name=portGroupCheckboxes]:checked');
    if (portGroupCheckboxListener.length > 0) {
        return
    }

    var showPortGroupPortsDropdownClass = document.querySelectorAll('.openedPortConfigsClass');
    for (let x=0; x < showPortGroupPortsDropdownClass.length; x++) {
        if (showPortGroupPortsDropdownClass[x].style.display = 'block') {
            return
        }
    }

    let domain = document.querySelector("#pageAttributes").getAttribute('domain');
    const data = await commons.postData("/api/v1/portGroup/getTableData",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain});

    if (data.name == "TypeError") {
        clearTimeout(intervalId);
    }

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#portGroupTable').innerHTML = data.portGroupTableData;

        var portGroupTable = document.querySelector("#portGroupTable1");
        var tableHeaderRow = portGroupTable.rows[0];

        for (var cellIndex=0; cellIndex < tableHeaderRow.cells.length; cellIndex++) {
            if (tableHeaderRow.cells[cellIndex].innerText === 'Ports') {
                var portsCellIndex = cellIndex;
            }

            if (tableHeaderRow.cells[cellIndex].innerText === 'Actively-Reserved') {
                var reservationMgmtCellIndex = cellIndex;
            }

            if (tableHeaderRow.cells[cellIndex].innerText === 'Reserve') {
                var reservePortGroupCellIndex = cellIndex;
            }

            if (tableHeaderRow.cells[cellIndex].innerText === 'Release') {
                var releasePortGroupCellIndex = cellIndex;
            }

            if (tableHeaderRow.cells[cellIndex].innerText === 'Reset-Active-Reservations') {
                var resetPortGroupCellIndex = cellIndex;
            }
        }

        intervalId = setTimeout(getPortGroupTable, refreshPageInterval);
    }
}

const getActiveUserMgmtTable = async (event) => {
    /* Get just the port-group activeUsers */
    portGroup = event.target.getAttribute('portGroup');
    getActiveUserMgmtTableData(portGroup);
}

const getActiveUserMgmtTableData = async (portGroup) => {
    let domain = document.querySelector("#pageAttributes").getAttribute('domain');
    document.querySelector("#insertActiveUserMgmtPortGroup").innerHTML = `Domain:${domain}&ensp;&ensp;Port-Group:&ensp;${portGroup}`;

    const data = await commons.postData("/api/v1/portGroup/activeUsersTable",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain, portGroup: portGroup});

    commons.getInstantMessages('portGroup');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        // Show the active-user list
        document.querySelector("#insertPortGroupActiveUsers").innerHTML = data.tableData;
    }
}

const getWaitListUserMgmtTable = async (event) => {
    portGroup = event.target.getAttribute('portGroup');
    getWaitListUserMgmtTableData(portGroup);
}

const getWaitListUserMgmtTableData = async (portGroup) => {
    let domain = document.querySelector("#pageAttributes").getAttribute('domain');
    const data = await commons.postData("/api/v1/portGroup/waitListTable",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain, portGroup: portGroup});

    commons.getInstantMessages('portGroup');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#portGroupInsertWaitList").innerHTML = data.tableData;
    }
}

const activeUsersList = (obj) => {
    // User clicked on activeUser link

    let portGroup = obj.getAttribute('portGroup');
    getActiveUserMgmtTableData(portGroup);
    getWaitListUserMgmtTableData(portGroup);
}

const portGroupRemoveFromActiveUsersButton = document.querySelector("#portGroupRemoveFromActiveUsersButton");
portGroupRemoveFromActiveUsersButton.addEventListener('click', async event => {
    let activeUsersCheckboxes = document.querySelectorAll('input[name="portGroupActiveUsersCheckboxes"]:checked');
    let selectedActiveUsers = [];

    activeUsersCheckboxes.forEach((checkbox) => {
        let portGroupActiveUsersCheckboxList = {sessionId: checkbox.getAttribute('sessionId'),
                                                stage: checkbox.getAttribute('stage'),
                                                task: checkbox.getAttribute('task'),
                                                user: checkbox.getAttribute('user')
                                               }
        selectedActiveUsers.push(portGroupActiveUsersCheckboxList)
        checkbox.checked = false;
    })

    let domain = document.querySelector("#pageAttributes").getAttribute('domain');
    const data = await commons.postData("/api/v1/portGroup/removeFromActiveUsersListManually",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain, portGroup: portGroup, activeUsersList: selectedActiveUsers});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getActiveUserMgmtTableData(portGroup);
        getWaitListUserMgmtTableData(portGroup);
    }
})

const portGroupRemoveFromWaitListButton = document.querySelector("#portGroupRemoveFromWaitListButton");
portGroupRemoveFromWaitListButton.addEventListener('click', async event => {
    let waitListCheckboxes = document.querySelectorAll('input[name="portGroupWaitListCheckboxes"]:checked');
    let selectedWaitListUsers = [];

    waitListCheckboxes.forEach((checkbox) => {
        let portGroupWaitListCheckboxList = {sessionId: checkbox.getAttribute('sessionId'),
                                             portGroup: checkbox.getAttribute('portGroup'),
                                             stage: checkbox.getAttribute('stage'),
                                             task: checkbox.getAttribute('task'),
                                             user: checkbox.getAttribute('user')
                                            }
        selectedWaitListUsers.push(portGroupWaitListCheckboxList)
        checkbox.checked = false;
    })

    let domain = document.querySelector("#pageAttributes").getAttribute('domain');
    const data = await commons.postData("/api/v1/portGroup/removeFromWaitList",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain, waitListUsers: selectedWaitListUsers});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getWaitListUserMgmtTableData(portGroup);
    }
})

const reservePortGroup = async (event) => {
    let domain = document.querySelector("#pageAttributes").getAttribute('domain');
    let portGroup = event.getAttribute('portGroup');
    const data = await commons.postData("/api/v1/portGroup/reserve",  
                    {remoteController: sessionStorage.getItem("remoteController"),
                     domain: domain, portGroup: portGroup});

    commons.getInstantMessages('portGroup');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortGroupTable();
    }    
}

const releasePortGroup = async (event) => {
    let domain = document.querySelector("#pageAttributes").getAttribute('domain');
    let portGroup = event.getAttribute('portGroup');

    const data = await commons.postData("/api/v1/portGroup/release",  
                    {remoteController: sessionStorage.getItem("remoteController"),
                     domain: domain, portGroup: portGroup});

    commons.getInstantMessages('portGroup');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortGroupTable();
    }    
}

const resetPortGroup = async (event) => {
    let domain = document.querySelector("#pageAttributes").getAttribute('domain');
    let portGroup = event.getAttribute('portGroup');
    const data = await commons.postData("/api/v1/portGroup/reset",  
                    {remoteController: sessionStorage.getItem("remoteController"),
                     domain: domain, portGroup: portGroup});

    commons.getInstantMessages('portGroup');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortGroupTable();
    }    
}

/*
const getPortConfigurationTable = async (event) => {
    let domain = document.querySelector("#pageAttributes").getAttribute('domain');
    let portGroup = event.target.getAttribute('portGroup');

    // Open the port's configuration modal
    document.querySelector('#portConfigsModal').style.display = 'block';

    const data = await commons.postData("/api/v1/portGroup/portsTable",  
                    {remoteController: sessionStorage.getItem("remoteController"),
                     domain: domain, portGroup: portGroup});

    commons.getInstantMessages('portGroup');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertPortGroupPortsTable").innerHTML = data.portsTable;
    }
}
*/

let closePortConfigsModalButton = document.querySelector("#closePortConfigsModal")
closePortConfigsModalButton.addEventListener('click', event => {
    document.querySelector('#portConfigsModal').style.display = 'none';
})

const createPortGroupButton = document.querySelector("#createPortGroupButton");
if (createPortGroupButton) {
    createPortGroupButton.addEventListener('click', async event => {
        let domain = document.querySelector("#pageAttributes").getAttribute('domain');
        let portGroup = document.querySelector("#createPortGroupInput").value;
        if (portGroup == '') {
            alert('Error: Port Group name cannot be blank')
            return
        }


        const data = await commons.postData("/api/v1/portGroup/create",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     domain: domain, portGroup: portGroup});

        commons.getInstantMessages('portGroup');
        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        } else {
            getPortGroupTable();
        }

        document.querySelector("#createPortGroupInput").value = '';
    })
}

let removePortGroups = document.querySelector('#removePortGroups');
removePortGroups.addEventListener('click', async event => {
    var portGroupCheckboxList = new Array();
    let portGroupCheckboxes = document.querySelectorAll('input[name="portGroupCheckboxes"]:checked');
    portGroupCheckboxes.forEach((checkbox) => {
        portGroupCheckboxList.push(checkbox.getAttribute('portGroup'));
        checkbox.checked = false;
    })

    let domain = document.querySelector("#pageAttributes").getAttribute('domain');
    const data = await commons.postData("/api/v1/portGroup/delete",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain, portGroups: portGroupCheckboxList});

    commons.getInstantMessages('portGroup');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortGroupTable();
    }
})


const getPortGroupCronScheduler = async (object) => {
    // Get dropdown selections for minute, hour, day, month and dayOfWeek

    document.querySelector("#portGroupSchedulerStatus").innerHTML = '';

    let portGroup = object.getAttribute('portGroup');
    if (portGroup != "all") {
        document.querySelector("#insertPortGroupName").innerHTML = portGroup;
    }

    const data = await commons.postData("/api/v1/portGroup/scheduler/getCronScheduler",  
                                        {remoteController: sessionStorage.getItem("remoteController")})
    if (data.status == 'failed') {
        commons.getInstantMessages('portGroup');
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertSchedulerDatetimePicker').innerHTML = data.schedulerDateTimePicker;
        document.querySelector('#insertSchedulerExpiresDatetimePicker').innerHTML = data.schedulerExpiresDateTimePicker;
        viewPortGroupScheduler(portGroup);
    }
}

const saveScheduledPortGroup = async () => {
    /* Submit button to save a scheduled env */

    let domain = document.querySelector("#pageAttributes").getAttribute('domain');

    let selectedPortGroups = [];
    let portGroupCheckboxes = document.querySelectorAll('input[name="portGroupCheckboxes"]:checked');
    portGroupCheckboxes.forEach((checkbox) => {
        selectedPortGroups.push(checkbox.getAttribute('portGroup'));
        checkbox.checked = false;
    })

    if (selectedPortGroups.length == 0) {
        var portGroup = document.querySelector("#insertPortGroupName").innerHTML;

        // User clicked on the env row "On-Scheduler" total crons
        if (portGroup != "all") {
            selectedPortGroups = [portGroup];
        }
    }

    if (selectedPortGroups.length == 0 && env == null) {
        // portGroup = all, means that the user did not click on an env row
        // So coming in here means the user did not select any portGroup to reserve.
        alert('Please select one or more Port-Group to reserve')
        return
    }

    let minute = document.querySelector("#reserve-minute").value;
    let hour = document.querySelector("#reserve-hour").value;
    let dayOfMonth = document.querySelector("#reserve-dayOfMonth").value;
    let month = document.querySelector("#reserve-month").value;
    let dayOfWeek = document.querySelector("#reserve-dayOfWeek").value;
    let removeJobAfterRunning = document.querySelector('#removeJobAfterRunning').checked;
    let reservationUser = document.querySelector("#reservationDomainUserSelections").value;

    let release_minute = document.querySelector("#release-minute").value;
    let release_hour = document.querySelector("#release-hour").value;
    let release_dayOfMonth = document.querySelector("#release-dayOfMonth").value;
    let release_month = document.querySelector("#release-month").value;
    let release_dayOfWeek = document.querySelector("#release-dayOfWeek").value;

    const response = await commons.postData("/api/v1/portGroup/scheduler/add",  
                            Object.assign({remoteController: sessionStorage.getItem("remoteController"),
                                           minute: minute, hour:hour, dayOfMonth: dayOfMonth,
                                           month: month, dayOfWeek: dayOfWeek,
                                           removeJobAfterRunning: removeJobAfterRunning,
                                           domain: domain,
                                           portGroups: selectedPortGroups,
                                           reservationUser: reservationUser,
                                           release_minute: release_minute,
                                           release_hour: release_hour,
                                           release_dayOfMonth: release_dayOfMonth,
                                           release_month: release_month,
                                           release_dayOfWeek: release_dayOfWeek})
                                           );

    commons.getInstantMessages('portGroup');

    if (response.status == 'success') {
        document.querySelector('#portGroupSchedulerStatus').style.color = 'green';
        document.querySelector("#portGroupSchedulerStatus").innerHTML = 'Success';
    } else {
        document.querySelector('#portGroupSchedulerStatus').style.color = 'red';
        document.querySelector("#portGroupSchedulerStatus").innerHTML = `<h7>${response.errorMsg}</h7>`;
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }

    document.querySelector('#removeJobAfterRunning').checked = false;

    if (portGroup == "all") {
        setTimeout(() => {
            viewPortGroupScheduler(portGroup="all");
        }, 6000);
    } else {
        setTimeout(() => {
            viewPortGroupScheduler(portGroup="all");
        }, 6000);
    }

    getPortGroupTable();
    //getPortGroupSchedulerCount();
}

const viewPortGroupScheduler = async (portGroup) => {
    // Reservation table data
    const data = await commons.postData("/api/v1/portGroup/scheduler/scheduledPortGroups",  
                                          {remoteController: sessionStorage.getItem("remoteController"),
                                           portGroup: portGroup});

    if (data.status == 'failed') {
        commons.getInstantMessages('portGroup');
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertPortGroupSchedules').innerHTML = data.portGroupSchedules;

        if (data.areThereJobs == false) {
            document.querySelector("#removeScheduledPortGroupsButton").style.display = 'none';
        } else {
            document.querySelector("#removeScheduledPortGroupsButton").style.display = 'block';
        }

        getDomainUserDropdown();
    }
}

const getPortGroupSchedulerCount = async () => {
    const data = await commons.postData("/api/v1/scheduler/getSchedulerCount",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                            searchPattern: "portGroup="});
    if (data.status == 'failed') {
        commons.getInstantMessages('portGroup');
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertPortGroupSchedulerCount').innerHTML = data.totalScheduledCronJobs;
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

const removeScheduledPortGroupsButton = async () => {
    /* <input type="checkbox" name="portGroupSchedulerMgmt" portGroup={portGroup} month={month} day={day} hour={hour} minute={min}/> */

    // Collect all the selected checkboxes and delete them all in one shot
    let scheduledJobsArray = document.querySelectorAll('input[name=portGroupSchedulerMgmt]:checked');
    let removeScheduledJobsArray = [];

    // jobSearchPattern: Defined in pipelineViews:ScheduleJobs() <input jobSearchPattern="portGroup={portGroup}">
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
    
    const data = await commons.postData("/api/v1/portGroup/scheduler/delete",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 removeScheduledPortGroups: removeScheduledJobsArray});

    commons.getInstantMessages('portGroup'); 
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }
    viewPortGroupScheduler(portGroup="all");
    //getPortGroupSchedulerCount();
}

document.querySelector("#closePortGroupSchedulerModal").addEventListener('click', event => {
    getPortGroupTable();
    //getPortGroupSchedulerCount();
})

window.getPortGroupCronScheduler = getPortGroupCronScheduler;
window.getPortGroupSchedulerCount = getPortGroupSchedulerCount;
window.saveScheduledPortGroup = saveScheduledPortGroup;
window.removeScheduledPortGroupsButton = removeScheduledPortGroupsButton;
window.activeUsersList = activeUsersList;
window.reservePortGroup = reservePortGroup;
window.releasePortGroup = releasePortGroup;
window.resetPortGroup = resetPortGroup;

