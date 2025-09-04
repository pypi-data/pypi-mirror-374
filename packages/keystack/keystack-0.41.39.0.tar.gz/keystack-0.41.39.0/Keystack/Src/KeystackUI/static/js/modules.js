import * as commons from './commons.js';

// Call installMessages when opening a module page
document.addEventListener("DOMContentLoaded", function() {
    // Remove the footer to show the "modify" and "close" button and stretch the main body to show more contents
    document.querySelector("#mainBodyDiv").style.height = "60vw";
    let isUserSysAdmin = document.querySelector("#user").getAttribute('sysAdmin');
    let domainUserRole = document.querySelector("#domainUserRole").getAttribute('role');

    if (domainUserRole == 'engineer') {
        let divs = ["#modifyModulesbutton"]
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

    // Remove the footer because it blocks the modify/close buttons
    //var elem = document.querySelector("#footer");
    //elem.parentNode.removeChild(elem);
    commons.getInstantMessages('modules');
    getModuleDetails();
    commons.getServerTime();
})	

const getFileContents = async (object) => {
    try {
        document.querySelector("#modifyFileModal");
        const filePath = object.getAttribute('filePath');

        const data = await commons.postData("/api/v1/fileMgmt/getFileContents",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             filePath: filePath})

        if (data.status == "failed") {
            let status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
            document.querySelector("#modifyFileStatus").innerHTML = status;
        } else {
            // Text area. Set the name attr with the module preferences file path.
            document.getElementById("insertFileContents").innerHTML =
            `<textarea id="textareaId" name=${data.fullPath} cols="123" rows="29">${data.fileContents}</textarea><br><br>`;

            let toggle = document.getElementById("insertFileContents");
            // Toggle to show text 
            //toggle.style.display = toggle.style.display == "block" ? "none" : "block";
            // toggle.style.display = toggle.style.display == "block";
            toggle.style.display = "block";
            
            document.getElementById("currentOpenedFile").innerHTML = '<h7>' + data.fullPath + '</h7>';
            //document.getElementById('modifyButton').style.display = "block";
            //document.getElementById('textAreaButton').style.display = "block";
        }
    } catch (error) {
        //console.error(`modules.getFileContents() error: ${error}`);
        console.error(error)
    }

    commons.getInstantMessages('modules');	  
}

const getModuleDetails = async () => {
    const module = document.querySelector('#moduleForJs').getAttribute('module');
    const data = await commons.postData("/api/v1/modules/details",  
                                        {remoteController: sessionStorage.getItem("remoteController"), 
                                         module: module})

    document.querySelector('#insertModuleDetails').innerHTML = data.moduleDetails;

    const toggler = document.getElementsByClassName("caret");
    for (let i = 0; i < toggler.length; i++) {
        toggler[i].addEventListener("click", function() {
            this.parentElement.querySelector(".nested").classList.toggle("active");
            this.classList.toggle("caret-down");
        });
    }
}

const closeText = () => {
    // Toggle to hide buttons
    //toggle.style.display = toggle.style.display == "none" ? "block" : "none";
    document.querySelector("#insertFileContents").style.display = "none";
    document.querySelector("#modifyFileStatus").innerHTML = "";

    let toggle = document.querySelector("#textareaId");
    if (toggle.value) {
        // User attempting to open a non text file, the textarea is not created.
        // Come in here only if textarea exists
        toggle.value = ''
    }
}

const modifyFile = async () => {
    try {
        const textarea = document.getElementById('textareaId').value;
        const filePath = document.getElementById('textareaId').name;

        const data = await commons.postData("/api/v1/fileMgmt/modifyFile",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             textarea: textarea, filePath: filePath})

        if (data.status == "success") {
            const status = `<div style='color:green'>Successfully modified file</div>`;
            document.querySelector("#modifyFileStatus").innerHTML = status;
        } else {
            const status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
            document.querySelector("#modifyFileStatus").innerHTML = status;
        }
    } catch (error) {    
        console.error("modules.modifyFile() error: " + error);
    }
    commons.getInstantMessages('modules');
}

window.getFileContents = getFileContents;
window.closeText = closeText;
window.modifyFile = modifyFile;

