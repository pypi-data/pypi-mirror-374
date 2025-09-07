import * as commons from './commons.js';

var customDeviceTypeInput = null;
var deviceType = null;
var deviceName = null;
var field = null;

// For individual port selection
var portCheckboxList = [];
var selectAllPortsCheckboxes = null;

document.addEventListener("DOMContentLoaded", (event) => {
    let domainUserRole = document.querySelector("#domainUserRole").getAttribute('role');
    if (['engineer', 'manager'].includes(domainUserRole)) {
        let divs = ["#systemSettingsDropdown"]
        for (let x=0; x<divs.length; x++) {
            let currentDiv = divs[x]
            document.querySelector(currentDiv).classList.add('hideFromUser');
        }            
    }
 

    commons.getInstantMessages('portMgmt');
    commons.getServerTime();
    getDevice();

    let deviceTypeSelectionDropdown = document.querySelector('#selectPortMgmtDeviceType');
    if (deviceTypeSelectionDropdown) {
        deviceTypeSelectionDropdown.addEventListener('click', event => {
            event.preventDefault();
            document.querySelector('#insertSelectedDeviceType').innerHTML = '';
            deviceType = event.target.innerText;
        
            if (deviceType != 'Enter') {
                customDeviceTypeInput = null;
                document.querySelector('#insertSelectedDeviceType').innerHTML = event.target.innerText;
                document.querySelector('#insertCustomDeviceType').innerHTML = '';
                document.querySelector('input[name=customInput][id=layer1CustomInput]').value == '';
            }
        })
    }

    let customDeviceTypeEnterButton = document.querySelector('#customDeviceTypeIdEnterButton');
    if (customDeviceTypeEnterButton) {
        customDeviceTypeEnterButton.addEventListener('click', event => {
            event.preventDefault(); 
            customDeviceTypeInput = document.querySelector('input[name=customInput][id=layer1CustomInput]').value;
            if (customDeviceTypeInput) {
                deviceType = customDeviceTypeInput;
                document.querySelector('#insertSelectedDeviceType').innerHTML = null;
                document.querySelector('#insertCustomDeviceType').innerHTML = deviceType;
                document.querySelector('input[name=customInput][id=layer1CustomInput]').value = '';
            }
        })
    }
})

const hide = (classObject) => {
    let allClassElements = document.querySelectorAll(classObject);
    allClassElements.forEach(classElement => {
        classElement.classList.add("hide");
    })
}

const unhide = (classObject) => {
    let allClassElements = document.querySelectorAll(classObject);
    allClassElements.forEach(classElement => {
        classElement.classList.remove("hide");
    })
}

const uncheckAllPorts = () => {
    var allPortsCheckboxes = document.querySelectorAll('input[name="portMgmtCheckboxes"]');
    for (var x=0; x < allPortsCheckboxes.length; x++) {
        allPortsCheckboxes[x].checked = false;
    }

    // Uncheck the selectAll checkbox
    selectAllPortsCheckboxes = document.querySelector('#selectAllPortsCheckboxes');
    selectAllPortsCheckboxes.checked = false;
}

const editPortDeviceField = async (object) => {
    /* Each field is editable provided by getDevice() 
       setting deviceName=$deviceName and field=$fiel
    */

    deviceName = object.getAttribute('deviceName');
    field = object.getAttribute('field');

    // Open the edit modal
    document.querySelector('#editPortDeviceModal').style.display = 'block';

    // Show the field name
    document.querySelector("#insertDeviceName").innerHTML = deviceName;

    if (field == 'deviceType') {
        unhide('.editPortDeviceTypeSelection')
        hide('.editConnectionProtocol')
        hide('.editInputField')

    } else if (field == 'connectionProtocol') {
        unhide('.editConnectionProtocol')
        hide('.editInputField')
        hide('.editPortDeviceTypeSelection')
  
    } else {
        unhide('.editInputField')
        hide('.editConnectionProtocol')
        hide('.editPortDeviceTypeSelection')
        document.querySelector("#inputField").innerHTML = `${field}:&emsp;`;
    }    
}

// User clicked on edit button to make changes on device profile
let editPortMgmtDevice = document.querySelector("#editPortMgmtDeviceButton");
if (editPortMgmtDevice) {
    editPortMgmtDevice.addEventListener('click', async event => {
        event.preventDefault;

        if (field == 'deviceType') {
            if (customDeviceTypeInput) {
                var value = customDeviceTypeInput;
                customDeviceTypeInput = null;
            } else {
                var value = deviceType;
            }

        } else if (field == 'ports') {
            var value = document.querySelector('#addPortsManuallyTextAreaId').value;
            document.querySelector('#addPortsManuallyTextAreaId').value = '';
        
        } else if (field == 'connectionProtocol') {
            var value = document.querySelector('input[name=connectProtocol]:checked').value;
            document.querySelector('input[name=connectProtocol]').checked = 'ssh'; 

        } else {
            var value = document.querySelector('input[id=editField]').value;
            document.querySelector('input[id=editField]').value = '';
        }

        const data = await commons.postData("/api/v1/portMgmt/editPortDeviceProfile",  
                {remoteController: sessionStorage.getItem("remoteController"),
                deviceName: deviceName, field: field, value: value}
        )

        commons.getInstantMessages('portMgmt');

        if (data.status == 'success') {
            hide('.editInputField')
            hide('.editConnectionProtocol')
            hide('.editPortDeviceTypeSelection')

            commons.blinkSuccess();
            document.querySelector("#insertStatus").innertHTML = `Succcessfully modified: ${field} = ${value}`;
            window.location.reload();
        }

        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        }
    })
}

let closeEditModal = document.querySelector("#closeEditModal");
if (closeEditModal) {
    closeEditModal.addEventListener('click', event =>  {
        document.querySelector('#editPortDeviceModal').style.display = 'none';
        deviceName = null;
        field = null;
        document.querySelector("#insertDeviceName").innerHTML = '';
        document.querySelector("#inputField").innerHTML = '';
        document.querySelector('input[id=editField]').value = '';
    })
}

// Delete a profile
let deletePortMgmtDevice = document.querySelector("#deletePortMgmtDeviceButton");
if (deletePortMgmtDevice) {
    deletePortMgmtDevice.addEventListener('click', async event => {
        event.preventDefault;
        let profile = document.querySelector("#deletePortMgmtProfileButton").getAttribute("deviceName");

        const data = await commons.postData("/api/v1/portMgmt/delete",  
                {remoteController: sessionStorage.getItem("remoteController"),
                deviceName: profile}
        )

        if (data.status == 'success') {
            commons.blinkSuccess();
            document.querySelector('#portProfileDetailsTable').innerHTML = '';
            document.querySelector('#portConnectionsTable').innerHTML = '';
            //window.location.reload();
        }

        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        }

        commons.getInstantMessages('portMgmt');
    })
}

// Create a new port-mgmt profile
let createLayer1Profile = document.querySelector('#layer1CreateProfileButton');
if (createLayer1Profile) {
    createLayer1Profile.addEventListener('click', async event => {
        event.preventDefault();
    
        let profileName = document.querySelector('input[id=layer1Name]').value;
        if  (profileName == '') {
            alert('Error: Must include a port device name')
            return
        }

        if (customDeviceTypeInput) {
            deviceType = customDeviceTypeInput;
        }

        let portsAdded = document.querySelector('#addPortsManuallyTextAreaId').value;
        if (portsAdded) {
            var ports = portsAdded;
        } else {
            var ports = null;
        }
        
        let profileFieldValues = {name: profileName,
                                  deviceType: deviceType,
                                  vendor:       document.querySelector('input[id=layer1Vendor]').value,
                                  model:        document.querySelector('input[id=layer1Model]').value,
                                  serialNumber: document.querySelector('input[id=layer1SerialNumber]').value,
                                  location:     document.querySelector('input[id=layer1Location]').value,
                                  ipAddress:    document.querySelector('input[id=layer1IpAddress]').value,
                                  ipPort:       document.querySelector('input[id=layer1IpPort]').value,
                                  loginName:    document.querySelector('input[id=layer1LoginName]').value,
                                  password:     document.querySelector('input[id=layer1Password]').value,
                                  connectionProtocol: document.querySelector('input[name=connectProtocol]:checked').value,
                                  ports:     ports}

        // Set all empty values with None string so users have something to click to edit each field
        Object.keys(profileFieldValues).forEach(key => {
            if (profileFieldValues[key] == '') {
                profileFieldValues[key] = 'None'
            }
        })

        //console.log(`profileFieldValues = ${JSON.stringify(profileFieldValues)}`);
        const data = await commons.postData("/api/v1/portMgmt/createProfile",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         profileFieldValues: profileFieldValues
                        });
    
        if (data.status == 'success') {
            commons.blinkSuccess();
            commons.getInstantMessages('portMgmt');
            resetParams();

            var httpProtocol = 'https';
            if (window.location.protocol === 'http:') {
                httpProtocol = 'http';
            }
            window.location = `${window.location.protocol}//${window.location.host}/portMgmt/deviceAttributes/${profileName}`;
        }
    
        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        }
    })
}

const getDevice = async () => {
    let deviceAttributes = document.querySelector('pageAttributes');
    if (deviceAttributes) {
        let device = deviceAttributes.getAttribute('device');
        const data = await commons.postData("/api/v1/portMgmt/getDevice",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         deviceName: device});

        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        } else {
            document.querySelector('#portProfileDetailsTable').innerHTML = data.device;

            let result = await getPortConnections();
            if (result) {
                testConnection();
            }
        }
    }
}

// User adding a new field
const addFieldButton = document.querySelector("#addFieldButton");
if (addFieldButton) {
    addFieldButton.addEventListener('click', async event => {
        //let fieldName = document.querySelectorAll('input[name="fieldNameInput"]').value;
        let fieldName = document.querySelector("#fieldNameInput").value;
        let fieldValue = document.querySelector("#fieldValueInput").value;
        let fieldType = document.querySelector("#fieldType").value;

        if (fieldName.includes(" ")) {
            alert(`The Field Name cannot have spaces: ${fieldName}`)
            return
        }

        if (fieldValue == "") {
            alert('Please provide a field value for the field name')
            return
        }

        if (fieldType == "") {
            alert(`Please select a field type for the field: string, inteter, boolean`)
            return
        }

        let deviceAttributes = document.querySelector('pageAttributes');
        let profile = deviceAttributes.getAttribute('profile');
        const data = await commons.postData("/api/v1/portMgmt/portConnection/addField",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                    profile: profile,
                                    fieldName: fieldName,
                                    fieldValue: fieldValue,
                                    fieldType: fieldType});

        commons.getInstantMessages('portMgmt');
        
        // Reset the field type dropdown option to default
        document.querySelector("#fieldType").value = "";
        document.querySelector("#fieldNameInput").value = ""
        document.querySelector("#fieldValueInput").value = "";

        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        } else {
            commons.blinkSuccess();
            getAddRemoveFieldsTable();
            getPortConnections();
        }    
    })
}

// Get addRemoveFields data table for modal
const addRemoveFieldModalClick = document.querySelector("#addRemoveFields");
if (addRemoveFieldModalClick) {
    addRemoveFieldModalClick.addEventListener('click', event => {
        getAddRemoveFieldsTable();
    })
}

const getAddRemoveFieldsTable = async () => {
    let deviceAttributes = document.querySelector('pageAttributes');
    let profile = deviceAttributes.getAttribute('profile');

    const data = await commons.postData("/api/v1/portMgmt/portConnection/removeFieldsTable",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 profile: profile})

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#removeFieldTableData").innerHTML = data.removeFieldTable;
    }
}

// Get user selected remove-field checkboxes
const removeFieldButton = document.querySelector("#removeFieldsButton");
if (removeFieldButton) {
    removeFieldButton.addEventListener('click', event => {
        let removeFieldCheckboxes = [];
        let removeFieldCheckboxesObj = document.querySelectorAll('input[name="removeFieldCheckboxes"]')

        for (var x=0; x < removeFieldCheckboxesObj.length; x++) {
            if (removeFieldCheckboxesObj[x].checked) {
                removeFieldCheckboxes.push(removeFieldCheckboxesObj[x].getAttribute("field"))
                removeFieldCheckboxesObj[x].checked = false;
            }
        }

        if (removeFieldCheckboxes.length > 0) {
            removeFields(removeFieldCheckboxes);
            clearRemoveFieldCheckboxes();

        } else {
            alert('Please select 1 or more fields')
        }
    })
}

const removeFields = async (fields) => {
    /* Remove the fields */

    let deviceAttributes = document.querySelector('pageAttributes');
    let profile = deviceAttributes.getAttribute('profile');
    const data = await commons.postData("/api/v1/portMgmt/portConnection/removeFields",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     profile: profile, 'fields': fields})

    commons.getInstantMessages('portMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#removeFieldTableData").innerHTML = data.removeFieldTable;
    }

    getAddRemoveFieldsTable();
    getPortConnections();
}

const clearRemoveFieldCheckboxes = () => {
    let removeFieldCheckboxesObj = document.querySelectorAll('input[name="removeFieldCheckboxes"]')
    for (var x=0; x < removeFieldCheckboxesObj.length; x++) {
        removeFieldCheckboxesObj[x].checked = false;
    }
}

const closeRemoveFieldModal = document.querySelector("#closeRemoveFieldsModal");
if (closeRemoveFieldModal) {
    closeRemoveFieldModal.addEventListener('click', event => {
        clearRemoveFieldCheckboxes();
    })
}

const setRemotePort = async (event) => {
    /* cellValue: ${event.target.innerHTML}
       port: event.target.getAttribute("port")
    */

    if (event.target.getAttribute("port") === null) {
        return
    }

    let deviceAttributes = document.querySelector('pageAttributes');
    let profile = deviceAttributes.getAttribute('profile');
    const data = await commons.postData("/api/v1/portMgmt/setRemotePortConnection",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 profile: profile,
                                 port: event.target.getAttribute("port"),
                                 remoteProfile: event.target.getAttribute("remoteProfile"),
                                 remotePort: event.target.innerHTML});

    commons.getInstantMessages('portMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections();
    }
}

const setMultiTenant = async (event) => {
    /* cellValue: ${event.target.innerHTML
       multi-tenant True|False: event.target.getAttribute("port")
    */

    if (event.target.getAttribute("port") === null) {
        return
    }

    let deviceAttributes = document.querySelector('pageAttributes');
    let profile = deviceAttributes.getAttribute('profile');
    const data = await commons.postData("/api/v1/portMgmt/setPortMultiTenant",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 profile: profile,
                                 port: event.target.getAttribute("port"),
                                 multiTenantSelection: event.target.innerHTML});

    commons.getInstantMessages('portMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections();
    }
}

const setOpticMode = async (event) => {
    /* cellValue: ${event.target.innerHTML
       port: event.target.getAttribute("port")
       opticMode:  event.target.innerHTML
    */

    if (event.target.getAttribute("port") === null) {
        return
    }

    let deviceAttributes = document.querySelector('pageAttributes');
    let profile = deviceAttributes.getAttribute('profile');
    const data = await commons.postData("/api/v1/portMgmt/setOpticMode",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 profile: profile,
                                 port: event.target.getAttribute("port"),
                                 opticMode: event.target.innerHTML});

    commons.getInstantMessages('portMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections();
    }
}

const testConnection = async () => {
    let deviceAttributes = document.querySelector('pageAttributes');
    let profile = deviceAttributes.getAttribute('profile');
    let ipAddress = deviceAttributes.getAttribute('ipAddress');
    let ipPort = deviceAttributes.getAttribute('ipPort');

    const data = await commons.postData("/api/v1/portMgmt/testConnection",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 profile: profile, ipAddress: ipAddress, ipPort: ipPort});

    /*
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        document.querySelector("#insertProfileStatus").innerHTML = data.html;
    } else {
        document.querySelector("#insertProfileStatus").innerHTML = data.html;
    }
    */
}

let removeSelectedPorts = document.querySelector('#removePortsFromProfile');
if (removeSelectedPorts) {
    removeSelectedPorts.addEventListener('click', event => {
        var portCheckboxList = new Array();
        let portMgmtCheckboxes = document.querySelectorAll('input[name="portMgmtCheckboxes"]:checked');
        portMgmtCheckboxes.forEach((checkbox) => {
            portCheckboxList.push(checkbox.getAttribute('port'));
            checkbox.checked = false;
        })
        removePorts(portCheckboxList);
    })
}

const removePorts = async (portList) => {
    let deviceAttributes = document.querySelector('pageAttributes');
    let profile = deviceAttributes.getAttribute('profile')

    const data = await commons.postData("/api/v1/portMgmt/removePorts",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         profile: profile, ports: portList});

    commons.getInstantMessages('portMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        uncheckAllPorts();
    }
}

const addPortsToPortGroup = async (portGroup, portList) => {
    let deviceAttributes = document.querySelector('pageAttributes');
    let profile = deviceAttributes.getAttribute('profile')

    const data = await commons.postData("/api/v1/portMgmt/addPortsToPortGroup",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         portGroup: portGroup, profile: profile, ports: portList});

    commons.getInstantMessages('portMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        uncheckAllPorts();
        commons.blinkSuccess();
        getPortConnections();
    }
}

const removePortsFromPortGroup = async (portGroup, portList) => {
    // portList format: portGroup:port
    let deviceAttributes = document.querySelector('pageAttributes');
    let profile = deviceAttributes.getAttribute('profile');

    const data = await commons.postData("/api/v1/portMgmt/removePortsFromPortGroup",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         profile: profile, portGroup:portGroup, ports: portList});

    commons.getInstantMessages('portMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        uncheckAllPorts();
        commons.blinkSuccess();
        getPortConnections();
    }
}

const getConnectPortsToLinkDeviceDropdown = async () => {
    /* Get a dropdown menu of link switches.
       When user selects a link switch, there is an event 
       listener to get all the ports to select as out-ports.
    */
    let deviceAttributes = document.querySelector('pageAttributes');
    let profile = deviceAttributes.getAttribute('profile');
   
    const data = await commons.postData("/api/v1/portMgmt/getConnectPortsToLinkDeviceDropdown",  
                           {remoteController: sessionStorage.getItem("remoteController")});
   
    commons.getInstantMessages('portMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#connectPortsToLinkDevice").innerHTML = data.linkDevicesHtml;

        let selectConnectToLinkDevice = document.querySelector('#selectConnectToLinkDevice');
        selectConnectToLinkDevice.addEventListener('click', event => {
            portCheckboxList = [];
            let portMgmtCheckboxes = document.querySelectorAll('input[name="portMgmtCheckboxes"]:checked');
            portMgmtCheckboxes.forEach((checkbox) => {
                portCheckboxList.push(checkbox.getAttribute('port'));
                checkbox.checked = false;
            })

            let toLinkDevice = event.target.innerText;
            connectToLinkDevice(profile, portCheckboxList, toLinkDevice);
        })
    }
}

const connectToLinkDevice = async (fromLinkDeviceProfile, fromPorts, toLinkDeviceProfile) => {
    const data = await commons.postData("/api/v1/portMgmt/connectToLinkDevice",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         fromLinkDeviceProfile: fromLinkDeviceProfile,
                         ports: fromPorts,
                         toLinkDeviceProfile: toLinkDeviceProfile, 
                         });

    commons.getInstantMessages('portMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        uncheckAllPorts();
        commons.blinkSuccess();
        getPortConnections();
    }
}

const addPortsToPortGroupDropdown = async () => {
    // Adding ports to a port-group: PortGroup dropdown options for ports

    const data = await commons.postData("/api/v1/portMgmt/selectPortGroupToAddPorts",  
                        {remoteController: sessionStorage.getItem("remoteController")});

    commons.getInstantMessages('portMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#addPortsToPortGroup").innerHTML = data.portGroupOptions;


        let addSelectedPortsToPortGroup = document.querySelector('#selectPortGroupToAddPorts');
        addSelectedPortsToPortGroup.addEventListener('click', event => {
            portCheckboxList = [];
            let portMgmtCheckboxes = document.querySelectorAll('input[name="portMgmtCheckboxes"]:checked');
            portMgmtCheckboxes.forEach((checkbox) => {
                portCheckboxList.push(checkbox.getAttribute('port'));
                checkbox.checked = false;
            })

            let selectedPortGroup = event.target.innerText;
            addPortsToPortGroup(selectedPortGroup, portCheckboxList);
        })
    }
}

const removePortsFromPortGroupDropdown = async () => {
    // Remove ports from a port-group: PortGroup dropdown options for ports.
    const data = await commons.postData("/api/v1/portMgmt/selectPortGroupToRemovePorts",  
                        {remoteController: sessionStorage.getItem("remoteController")});

    commons.getInstantMessages('portMgmt');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#removePortsFromPortGroup").innerHTML = data.portGroupOptions;

        let addSelectedPortsToPortGroup = document.querySelector('#selectPortGroupToRemovePorts');
        addSelectedPortsToPortGroup.addEventListener('click', event => {
            portCheckboxList = [];
            let portMgmtCheckboxes = document.querySelectorAll('input[name="portMgmtCheckboxes"]:checked');
            portMgmtCheckboxes.forEach((checkbox) => {
                portCheckboxList.push(checkbox.getAttribute('port'));
                checkbox.checked = false;
            })

            let selectedPortGroup = event.target.innerText;
            removePortsFromPortGroup(selectedPortGroup, portCheckboxList);
        })
    }
}

const disconnectPortsFromLinkDevice = document.querySelector("#disconnectPortsFromLinkDevice");
if (disconnectPortsFromLinkDevice) {
    disconnectPortsFromLinkDevice.addEventListener('click', async (event) => {
        let deviceAttributes = document.querySelector('pageAttributes');
        let profile = deviceAttributes.getAttribute('profile');

        let portCheckboxList = [];
        let portMgmtCheckboxes = document.querySelectorAll('input[name="portMgmtCheckboxes"]:checked');
        portMgmtCheckboxes.forEach((checkbox) => {
            portCheckboxList.push(checkbox.getAttribute('port'));
            checkbox.checked = false;
        })

        const data = await commons.postData("/api/v1/portMgmt/disconnectPorts",  
                            {remoteController: sessionStorage.getItem("remoteController"),
                            profile: profile,
                            ports: portCheckboxList});

        commons.getInstantMessages('portMgmt');
        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        } else {
            uncheckAllPorts();
            commons.blinkSuccess();
            getPortConnections(); 
        }   
    })
}

const resetParams = () => {
    document.querySelector('input[id=layer1Name]').value = '';
    customDeviceTypeInput = null;

    document.querySelector('#insertSelectedDeviceType').innerHTML = '';
    document.querySelector('#insertCustomDeviceType').innerHTML = '';
    document.querySelector('input[id=layer1CustomInput]').value = '';
    document.querySelector('input[id=layer1Vendor]').value = '';
    document.querySelector('input[id=layer1Model]').value = '';
    document.querySelector('input[id=layer1Location]').value = '';
    document.querySelector('input[id=layer1IpAddress]').value = '';
    document.querySelector('input[id=layer1IpPort]').value = '';
    document.querySelector('input[id=layer1LoginName]').value = '';
    document.querySelector('input[id=layer1Password]').value = '';
    document.querySelector('input[name=connectProtocol][id=layer1IpSSHProtocol]').checked = 'ssh'; 
    document.querySelector('#addPortsManuallyTextAreaId').value = ''; 
}


window.editPortDeviceField = editPortDeviceField;
window.addPortsToPortGroupDropdown =  addPortsToPortGroupDropdown;
window.removePortsFromPortGroupDropdown =  removePortsFromPortGroupDropdown;
