import * as commons from './commons.js';

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
           
    getApps();
    getAppStoreApps();
    commons.getInstantMessages('apps');
    commons.getServerTime();
})

async function getApps() {
    let data = await commons.postData("/api/v1/apps",  
                                    {remoteController: sessionStorage.getItem("remoteController")})

    if (data.status == "failed") {  
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertInstalledApps").innerHTML = data.apps;
    }

    commons.getInstantMessages('apps');
}

async function removeApp() {
    let apps = document.querySelectorAll("input[name=appsCheckbox]:checked");
    let removeSelectedAppsList = [];

    for (let x=0; x < apps.length; x++) {
        let env = apps[x].getAttribute('value');
        removeSelectedAppsList.push(env)
    }

    let data = await commons.postData("/api/v1/apps/remove",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         apps:removeSelectedAppsList})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getApps();
        commons.blinkSuccess();
    }

    commons.getInstantMessages('apps');
}

async function getAppDescription(object) {
    let app = object.getAttribute('app');
    let isAppInstalled = object.getAttribute('isAppInstalled');
    let data = await commons.postData("/api/v1/apps/description",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         app:app,
                         isAppInstalled:isAppInstalled})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertAppDescription").innerHTML = data.description;
    }

    commons.getInstantMessages('apps');
}

async function getAppStoreApps() {
    let data = await commons.postData("/api/v1/apps/getAvailableApps", 
                                        {remoteController: sessionStorage.getItem("remoteController")})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertAppStoreApps").innerHTML = data.availableApps;
    }

    commons.getInstantMessages('apps');
}

async function getAppStoreAppDescription(object) {
    let app = object.getAttribute('app');
    let data = await commons.postData("/api/v1/apps/getAppStoreAppDescription",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     app:app})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertAppDescription").innerHTML = data.appDescription;
    }

    commons.getInstantMessages('apps');
}

async function updateApps() {
    let apps = document.querySelectorAll("input[name=appsCheckbox]:checked");
    let appsList = [];

    for (let x=0; x < apps.length; x++) {
        let appName = apps[x].getAttribute('appName');
        let remoteUrl = apps[x].getAttribute('remoteUrl');
        appsList.push([appName, remoteUrl])
    }

    console.log(`updateApps: appsList final: ${appsList} ---`)
    let data = await commons.postData("/api/v1/apps/update",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     selectedApps: appsList})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getApps();
        commons.blinkSuccess();
    }

    commons.getInstantMessages('apps');
}

async function installApps() {
    let apps = document.querySelectorAll("input[name=appStoreAppsCheckbox]:checked");
    let appsList = [];

    // appName: https://github.com/openixia/keystack-ixload.git
    for (let x=0; x < apps.length; x++) {
        let appName = apps[x].getAttribute('cloneUrl');
        appsList.push(appName)
    }

    let data = await commons.postData("/api/v1/apps/install",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     selectedApps:appsList})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getApps();
        getAppStoreApps();
        commons.blinkSuccess();
    }

    commons.getInstantMessages('apps');
}

window.installApps = installApps;
window.updateApps = updateApps;
window.removeApp = removeApp;
window.getAppDescription = getAppDescription;
window.getAppStoreAppDescription = getAppStoreAppDescription;

