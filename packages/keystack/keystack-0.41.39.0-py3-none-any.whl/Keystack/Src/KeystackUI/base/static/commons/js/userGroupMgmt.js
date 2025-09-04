import * as commons from './commons.js';

var currentUserGroup = 'Not-Selected';

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
    
    commons.getServerTime();
    getUserAccountDataTable();
    getUserGroupsDropdown();
    displayCurrentUserGroup();
})

function displayCurrentUserGroup() {
    document.querySelector('#topbarTitlePage').innerHTML = `User-Group&emsp;&emsp;|&emsp;&emsp;${currentUserGroup}`;
    document.querySelector('#insertUserGroupUsers').innerHTML = `${currentUserGroup}`;
}

function clearUserGroupUsers() {
    document.querySelector('#insertSelectedUsersDataTable').innerHTML = '';
}

const getUserAccountDataTable= async () => {
    // Get all users
    const data = await commons.postData("/api/v1/system/userGroup/getUserAccountDataTable",  
                        {remoteController: sessionStorage.getItem("remoteController")});

    if (data.status == 'failed') {
        commons.getInstantMessages('userGroup'); 
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertSelectUserDataTable').innerHTML = data.userNamesDataTable;
    }
}

const createUserGroup = document.querySelector('#createUserGroupNameId');
createUserGroup.addEventListener('click', async event => {
    event.preventDefault();
    let userGroup = document.querySelector('#userGroupName').value;
    if (userGroup == "") {
        alert('Please give a name for the user group without spaces')
        return
    }

    console.log(`createUserGroup: ${userGroup}`)
    const data = await commons.postData("/api/v1/system/userGroup/create",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         userGroupName: userGroup});

    if (data.status == 'failed') {
        commons.getInstantMessages('userGroup'); 
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        currentUserGroup = userGroup;
        displayCurrentUserGroup();
        clearUserGroupUsers();
        getUserGroupsDropdown();
    }
})

const addUsersToUserGroup = document.querySelector('#addUsersToUserGroup');
addUsersToUserGroup.addEventListener('click', async event => {
    event.preventDefault();
    if (currentUserGroup == 'Not-Selected') {
        alert('Please select a User-Group first')
        return
    }

    let userAccountSelectionsArray = document.querySelectorAll('input[name=userAccountCheckboxes]:checked');
    let selectedUserGroupAccountsArray = [];

    for (let x=0; x < userAccountSelectionsArray.length; x++) {
        let userAccount = userAccountSelectionsArray[x].getAttribute('account');
        selectedUserGroupAccountsArray.push(userAccount);
        userAccountSelectionsArray[x].checked = false;
    }

    const data = await commons.postData("/api/v1/system/userGroup/addUsersToUserGroup",
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                        userGroup: currentUserGroup,
                                        users: selectedUserGroupAccountsArray})
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getUserGroupUsers(currentUserGroup);
    }
    commons.getInstantMessages('userGroup');                                                                    
    selectedUserGroupAccountsArray = [];
})

const removeUsersFromUserGroup = document.querySelector('#removeUsersFromUserGroup');
removeUsersFromUserGroup.addEventListener('click', async event => {
    event.preventDefault();
    if (currentUserGroup == 'Not-Selected') {
        alert('Please select a User-Group first')
        return
    }

    let userAccountSelectionsArray = document.querySelectorAll('input[name=userGroupUsersCheckboxes]:checked');
    let selectedUserGroupAccountsArray = [];

    for (let x=0; x < userAccountSelectionsArray.length; x++) {
        let userAccount = userAccountSelectionsArray[x].getAttribute('account');
        selectedUserGroupAccountsArray.push(userAccount);
        userAccountSelectionsArray[x].checked = false;
    }

    const data = await commons.postData("/api/v1/system/userGroup/removeUsersFromUserGroup",
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                        userGroup: currentUserGroup,
                                        users: selectedUserGroupAccountsArray})
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getUserGroupUsers(currentUserGroup);
    }
    commons.getInstantMessages('userGroup');                                                               
    selectedUserGroupAccountsArray = [];
})

const deleteUserGroup = document.querySelector('#deleteUserGroup');
deleteUserGroup.addEventListener('click', async event => {
    event.preventDefault();
    if (currentUserGroup == 'Not-Selected') {
        alert('Please select a user-group to delete')
        return
    }

    const data = await commons.postData("/api/v1/system/userGroup/delete",
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                        userGroup: currentUserGroup})
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        document.querySelector('#insertSelectedUsersDataTable').innerHTML = '';
        currentUserGroup = 'Not-Selected';
        displayCurrentUserGroup();
        getUserGroupsDropdown();
    }
                                                                    
    commons.getInstantMessages('userGroup');
})

async function getUserGroupUsers(userGroup) {
    console.log(`userGroup:getUserGroupUsers: ${userGroup.toString()}`);
    const data = await commons.postData("/api/v1/system/userGroup/users",
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         userGroup: userGroup})
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        document.querySelector('#insertSelectedUsersDataTable').innerHTML = data.userGroupUsers;
    }
    commons.getInstantMessages('userGroup');
}

const getUserGroupsDropdown = async () => {
    const data = await commons.postData("/api/v1/system/userGroup/getUserGroupsDropdown",  
                                    {remoteController: sessionStorage.getItem("remoteController")});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertUserGroupSelections').innerHTML = data.userGroupsDropdownHtml;
    }
}

const selectUserGroup = document.querySelector('#selectUserGroup');
selectUserGroup.addEventListener('click', event => {
    event.preventDefault();

    // Get the displayed text
    currentUserGroup = event.target.innerText;
    console.info(`Selected User-Group: ${currentUserGroup}`)
    displayCurrentUserGroup();
    getUserGroupUsers(currentUserGroup);
    document.querySelector("#insertUserGroupName").innerHTML = currentUserGroup;
})


