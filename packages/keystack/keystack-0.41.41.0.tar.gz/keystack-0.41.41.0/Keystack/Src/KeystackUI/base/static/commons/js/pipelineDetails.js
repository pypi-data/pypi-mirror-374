import * as commons from './commons.js';

var intervalId = null;

document.addEventListener("DOMContentLoaded", function() {
    let domainUserRole = document.querySelector("#domainUserRole").getAttribute('role');
    if (domainUserRole == 'engineer') {
        // "#messages", "#messagesIcon", "#debugDropdown", "#utilization", "#utilizationIcon", 
        let divs = ["#modifyTestcases", "#managePipelines", "#testScheduler", "#insertJobSchedulerCount",
                    "#systemSettingsDropdown", "#modifyPlaybookInPipelineButton", "#modifyEnvInPipelineButton"]
        for (let x=0; x<divs.length; x++) {
            let currentDiv = divs[x]
            document.querySelector(currentDiv).classList.add('hideFromUser');
        }            
    }

    getSessionData('sessionData');
    getSessionData('testcaseData');
    intervalId = setInterval(getSessionData, 3000);
});

async function getSessionData(insertDataIdTo) {
    // testResultPath was passed in by sessionMgmt.views.SessionDetails()
    let testResultsPath = document.querySelector('#testResultsPath').getAttribute('path');
    const data = await commons.postData("/api/v1/pipeline/getSessionDetails", 
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                             'testResultsPath': testResultsPath});
    if (data.name == "TypeError") {
        console.error(`getSessionDetails ERROR: message:${data.message}  stack:${data.stack}`)
        clearInterval(intervalId);
    } else {
        if (insertDataIdTo == "sessionData") {
            document.querySelector('#insertSessionData').innerHTML = data.sessionData;
        }
        if (insertDataIdTo == "testcaseData") {
            document.querySelector('#insertTestcaseData').innerHTML = data.testcaseData;
            await addListeners({caretName:"caret2"});
        }

        document.querySelector('#topbarTitlePage').innerHTML = `${data.stageTaskEnv}`;
    }
}

async function getFileContents(object) {
    try {
        document.querySelector("#modalShowTestLogs");
        let filePath = object.getAttribute('filePath');

        const data = await commons.postData("/api/v1/fileMgmt/getFileContents",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                         filePath: filePath})

        // Show file contents in a new tab
        var myWindow = window.open("", '_blank');
        myWindow.document.write(`<pre>${data.fileContents}</pre>`);

    } catch (error) {
        console.log("fileMgmt.getFileContents() error: " + error);
    }
}

function addListeners({caretName=null, newVarName='x'}) {
    // caret2
    window[caretName] = document.getElementsByClassName(caretName);

    // By default, open the top-level folder to show the testcases
    window[caretName][0].parentElement.querySelector(".nested").classList.toggle("active")

    for (let x= 1; x < window[caretName].length; x++) {
        window[caretName][x].addEventListener("click", function() {
            this.parentElement.querySelector(".nested").classList.toggle("active");
            //this.classList.toggle("caret-down");
        });
    }
}

window.getFileContents = getFileContents;
