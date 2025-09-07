import * as commons from './commons.js';

var nestedFolderCounter = 0;
// Default 100.  User defined in setFilesPerPage()
var resultsPerPage = 100;
var sessionsInterval = 10000;
var intervalId = 0;
var isCurrentlyInAwsS3UploadPage = null;

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
    
    getAwsS3Uploads();
    commons.getServerTime();
    commons.getInstantMessages('debug');

    isAwsS3ServiceRunning();
    isAwsS3DebugEnabled();

    setInterval(() => {
       isAwsS3ServiceRunning();
    }, 10000);
})

async function getAwsS3Uploads(object=null) {
    /* object is page buttons onclick */
    isCurrentlyInAwsS3UploadPage = true;

    // Blank out the page
    document.querySelector('#insertContents').innerHTML = '';
    let pageIndexRange = [];
    let getPageNumber = 1;

    if (object == null) {
        // Default getting up to 25 test results per page
        pageIndexRange.push(`0:${resultsPerPage}`);
    } else {
        // Uesr selected a page number that contains a range of file indexes. Ex: 101-200.
        getPageNumber = object.getAttribute("getPageNumber");
        pageIndexRange.push(object.getAttribute("pageIndexRange"));
    }

    // pageIndexRange = 0:100
    const splitIndexRange = pageIndexRange[0];
    const startingIndex =  Number(splitIndexRange.split(":")[0]);
    const total = parseInt(startingIndex) + parseInt(resultsPerPage);

    let data = await commons.postData("/api/v1/debug/awsS3/getUploads",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                        pageIndexRange:pageIndexRange, getPageNumber:getPageNumber,
                                        resultsPerPage:Number(resultsPerPage)})

    document.querySelector('#insertContents').innerHTML += data.pages;

    // This must sit here after getTestResultPages() in order to work.
    // This code goes in conjuntion with testResultsTreeView.css for expanding the nested tree view
    await addListeners("caret2");

    if (intervalId == 0) {
        intervalId = setInterval(getAwsS3Uploads, sessionsInterval)
    }
}

function addListeners(caretName="caret2") {
    // caret2
    window[caretName] = document.getElementsByClassName(caretName);

    for (let x= 0; x < window[caretName].length; x++) {
        window[caretName][x].addEventListener("click", function() {
            this.parentElement.querySelector(".nested").classList.toggle("active");            
        });
    }
}

function getSelectedCheckboxes() {
    // Collect all the selected checkboxes and delete them all in one shot
    var checkboxArray = document.querySelectorAll('input[name=awsS3UploadsCheckbox]:checked');
    
    let selectedS3Uploads = new Array();

    for (let x=0; x < checkboxArray.length; x++) {
        let testResultsPath = checkboxArray[x].getAttribute('value');
        selectedS3Uploads.push(testResultsPath)

        // Uncheck the checkbox because getSessionIds() will not refresh 
        // the page is any deleteSessionId checkbox is checked
        checkboxArray[x].checked = false;
    }

    return selectedS3Uploads;
}

async function getFileContents(object) {
    try {
        let filePath = object.getAttribute('filePath');
        console.log(`fileMgmt.getFileContents(): filePath: ${filePath}`)
        document.querySelector("#openFileModal");

        const data = await commons.postData("/api/v1/fileMgmt/getFileContents",  
                                            {remoteController: sessionStorage.getItem("remoteController"), filePath: filePath})

        if (data.status == "failed") {
            errorMsg = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
            document.querySelector("#modifyFileStatus").innerHTML = errorMsg;
        } else {
            // Text area. Set the name attr with the module preferences file path.
            document.querySelector("#insertFileContents").innerHTML = `<textarea id="textareaId" name=${data.fullPath} cols="123" rows="30">${data.fileContents}</textarea><br><br>`;

            let toggle = document.querySelector("#insertFileContents");
            // Toggle to show text 
            // toggle.style.display = toggle.style.display == "block" ? "none" : "block";
            // toggle.style.display = toggle.style.display == "block";
            toggle.style.display = "block";                
            document.querySelector("#currentOpenedFile").innerHTML = '<h7>' + data.fullPath + '</h7>';
        }
    } catch (error) {
        console.log("awsS3.getFileContents() error: " + error);
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }
}

function closeText() {
    // Toggle to hide buttons
    document.querySelector("#insertFileContents").style.display = "none";

    let toggle = document.querySelector("#textareaId");
    if (toggle.value) {
        // User attempting to open a non text file, the textarea is not created.
        // Come in here only if textarea exists
        toggle.value = ''
    }
}

function closeModal(id) {
    document.querySelector(id).style.display = 'none';
}

function setFilesPerPage(event) {
    resultsPerPage = event.options[event.selectedIndex].value;
    getAwsS3Uploads();
}

async function deleteSelected() {
    let deleteSelectedCheckboxes = getSelectedCheckboxes();
    const data = await commons.postData("/api/v1/debug/awsS3/deleteUploads",  
          {remoteController: sessionStorage.getItem("remoteController"), selectedFiles: deleteSelectedCheckboxes, deleteAll:false})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getAwsS3Uploads();
    }
    commons.getInstantMessages('debug');
    commons.blinkSuccess();
}

async function deleteAll() {
    const data = await commons.postData("/api/v1/debug/awsS3/deleteUploads",  
          {remoteController: sessionStorage.getItem("remoteController"), selectedFiles:null, deleteAll: true})
    
    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getAwsS3Uploads();
        commons.blinkSuccess();
    }
    commons.getInstantMessages('debug');
}

async function restartAwsS3Service() {
    const data = await commons.postData("/api/v1/debug/awsS3/restartService",  
                                            {remoteController: sessionStorage.getItem("remoteController")})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        isAwsS3ServiceRunning();
    }
    commons.getInstantMessages('debug');
}

async function stopAwsS3Service() {
    const data = await commons.postData("/api/v1/debug/awsS3/stopService",  
                                    {remoteController: sessionStorage.getItem("remoteController")})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        isAwsS3ServiceRunning();
        commons.blinkSuccess();
    }
    commons.getInstantMessages('debug');
}

async function isAwsS3ServiceRunning() {
    const data = await commons.postData("/api/v1/debug/awsS3/isServiceRunning",  
                                        {remoteController: sessionStorage.getItem("remoteController")})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        let isAwsS3ServiceRunning = data.isAwsS3ServiceRunning;

        if (isAwsS3ServiceRunning) {
            //alert(`AWS S3 Service is running`)
            document.querySelector("#topbarTitlePage").innerHTML = `AWS S3 service is running&ensp;&ensp;&ensp;<button class="btn btn-sm btn-outline-success" onclick="stopAwsS3Service()">Stop</button>&ensp;&ensp;<button class="btn btn-sm btn-outline-success" onclick="restartAwsS3Service()">Restart</button>`;
        } else {
            //alert(`AWS S3 Service is not running`)
            document.querySelector("#topbarTitlePage").innerHTML = `AWS S3 service is not running&ensp;&ensp;&ensp;<button class="btn btn-sm btn-outline-success" onclick="restartAwsS3Service()">Start</button>`;
        }
    }
}

async function GetAwsS3Logs() {
    isCurrentlyInAwsS3UploadPage = false;
    const data = await commons.postData("/api/v1/debug/awsS3/getLogs",  
                                    {remoteController: sessionStorage.getItem("remoteController")})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertContents").innerHTML = data.awsS3Logs;

        if (intervalId) {
            // Stop refreshing the aws s3 upload page while viewing the log page
            clearInterval(intervalId);
            // Hard set the intervalId to 0 to make sure it's 0
            intervalId = 0;
        }
    }
    commons.getInstantMessages('debug');
}

async function clearAwsS3Logs() {
    const data = await commons.postData("/api/v1/debug/awsS3/clearLogs",  
                                            {remoteController: sessionStorage.getItem("remoteController")})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        closeModal("#clearAwsS3LogsModal");
        commons.blinkSuccess();
        GetAwsS3Logs();
    }
    commons.getInstantMessages('debug');
}

async function enableAwsS3DebugLogs() {
    const data = await commons.postData("/api/v1/debug/awsS3/enableDebugLogs",  
                                            {remoteController: sessionStorage.getItem("remoteController")})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        document.querySelector("#insertDisableAwsS3DebugLogs").innerHTML = 'Disable AWS S3 Debug';
        document.querySelector("#insertDisableAwsS3DebugLogs").style.display = 'block';
    }
    commons.getInstantMessages('debug');
}

async function disableAwsS3DebugLogs() {
    const data = await commons.postData("/api/v1/debug/awsS3/disableDebugLogs",  
                                            {remoteController: sessionStorage.getItem("remoteController")})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        document.querySelector("#insertDisableAwsS3DebugLogs").innerHTML = '';
        document.querySelector("#insertDisableAwsS3DebugLogs").style.display = 'none';
    }
    commons.getInstantMessages('debug');
}

async function isAwsS3DebugEnabled() {
    const data = await commons.postData("/api/v1/debug/awsS3/isDebugEnabled",  
                                            {remoteController: sessionStorage.getItem("remoteController")})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        if (data.isAwsS3DebugEnabled) {
            document.querySelector("#insertDisableAwsS3DebugLogs").innerHTML = 'Disable AWS S3 Debug';
            document.querySelector("#insertDisableAwsS3DebugLogs").style.display = 'block';
        } else {
            document.querySelector("#insertDisableAwsS3DebugLogs").innerHTML = '';
            document.querySelector("#insertDisableAwsS3DebugLogs").style.display = 'none';
        }
    }
    commons.getInstantMessages('debug');
}

async function GetPipelineAwsS3LogFiles() {
    const data = await commons.postData("/api/v1/debug/awsS3/getPipelineLogFiles",  
                                        {remoteController: sessionStorage.getItem("remoteController")})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        if (intervalId) {
            // Stop refreshing the aws s3 upload page while viewing the log page
            clearInterval(intervalId);
            // Hard set the intervalId to 0 to make sure it's 0
            intervalId = 0;
        }
        commons.blinkSuccess();
        document.querySelector("#insertContents").innerHTML = data.dropdownFileMenu;
    }
    commons.getInstantMessages('debug');
}

window.getAwsS3Uploads = getAwsS3Uploads;
window.deleteAll = deleteAll;
window.GetAwsS3Logs = GetAwsS3Logs;
window.clearAwsS3Logs = clearAwsS3Logs;
window.enableAwsS3DebugLogs = enableAwsS3DebugLogs;
window.disableAwsS3DebugLogs = disableAwsS3DebugLogs;
window.GetPipelineAwsS3LogFiles = GetPipelineAwsS3LogFiles;
window.isAwsS3DebugEnabled = isAwsS3DebugEnabled;
window.isAwsS3ServiceRunning = isAwsS3ServiceRunning;
window.stopAwsS3Service = stopAwsS3Service;
window.restartAwsS3Service = restartAwsS3Service;
window.deleteSelected = deleteSelected;
window.deleteAll = deleteAll;
window.getFileContents = getFileContents;
window.setFilesPerPage = setFilesPerPage;
window.closeModal = closeModal;
window.closeText = closeText;








