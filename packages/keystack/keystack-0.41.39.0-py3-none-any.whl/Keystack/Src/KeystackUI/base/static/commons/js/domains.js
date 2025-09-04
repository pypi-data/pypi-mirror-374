import * as commons from './commons.js';

var selectedDomainsArray = new Array();
var selectedUsersForDomain = new Array();

var currentDomain = 'Communal';

document.addEventListener("DOMContentLoaded", function() {
    let isUserSysAdmin = document.querySelector("#user").getAttribute('sysAdmin');
    let domainUserRole = document.querySelector("#domainUserRole").getAttribute('role');

    if (['engineer', 'manager'].includes(domainUserRole) || isUserSysAdmin == "False") {
        let divs = ["#systemSettingsDropdown"]
        for (let x=0; x<divs.length; x++) {
            let currentDiv = divs[x]
            document.querySelector(currentDiv).classList.add('hideFromUser');
        }            
    }

    getDomains();
    commons.getInstantMessages('domains');
    commons.getServerTime();
})

/*
const getDomainUserGroups = async () => {
    // Get table data of selected user-groups in a domain

    const data = await commons.postData("/api/v1/system/domain/getUserGroups", 
                                    {remoteController: sessionStorage.getItem("remoteController")})

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {  
        if (data.userGroupTableData != null) {
            document.querySelector('#insertDomainSelectedUserGroupDataTable').innerHTML = data.userGroupTableData;
        }
    }
}
*/

const getSelectedDomains = () => {
    /* Manage Domains:  Collect all the selected checkboxes and 
       delete them all in one shot
    */
    var checkboxArray = document.querySelectorAll('input[name=domainsCheckboxes]:checked');
    selectedDomainsArray = [];
    
    for (let x=0; x < checkboxArray.length; x++) {
        let domain = checkboxArray[x].getAttribute('domain');
        selectedDomainsArray.push(domain)

        // Uncheck the checkbox because getGroups() will not refresh 
        // the page if any delete group checkbox is checked
        checkboxArray[x].checked = false;
    }
}

const getSelectedUsersFromDomainSelection = () => {
    let userCheckboxes = document.querySelectorAll('input[name="selectedUserForDomain"]');
    for (let x=0; x < userCheckboxes.length; x++) {
        if (userCheckboxes[x].checked) {
            let userIndex = userCheckboxes[x].getAttribute('userIndex');
            let userFullName = userCheckboxes[x].getAttribute('userFullName');

            let selectedUserRole = document.querySelectorAll(`input[name="userRole-${userIndex}"]`);
            for (let y=0; y < selectedUserRole.length; y++) {
                if (selectedUserRole[y].checked) {
                    selectedUsersForDomain.push([userFullName, selectedUserRole[y].value]);
                }
            }
        }
    }
}

document.querySelector("#closeAddUsersToDomainModal").addEventListener('click', event => {
    document.querySelector("#addUsersToDomainModal").style.display = 'none';
})

// topbar Add-Users-To-Domain modal
document.querySelector("#addUsersToDomain").addEventListener('click', async event => {
    getSelectedDomains();
    if (selectedDomainsArray.length == 0) {
        alert('Please select a domain first')
        return
    }

    const data = await commons.postData("/api/v1/system/domain/getAllUsersTableData", 
                    {remoteController: sessionStorage.getItem("remoteController")})

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {   
        document.querySelector('#addUsersToDomainsId').innerHTML = `Add Users To Domain(s): ${selectedDomainsArray}`
        document.querySelector('#insertUsersTableData').innerHTML = data.tableData;
        document.querySelector("#addUsersToDomainModal").style.display = 'block';
    }
})

document.querySelector("#addUsersToDomainButton").addEventListener('click', async event => {
    addUsersToDomains(selectedUsersForDomain, selectedDomainsArray);
})

document.querySelector("#removeUsersFromDomainButton").addEventListener('click', async event => {
    removeUsersFromDomains(selectedUsersForDomain, selectedDomainsArray);
})

const addUsersToDomains = async (usersAndDomainRoles, domains) => {
    /* Add domains to users */

    getSelectedUsersFromDomainSelection();
    const data = await commons.postData("/api/v1/system/domain/addUsersToDomains", 
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     usersAndDomainRoles: usersAndDomainRoles,
                                     domains: domains})

    commons.getInstantMessages('domains'); 
    document.querySelector("#addUsersToDomainModal").style.display = "none";
    selectedUsersForDomain = [];

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {  
        commons.blinkSuccess();
        getDomains();
    }
}

const removeUsersFromDomains = async (usersAndDomainRoles, domains) => {
    /* Remove domains from users */
    getSelectedUsersFromDomainSelection();
    const data = await commons.postData("/api/v1/system/domain/removeUsersFromDomains", 
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     usersAndDomainRoles: usersAndDomainRoles,
                                     domains: domains})

    commons.getInstantMessages('domains');
    document.querySelector("#addUsersToDomainModal").style.display = "none";
    selectedUsersForDomain = [];

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {  
        commons.blinkSuccess();
        getDomains();
    }
}

const getDomains = async () => {
    /* For Manage Domain. Get Table data for users to select
    and remove */

    const data = await commons.postData("/api/v1/system/domain/get", 
                                    {remoteController: sessionStorage.getItem("remoteController")})

    commons.getInstantMessages('domains'); 
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {    
        document.querySelector('#domainTableData').innerHTML = data.tableData;
    }
}

/*
const getDomainsDropdown = async () => {
    const data = await commons.postData("/api/v1/system/domain/getDomainsDropdown", 
                                    {remoteController: sessionStorage.getItem("remoteController")})
                              
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertDomains').innerHTML = data.domainsDropdown;
    }
}


const selectDomain = document.querySelector('#selectDomain');
selectDomain.addEventListener('click', event => {
    event.preventDefault();

    // Get the displayed text
    currentDomain = event.target.innerText;
    console.info(`Selected Domain: ${currentDomain}`)
    displayCurrentDomain();
    //getDomainUserGroups();
    //getUserGroupTable();
})


const getUserGroupTable = async () => {
    // Get all user-groups table data for users to select for a domain

    const data = await commons.postData("/api/v1/system/userGroup/getUserGroupTable", 
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     domain: currentDomain})

    commons.getInstantMessages('domains'); 
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertUserGroupTable').innerHTML = data.userGroupTable;
    }
}

const addUserGroupsToCurrentDomain = document.querySelector('#addUserGroupToDomain');
addUserGroupsToCurrentDomain.addEventListener('click', async event => {
    event.preventDefault();

    let userGroupSelectionsArray = document.querySelectorAll('input[name=userGroupsTableCheckboxes]:checked');
    let selectedUserGroupsArray = [];

    for (let x=0; x < userGroupSelectionsArray.length; x++) {
        let userGroup = userGroupSelectionsArray[x].getAttribute('userGroup');
        selectedUserGroupsArray.push(userGroup);
        userGroupSelectionsArray[x].checked = false;
    }

    //console.info(`AddUserGroupsToDomain: ${JSON.stringify(selectedUserGroupsArray)} to domain: ${currentDomain}`)

    const data = await commons.postData("/api/v1/system/domain/addUserGroups",
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                        domain: currentDomain,
                                        userGroups: selectedUserGroupsArray})

    commons.getInstantMessages('domains'); 
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getDomainUserGroups();
        getUserGroupTable();
    }
                                                                   
    selectedUserGroupsArray = [];
    userGroupSelectionsArray = [];
})

const removeUserGroupsFromCurrentDomain = document.querySelector('#removeUserGroupsFromDomain');
removeUserGroupsFromCurrentDomain.addEventListener('click', async event => {
    event.preventDefault();

    let domainSelectedUserGroupsSelectionsArray = document.querySelectorAll('input[name=domainUserGroupCheckboxes]:checked');
    let domainSelectedUserGroupsArray = [];

    for (let x=0; x < domainSelectedUserGroupsSelectionsArray.length; x++) {
        let userGroup = domainSelectedUserGroupsSelectionsArray[x].getAttribute('userGroup');
        domainSelectedUserGroupsArray.push(userGroup);
        domainSelectedUserGroupsSelectionsArray[x].checked = false;
    }

    const data = await commons.postData("/api/v1/system/domain/removeUserGroups",
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                        domain: currentDomain,
                                        userGroups: domainSelectedUserGroupsArray})

    commons.getInstantMessages('domains'); 
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getDomainUserGroups();
        getUserGroupTable();
    }
                                                                   
    domainSelectedUserGroupsArray = [];
    domainSelectedUserGroupsSelectionsArray = [];
})
*/

const createDomain = async () => {
    const domain = document.querySelector('#createDomainId').value;

    if (domain.includes('-')) {
        alert('Domain name cannot have dashes and spaces. Use underscores instead.');
        return
    }

    if (domain.includes(' ')) {
        alert('Domain name cannot have spaces');
        return
    }

    const data = await commons.postData("/api/v1/system/domain/create",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     domain: domain})

    commons.getInstantMessages('domains'); 
    if (data.status == "success") {
        const status = `<div style='color:green'>Successfully created domain: ${domain}</div>`;
        //document.querySelector("#domainStatus").innerHTML = status;
        //getDomainsDropdown();
        getDomains();
    } else {
        const status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
        document.querySelector("#domainStatus").innerHTML = status;
    }
   
    document.querySelector('#createDomainId').value = '';
}

const deleteDomain = document.querySelector('#deleteDomain');
deleteDomain.addEventListener('click', async event => {
    /* User selected a domain from dropdown menu */
    event.preventDefault();

    getSelectedDomains();
    if (selectedDomainsArray.includes('Communal')) {
        alert('Cannot delete the default domain: Communal')
        selectedDomainsArray = [];
        return
    }
    const data = await commons.postData("/api/v1/system/domain/delete",
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         domains: selectedDomainsArray});

    commons.getInstantMessages('domains');                                      
    if (data.status == "success") {
        let status = `<div style='color:green'>Successfully deleted domain: ${selectedDomainsArray}</div>`
        getDomains();
    } else {
        let status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
    }
})

const resetInputBox = () => {
    document.querySelector("#domainStatus").innerHTML = '';
}

window.createDomain = createDomain;
window.resetInputBox = resetInputBox;
//window.getUserGroupTable = getUserGroupTable;

