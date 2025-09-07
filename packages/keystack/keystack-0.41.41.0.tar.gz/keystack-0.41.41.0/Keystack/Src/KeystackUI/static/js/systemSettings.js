import * as commons from './commons.js';

document.addEventListener("DOMContentLoaded", function() { 
    /*
    let domainUserRole = document.querySelector("#domainUserRole").getAttribute('role');
    let noPrivileges = ['engineer', 'manager', 'director']
    if (noPrivileges.includes(domainUserRole)) {
        let divs = ["#systemSettingsDropdown"]
        for (let x=0; x<divs.length; x++) {
            let currentDiv = divs[x]
            document.querySelector(currentDiv).classList.add('hideFromUser');
        }            
    }
    */

    document.querySelector("#insertSettingsStatus").innerHTML = '';
    //document.querySelector("#footer").remove();
    document.querySelector("#mainBodyDiv").style.height = "100vh";
    getSettings();
    commons.getServerTime();
})

const getSettings = async () => {
    const data = await commons.postData("/api/v1/system/getSystemSettings",
                                        {remoteController: sessionStorage.getItem("remoteController")});

    if (data.status == "failed") {
        let status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
        document.querySelector("#insertSettingsStatus").innerHTML = status;
    } else {
        document.querySelector("#systemSettingsTextAreaId").innerHTML = data.settings;
    }
}

const modifyFile = async () => {
    try {
        let textarea = document.querySelector('#systemSettingsTextAreaId').value;
        console.log('systemSettings:modifyFile(): textarea');

        const data = await commons.postData("/api/v1/system/modifySystemSettings",
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         textarea: textarea})

        if (data.status == "success") {
            let status = `<div style='color:green'>Successfully modified file</div>`;
        } else {
            let status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
        }

    } catch (error) {    
        console.log("systemSettings:modifyFile() error: " + error);
    }
}

window.modifyFile = modifyFile;
window.getSettings = getSettings;
