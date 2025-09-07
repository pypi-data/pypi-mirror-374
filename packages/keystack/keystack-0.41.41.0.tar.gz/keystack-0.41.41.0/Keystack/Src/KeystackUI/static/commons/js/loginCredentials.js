import * as commons from './commons.js';

document.addEventListener("DOMContentLoaded", function() {
    if (['engineer', 'manager'].includes(domainUserRole) || isUserSysAdmin == "False") {
        let divs = ["#systemSettingsDropdown"]
        for (let x=0; x<divs.length; x++) {
            let currentDiv = divs[x]
            document.querySelector(currentDiv).classList.add('hideFromUser');
        }            
    }

    document.querySelector("#insertSettingsStatus").innerHTML = '';
    document.querySelector("#mainBodyDiv").style.height = "100vh";
    getSettings();
    commons.getServerTime();
})

const getSettings = async () => {
    let domain =  document.querySelector("#pageAttributes").getAttribute('domain');
    console.log(`--- loginCredentials: ${domain}`)
    const data = await commons.getData("/api/v1/system/loginCredentials", 
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain:  document.querySelector("#pageAttributes").getAttribute('domain')});

    if (data.status == "failed") {
        const status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
        document.querySelector("#insertSettingsStatus").innerHTML = status;
    } else {
        document.querySelector("#loginCredentialsTextAreaId").innerHTML = data.settings;
    }
}

const modifyFile = async () => {
    try {
        const textarea = document.querySelector('#loginCredentialsTextAreaId').value;
        //console.log(`systemSettings modifyFile(): ${textarea}`)

        const data = await commons.postData("/api/v1/system/loginCredentials",
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain:  document.querySelector("#pageAttributes").getAttribute('domain'),
                                             textarea: textarea})

        if (data.status == "success") {
            const status = `<div style='color:green'>Successfully modified file</div>`;
            document.querySelector("#insertSettingsStatus").innerHTML = status;
        } else {
            const status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
            document.querySelector("#insertSettingsStatus").innerHTML = status;
        }
    } catch (error) {    
        console.error("settings modifyFile() error: " + error);
    }
}

window.getSettings = getSettings;
window.modifyFile = modifyFile;

