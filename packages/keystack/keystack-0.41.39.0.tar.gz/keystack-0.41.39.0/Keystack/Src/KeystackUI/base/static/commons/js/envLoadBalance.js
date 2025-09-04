import * as commons from './commons.js';

var individualEnvsArray = [];
var envGroupArray = [];

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

    if (['engineer'].includes(domainUserRole) || isUserSysAdmin == "False") {
        let divs = ["#loadBalanceGroupNavbar", "#createLoadBlanceGroupLink", "#createLoadBalanceGroup", "#loadBalanceGroups",
                    "#resetLoadBalanceGroup", "#removeSelectedLBG", "#removeAllEnvFromLBG", "#selectEnvForLBG",
                    "#insertEnvs", "#insertEnvsInstruction", "#insertLoadBalanceGroupName2"]
        for (let x=0; x<divs.length; x++) {
            let currentDiv = divs[x]
            document.querySelector(currentDiv).classList.add('hideFromUser');
        }            
    }

    getEnvs();
    getLoadBalanceGroups();
    commons.getInstantMessages('envs');
    commons.getServerTime();
})

const createLoadBalanceGroup = async () => {
    // Create a new env load balancer. Get the value from the input field.
    let loadBalanceGroup = document.querySelector('#createNewBalancerGroupId').value;

    if (loadBalanceGroup.indexOf('/') > 0) {
        alert('Load Balaner name cannot have slashes');
        return
    }

    let data = await commons.postData("/api/v1/env/loadBalanceGroup/create",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         loadBalanceGroup: loadBalanceGroup})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getLoadBalanceGroups();
        commons.blinkSuccess();
    }

    commons.getInstantMessages('envs');
    // Blank the input field
    document.querySelector('#createNewBalancerGroupId').value = '';
}

const addEnvsToLoadBalanceGroup = async () => {
    // from onclick button. User checkboxed env group / envs
    const loadBalanceGroup = document.querySelector("input[name=loadBalancerGroupRadio]:checked").value;
    getSelectedEnvsForLBG();

    const data = await commons.postData("/api/v1/env/loadBalanceGroup/addEnvs",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         loadBalanceGroup: loadBalanceGroup,
                         envGroupsFullPaths: envGroupArray, 
                         individualEnvsFullPaths: individualEnvsArray})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getLoadBalanceGroupEnvs();
        getEnvs();
        commons.blinkSuccess();
    }

    commons.getInstantMessages('envs');
    individualEnvsArray = [];
    envGroupArray = [];
}

const getLoadBalanceGroups = async () => {
    // Radio buttons: Show all the created load balance groups
    const data = await commons.postData("/api/v1/env/loadBalanceGroup/get",  
                                        {remoteController: sessionStorage.getItem("remoteController")})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        if (data.totalLoadBalanceGroups > 0) {
            document.querySelector("#insertLoadBalanceGroups").innerHTML = data.loadBalanceGroups;

            let currentSelectedLoadBalanceGroup = document.querySelector("input[name=loadBalancerGroupRadio]:checked").value;
            document.querySelector("#insertCurrentLoadBalanceGroup").innerHTML = currentSelectedLoadBalanceGroup;

            let loadBalanceGroup = document.querySelector("#loadBalanceGroups");
            loadBalanceGroup.classList.remove('hide');
        } else {
            document.querySelector("#insertLoadBalanceGroups").innerHTML = '<div class="marginLeft20px">None</div>';
            document.querySelector("#insertCurrentLoadBalanceGroup").innerHTML += 'None';

            let loadBalanceGroup = document.querySelector("#loadBalanceGroups");
            loadBalanceGroup.classList.add('hide');
            //loadBalanceGroup.parentElement.querySelector(".show").classList.toggle("show");
        }

        getLoadBalanceGroupEnvs();
    }       
}

const getLoadBalanceGroupEnvs = async () => {
    // User selects a load balancer to manage. Show all the Envs for the load balancer.
    // let loadBalancerRadio = document.querySelector("input[name=loadBalancerGroupRadio]:checked");
    //let loadBalanceGroup = loadBalancerRadio ? loadBalancerRadio.value : "";

    const loadBalanceGroup = document.querySelector("input[name=loadBalancerGroupRadio]:checked").value;

    const data = await commons.postData("/api/v1/env/loadBalanceGroup/getEnvsUI",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             loadBalanceGroup:loadBalanceGroup})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertLoadBalanceGroupEnvs").innerHTML = data.loadBalanceGroupEnvs;
        document.querySelector("#insertLoadBalanceGroupName").innerHTML = `Load-Balance Group Envs:&nbsp;&nbsp;${loadBalanceGroup}`;
        document.querySelector("#insertLoadBalanceGroupName2").innerHTML = `Select Envs for the load-balance group:<br>${loadBalanceGroup}`;
    } 
    commons.getInstantMessages('envs');    
}

const getEnvs = async () => {
    // Blank out the page
    document.querySelector('#insertEnvs').innerHTML = '';

    const data = await commons.postData("/api/v1/env/loadBalanceGroup/getAllEnvs",  
                                        {remoteController: sessionStorage.getItem("remoteController")})

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertEnvs').innerHTML += data.envs;

        // This must sit here after getTestResultPages() in order to work.
        // This code goes in conjuntion with testResultsTreeView.css for expanding the nested tree view
        await addListeners("caret2");
    }
    commons.getInstantMessages('envs');
}

const addListeners = (caretName) => {
    window[caretName] = document.getElementsByClassName(caretName);

    for (let x= 0; x < window[caretName].length; x++) {
        window[caretName][x].addEventListener("click", function() {
            this.parentElement.querySelector(".nested").classList.toggle("active");            
        });
    }
}

const clearAll = () => {
    const checkboxes = document.querySelectorAll('input[type="checkbox"]')
    for (var x=0; x < checkboxes.length; x++) {
        checkboxes[x].checked = false;
    }
}

const getSelectedEnvsForLBG = () => {
    // Individial Envs
    const individualEnvCheckbox = document.querySelectorAll('input[name=envCheckboxLBG]:checked');

    for (let x=0; x < individualEnvCheckbox.length; x++) {
        let envPath = individualEnvCheckbox[x].getAttribute('value');
        individualEnvsArray.push(envPath)
        individualEnvCheckbox[x].checked = false;
    }

    // Env groups
    const envGroupCheckboxes = document.querySelectorAll('input[name=envGroupCheckbox]:checked');

    for (let x=0; x < envGroupCheckboxes.length; x++) {
        let envPath = envGroupCheckboxes[x].getAttribute('value');
        envGroupArray.push(envPath)
        envGroupCheckboxes[x].checked = false;
    }
}

const addEnvsToLoadBalancer = () => {
    getLoadBalanceGroups();
}

const updateLoadBalanceGroup = () => {
    // User changed load balance group
    getLoadBalanceGroupEnvs();
}

const disableEnvCheckboxes = (object) => {
    // Each env group checked will come in here by onclick.
    // If checked, disabled all env checkboxes in the group. 
    // If unchecked, enable all env checkboxes in the group.
    let selectedValue = object.value;
    let isChecked = object.checked;

    let checkboxes = document.querySelectorAll(`input[envPath="${selectedValue}"]`);
    for (let x = 0; x < checkboxes.length; x++) {
        if (isChecked) {
            checkboxes[x].checked = false;
            checkboxes[x].disabled = true;
        } else {
            checkboxes[x].checked = false;
            checkboxes[x].disabled = false;
        }
    }
}

const removeAllEnvs = async () => {
    const loadBalanceGroup = document.querySelector("input[name=loadBalancerGroupRadio]:checked").value;
    const data = await commons.postData("/api/v1/env/loadBalanceGroup/removeAllEnvs",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         loadBalanceGroup: loadBalanceGroup})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getLoadBalanceGroupEnvs();
        commons.blinkSuccess();
    }

    commons.getInstantMessages('envs');        
}

const removeSelectedEnv = async () => {
    const loadBalanceGroup = document.querySelector("input[name=loadBalancerGroupRadio]:checked").value;
    const removeSelectedEnvs = document.querySelectorAll("input[name=removeEnvFromLB]:checked");
    let removeSelectedEnvList = [];

    for (let x=0; x < removeSelectedEnvs.length; x++) {
        let env = removeSelectedEnvs[x].getAttribute('value');
        removeSelectedEnvList.push(env)
    }

    let data = await commons.postData("/api/v1/env/loadBalanceGroup/removeEnvs",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         loadBalanceGroup: loadBalanceGroup, 
                         removeSelectedEnvs: removeSelectedEnvList});

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getLoadBalanceGroupEnvs();
        commons.blinkSuccess();
    } 
    commons.getInstantMessages('envs');    
}

const deleteLoadBalanceGroup = async () => {
    const loadBalanceGroup = document.querySelector("input[name=loadBalancerGroupRadio]:checked").value;
    const data = await commons.postData("/api/v1/env/loadBalanceGroup/delete",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         loadBalanceGroup: loadBalanceGroup})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getLoadBalanceGroups();
        getLoadBalanceGroupEnvs();
        commons.blinkSuccess();
    }

    commons.getInstantMessages('envs');             
}

const resetLoadBalanceGroup = async () => {
    const loadBalanceGroup = document.querySelector("input[name=loadBalancerGroupRadio]:checked").value;
    const data = await commons.postData("/api/v1/env/loadBalanceGroup/reset",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         loadBalanceGroup: loadBalanceGroup})

    if (data.status == "failed") {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getLoadBalanceGroupEnvs();
        commons.blinkSuccess();
    }

    commons.getInstantMessages('envs');             
}

window.disableEnvCheckboxes = disableEnvCheckboxes;
window.resetLoadBalanceGroup = resetLoadBalanceGroup;
window.removeAllEnvs = removeAllEnvs;
window.removeSelectedEnv = removeSelectedEnv;
window.deleteLoadBalanceGroup = deleteLoadBalanceGroup;
window.createLoadBalanceGroup = createLoadBalanceGroup;
window.addEnvsToLoadBalanceGroup = addEnvsToLoadBalanceGroup;
window.getEnvs = getEnvs;
window.updateLoadBalanceGroup = updateLoadBalanceGroup;

