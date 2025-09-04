import * as commons from './commons.js';

var fullName = '';
var loginName = '';
var password = '';
var email = '';
var userRole = '';
var modifyFullName = '';

var selectedDomainsCheckboxes = null;
var userSelectedAllDomainsCheckbox = false;

document.addEventListener("DOMContentLoaded", function() {
    let domainUserRole = document.querySelector("#domainUserRole").getAttribute('role');
    let isUserSysAdmin = document.querySelector("#user").getAttribute('sysAdmin');
    let domain = document.querySelector("#pageAttributes").getAttribute("domain");

    if (['engineer', 'manager'].includes(domainUserRole) || isUserSysAdmin == 'False') {
        let divs = ["#systemSettingsDropdown"]
        for (let x=0; x<divs.length; x++) {
            let currentDiv = divs[x]
            document.querySelector(currentDiv).classList.add('hideFromUser');
        }            
    }

    document.querySelector("#insertSelectedDomainsLabel").style.display = 'none';
    commons.getServerTime();       
    getTableData();
    getDomainSelectionsForNewUser();
    commons.getInstantMessages('accountMgmt');
})

function viewPassword() {
    // There is an eye icon next to password input box.
    let passwordView = ['#password', '#modifyPassword']

    for (let x=0; x < passwordView.length; x++) {
        let currentPasswordView = document.querySelector(passwordView[x])

        if (currentPasswordView.type === "password") {
            currentPasswordView.type = "text";
        } else {
            currentPasswordView.type = "password";
        }
    }
}

function toggleCard(cardId, classname) {
    // classname hideModifyUserCard
    let div = document.querySelector(cardId);
  
    if (div.classList.contains(classname)) {
        div.classList.remove(classname);
    } else {
        div.classList.add(classname);
    }
}

function closeForm() {
    clearFields();
    toggleCard('#hideCard', 'hideCard');
}

function closeModifyUserForm() {
    clearFields();
    toggleCard('#hideModifyUserCard', 'hideModifyUserCard')

    let modifyUserCardHeaader = document.querySelector('#modifyUserCardHeaader');
    modifyUserCardHeader.innerHTML = 'Modify User:&ensp;'
}

function clearFields() {
    document.querySelector('#modifyLoginName').value = '';
    document.querySelector('#modifyPassword').value = '';
    document.querySelector('#modifyEmail').value = '';

    document.querySelector('#fullName').value = '';
    document.querySelector('#sysAdmin').checked = false;
    document.querySelector('#modifySysAdminTrue').checked = false;
    document.querySelector('#modifySysAdminFalse').checked = true;
    document.querySelector('#loginName').value = '';
    document.querySelector('#password').value = '';
    document.querySelector('#email').value = '';
    modifyFullName = '';
}

const getDomainSelectionsForNewUser = async () => {
    // Domain selection dropdown selection for new user
    let data = await commons.postData("/api/v1/system/account/getDomainSelectionForUserAccount",  
                                    {remoteController: sessionStorage.getItem("remoteController")})

    commons.getInstantMessages('accountMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertDomainSelections").innerHTML = data.domainSelections; 
        document.querySelector("#insertDomainSelectionForExistingUsers").innerHTML = data.domainSelections;

        // User selected individual domains
        let selectDomains = document.querySelector('#selectDomainsForUserAccountButton');
        selectDomains.addEventListener('click', selectDomainCheckbox => {
            let selectedDomainsObj = document.querySelectorAll('input[name="selectedDomains"]');
            selectedDomainsCheckboxes = [];

            for (var x=0; x < selectedDomainsObj.length; x++) {
                if (selectedDomainsObj[x].checked) {
                    let userSelectedDomain = selectedDomainsObj[x].getAttribute("domain")
                    let userSelectedDomainIndex = selectedDomainsObj[x].getAttribute("domainIndex")

                    let userRoleObj = document.querySelectorAll(`input[name="userRole-${userSelectedDomainIndex}"]`);
                    for (let i=0; i < userRoleObj.length; i++) {
                        if (userRoleObj[i].checked) {
                            var userRole = userRoleObj[i].value;
                        }
                    }

                    selectedDomainsCheckboxes.push([userSelectedDomain, userRole]);
                    selectedDomainsObj[x].checked = false;
                }
            }

            if (selectedDomainsCheckboxes != 'All' && selectedDomainsCheckboxes.length == 0) {
                // User might've unchecked the 'All' checkboxes and did not select any individual domain
                // So get all domains
                selectedDomainsCheckboxes = 'All';
            }

            document.querySelector("#insertSelectedDomainsLabel").style.display = 'block';
            document.querySelector("#insertSelectedDomains").innerHTML = selectedDomainsCheckboxes;

            /*
            if (userSelectedAllDomainsCheckbox) {

            } else {
                let selectedDomainsObj = document.querySelectorAll('input[name="selectedDomains"]');

                selectedDomainsCheckboxes = []; 
                for (var x=0; x < selectedDomainsObj.length; x++) {
                    if (selectedDomainsObj[x].checked) {
                        selectedDomainsCheckboxes.push(selectedDomainsObj[x].getAttribute("domain"));
                        selectedDomainsObj[x].checked = false;
                    }
                }

                if (selectedDomainsCheckboxes != 'All' && selectedDomainsCheckboxes.length == 0) {
                    // User might've unchecked the 'All' checkboxes and did not select any individual domain
                    // So get all domains
                    selectedDomainsCheckboxes = 'All';
               }

                document.querySelector("#insertSelectedDomainsLabel").style.display = 'block';
                document.querySelector("#insertSelectedDomains").innerHTML = selectedDomainsCheckboxes;
            }
            */
        })

    }
}

async function addUser() {
    // Get the radio button selection
    //let userRole =   document.querySelector('input[name="userRole"]:checked').id;
    //let sysAdminInput =   document.querySelector('input[name="sysAdmin"]');
    let sysAdminInput =   document.querySelector('#sysAdmin').checked;
    if (sysAdminInput) {
        var sysAdmin = true;
    } else {
        var sysAdmin = false;
    }

    let fullName =   document.querySelector('#fullName').value;
    fullName =       fullName.replace(/\b[a-z]/g, match => match.toUpperCase());
    let loginName =  document.querySelector('#loginName').value;
    let password =   document.querySelector('#password').value;
    let email =      document.querySelector('#email').value;

    var userFields = {"fullName":fullName, "loginName":loginName, "password":password};
    for (const [key, value] of Object.entries(userFields)) {
        if (value == "") {
            alert(`The user field cannot be empty: ${key}`)
            return
        }        
    }

    if (fullName.split(" ").length < 2) {
        alert('Full name must have first and last name');
        return
    }

    if (password.split(" ").length > 1) {
        alert('Password cannot have spaces');
        return
    }

    /*
    if (userRole == "") {
        alert("Please select a user role for the new user");
        return
    }
    */

    let data = await commons.postData("/api/v1/system/account/add",  
                                            {remoteController: sessionStorage.getItem("remoteController"), 
                                             fullName:fullName, loginName:loginName, password:password,
                                             email:email, sysAdmin: sysAdmin,
                                             selectedDomainsCheckboxes: selectedDomainsCheckboxes})

    commons.getInstantMessages('accountMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getTableData();
        clearFields();
        commons.blinkSuccess();
    }

    document.querySelector("#insertSelectedDomainsLabel").style.display = 'none';
    document.querySelector("#insertSelectedDomains").innerHTML = '';
    selectedDomainsCheckboxes = null;
}

async function modifyUser() {
    let sysAdmin =   document.querySelector('input[name="modifySysAdmin"]:checked').value;
    let loginName =  document.querySelector('#modifyLoginName').value;
    let password =   document.querySelector('#modifyPassword').value;
    let email =      document.querySelector('#modifyEmail').value;
    const userDetails = [{'loginName':loginName}, {'password':password}, {'email':email}, {'sysAdmin':sysAdmin}];
    const validModifiedFields = {};

    userDetails.forEach(detail => {
        for(const [key, value] of Object.entries(detail)) {
            if (value) {
                validModifiedFields[key] = value;
            }
        }
    })

    const data = await commons.postData("/api/v1/system/account/modify",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     userFullName: modifyFullName,
                                     modifyFields: validModifiedFields});

    commons.getInstantMessages('accountMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        clearFields();
        commons.blinkSuccess();
        getTableData();
    }
}

async function modifyUserForm(object) {
    /* object = the user's fullName by clicking on the user fullName */

    toggleCard('#hideModifyUserCard', 'hideModifyUserCard');
    let modifyUserCardHeaader = document.querySelector('#modifyUserCardHeaader');
    modifyFullName = object.getAttribute('user');
    modifyUserCardHeader.innerHTML = `Modify: ${modifyFullName}`;

    const userDetails = await commons.postData("/api/v1/system/account/getUserDetails",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             fullName: modifyFullName})

    var currentLoginName = document.querySelector('#modifyLoginName').setAttribute('placeholder', userDetails.loginName);
    var currentPassword = document.querySelector('#modifyPassword').setAttribute('type', 'password');
    var currentPassword = document.querySelector('#modifyPassword').setAttribute('placeholder', userDetails.password);
    var currentEmail = document.querySelector('#modifyEmail').setAttribute('placeholder', userDetails.email);
    var currentUserRole = userDetails.sysAdmin;

    getTableData();
    commons.getInstantMessages('accountMgmt');
}

async function deleteUser(object) {
    let userFullName = object.getAttribute('userFullName');
    let data = await commons.postData("/api/v1/system/account/delete",  
                            {remoteController: sessionStorage.getItem("remoteController"),
                             fullName:userFullName})

    commons.getInstantMessages('accountMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getTableData();
    }
}

async function getTableData() {
    const data = await commons.postData("/api/v1/system/account/tableData",  
                                        {remoteController: sessionStorage.getItem("remoteController")})

    commons.getInstantMessages('accountMgmt');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {                                   
        document.querySelector('#tableData').innerHTML = data.tableData
        commons.sortTable({tableId:"#userAccountTableData", columnIndex:1})

        let removeDomainsFromUserButton = document.querySelectorAll(".removeDomainsFromUserButton");
        for (let y=0; y < removeDomainsFromUserButton.length; y++) {

            removeDomainsFromUserButton[y].addEventListener('click', event => {
                let userFullName = event.target.getAttribute('user');
                let userIndex = event.target.getAttribute('userIndex');
                let userAccountDomainSelections = document.querySelectorAll(`input[name="selectedDomainsToRemove-${userIndex}"]`) 
                let removeDomainsCheckboxes = [];
                for (let z=0; z < userAccountDomainSelections.length; z++) {
                    if (userAccountDomainSelections[z].checked) {
                        removeDomainsCheckboxes.push(userAccountDomainSelections[z].getAttribute('domain'));
                    }
                }

                if (removeDomainsCheckboxes.length > 0) {
                    removeDomainsFromUserAccount(userFullName, removeDomainsCheckboxes);
                }
            })
        }

        let addDomainsForExistingUsersButton = document.querySelectorAll(".addDomainsForExistingUsersButton");
        for (let y=0; y < addDomainsForExistingUsersButton.length; y++) {
            addDomainsForExistingUsersButton[y].addEventListener('click', event => {
                let userFullName = event.target.getAttribute('user');
                let userIndex = event.target.getAttribute('userIndex');

                document.querySelector("#addDomainsToExistingUsersModal").style.display = 'block';
            })
        }
    }
}

const removeDomainsFromUserAccount = async (userFullName, domainList) => {
    const data = await commons.postData("/api/v1/system/account/removeDomainsFromUserAccount",  
                    {remoteController: sessionStorage.getItem("remoteController"),
                    accountUser: userFullName,
                    domains: domainList});

    commons.getInstantMessages('accountMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getTableData();
    }  
}

function searchForUser() {
    // Call search in commons.js
    commons.search({searchInputId:"#searchForUser", tableId:'#userAccountTableData', columnIndex:1})
}

async function openApiKeyModal(obj) {
    fullName = obj.getAttribute('user');
    const data = await commons.postData("/api/v1/system/account/getApiKey",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         userFullName: fullName});
    document.querySelector('#insertApiKey').innerHTML = `User: ${fullName}<br><br>API-Key: ${data.apiKey}`;
    document.querySelector('#getUser').setAttribute('user', fullName);

}

async function getPassword(obj) {
    fullName = obj.getAttribute('user');
    const data = await commons.postData("/api/v1/system/account/getPassword",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     userFullName: fullName})
    alert(`User: ${fullName}\nPassword: ${data.password}`)
}

async function regenerateApiKey(obj) {
    fullName = document.querySelector('#getUser').getAttribute('user')
    const data = await commons.postData("/api/v1/system/account/regenerateApiKey",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         userFullName: fullName})
    document.querySelector('#insertApiKey').innerHTML = `User: ${fullName}<br><br>API-Key: ${data.apiKey}`
}

window.toggleCard = toggleCard;
window.viewPassword = viewPassword;
window.addUser = addUser;
window.closeForm = closeForm;
window.clearFields = clearFields;
window.closeModifyUserForm = closeModifyUserForm;
window.modifyUser = modifyUser;
window.modifyUserForm = modifyUserForm;
window.regenerateApiKey = regenerateApiKey;
window.getPassword = getPassword;
window.openApiKeyModal = openApiKeyModal;
window.deleteUser = deleteUser;








