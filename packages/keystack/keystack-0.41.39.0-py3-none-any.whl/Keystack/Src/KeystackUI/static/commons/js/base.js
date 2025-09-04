import * as commons from './commons.js';

var moduleClasses = [];
var intervalId = null;

document.addEventListener("DOMContentLoaded", function() {
    setTimeout(() => {
        // Default session timeout 3 hr
        // 36000000=1hr, 108000000=3hr
        window.location.href = '/logout'
    }, 10800000);

    let intervalId = setTimeout(commons.getServerTime, 100);

    insertSessionDomains();
    insertInventoryDomains();
    getControllerList();
    insertUserAllowedDomainsAndUserRole();

    // Stop the blinking error message
    let flashingError = document.querySelector("#flashingError");
    flashingError.addEventListener('click', event => {
        event.preventDefault();
        document.querySelector("#flashingError").innerHTML = '';
    })
})

const getLocalServerTime = () => {
    const data = commons.getServerTime();
    if (data.name == "TypeError") {
        clearTimeout(intervalId);
    }
}

document.querySelector("#showVersionId").addEventListener('click', event => {
    verifyVersion();
})

async function verifyVersion() {
    const data = await commons.getData("/api/v1/system/verifyVersion", 'GET', 
                                        {remoteController: sessionStorage.getItem("remoteController")});
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertKeystackVersion').innerHTML = data.keystackVersion;
    }
}

const insertUserAllowedDomainsAndUserRole = async () => {   
    const data = await commons.postData("/api/v1/system/getUserAllowedDomainsAndRoles",  
        {remoteController: remoteController})
        
    commons.getInstantMessages('globals');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertUserDomainMembershipTable").innerHTML = data.userAllowedDomainList;
    }
}

const hideClassFromRemoteControllers = () => {
    //console.log(`base.hideClassFromRemoteControllers() remoteController = ${sessionStorage.getItem('remoteController')}`)
    moduleClasses = document.querySelectorAll('.hideClassFromRemoteControllers');
    for (let moduleClass of moduleClasses) {
        moduleClass.style.display = "none";
    }
}

const unhideClassFromRemoteControllers = () => {
    //console.log(`base.unhideClassFromRemoteControllers() remoteController == ${sessionStorage.getItem('remoteController')}`)
    moduleClasses = document.querySelectorAll('.hideClassFromRemoteControllers');
    for (let moduleClass of moduleClasses) {
        moduleClass.style.display = "block";
    }
}

// This doesn't change. mainControllerIp is passed in by views located in base.html.
var mainControllerIp = document.querySelector("#mainControllerIp").getAttribute('value');
sessionStorage.setItem('mainControllerIp', mainControllerIp);

// New login remoteController == null
var remoteController = sessionStorage.getItem('remoteController');
//console.log(`Current remoteController: ${remoteController}`)
if (remoteController == null) {
    remoteController = mainControllerIp;
    sessionStorage.setItem('remoteController', mainControllerIp)
}

//console.log(`base:  mainControllerIp: ${mainControllerIp}  remoteController: ${remoteController}`)

if (remoteController == mainControllerIp) {
    unhideClassFromRemoteControllers();
} else {
    hideClassFromRemoteControllers();
}

if (typeof(sessionStorage) != "undefined") {
    // This changes when user selects a remoteController
    if (sessionStorage.getItem('remoteController') != null) {
        remoteController = sessionStorage.getItem('remoteController');
        //console.log(`CONTROLLER CHANGED.  mainControllerIp: ${mainControllerIp}  remoteController:${remoteController}`)
    }

    if (sessionStorage.getItem('remoteController') != mainControllerIp) {
        hideClassFromRemoteControllers();
    }
} else {
    //console.log(`CONTROLLER NOT CHANGED: mainControllerIp: ${mainControllerIp}  remoteController: ${remoteController}   typeOfSessionStore: ${typeof(sessionStorage)}`)
    // sessionStorage for controller is not defined yet. User hasn't selected a remoteController.
    // getControllerList() will default it to the mainControllerIp.
    sessionStorage.setItem('remoteController', remoteController);
}

export const getControllerList = async () => {
    if (remoteController == "None") {
        remoteController = mainControllerIp;
        sessionStorage.setItem("remoteController", remoteController);
        //console.log(`getControllerList: Setting remoteController to: ${remoteController}`)
    }

    mainControllerIp = sessionStorage.getItem("mainControllerIp");
    //console.log(`getControllerList() remoteController:${remoteController}  mainControllerIp:${mainControllerIp}`)

    // Get a list of configured controllers for dropdown menu
    // GetControllerList -> /topbar/settings/controllers
    const data = await commons.postData("/api/v1/system/controller/getControllerList",  
                                                {remoteController: remoteController})
                                                
    commons.getInstantMessages('controllers');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>'; 
        sessionStorage.setItem('remoteController', mainControllerIp);
    } else {
        document.querySelector('#getControllers').innerHTML = data.controllers;
    }
}

const connectToController = (object=null) => {
    if (object != null) {
        // User selected a remoteController
        remoteController = object.getAttribute('connectToController');
        //console.log(`Set connectToController: ${remoteController}`)
        // Make variable remoteController persist across all pages
        sessionStorage.setItem("remoteController", remoteController);
    }

    // This will update the remoteController dropdown list
    getControllerList();

    // Refresh the page with the connected controller's data
    window.location.reload();
}

const getPlaybookGroupMenu = async () => {
    // Called in base.html onclick. Get sidebar Playbook dropdown menu
    const data = await commons.postData("/api/v1/playbook/groups",  
                      {remoteController: sessionStorage.getItem("remoteController")});

    commons.getInstantMessages('playbooks');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertPlaybookGroupMenu').innerHTML = data.playbookGroups;
    }	
}

const getSidebarModules = async () => {
    /* Called in base.html onclick.
       Get all modules for sidebar one at a time 
       Using counter as index guidance.  
       If counter == len(allModules), then noMoreModule is set to True and break out.
    */
  
    document.querySelector('#insertModules').innerHTML = '';
    let counter = 0;
    let retry = 0;
    let retryMax = 3;

    while (true) {

        const data = await commons.postData("/api/v1/modules",  
                      {remoteController: sessionStorage.getItem("remoteController"), counter: counter})

        if (data.modulesHtml) {
            document.querySelector('#insertModules').innerHTML += data.modulesHtml;
            counter++;
  
            if (data.noMoreModule == true) {
                break
            }
        } else {
            // Must break if there is no data to avoid an infinite loop
            //console.log(`getModules: No more modules. Breaking.`)
            break
        }
    }
}
  
const getTestResultMenu = async (whichTestType) => {
    // Get sidebar test result dropdown menu
    const data = await commons.postData("/api/v1/results/sidebarMenu",  
                             {remoteController: sessionStorage.getItem("remoteController"),
                              whichResultType: whichTestType});

    commons.getInstantMessages('testResults');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertActiveTestResultMenu').innerHTML = data.testResults;
    }	
}

const getEnvGroupMenu = async () => {
    // Get sidebar Env dropdown menu
    const data = await commons.postData("/api/v1/env/envGroups",  
                        {remoteController: sessionStorage.getItem("remoteController")});

    commons.getInstantMessages('envs');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertEnvGroupMenu').innerHTML = data.envGroups;
    }	
}

const getTestcasesMenu = async () => {
    /* Get sidebar Testcsae Group Folders menu
       Called in base.html onclick.
    */
  
    document.querySelector('#insertTestcaseGroupsMenu').innerHTML = '';

    const data = await commons.postData("/api/v1/testcases",  
                    {remoteController: sessionStorage.getItem("remoteController")})

    document.querySelector('#insertTestcaseGroupsMenu').innerHTML += data.testcasesHtml;
}

const getTestcasesMenu_backup = async () => {
    /* Get sidebar Testcsae Group Folders menu
       Called in base.html onclick.
       Get all modules for sidebar one at a time 
       Using counter as index guidance.  
       If counter == len(allModules), then noMoreModule is set to True and break out.
    */
  
    document.querySelector('#insertTestcaseGroupsMenu').innerHTML = '';
    let counter = 0;
    let retry = 0;
    let retryMax = 3;

    while (true) {

        const data = await commons.postData("/api/v1/testcases",  
                      {remoteController: sessionStorage.getItem("remoteController"), counter: counter})

        if (data.testcasesHtml) {
            document.querySelector('#insertTestcaseGroupsMenu').innerHTML += data.testcasesHtml;
            counter++;
  
            if (data.noMoreModule == true) {
                break
            }
        } else {
            // Must break if there is no data to avoid an infinite loop
            break
        }
    }
}

const getPortGroupMenu = async () => {
    // sidebar: port-group domains
    const data = await commons.postData("/api/v1/portGroup/domains",  
                    {remoteController: sessionStorage.getItem("remoteController")});

    commons.getInstantMessages('portGroup');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>'; 
    } else {
        document.querySelector('#insertPortGroupDomains').innerHTML = data.domains;
    }
}

const insertSessionDomains = async () => {
    // sidebar: Insert pipeline domains for users to select
    const data = await commons.postData("/api/v1/pipelines/getSessionDomains",  
                    {remoteController: sessionStorage.getItem("remoteController")});

    commons.getInstantMessages('pipelines'); 
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>'; 
    } else {
        document.querySelector('#insertSessionDomains').innerHTML = data.sessionDomains;
    }
}

const insertInventoryDomains = async () => {
    // sidebar: lab inventory
    const data = await commons.postData("/api/v1/lab/inventory/domains",  
                    {remoteController: sessionStorage.getItem("remoteController")});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>'; 
    } else {
        document.querySelector('#insertInventoryDomains').innerHTML = data.inventoryDomains;
    }
}

window.getPlaybookGroupMenu = getPlaybookGroupMenu;
window.getEnvGroupMenu = getEnvGroupMenu;
window.getTestResultMenu = getTestResultMenu;
window.getSidebarModules = getSidebarModules;
window.getTestcasesMenu = getTestcasesMenu;
window.getControllerList = getControllerList;
window.connectToController = connectToController;
window.getPortGroupMenu = getPortGroupMenu;









