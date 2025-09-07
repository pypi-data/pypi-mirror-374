import * as commons from './commons.js';

var selectedAccessKeyArray = new Array();

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
    getAccessKeys();
    commons.getInstantMessages('controllers');
    commons.getServerTime();
})

const getSelectedAccessKeys = () => {
    // Collect all the selected checkboxes and delete them all in one shot
    var checkboxArray = document.querySelectorAll('input[name=accessKeyCheckboxes]:checked');
    
    for (let x=0; x < checkboxArray.length; x++) {
        let accessKey = checkboxArray[x].getAttribute('accessKey');
        selectedAccessKeyArray.push(accessKey)

        // Uncheck the checkbox because getControllers() will not refresh 
        // the page if any delete group checkbox is checked
        checkboxArray[x].checked = false;
    }
}

const registerAccessKey = async () => {
    const controllerName = document.querySelector("#controllerName").value;
    const controllerIp = document.querySelector("#controllerIp").value;
    const accessKey = document.querySelector("#accessKey").value;

    if (controllerIp == '') {
        alert("You must provide the remote controller's IP address");
        return
    }

    if (controllerName == '') {
        alert("You must provide the remote controller's name");
        return
    }

    if (accessKey == '') {
        alert("You must provide the remote controller's access key");
        return
    }

    const data = await commons.postData("/api/v1/system/controller/registerRemoteAccessKey", 
                                     {controllerIp: controllerIp,
                                      controllerName: controllerName,
                                      accessKey: accessKey})

    if (data.status == "success") {
        let status = `<div style='color:green'>Successfully registered Access-Key</div>`;
        document.querySelector("#registerAccesskeyStatus").innerHTML = status;
    } else {
        let status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
        document.querySelector("#registerAccesskeyStatus").innerHTML = status;
    }
    
    document.querySelector('#controllerName').value = '';
    document.querySelector('#controllerIp').value = '';
    document.querySelector('#accessKey').value = '';
    getAccessKeys();
}

const getAccessKeys = async () => {
    console.log('getAccessKeys()')
    const data = await commons.postData("/api/v1/system/controller/getAccessKeys", {})
    console.log(`getAccessKeys(): ${data.tableData}`)
    document.querySelector('#tableData').innerHTML = data.tableData;
}

const removeAccessKey = async () => {
    getSelectedAccessKeys();
    console.log(`Remove access-keys: ${selectedAccessKeyArray}`)

    const data = await commons.postData("/api/v1/system/controller/removeAccessKeys",  
                                            {'accessKeys': selectedAccessKeyArray});
    console.log(`Remove access-keys: ${data.status} ${data.errorMsg}`)

    if (data.status == "success") {
        let status = `<div style='color:green'>Successfully removed access-keys</div>`;
        document.querySelector("#removeControllerStatus").innerHTML = status;
    } else {
        let status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
        document.querySelector("#removeControllerStatus").innerHTML = status;
    }

    selectedAccessKeyArray = new Array();
    getAccessKeys();
}

const resetInputBox = () => {
    document.querySelector("#registerAccesskeyStatus").innerHTML = '';
    document.querySelector("#removeControllerStatus").innerHTML = '';
}

window.registerAccessKey = registerAccessKey;
window.resetInputBox = resetInputBox;
window.removeAccessKey = removeAccessKey;

