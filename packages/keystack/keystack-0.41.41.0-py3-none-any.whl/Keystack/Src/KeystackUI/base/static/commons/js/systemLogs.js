import * as commons from './commons.js';

var logCategory = '';

document.addEventListener("DOMContentLoaded", function() {
    let domainUserRole = document.querySelector("#domainUserRole").getAttribute('role');
    if (domainUserRole == 'engineer') {
        // "#messages", "#messagesIcon", "#debugDropdown", "#utilization", "#utilizationIcon", 
        let divs = ["#systemSettingsDropdown", "#deleteLogsButton"]
        for (let x=0; x<divs.length; x++) {
            let currentDiv = divs[x]
            document.querySelector(currentDiv).classList.add('hideFromUser');
        }            
    }    

    getLogTopicDropdown();
    getDefaultLogMessages(logCategory='pipelines');

    let deleteLogs = document.querySelector('#deleteLogs').getAttribute('deleteLogs');
    document.querySelector('#insertDeleteLogsNote').innerHTML = `removeLogsAfterDays=${deleteLogs}`;
    commons.getServerTime();
})

const getLogTopicDropdown = async () => {
    const data = await commons.postData("/api/v1/system/getLogMessageTopics",  
                                            {remoteController: sessionStorage.getItem("remoteController")});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertLogTopics').innerHTML = data.logTopicDropdown;

        document.querySelector("#selectLogTopic").addEventListener('click', event => {
            let logTopic = event.target.innerText;
            logCategory = logTopic;
            getLogMessages(logTopic);
        })
    }
}

const getLogMessages = async (logTopic) => {
    const data = await commons.postData("/api/v1/system/getLogMessages",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                             webPage: logTopic});

    document.querySelector('#tableDataSystemLogs').innerHTML = data.logs;
    document.querySelector('#topbarTitlePage').innerHTML = `SystemLogs: ${logTopic}`;
}

const getDefaultLogMessages = async (logTopic) => {
    const data = await commons.postData("/api/v1/system/getLogMessages",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                             webPage: logTopic});

    document.querySelector('#tableDataSystemLogs').innerHTML = data.logs;
    document.querySelector('#topbarTitlePage').innerHTML = `SystemLogs: ${logTopic}`;
}

document.querySelector("#deleteLogsButton").addEventListener('click', async event => {
    const data = await commons.postData("/api/v1/system/deleteLogs",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         domain: document.querySelector("#pageAttributes").getAttribute('domain'),
                                         webPage: logCategory});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#tableDataSystemLogs').innerHTML = '';
        getLogMessages(logCategory);
        getLogTopicDropdown();
    }
})

window.getLogMessages = getLogMessages;
window.getDefaultLogMessages = getDefaultLogMessages;
window.deleteLogsButton = deleteLogsButton;
