import * as commons from './commons.js';

var newPlaybookName = '';
var newPlaybookTextArea = '';
var suiteName = '';
var playbookGroup = '';
var stage = '';
var selectedModule = '';
var setupFile = '';
var selectedTestcases = [];


// Fill table data onload
document.addEventListener("DOMContentLoaded", function() {
    let isUserSysAdmin = document.querySelector("#user").getAttribute('sysAdmin');
    let domainUserRole = document.querySelector("#domainUserRole").getAttribute('role');

    if (domainUserRole == 'engineer') {
        // "#utilization", "#utilizationIcon",
        let divs = ["#playbookNavbar", "#modifyPlaybookButton"]
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

    getTableData();
    commons.getInstantMessages('playbooks');
    commons.getServerTime();
})

// Don't close the dropdown-menu when clicking inside
/*
document.querySelector('#doNotClose').addEventListener('click', function(event) {
    event.stopPropagation();
})
*/

let doNotClose = document.querySelector('#doNotClose')
if (doNotClose) {
    doNotClose.addEventListener('click', function(event) {
    event.stopPropagation();
    });
}

const deletePlaybooks = async (playbookList=null) => {
    let deletePlaybooks = [];
    let playbookCheckboxes = document.querySelectorAll('input[name="playbookCheckboxes"]:checked');
    playbookCheckboxes.forEach((checkbox) => {
        console.log(`Delete playbook clicked: ${checkbox.value}`)
        deletePlaybooks.push(checkbox.value);
    })

    console.log(`playbook template.deletePlaybooks(): ${deletePlaybooks}`);
    let data = await commons.postData("/api/v1/playbook/delete",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         deletePlaybooks: deletePlaybooks});

    if (data.status == "success") {
        let status = `<div style='color:green'>Successfully deleted playbooks</div>`;
        document.querySelector("#deletePlaybooksStatus").innerHTML = status;
    } else {
        let status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
        document.querySelector("#deletePlaybooksStatus").innerHTML = status;
    }
}

const getFileContents = async (filePath) => {
    try {
        // getFileContents calls sidebar/views
        const data = await commons.postData("/api/v1/fileMgmt/getFileContents",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             filePath: filePath.value})
        
        // Text area. Set the name attr with the module preferences file path.
        document.querySelector("#insertPlaybookFileContents").innerHTML =
        `<textarea id="textareaId" name="${data.fullPath}" cols="123" rows="25">${data.fileContents}</textarea><br><br>`;
        
        let toggle = document.querySelector("#insertPlaybookFileContents");
        // Toggle to show text 
        // toggle.style.display = toggle.style.display == "block" ? "none" : "block";
        // toggle.style.display = toggle.style.display == "block";
        if (toggle) {
            toggle.style.display = "block";
        }

        document.querySelector("#currentOpenedFile").innerHTML = '<h7>' + 'Playbook:&emsp;' + data.fullPath.split("/Playbooks/").slice(1) + '</h7>';
        document.querySelector('#textAreaButton').style.display = "block";

    } catch (error) {
        let status = `<div style='color:red'>Failed: Reading file contents</div>`;
        document.querySelector("#modifyPlaybookStatus").innerHTML = status;
    }

    commons.getInstantMessages('playbooks');	  
}

const modifyFile = async () => {
    /* Modify existing playbook */

    try {
        let textarea = document.querySelector('#textareaId').value;
        let filePath = document.querySelector('#textareaId').name;

        const data = await commons.postData("/api/v1/fileMgmt/modifyFile",
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             textarea: textarea, filePath: filePath})

        if (data.status == "success") {
            const status = `<div style='color:green'>Successfully modified Playbook</div>`;
            document.querySelector("#modifyPlaybookStatus").innerHTML = status;
        } else {
            const status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
            document.querySelector("#modifyPlaybookStatus").innerHTML = status;
        }
       
    } catch (error) {    
        console.log("modifyFile() error: " + error)
    }
    commons.getInstantMessages('playbooks');
}

const closeText = () => {
    /* Close the opened Playbook */ 

    try {
        document.querySelector("#textareaId").value = '';
    } catch (error) {

    }

    // Toggle to hide buttons
    //toggle.style.display = toggle.style.display == "none" ? "block" : "none";
    document.querySelector("#insertPlaybookFileContents").style.display = "none";
    document.querySelector('#textAreaButton').style.display = "none";
    document.querySelector("#currentOpenedFile").innerHTML = "";
    document.querySelector("#modifyPlaybookStatus").innerHTML = "";
    document.querySelector("#deletePlaybooksStatus").innerHTML = "";

    var checkboxes = document.querySelectorAll('input[type="playbookCheckboxes"]')
    for (var x=0; x < checkboxes.length; x++) {
        checkboxes[x].checked = false;
    }

    getTableData();
    commons.getInstantMessages('playbooks');
}

const getPlaybookTemplate = async () => {
    console.log('getPlaybookTemplate()')
    const data = await commons.postData("/api/v1/playbook/template",
                                        {remoteController: sessionStorage.getItem("remoteController")})
    document.querySelector("#insertPlaybookTemplate").value = data.playbookTemplate;
}

const createPlaybook = async () => {
    /* Create actual playbook */

    try {
        let textArea = document.querySelector('#insertPlaybookTemplate').value;
        let newPlaybook = document.querySelector('#newPlaybook').value;
        let playbookGroup = document.querySelector('#playbookGroup').value;
        let domain = document.querySelector('#pageAttributes').getAttribute('domain');

        console.log(`createPlaybook(): domain=${domain}  group=${playbookGroup}  newPlaybook=${newPlaybook}`)

        const data = await commons.postData("/api/v1/playbook/create", 
                    {remoteController: sessionStorage.getItem("remoteController"),
                     textArea: textArea,
                     domain: domain,
                     newPlaybook: newPlaybook,
                     playbookGroup:playbookGroup})

        if (data.status == "success") {
            let status = `<div style='color:green'>Successfully created Playbook</div>`;
            document.querySelector("#createPlaybookStatus").innerHTML = status;
        } else {
            let status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
            document.querySelector("#createPlaybookStatus").innerHTML = status;
        }

        console.log('createPlaybook(): success');
    } catch (error) {    
        console.log("createPlaybook() error: " + error);
    }
    getTableData();
    commons.getInstantMessages('playbooks');
}

const closeCreatePlaybook = () => {
    //getPlaybookTemplate();
    document.querySelector("#newPlaybook").value = '';
    document.querySelector('#playbookGroup').value = '';
    document.querySelector("#createPlaybookStatus").innerHTML = '';
    document.querySelector("#insertPlaybookTemplate").value = '';
    console.log('closeCreatePlaybook()');
}

const getTableData = async () => {
    let playbookGroup = document.querySelector('#playbookPageAttributes').getAttribute('playbookGroup');
    let domain = document.querySelector('#pageAttributes').getAttribute('domain');
    let pageAttributes = document.querySelector('#playbookPageAttributes').getAttribute('group');
    let playbookDomain = pageAttributes.split('/')[1];
    
    const data = await commons.postData("/api/v1/playbook/get",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         playbookGroup: pageAttributes})

    document.querySelector('#tableData').innerHTML = data.tableData;
    document.querySelector('#topbarTitlePage').innerHTML = `Playbooks&emsp;|&emsp;${playbookDomain} &ensp;&ensp;${playbookGroup}`;
    commons.sortTable({tableId:"#playbookTable", columnIndex:1});    
}

function searchForPlaybook() {
    // Call search in commons.js
    commons.search({searchInputId:"#searchForPlaybook", tableId:'#playbookTable', columnIndex:2})
}


window.getPlaybookTemplate = getPlaybookTemplate;
window.createPlaybook = createPlaybook;
window.closeCreatePlaybook = closeCreatePlaybook;
window.closeText = closeText;
window.deletePlaybooks = deletePlaybooks;
window.getFileContents = getFileContents;
window.modifyFile = modifyFile;




