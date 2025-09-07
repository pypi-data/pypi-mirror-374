import * as commons from './commons.js';

document.addEventListener("DOMContentLoaded", function() {
    getTestcaseDetails();
    commons.getServerTime();
    commons.getInstantMessages('testcases');
})


const getTestcaseDetails = async () => {
    const testcase = document.querySelector('#testcaseForJs').getAttribute('testcase');

    const data = await commons.postData("/api/v1/testcases/details",  
                                        {remoteController: sessionStorage.getItem("remoteController"), 
                                         testcase: testcase})

    document.querySelector('#insertTestcaseDetails').innerHTML = data.testcaseDetails;

    const toggler = document.getElementsByClassName("caret");

    for (let i = 0; i < toggler.length; i++) {
        toggler[i].addEventListener("click", function() {
            this.parentElement.querySelector(".nested").classList.toggle("active");
            this.classList.toggle("caret-down");
        });
    }
}

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
            toggle.style.display = "block";
            
            document.getElementById("currentOpenedFile").innerHTML = '<h7>' + data.fullPath + '</h7>';
        }
    } catch (error) {
        console.error(error)
    }

    commons.getInstantMessages('testcases');	  
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

async function addListeners(caretName="caret2", newVarName='x') {
    // caret2
    window[caretName] = document.getElementsByClassName(caretName);

    for (let x= 0; x < window[caretName].length; x++) {
        window[caretName][x].addEventListener("click", function() {
            this.parentElement.querySelector(".nested").classList.toggle("active");
            //this.classList.toggle("caret-down");               
        });
    }
}

window.getFileContents = getFileContents;
window.modifyFile = modifyFile;
window.closeText = closeText;


