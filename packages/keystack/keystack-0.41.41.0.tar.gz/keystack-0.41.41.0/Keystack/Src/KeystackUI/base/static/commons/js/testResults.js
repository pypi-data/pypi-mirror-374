import * as commons from './commons.js';

var nestedFolderCounter = 0;
var archiveResultsArray = new Array();
var resultsPerPage = 25;

/*
let hideInstantMessagesDiv = document.querySelector('.hideInstantMessages');
if (hideInstantMessagesDiv.classList.contains('hideInstantMessages')) {
    hideInstantMessagesDiv.classList.remove('hideInstantMessages');
}
*/

document.addEventListener("DOMContentLoaded", function() {
    let isUserSysAdmin = document.querySelector("#user").getAttribute('sysAdmin');
    let domainUserRole = document.querySelector("#domainUserRole").getAttribute('role');
    if (domainUserRole == 'engineer') {
        // "#utilization", "#utilizationIcon", 
        let divs = ["#testResultsSecondNavbar"]
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

    commons.getServerTime();

    let title = document.querySelector('#topbarTitlePage').innerHTML;
    if (title == "Test Results Archive") {
        //document.querySelector('#archiveResultNote').innerHTML = '* Results in archive will never be deleted until they are manually deleted';
    } else {
        let removeResultsAfterDays = document.querySelector('#logDeleteNote').getAttribute('deleteResultsAfterDays');
        document.querySelector('#insertRemoveResultsInfo').innerHTML = `* removeResultsAfterDays=${removeResultsAfterDays}`
        commons.getInstantMessages('testResults');
    }

    let domain = document.querySelector('#pageAttributes').getAttribute('domain');
    let playbook = document.querySelector('#resultPageAttributes').getAttribute('playbook');
    //let path = document.querySelector('#resultPageAttributes').getAttribute('resultFolderPath');

    document.querySelector('#topbarTitlePage').innerHTML += `&emsp;|&emsp;&emsp;DOMAIN=${domain} &emsp;| &emsp;&emsp;PLAYBOOK=${playbook}`;
    getTestResultPages();
})

const setResultsPerPage = (event) => {
    resultsPerPage = event.options[event.selectedIndex].value;
    getTestResultPages();
}

const addListeners = ({caretName="caret2", newVarName="x"}) => {
    // caret2
    //let toggler = document.getElementsByClassName(caretName);
    window[caretName] = document.getElementsByClassName(caretName);

    for (let x= 0; x < window[caretName].length; x++) {
        window[caretName][x].addEventListener("click", function() {
            this.parentElement.querySelector(".nested").classList.toggle("active");
            //this.classList.toggle("caret-down");               
        });
    }
}

const toggleFolder = async (object=null) => {
    //object.classList.toggle("active");
    //await object.parentElement.querySelector(".nested").classList.toggle("active");
    //await object.parentElement.querySelector(".nested").classList.toggle();
    await object.parentElement.querySelector(".nested");
}

const getTestResultPages = async (object=null) => {
    /* object is page buttons onclick */

    // Blank out the page
    document.querySelector('#insertTestResultPages').innerHTML = '';
    let pageIndexRange = [];
    let getPageNumber = 1;

    if (object == null) {
        // Default getting up to 25 test results per page
        pageIndexRange.push(`0:${resultsPerPage}`);
    } else {
        pageIndexRange.push(object.getAttribute("pageIndexRange"));
        getPageNumber = object.getAttribute("getPageNumber");
    }

    let resultFolderPath = document.querySelector("#resultPageAttributes").getAttribute("resultFolderPath");

    const splitIndexRange = pageIndexRange[0];
    const startingIndex =  Number(splitIndexRange.split(":")[0]);
    const total = parseInt(startingIndex) + parseInt(resultsPerPage);

    // splitIndexRange[0]
    for (let pageIndex = startingIndex; pageIndex < total; pageIndex++) {
        let data = await commons.postData("/api/v1/results/pages",  
                {remoteController:sessionStorage.getItem("remoteController"),
                 resultFolderPath:resultFolderPath, 
                 pageIndexRange:pageIndexRange,
                 getPageNumber:getPageNumber,
                 pageIndex:Number(pageIndex),
                 resultsPerPage:Number(resultsPerPage)})

        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = `<strong>Error</strong>`;
        } else {
            document.querySelector('#insertTestResultPages').innerHTML += data.pages;

            // This must sit here after getTestResultPages() in order to work.
            // This code goes in conjuntion with testResultsTreeView.css for expanding the nested tree view
            await addListeners({caretName:"caret2"});
            
            if (data.lastPage == true) {
                break
            }
        }
    }
    commons.getInstantMessages('testResults');
}

const insertTestResultPages = (data) => {
    document.querySelector('#insertTestResultPages').innerHTML += data;
}

const insertNestedFolder = (id, data) => {
    document.querySelector(id).innerHTML = data;
}

const getNestedFolderFiles = async (object=null) => {
    let nestedFolderPath = object.getAttribute('nestedFolderPath');
    let insertToDivId = object.getAttribute('insertToDivId');
  
    //console.log(`getNestedFolderFiles: ${nestedFolderPath}  ${insertToDivId}`)
    let data = await commons.postData("/api/v1/results/nestedFolderFiles",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             nestedFolderPath: nestedFolderPath, 
                                             insertToDivId: insertToDivId})

    //await document.querySelector(insertToDivId).innerHTML = data.folderFiles
    await insertNestedFolder(insertToDivId, data.folderFiles);

    // This must sit here after getTestResultPages() in order to work.
    // This code goes in conjuntion with testResultsTreeView.css for expanding the nested tree view
    await addListeners({caretName:data.caretName, newVarName:data.newVarName});
}

const closeText = () => {
    // Toggle to hide buttons
    //toggle.style.display = toggle.style.display == "none" ? "block" : "none";
    document.querySelector("#insertFileContents").style.display = "none";

    let toggle = document.querySelector("#textareaId");
    if (toggle.value) {
        // User attempting to open a non text file, the textarea is not created.
        // Come in here only if textarea exists
        toggle.value = ''
    }
}

const getSelectedSessions = () => {
    // Collect all the selected checkboxes and delete them all in one shot
    var checkboxArray = document.querySelectorAll('input[name=testResultCheckbox]:checked');
    
    for (let x=0; x < checkboxArray.length; x++) {
        let testResultsPath = checkboxArray[x].getAttribute('value');
        archiveResultsArray.push(testResultsPath)

        // Uncheck the checkbox because getSessionIds() will not refresh 
        // the page is any deleteSessionId checkbox is checked
        checkboxArray[x].checked = false;
    }
}

const archiveResults = async () => {
    getSelectedSessions();
    let data = await commons.postData("/api/v1/results/archive",  
                                  {remoteController: sessionStorage.getItem("remoteController"),
                                   results: archiveResultsArray})
    commons.getInstantMessages('testResults');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        //window.location.reload();
        getTestResultPages();
    }
}

const getFileContents = async (object) => {
    try {
        document.querySelector("#openFileModal");
        let filePath = object.getAttribute('filePath');

        const data = await commons.postData("/api/v1/fileMgmt/getFileContents",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         filePath: filePath})

        if (data.status == "failed") {
            let status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`
            document.querySelector("#modifyFileStatus").innerHTML = status
        } else {
            // Text area. Set the name attr with the module preferences file path.
            document.getElementById("insertFileContents").innerHTML =
            `<textarea id="textareaId" name=${data.fullPath} cols="123" rows="30">${data.fileContents}</textarea><br><br>`

            let toggle = document.getElementById("insertFileContents")
            // Toggle to show text 
            // toggle.style.display = toggle.style.display == "block" ? "none" : "block";
            // toggle.style.display = toggle.style.display == "block";
            toggle.style.display = "block";
            
            document.getElementById("currentOpenedFile").innerHTML = '<h7>' + data.fullPath + '</h7>'
        }
    } catch (error) {
        console.error(`fileMgmt.getFileContents: ${error}`)
    }  
}

const selectAll = () => {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]')
    for (var x=0; x < checkboxes.length; x++) {
        checkboxes[x].checked = true;
    }
}

const clearAll = () => {
    var checkboxes = document.querySelectorAll('input[type="checkbox"]')
    for (var x=0; x < checkboxes.length; x++) {
        checkboxes[x].checked = false;
    }

    document.querySelector('#forceDeleteTestResults').checked = false;
}

const deleteSelected = async () => {
    // hmtl code for testResultCheckbox is created in views TestResult class
    var cboxes = document.getElementsByName('testResultCheckbox');
    var len = cboxes.length;
    var selectedCheckboxArray = new Array();
    let forceDeleteTestResults = document.querySelector('#forceDeleteTestResults').checked;

    for (var i=0; i<len; i++) {
        if (cboxes[i].checked) {
            selectedCheckboxArray.push(cboxes[i].value)
        }
    }   

    const data = await commons.postData("/api/v1/results/delete",  
                                         {remoteController: sessionStorage.getItem("remoteController"),
                                          deleteTestResults: selectedCheckboxArray,
                                          forceDeleteTestResults: forceDeleteTestResults})

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getTestResultPages();
        commons.blinkSuccess();
    }
    clearAll();
    commons.getInstantMessages('testResults');
}

const deleteAllInDomain = async () => {
    /* Delete all test results in the current domain */
    // <div id="pageAttributes" group={{group}}
    let domain = document.querySelector("#pageAttributes").getAttribute("domain");
    let testResultActiveOrArchive = document.querySelector("#testResultActiveOrArchive").getAttribute("value");
    let forceDeleteTestResults = document.querySelector('#forceDeleteTestResults').checked;

    const data = await commons.postData("/api/v1/results/deleteAllInDomain",  
                                                    {remoteController: sessionStorage.getItem("remoteController"),
                                                     domain:domain, testResultActiveOrArchive:testResultActiveOrArchive,
                                                     forceDeleteTestResults: forceDeleteTestResults})
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getTestResultPages();
        commons.blinkSuccess();
    }
    commons.getInstantMessages('testResults');
    document.querySelector('#forceDeleteTestResults').checked = false;
}

const deleteAllInPlaybook = async () => {
    /* Delete all test results in the current group */
    // <div id="pageAttributes" group={{group}}
    let path = document.querySelector("#resultFolderPath").getAttribute("value");
    let forceDeleteTestResults = document.querySelector('#forceDeleteTestResults').checked;

    const data = await commons.postData("/api/v1/results/deleteAllInPlaybook",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         path:path,
                                         forceDeleteTestResults: forceDeleteTestResults})
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getTestResultPages();
        commons.blinkSuccess();
    }
    commons.getInstantMessages('testResults');
    document.querySelector('#forceDeleteTestResults').checked = false;
}

document.addEventListener("DOMContentLoaded", function(){
    document.querySelectorAll('.keystackSidebar .nav-link').forEach(function(element){
        element.addEventListener('click', function (e) {
            let nextEl = element.nextElementSibling;
            let parentEl  = element.parentElement;	

            if(nextEl) {
                e.preventDefault();	
                let mycollapse = new bootstrap.Collapse(nextEl);

                if(nextEl.classList.contains('show')){
                    mycollapse.hide();
                } else {
                    mycollapse.show();
                    // find other submenus with class=show
                    var opened_submenu = parentEl.parentElement.querySelector('.submenu.show');
                    // if it exists, then close all of them
                    if(opened_submenu){
                        new bootstrap.Collapse(opened_submenu);
                    }
                }
            }
        });
    })
}); 

window.getFileContents = getFileContents;
window.closeText = closeText;
window.clearAll = clearAll;
window.selectAll = selectAll;
window.deleteSelected = deleteSelected;
window.deleteAllInDomain = deleteAllInDomain;
window.deleteAllInPlaybook = deleteAllInPlaybook;
window.archiveResults = archiveResults;
window.setResultsPerPage = setResultsPerPage;
window.getTestResultPages = getTestResultPages;









