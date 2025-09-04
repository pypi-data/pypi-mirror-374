import * as commons from './commons.js';
import * as base from "./base.js";

var selectedControllersArray = new Array();

/*
let hideInstantMessagesDiv = document.querySelector('.hideInstantMessages');
if (hideInstantMessagesDiv.classList.contains('hideInstantMessages')) {
    hideInstantMessagesDiv.classList.remove('hideInstantMessages');
}
*/

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
    
    getControllers();
    commons.getInstantMessages('controllers');
    commons.getServerTime();
})

function getSelectedSessions() {
    // Collect all the selected checkboxes and delete them all in one shot
    var checkboxArray = document.querySelectorAll('input[name=controllerCheckboxes]:checked');
    
    for (let x=0; x < checkboxArray.length; x++) {
        let controller = checkboxArray[x].getAttribute('controller');
        selectedControllersArray.push(controller)

        // Uncheck the checkbox because getControllers() will not refresh 
        // the page if any delete group checkbox is checked
        checkboxArray[x].checked = false;
    }
}

async function getControllers() {
    const data = await commons.postData("/api/v1/system/controller/getControllers",   
                                        {remoteController: sessionStorage.getItem("remoteController")});
    if (data.status == "failed") {
        commons.getInstantMessages('controllers');
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#tableData').innerHTML = data.tableData;
    }
}

async function addController() {
    let controllerName     = document.querySelector('#controllerName').value;
    let controllerIp       = document.querySelector('#controllerIp').value;
    let ipPort             = document.querySelector('#ipPort').value;
    let https              = document.querySelector('[name="https"]:checked').value;
    let verifyConnectivity = document.querySelector('[name="verifyConnectivity"]:checked').value;

    if (controllerName == '') {
        alert('You must provide a name for the controller');
        return
    }

    if (controllerIp == '') {
        alert('You must provide an IP address for the controller');
        return
    }

    console.log('addController()')
    // Clear the previous access key first
    /*
    document.querySelector("#insertAccessKey").innerHTML = '';
    const data1 = await postData("{% url "generateAccessKey" %}", "{{csrf_token}}", "POST")
    let accessKey = data1.accessKey;
    document.querySelector("#insertAccessKey").innerHTML = `Register this access key on the remote controller: ${data1.accessKey}`;
    */ 

    console.log(`addController: ${controllerIp}`);
    const data = await commons.postData("/api/v1/system/controller/add",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     controllerName: controllerName, 
                                     controllerIp: controllerIp,
                                     ipPort: ipPort, 
                                     https: https, 
                                     verifyConnectivity: verifyConnectivity})

    if (data.status == "success") {
        let status = `<div style='color:green'>Successfully added controller: ${controllerIp} ${ipPort}</div>`
        document.querySelector("#insertAccessKey").innerHTML = `Register this access key on the remote controller: ${data.accessKey}`;
    } else {
        let status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
        document.querySelector("#controllerStatus").innerHTML = status;
    }
   
    document.querySelector('#controllerName').value = '';
    document.querySelector('#controllerIp').value = '';
    document.querySelector('#ipPort').value = '';
    commons.getInstantMessages('controllers');
    getControllers();

    // Update the controller dropdown menu list in base.html
    base.getControllerList();
}

async function removeControllerButton() {
    getSelectedSessions();
    console.log(`Remove controllers: ${selectedControllersArray}`);
    let currentController = sessionStorage.getItem("remoteController");
    console.log(`Remove controllers: CurrentController = ${currentController}`);
    if (currentController.includes(":")) {
        currentController = currentController.split(":")[0];
    }

    let mainController = sessionStorage.getItem("mainController");

    if (selectedControllersArray.includes(currentController)) {
        alert(`You cannot remove a controller that is currently active: ${currentController}\n\nSwitch to the main controller ${mainController} in order to remove remote controllers.`)
        selectedControllersArray = [];
        return
    }

    const data = await commons.postData("/api/v1/system/controller/delete",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         'controllers': selectedControllersArray});

    if (data.status == "success") {
        let status = `<div style='color:green'>Successfully removed controller: ${selectedControllersArray}</div>`;
        document.querySelector("#removeControllerStatus").innerHTML = status;
    } else {
        let status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
        document.querySelector("#removeControllerStatus").innerHTML = status;
    }

    commons.getInstantMessages('controllers');
    selectedControllersArray = [];
    getControllers();

    // Update the controller dropdown menu list in base.html
    base.getControllerList();
}

function resetInputBox() {
    document.querySelector("#controllerStatus").innerHTML = '';
    document.querySelector("#insertAccessKey").innerHTML = '';
}

window.addController = addController;
window.removeControllerButton = removeControllerButton;
window.resetInputBox = resetInputBox;
window.getControllerList = base.getControllerList;





