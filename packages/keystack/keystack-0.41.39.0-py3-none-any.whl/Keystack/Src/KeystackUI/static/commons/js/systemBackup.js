import * as commons from './commons.js';

// This var gets changed accordingly to what the user clicks
var backupFilename = null;

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

    commons.getInstantMessages('system');
    commons.getServerTime();
    getBackupFilesTable();
})

document.querySelector('#systemBackup').addEventListener('click', async event => {
    let backupFilename = document.querySelector("#backupFilename").value;
    if (backupFilename == '') {
        backupFilename = null
    }

    let response = await commons.postData("/api/v1/system/systemBackup",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             backupFilename: backupFilename
                                            })

    commons.getInstantMessages('system');

    if (response.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getBackupFilesTable();
    }
})


const getBackupFilesTable= async () => {
    const data = await commons.postData("/api/v1/system/getBackupFilesTable",  
                                          {remoteController: sessionStorage.getItem("remoteController")});

    commons.getInstantMessages('system');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#backupFiles').innerHTML = data.backupFilesHtml;

        const restoreSystemBackup = document.querySelectorAll('.restoreSystemBackup');
        for (var x=0; x < restoreSystemBackup.length; x++) {
            restoreSystemBackup[x].addEventListener('click', async event => {
                backupFilename = event.target.getAttribute('systemBackupFile');
            })
        }
    }
}

const uploadBackupFileForm = document.querySelector('#uploadBackupFileForm');
uploadBackupFileForm.addEventListener('submit', async event => {
    event.preventDefault();
    const url = '/api/v1/system/uploadBackupFile';
    const formData = new FormData(uploadBackupFileForm);

    formData.append('uploadBackupFile', uploadBackupFileForm[0]);

    const fileInput = document.querySelector('input[type=file]');
    // C:\fakepath\aiml_sanity_config.txt
    const path = fileInput.value;
    const fileName = path.split(/(\\|\/)/g).pop();

    if (fileName == '') {
        alert('Please select a .gz file to upload')
        return
    }

    let extension = fileName.split('.')[1]

    if (extension != 'gz') {
        alert('Upload a backup file must have a .gz extension')
        return
    }

    const fetchOptions = {
      method: 'post',
      body: formData
    };
  
    try {
        const response = await fetch(url, fetchOptions);
        const data = await response.json();
        commons.getInstantMessages('system');
        getBackupFilesTable();
        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        } else {
            commons.blinkSuccess();
        }
    } catch (error) {
        console.error(`Uploading backup file error: ${error}`)
        return error
    };
})

document.querySelector("#restoreSystemBackupConfirmed").addEventListener('click', async event => {
    let response = await commons.postData("/api/v1/system/systemRestore",  
                                                {remoteController: sessionStorage.getItem("remoteController"),
                                                backupFilename:backupFilename
                                                })
    commons.getInstantMessages('system');

    if (response.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getBackupFilesTable();
        document.querySelector("#restoreSystemBackupModal").style.display = "none";
        document.querySelector('.modal-backdrop').remove();
    }
})

const uncheckAllPorts = () => {
    /* Port Connections */
    var allPortsCheckboxes = document.querySelectorAll('input[name="portMgmtCheckboxes"]');
    for (var x=0; x < allPortsCheckboxes.length; x++) {
        allPortsCheckboxes[x].checked = false;
    }

    // Uncheck the selectAll checkbox
    let selectAllPortsCheckboxes = document.querySelector('#selectAllPortsCheckboxes');
    selectAllPortsCheckboxes.checked = false;
}

document.querySelector("#deleteBackupFiles").addEventListener('click', async event => {
    var backupFiles = [];
    var allCheckboxes = document.querySelectorAll('input[name="backupFileCheckbox"]');
    for (var x=0; x < allCheckboxes.length; x++) {
        if (allCheckboxes[x].checked == true) {
            backupFiles.push(allCheckboxes[x].getAttribute("backupFilename"))
        }
    }

    let response = await commons.postData("/api/v1/system/deleteBackupFiles",
                                                {remoteController: sessionStorage.getItem("remoteController"),
                                                 backupFiles: backupFiles
                                                })
    commons.getInstantMessages('system');

    if (response.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getBackupFilesTable();
    }
})
