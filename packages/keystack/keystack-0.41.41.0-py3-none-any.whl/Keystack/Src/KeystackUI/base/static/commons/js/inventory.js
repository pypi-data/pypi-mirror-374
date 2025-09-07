import * as commons from './commons.js';

var deviceType = null;
var selectedDeviceTypeForEdit = null;
var deviceLocation = null;
var selectedDeviceLocationForEdit = null;
var deviceVendor = null;
var selectedDeviceVendorForEdit = null;

var deviceName = null;
var field = null;

// Show devices based on the filter
var deviceTypeCheckboxes = 'All';
var userSelectedAllDeviceTypesCheckbox = false;
var deviceLocationCheckboxes = 'All';
var userSelectedAllDeviceLocationsCheckbox = false;
var deviceVendorCheckboxes = 'All';
var userSelectedAllDeviceVendorsCheckbox = false;

// GetPortConnections
var selectAllPortsCheckboxes = null;

// User add devices to the selected Env. This will change when users reselect env.
var addDevicesToSelectedEnvFullPath = null;

var devicesPerPage = 25;
// Set default page number = 1
var getCurrentPageNumber = 1;
// For previous/next button calculation
var startPageIndex = 0;
var totalPages = 0;

// Each getPortConnection is an accordion expansion
// with its own table and its own unique row ID
// Using these variable to track which device the user
// expanded last and insert the device table to the right row Id
var insertPortConnectsTableId = null;
var addPortsToPortGroupId = null;
var removePortsFromPortGroupId = null;
var connectPortsToLinkDeviceId = null;
var addRemoveKeysId = null;
var addPortsId = null;
var domain = null;

// Maps key=device value=tableRowId
var portConnectionTableRowsJsonMapping = null;

document.addEventListener("DOMContentLoaded", (event) => {
    let isUserSysAdmin = document.querySelector("#user").getAttribute('sysAdmin');
    let domainUserRole = document.querySelector("#domainUserRole").getAttribute('role');

    if (domainUserRole == 'engineer') {
        // "#messages", "#messagesIcon", "#debugDropdown", "#utilization", "#utilizationIcon", 
        let divs = ["#showAddDeviceForm", "#deleteDevices", 
                    "#exportDevicesToCSV", "#importCSVDevices", "#addDevicesToEnv", "#createFilters"];
        for (let x=0; x<divs.length; x++) {
            let currentDiv = divs[x]
            document.querySelector(currentDiv).classList.add('hideFromUser');
        }
        
        document.querySelector("#editDeviceButton").style.display = 'none';
        document.querySelector("#loginPasswordInput").style.display = 'none';
        document.querySelector("#password").style.display = 'none';
    }

    if (['engineer', 'manager'].includes(domainUserRole) || isUserSysAdmin == "False") {
        let divs = ["#systemSettingsDropdown"]
        for (let x=0; x<divs.length; x++) {
            let currentDiv = divs[x]
            document.querySelector(currentDiv).classList.add('hideFromUser');
        }            
    }

    domain = inventoryAttributes.getAttribute('domain');
    document.querySelector('#topbarTitlePage').innerHTML = `Lab Inventory:&emsp;${domain}`;
    commons.getInstantMessages('labInventory');
    commons.getServerTime();
    document.querySelector("#setDevicesPerPageDropdown").innerHTML = devicesPerPage;
    document.querySelector(".inventoryNavLink").classList.add("hideFromUser");

    let showInventory = document.querySelector("#showInventory");
    if (showInventory) {
        showInventory.classList.remove('hideFromUser');
    }

    let addDeviceForm = document.querySelector("#addDeviceForm");
    if (addDeviceForm) {
        addDeviceForm.classList.add('hideFromUser');
    }

    getInventory();
    createInitialDeviceFiltersInDB();

    getDeviceTypeOptions();
    getDeviceTypeSelectionDropdownForEdit();
    //getDeviceTypeFilterOptions();

    //getDeviceLocationOptions();
    //getDeviceLocationSelectionDropdownForEdit();
    //getDeviceLocationFilterOptions();

    //getDeviceVendorOptions();
    //getDeviceVendorSelectionDropdownForEdit();
    //getDeviceVendorFilterOptions();

    commons.getInstantMessages('labInventory');
})


const showInventory = document.querySelector("#showInventoryTableNavLink");
showInventory.addEventListener('click', event => {
    document.querySelector("#showInventory").classList.remove('hideFromUser');
    document.querySelector("#addDeviceForm").classList.add('hideFromUser');
    document.querySelector(".inventoryNavLink").classList.add("hideFromUser")
    getInventory();
})

const addDeviceForm = document.querySelector("#showAddDeviceForm");
addDeviceForm.addEventListener('click', event => {
    document.querySelector("#addDeviceForm").classList.remove('hideFromUser');
    document.querySelector("#showInventory").classList.add('hideFromUser');
    document.querySelector(".inventoryNavLink").classList.remove("hideFromUser")
})

const hide = (classObject) => {
    // Call hide in .css. Add "hide" in the class to display: none;
    let allClassElements = document.querySelectorAll(classObject);
    allClassElements.forEach(classElement => {
        classElement.classList.add("hide");
    })
}

const unhide = (classObject) => {
    // Remove the hide from the class to show
    let allClassElements = document.querySelectorAll(classObject);
    allClassElements.forEach(classElement => {
        classElement.classList.remove("hide");
    })
}

const uncheckAllPorts = () => {
    /* Port Connections */
    var allPortsCheckboxes = document.querySelectorAll('input[name="portMgmtCheckboxes"]');
    for (var x=0; x < allPortsCheckboxes.length; x++) {
        allPortsCheckboxes[x].checked = false;
    }

    // Uncheck the selectAll checkbox
    selectAllPortsCheckboxes = document.querySelector('#selectAllPortsCheckboxes');
    selectAllPortsCheckboxes.checked = false;
}

const getSelectedPorts = () => {
    /* Port Connections */
    let selectedPorts = [];
    var allPortsCheckboxes = document.querySelector("#portMgmtTable");
    for (var x=0; x < allPortsCheckboxes.length; x++) {
        allPortsCheckboxes[x].checked = false;
        if (allPortsCheckboxes[x].checked) {
            selectedPorts.push(allPortsCheckboxes[x])
        }
    }
}

const importCsvForm = document.querySelector('#formImportCSV');
importCsvForm.addEventListener('submit', async event => {
    event.preventDefault();

    let overwriteExistingDevices = document.querySelector('input[id="overwriteExistingDevicesCheckbox"]').checked;
    const url = '/api/v1/lab/inventory/importCSV';
    const formData = new FormData(importCsvForm);

    formData.append('importCsvForm', importCsvForm[0]);
    formData.append('domain', domain);
    formData.append('overwriteExistingDevices', overwriteExistingDevices)

    const fileInput = document.querySelector('input[type=file]');
    // C:\fakepath\aiml_sanity_config.txt
    const path = fileInput.value;
    const fileName = path.split(/(\\|\/)/g).pop();

    if (fileName == '') {
        alert('Please select a .csv file to import')
        return
    }

    let extension = fileName.split('.')[1]

    if (extension != 'csv') {
        alert('Importing an inventory file must have a .csv extension')
        return
    }

    const fetchOptions = {
      method: 'post',
      body: formData
    };
  
    try {
        const response = await fetch(url, fetchOptions);
        const data = await response.json();
        commons.getInstantMessages('labInventory');
        getInventory();
        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        } else {
            commons.blinkSuccess();
        }
    } catch (error) {
        console.error(`importCSV error: ${error}`)
        return error
    };

    document.querySelector('input[id="overwriteExistingDevicesCheckbox"]').checked = false;
})

// Select all devices checkbox for delete
/*
const selectAllDevicesCheckboxes = document.querySelector('#selectAllDevicesForDelete');
selectAllDevicesCheckboxes.addEventListener('change', selectAllDevicesCheckboxEvent => {
    var allDevicesCheckboxes = document.querySelectorAll('input[name="devices"]')

    if (selectAllDevicesCheckboxEvent.target.checked) {
        for (var x=0; x < allDevicesCheckboxes.length; x++) {
            allDevicesCheckboxes[x].checked = true;
        }
    } else {
        for (var x=0; x < allDevicesCheckboxes.length; x++) {
            allDevicesCheckboxes[x].checked = false;
        }
    }
})
*/

const deleteDevicesButton = document.querySelector('#deleteDevicesButton');
deleteDevicesButton.addEventListener('click', event => {
    event.preventDefault;
    let deleteDevicesArray = [];
    let deleteDeviceCheckboxes = document.querySelectorAll('input[name="devices"]')

    for (var x=0; x < deleteDeviceCheckboxes.length; x++) {
        if (deleteDeviceCheckboxes[x].checked) {
            let domain = deleteDeviceCheckboxes[x].getAttribute('domain');
            let deviceName = deleteDeviceCheckboxes[x].getAttribute('deviceName');
            deleteDevicesArray.push(deviceName)
            deleteDeviceCheckboxes[x].checked = false;
        }
    }

    if (deleteDevicesArray.length > 0) {
        deleteDevices(deleteDevicesArray);
        document.querySelector('#selectAllDevicesForDelete').checked = false;
    }
})

const portConnections = document.querySelector('#portConnections');
portConnections.addEventListener('click', event => {
    event.preventDefault;
    var devicesCheckboxes = document.querySelectorAll('input[name="devices"]')
    let devicesArray = [];

    for (var x=0; x < devicesCheckboxes.length; x++) {
        if (devicesCheckboxes[x].checked) {
            devicesArray.push(devicesCheckboxes[x].getAttribute('deviceName'))
        }
    }

    if (devicesArray.length > 1) {
        alert('Please select one device')
        return
    }

    var httpProtocol = 'https';
    if (window.location.protocol === 'http:') {
        httpProtocol = 'http';
    }

    // Call showProfile views
    window.location = `${window.location.protocol}//${window.location.host}/portMgmt/showProfile/${devicesArray[0]}`;    
})

const createInitialDeviceFiltersInDB = () => {
    const data = commons.postData("/api/v1/lab/inventory/createInitialDeviceFilters",  
                                    {remoteController: sessionStorage.getItem("remoteController")});

    commons.getInstantMessages('labInventory');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }
}

// Create new device type
const addDeviceType = document.querySelector('#createDeviceTypeEnterButton');
addDeviceType.addEventListener('click', async event => {
    event.preventDefault();
    let newDeviceLocation = document.querySelector('input[name=deviceTypeInput]').value;

    const data = await commons.postData("/api/v1/lab/inventory/addDeviceType",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         deviceType: commons.capitalizeWords(newDeviceLocation.trim())});

    commons.getInstantMessages('labInventory');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getDeviceTypeFilterOptions();
        getDeviceTypeOptions();
        getDeviceTypeSelectionDropdownForEdit();
        getDeviceTypeTableForRemoval();
        document.querySelector('input[id=deviceTypeInput]').value = '';
    }
})

const getDeviceTypeOptions = async () => {
    /* For add-device dropdown options */

    const data = await commons.postData("/api/v1/lab/inventory/getDeviceTypeOptions",  
                                    {remoteController: sessionStorage.getItem("remoteController")});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertDeviceTypeOptions").innerHTML = data.deviceTypes;

        let deviceTypeDropdown = document.querySelector("#selectDeviceTypeOptions");
        deviceTypeDropdown.addEventListener('click', event => {
            deviceType = event.target.innerText;
            document.querySelector("#insertSelectedDeviceType").innerHTML = deviceType;
        })
    }
}

const getDeviceTypeFilterOptions = async () => {
    const data = await commons.postData("/api/v1/lab/inventory/getDeviceTypeFilterOptions",  
                                    {remoteController: sessionStorage.getItem("remoteController")});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertDeviceTypeFilterOptions").innerHTML = data.deviceTypesDropdown;

        // User selected all
        let selectedAllDeviceTypes = document.querySelector("#selectedAllDeviceTypes");
        selectedAllDeviceTypes.addEventListener('click', event => {
            let selectedAllDeviceTypesObj = document.querySelectorAll('input[name="selectedAllDeviceTypes"]');
            let selectedDeviceTypesObj = document.querySelectorAll('input[name="selectedDeviceTypes"]');
            deviceTypeCheckboxes = 'All';

            if (selectedAllDeviceTypesObj[0].checked) {
                userSelectedAllDeviceTypesCheckbox = true;
                // Disable individual checkboxes
                for (var x=0; x < selectedDeviceTypesObj.length; x++) {
                    selectedDeviceTypesObj[x].disabled = true; 
                    selectedDeviceTypesObj[x].checked = false;
                }
            } else {
                userSelectedAllDeviceTypesCheckbox = false;
                // User uncheckbed the 'All' checkbox.  Enable all checkboxes.
                for (var x=0; x < selectedDeviceTypesObj.length; x++) {
                    selectedDeviceTypesObj[x].disabled = false; 
                }                
            }
        })

        // User selected individual device types
        let selectDeviceTypeFilter = document.querySelector('#selectDeviceTypeFilterButton');
        selectDeviceTypeFilter.addEventListener('click', selectDeviceTypeCheckbox => {
            if (userSelectedAllDeviceTypesCheckbox) {
                getInventory();
            } else {
                let selectedDeviceTypesObj = document.querySelectorAll('input[name="selectedDeviceTypes"]');

                deviceTypeCheckboxes = []; 
                for (var x=0; x < selectedDeviceTypesObj.length; x++) {
                    if (selectedDeviceTypesObj[x].checked) {
                        deviceTypeCheckboxes.push(selectedDeviceTypesObj[x].getAttribute("deviceTypeSelected"));
                    }
                }

                if (deviceTypeCheckboxes != 'All' && deviceTypeCheckboxes.length == 0) {
                    // User might've unchecked the 'All' checkboxes and did not select any individual device type
                    // So get all device types
                    deviceTypeCheckboxes = 'All';
               }
                getInventory();
            }
        })
    }
}

const getDeviceTypeSelectionDropdownForEdit = async () => {
    const data = await commons.postData("/api/v1/lab/inventory/getDeviceTypeDropdownForEditing",  
                        {remoteController: sessionStorage.getItem("remoteController")});

    commons.getInstantMessages('labInventory');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertDeviceTypeDropdownForEdit').innerHTML = data.deviceTypeDropdownForEditing;

        let deviceTypeForEdit = document.querySelector('#selectDeviceTypeForEdit');
        deviceTypeForEdit.addEventListener('click', event => {
            event.preventDefault();
            document.querySelector('#insertSelectedDeviceTypeForEdit').innerHTML = '';
            selectedDeviceTypeForEdit = event.target.innerText;
        
            if (deviceType != 'Enter') {
                document.querySelector('#insertSelectedDeviceTypeForEdit').innerHTML = selectedDeviceTypeForEdit;
            }
        })
    }
}


document.querySelector("#manageDeviceTypeFilters").addEventListener('click', async event => {
    getDeviceTypeTableForRemoval();
})
 
const getDeviceTypeTableForRemoval = async () => {
    const data = await commons.postData("/api/v1/lab/inventory/getDeviceTypeFilterMgmtTable",  
                                                {remoteController: sessionStorage.getItem("remoteController")})

    commons.getInstantMessages('labInventory');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertDeviceTypesTable").innerHTML = data.table;

        // Check or uncheck the select-all checkboxes. When user click on the remove button,
        // it will look for all the selected checkboxes
        let selectAllDeviceTypesForDelete = document.querySelector('#selectAllDeviceTypesForDelete');
        selectAllDeviceTypesForDelete.addEventListener('click', selectAllDeviceTypesForDeleteCheckbox => {
            let allCheckboxes = document.querySelectorAll('input[name="removeDeviceTypeCheckbox"]')
            if (selectAllDeviceTypesForDeleteCheckbox.target.checked) {
                for (var x=0; x < allCheckboxes.length; x++) {
                    allCheckboxes[x].checked = true;
                }
            } else {
                for (var x=0; x < allCheckboxes.length; x++) {
                    allCheckboxes[x].checked = false;
                }
            }
        })
    }
}

let removeDeviceTypesFilterButton = document.querySelector('#removeDeviceTypesFilterButton');
removeDeviceTypesFilterButton.addEventListener('click', event => {
    let allRemoveDeviceTypeCheckboxes = document.querySelectorAll('input[name="removeDeviceTypeCheckbox"]');
    var removeAddtionalDeviceTypesArray = [];

    for (var x=0; x < allRemoveDeviceTypeCheckboxes.length; x++) {
        if (allRemoveDeviceTypeCheckboxes[x].checked) {
            let removeDeviceType = allRemoveDeviceTypeCheckboxes[x].getAttribute("deviceType") ;
            removeAddtionalDeviceTypesArray.push(removeDeviceType);
            allRemoveDeviceTypeCheckboxes[x].checked = false;
        }
    }

    if (removeAddtionalDeviceTypesArray.length > 0) {
        removeDeviceTypes(removeAddtionalDeviceTypesArray);
    }
})

const removeDeviceTypes = async (deviceTypes) => {
    const data = await commons.postData("/api/v1/lab/inventory/removeDeviceType",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         deviceTypes: deviceTypes});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getDeviceTypeTableForRemoval();
    }
}

// Create a new device location
const addDeviceLocation = document.querySelector('#createDeviceLocationEnterButton');
addDeviceLocation.addEventListener('click', async event => {
    event.preventDefault();
    let newDeviceLocation = document.querySelector('input[name=deviceLocationInput]').value;

    const data = await commons.postData("/api/v1/lab/inventory/addDeviceLocation",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         location: commons.capitalizeWords(newDeviceLocation.trim())});

    commons.getInstantMessages('labInventory');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getDeviceLocationFilterOptions();
        getDeviceLocationOptions();
        getDeviceLocationSelectionDropdownForEdit();
        getDeviceLocationTableForRemoval();
        document.querySelector('input[id=deviceLocationInput]').value = '';
    }
})

const getDeviceLocationOptions = async () => {
    /* For add-device dropdown options */

    const data = await commons.postData("/api/v1/lab/inventory/getDeviceLocationOptions",  
                                    {remoteController: sessionStorage.getItem("remoteController")});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertLocationOptions").innerHTML = data.deviceLocations;

        let deviceLocationDropdown = document.querySelector("#selectDeviceLocationOptions");
        deviceLocationDropdown.addEventListener('click', event => {
            deviceLocation = event.target.innerText;
            document.querySelector("#insertSelectedLocation").innerHTML = deviceLocation;
        })
    }
}

const getDeviceLocationFilterOptions = async () => {
    const data = await commons.postData("/api/v1/lab/inventory/getDeviceLocationFilterOptions",  
                                    {remoteController: sessionStorage.getItem("remoteController")});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertDeviceLocationFilterOptions").innerHTML = data.deviceLocations;

        // User selected all
        let selectedAllDeviceLocations = document.querySelector("#selectedAllDeviceLocations");
        selectedAllDeviceLocations.addEventListener('click', event => {
            let selectedAllDeviceLocationsObj = document.querySelectorAll('input[name="selectedAllDeviceLocations"]');
            let selectedDeviceLocationsObj = document.querySelectorAll('input[name="selectedDeviceLocations"]');
            deviceLocationCheckboxes = 'All';

            if (selectedAllDeviceLocationsObj[0].checked) {
                userSelectedAllDeviceLocationsCheckbox = true;
                // Disable individual checkboxes
                for (var x=0; x < selectedDeviceLocationsObj.length; x++) {
                    selectedDeviceLocationsObj[x].disabled = true; 
                    selectedDeviceLocationsObj[x].checked = false;
                }
            } else {
                userSelectedAllDeviceLocationsCheckbox = false;
                // User uncheckbed the 'All' checkbox.  Enable all individual checkboxes.
                for (var x=0; x < selectedDeviceLocationsObj.length; x++) {
                    selectedDeviceLocationsObj[x].disabled = false; 
                }                
            }
        })

        // User selected individual device locations
        let selectDeviceLocationFilter = document.querySelector('#selectDeviceLocationFilterButton');
        selectDeviceLocationFilter.addEventListener('click', selectDeviceLocationCheckbox => {
            if (userSelectedAllDeviceLocationsCheckbox) {
                getInventory();
            } else {
                let selectedDeviceLocationsObj = document.querySelectorAll('input[name="selectedDeviceLocations"]');

                deviceLocationCheckboxes = []; 
                for (var x=0; x < selectedDeviceLocationsObj.length; x++) {
                    if (selectedDeviceLocationsObj[x].checked) {
                        deviceLocationCheckboxes.push(selectedDeviceLocationsObj[x].getAttribute("deviceLocationSelected"));
                    }
                }

                if (deviceLocationCheckboxes != 'All' && deviceLocationCheckboxes.length == 0) {
                    // User might've unchecked the 'All' checkboxes and did not select any individual device type
                    // So get all device locations
                    deviceLocationCheckboxes = 'All';
               }
                getInventory();
            }
        })
    }
}

const getDeviceLocationSelectionDropdownForEdit = async () => {
    const data = await commons.postData("/api/v1/lab/inventory/getDeviceLocationDropdownForEditing",  
        {remoteController: sessionStorage.getItem("remoteController")});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertDeviceLocationDropdownForEdit").innerHTML = data.deviceLocationDropdownForEditing;

        let deviceLocationDropdown = document.querySelector("#selectDeviceLocationForEdit");
        deviceLocationDropdown.addEventListener('click', event => {
            event.preventDefault();
            selectedDeviceLocationForEdit = event.target.innerText;
            document.querySelector("#insertSelectedDeviceLocationForEdit").innerHTML = selectedDeviceLocationForEdit;
        })
    }
}

document.querySelector("#manageDeviceLocationFilters").addEventListener('click', async event => {
    getDeviceLocationTableForRemoval();
})
 
const getDeviceLocationTableForRemoval = async () => {
    const data = await commons.postData("/api/v1/lab/inventory/getDeviceLocationFilterMgmtTable",  
                                                {remoteController: sessionStorage.getItem("remoteController")})

    commons.getInstantMessages('labInventory');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertDeviceLocationsTable").innerHTML = data.table;

        // Check or uncheck the select-all checkboxes. When user click on the remove button,
        // it will look for all the selected checkboxes
        let selectAllDeviceLocationsForDelete = document.querySelector('#selectAllDeviceLocationsForDelete');
        selectAllDeviceLocationsForDelete.addEventListener('click', selectAllDeviceLocationsForDeleteCheckbox => {
            let allCheckboxes = document.querySelectorAll('input[name="removeDeviceLocationCheckbox"]')
            if (selectAllDeviceLocationsForDeleteCheckbox.target.checked) {
                for (var x=0; x < allCheckboxes.length; x++) {
                    allCheckboxes[x].checked = true;
                }
            } else {
                for (var x=0; x < allCheckboxes.length; x++) {
                    allCheckboxes[x].checked = false;
                }
            }
        })
    }
}

let removeDeviceLocationsFilterButton = document.querySelector('#removeDeviceLocationsFilterButton');
removeDeviceLocationsFilterButton.addEventListener('click', event => {
    let allRemoveDeviceLocationCheckboxes = document.querySelectorAll('input[name="removeDeviceLocationCheckbox"]');
    var removeAddtionalDeviceLocationsArray = [];

    for (var x=0; x < allRemoveDeviceLocationCheckboxes.length; x++) {
        if (allRemoveDeviceLocationCheckboxes[x].checked) {
            let removeDeviceLocation = allRemoveDeviceLocationCheckboxes[x].getAttribute("deviceLocation") ;
            removeAddtionalDeviceLocationsArray.push(removeDeviceLocation);
            allRemoveDeviceLocationCheckboxes[x].checked = false;
        }
    }

    if (removeAddtionalDeviceLocationsArray.length > 0) {
        removeDeviceLocations(removeAddtionalDeviceLocationsArray);
    }
})

const removeDeviceLocations = async (deviceLocations) => {
    const data = await commons.postData("/api/v1/lab/inventory/removeDeviceLocation",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         deviceLocations: deviceLocations});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getDeviceLocationTableForRemoval();
    }
}


// Create a new vendor
const addDeviceVendor = document.querySelector('#createDeviceVendorEnterButton');
addDeviceVendor.addEventListener('click', async event => {
    event.preventDefault();
    let newDeviceVendor = document.querySelector('input[name=deviceVendorInput]').value;

    const data = await commons.postData("/api/v1/lab/inventory/addDeviceVendor",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         vendor: commons.capitalizeWords(newDeviceVendor.trim())});

    commons.getInstantMessages('labInventory');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getDeviceVendorFilterOptions();
        getDeviceVendorOptions();
        getDeviceVendorSelectionDropdownForEdit()
        getDeviceVendorTableForRemoval();
        document.querySelector('input[id=deviceVendorInput]').value = '';
    }
})

const getDeviceVendorOptions = async () => {
    /* For add-device dropdown options */

    const data = await commons.postData("/api/v1/lab/inventory/getDeviceVendorOptions",  
                                    {remoteController: sessionStorage.getItem("remoteController")});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertVendorOptions").innerHTML = data.deviceVendors;

        let deviceVendorDropdown = document.querySelector("#selectDeviceVendorOptions");
        deviceVendorDropdown.addEventListener('click', event => {
            deviceVendor = event.target.innerText;
            document.querySelector("#insertSelectedVendor").innerHTML = deviceVendor;
        })
    }
}

const getDeviceVendorFilterOptions = async () => {
    const data = await commons.postData("/api/v1/lab/inventory/getDeviceVendorFilterOptions",  
                                    {remoteController: sessionStorage.getItem("remoteController")});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertDeviceVendorFilterOptions").innerHTML = data.deviceVendors;

        // User selected all
        let selectedAllDeviceVendors = document.querySelector("#selectedAllDeviceVendors");
        selectedAllDeviceVendors.addEventListener('click', event => {
            let selectedAllDeviceVendorsObj = document.querySelectorAll('input[name="selectedAllDeviceVendors"]');
            let selectedDeviceVendorsObj = document.querySelectorAll('input[name="selectedDeviceVendors"]');
            deviceVendorCheckboxes = 'All';

            if (selectedAllDeviceVendorsObj[0].checked) {
                userSelectedAllDeviceVendorsCheckbox = true;
                // Disable individual checkboxes
                for (var x=0; x < selectedDeviceVendorsObj.length; x++) {
                    selectedDeviceVendorsObj[x].disabled = true; 
                    selectedDeviceVendorsObj[x].checked = false;
                }
            } else {
                userSelectedAllDeviceVendorsCheckbox = false;
                // User uncheckbed the 'All' checkbox.  Enable all individual checkboxes.
                for (var x=0; x < selectedDeviceVendorsObj.length; x++) {
                    selectedDeviceVendorsObj[x].disabled = false; 
                }                
            }
        })

        // User selected individual device vendors
        let selectDeviceVendorFilter = document.querySelector('#selectDeviceVendorFilterButton');
        selectDeviceVendorFilter.addEventListener('click', selectDeviceVendorCheckbox => {
            if (userSelectedAllDeviceVendorsCheckbox) {
                getInventory();
            } else {
                let selectedDeviceVendorsObj = document.querySelectorAll('input[name="selectedDeviceVendors"]');

                deviceVendorCheckboxes = []; 
                for (var x=0; x < selectedDeviceVendorsObj.length; x++) {
                    if (selectedDeviceVendorsObj[x].checked) {
                        deviceVendorCheckboxes.push(selectedDeviceVendorsObj[x].getAttribute("deviceVendorSelected"));
                    }
                }

                if (deviceVendorCheckboxes != 'All' && deviceVendorCheckboxes.length == 0) {
                    // User might've unchecked the 'All' checkboxes and did not select any individual device vendor
                    // So get all device vendors
                    deviceVendorCheckboxes = 'All';
               }
                getInventory();
            }
        })
    }
}

const getDeviceVendorSelectionDropdownForEdit = async () => {
    const data = await commons.postData("/api/v1/lab/inventory/getDeviceVendorDropdownForEditing",  
        {remoteController: sessionStorage.getItem("remoteController")});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertDeviceVendorDropdownForEdit").innerHTML = data.deviceVendorDropdownForEditing;

        let deviceVendorDropdown = document.querySelector("#selectDeviceVendorForEdit");
        deviceVendorDropdown.addEventListener('click', event => {
            event.preventDefault();
            selectedDeviceVendorForEdit = event.target.innerText;
            document.querySelector("#insertSelectedDeviceVendorForEdit").innerHTML = selectedDeviceVendorForEdit;
        })
    }
}

document.querySelector("#manageDeviceVendorFilters").addEventListener('click', async event => {
    getDeviceVendorTableForRemoval();
})
 
const getDeviceVendorTableForRemoval = async () => {
    const data = await commons.postData("/api/v1/lab/inventory/getDeviceVendorFilterMgmtTable",  
                                                {remoteController: sessionStorage.getItem("remoteController")})

    commons.getInstantMessages('labInventory');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertDeviceVendorsTable").innerHTML = data.table;

        // Check or uncheck the select-all checkboxes. When user click on the remove button,
        // it will look for all the selected checkboxes
        let selectAllDeviceVendorsForDelete = document.querySelector('#selectAllDeviceVendorsForDelete');
        selectAllDeviceVendorsForDelete.addEventListener('click', selectAllDeviceVendorsForDeleteCheckbox => {
            let allCheckboxes = document.querySelectorAll('input[name="removeDeviceVendorCheckbox"]')
            if (selectAllDeviceVendorsForDeleteCheckbox.target.checked) {
                for (var x=0; x < allCheckboxes.length; x++) {
                    allCheckboxes[x].checked = true;
                }
            } else {
                for (var x=0; x < allCheckboxes.length; x++) {
                    allCheckboxes[x].checked = false;
                }
            }
        })
    }
}

let removeDeviceVendorsFilterButton = document.querySelector('#removeDeviceVendorsFilterButton');
removeDeviceVendorsFilterButton.addEventListener('click', event => {
    let allRemoveDeviceVendorCheckboxes = document.querySelectorAll('input[name="removeDeviceVendorCheckbox"]');
    var removeAddtionalDeviceVendorsArray = [];

    for (var x=0; x < allRemoveDeviceVendorCheckboxes.length; x++) {
        if (allRemoveDeviceVendorCheckboxes[x].checked) {
            let removeDeviceVendor = allRemoveDeviceVendorCheckboxes[x].getAttribute("deviceVendor") ;
            removeAddtionalDeviceVendorsArray.push(removeDeviceVendor);
            allRemoveDeviceVendorCheckboxes[x].checked = false;
        }
    }

    if (removeAddtionalDeviceVendorsArray.length > 0) {
        removeDeviceVendors(removeAddtionalDeviceVendorsArray);
    }
})

const removeDeviceVendors = async (deviceVendors) => {
    const data = await commons.postData("/api/v1/lab/inventory/removeDeviceVendor",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         deviceVendors: deviceVendors});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getDeviceVendorTableForRemoval();
    }
}




// Create a new device
let addDevice = document.querySelector('#addDeviceButton');
addDevice.addEventListener('click', async event => {
    event.preventDefault();

    let deviceName = document.querySelector('input[id=newDeviceName]').value;
    if  (deviceName == '') {
        alert('Error: Must include a device name')
        return
    }

    let portsAdded = document.querySelector('#addPortsManuallyTextAreaId').value;
    if (portsAdded) {
        var ports = portsAdded;
    } else {
        var ports = null;
    }
    
    if (deviceType != null) {
        deviceType.trim();
    }
    if (deviceVendor != null) {
        deviceVendor.trim()
    }
    if (deviceLocation != null) {
        deviceLocation.trim()
    }

    if (deviceType  == "") {
        deviceType = null;
    }

    // inventoryAdditionalKeys: {},
    let deviceKeyValues = {domain:             document.querySelector("#inventoryAttributes").getAttribute("domain"),
                           name:               deviceName.trim(),
                           notes:              document.querySelector('input[id=newDeviceNotes]').value,
                           deviceType:         deviceType,
                           vendor:             commons.capitalizeWords(deviceVendor),
                           model:              document.querySelector('input[id=newDeviceModel]').value,
                           serialNumber:       document.querySelector('input[id=newDeviceSerialNumber]').value,
                           location:           commons.capitalizeWords(deviceLocation),
                           ipAddress:          document.querySelector('input[id=newDeviceIpAddress]').value,
                           ipPort:             document.querySelector('input[id=newDeviceIpPort]').value,
                           loginName:          document.querySelector('input[id=newDeviceLoginName]').value,
                           password:           document.querySelector('input[id=newDevicePassword]').value,
                           connectionProtocol: document.querySelector('input[name=connectProtocol]:checked').value,
                           ports:              ports,
                           inventoryAdditionalKeyValues: {}}

    // Set all invisible empty values with a "None" string so users have something to click to edit each key
    Object.keys(deviceKeyValues).forEach(key => {
        if (deviceKeyValues[key] == '') {
            deviceKeyValues[key] = 'None'
        }
    })

    const data = await commons.postData("/api/v1/lab/inventory/addDevice",  
                    {remoteController: sessionStorage.getItem("remoteController"),
                     deviceKeyValues: deviceKeyValues
                    });

    commons.getInstantMessages('labInventory');
    if (data.status == 'success') {
        commons.blinkSuccess();
        resetParams();
    }

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }
})

const unhidePortConnectionsRow = (object) => {
    /* Port-Connection table row is hidden.
    Open it when user clicks on the Device port expand icon */

    let row = Number(object.getAttribute('row'));
    let device = object.getAttribute('device');
    let table = document.querySelector("#inventoryTable");

    // These ID variables has unique row-ID defined in getDevices.
    // We need to know which table ID row to insert html dropdowns to.  
    insertPortConnectsTableId  = object.getAttribute("insertPortConnectsTableId");
    addPortsToPortGroupId      = object.getAttribute("addPortsToPortGroupId");
    removePortsFromPortGroupId = object.getAttribute("removePortsFromPortGroupId");
    connectPortsToLinkDeviceId = object.getAttribute("connectPortsToLinkDeviceId");
    addRemoveKeysId            = object.getAttribute("addRemoveKeysId");
    addPortsId                 = object.getAttribute("addPortsId");

    // The port-connection row is always the next row after the expanded device.
    // So row+1
    var portConnectionsRow = table.rows[row+1];

    if (portConnectionsRow.classList.contains("hideFromUser")) {
        portConnectionsRow.classList.remove("hideFromUser");
        getPortConnections(device);
    } else {
        portConnectionsRow.classList.add("hideFromUser");
    }
}

const getSelectedCheckboxPorts = (getCheckboxTableInputNameId) => {
    /* Helper function for getInventory() to get all the selected ports */

    let portMgmtCheckboxes = document.querySelectorAll(`input[name="portMgmtCheckboxes-${getCheckboxTableInputNameId}"]:checked`);
    let portCheckboxList = [];
    let domain = null;
    let device = null;

    for (let y=0; y < portMgmtCheckboxes.length; y++) {
        domain = portMgmtCheckboxes[y].getAttribute('domain');
        device = portMgmtCheckboxes[y].getAttribute('device');
        portCheckboxList.push(portMgmtCheckboxes[y].getAttribute('port'));
        portMgmtCheckboxes[y].checked = false;
    }

    return [device, portCheckboxList]
}

document.querySelector("#setDevicesPerPage").addEventListener('click', event => {
    devicesPerPage = event.target.innerText;
    document.querySelector("#setDevicesPerPageDropdown").innerHTML = devicesPerPage;
    getInventory();
})

const insertInventoryTable = async (inventoryTable) => {
    document.querySelector("#insertInventoryTable").innerHTML = inventoryTable;

    // Select all devices checkbox for delete
    const selectAllDevicesCheckboxes = document.querySelector('#selectAllDevicesForDelete');
    selectAllDevicesCheckboxes.addEventListener('change', selectAllDevicesCheckboxEvent => {
        var allDevicesCheckboxes = document.querySelectorAll('input[name="devices"]')

        if (selectAllDevicesCheckboxEvent.target.checked) {
            for (var x=0; x < allDevicesCheckboxes.length; x++) {
                allDevicesCheckboxes[x].checked = true;
            }
        } else {
            for (var x=0; x < allDevicesCheckboxes.length; x++) {
                allDevicesCheckboxes[x].checked = false;
            }
        }
    })
}

const getInventory = async (getPageNumberButton=null, previousNextPage=null) => {
    let pageIndexRange = [];

    if (getPageNumberButton == null) {
        // Default devices per page
        // Creating just a one item array
        if (previousNextPage === null) {
            pageIndexRange.push(`0:${devicesPerPage}`);
        } else {
            if (previousNextPage === 'incr') {
                if (getCurrentPageNumber != totalPages) {
                    startPageIndex = getCurrentPageNumber * devicesPerPage;
                    let endPageIndex = startPageIndex + devicesPerPage
                    pageIndexRange.push(`${startPageIndex}:${endPageIndex}`);
                    getCurrentPageNumber++;
                } else {
                    return
                }
            }

            if (previousNextPage === 'decr') {
                if (getCurrentPageNumber != 1) {
                    startPageIndex = startPageIndex - devicesPerPage;
                    let endPageIndex = startPageIndex + devicesPerPage
                    pageIndexRange.push(`${startPageIndex}:${endPageIndex}`);
                    getCurrentPageNumber--;
                } else {
                    return
                }
            }
        }
    } else {
        // Creating just an one-item array
        pageIndexRange.push(getPageNumberButton.getAttribute("pageIndexRange"));
        getCurrentPageNumber = getPageNumberButton.getAttribute("getCurrentPageNumber");
    }

    const splitIndexRange = pageIndexRange[0];
    const startingIndex   = Number(splitIndexRange.split(":")[0]);
    const total           = parseInt(startingIndex) + parseInt(devicesPerPage);

    // Update the global startPageIndex for previous/next button calculation
    startPageIndex = startingIndex;

    let inventoryAttributes= document.querySelector('#inventoryAttributes');
    if (inventoryAttributes) {
        let domain = inventoryAttributes.getAttribute('domain');

        const data = await commons.postData("/api/v1/lab/inventory/getDevices",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         domain: domain, 
                                         deviceTypeFilter: deviceTypeCheckboxes,
                                         deviceLocationFilter: deviceLocationCheckboxes,
                                         deviceVendorFilter: deviceVendorCheckboxes,
                                         pageIndexRange: pageIndexRange,
                                         getCurrentPageNumber: getCurrentPageNumber,
                                         devicesPerPage: Number(devicesPerPage)
                                        });

        commons.getInstantMessages('labInventory');

        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        } else {
            totalPages = data.totalPages;
            document.querySelector("#insertPagination").innerHTML = data.pagination;
            await insertInventoryTable(data.inventoryTable);

            getDeviceTypeFilterOptions();
            getDeviceTypeOptions();
            getDeviceLocationOptions();
            getDeviceLocationSelectionDropdownForEdit();
            getDeviceLocationFilterOptions();
            getDeviceVendorOptions();
            getDeviceVendorSelectionDropdownForEdit();
            getDeviceVendorFilterOptions();

            let addPortsToPortGroupTableRows            = data.addPortsToPortGroupTableRows;
            let removePortsFromPortGroupTableRows       = data.removePortsFromPortGroupTableRows;
            let connectPortsToLinkDeviceTableRows       = data.connectPortsToLinkDeviceTableRows;
            let disconnectDeviceFromLinkDeviceTableRows = data.disconnectDeviceFromLinkDeviceTableRows;
            let addRemoveKeysTableRows                  = data.addRemoveKeysTableRows;
            let refreshTableRows                        = data.refreshTableRows;
            portConnectionTableRowsJsonMapping          = data.portConnectionTableRowsJson

            document.querySelector("#previousPage").addEventListener('click', event => {
                getInventory(getPageNumberButton=null, previousNextPage='decr');
            })
            
            document.querySelector("#nextPage").addEventListener('click', event => {
                getInventory(getPageNumberButton=null, previousNextPage='incr');
            })

            // Additional inventory Fields
            for (let x=0; x < data.additionalFieldNames.length; x++) {
                let currentFieldNameObj = document.querySelectorAll(`.${data.additionalFieldNames[x]}`)

                for (let y=0; y < currentFieldNameObj.length; y++) {
                    currentFieldNameObj[y].addEventListener('click', event => {
                        event.preventDefault;
                        changeAdditionalFieldValue(event);
                    })
                }
            }

            let inventoryAddKeyForAllDevices = document.querySelectorAll('.inventoryAddKeyForAllDevices');
            for (var x=0; x < inventoryAddKeyForAllDevices.length; x++) {
                inventoryAddKeyForAllDevices[x].addEventListener('change', inventoryAddKeyForAllDevicesClassEvent => {
                    inventoryChangeKeyValueForAllDevices(inventoryAddKeyForAllDevicesClassEvent);
                })
            }

            // Create an event listener to add ports to a port-group
            for (let x=0; x < addPortsToPortGroupTableRows.length; x++) {
                let addSelectedPortsToPortGroup = document.querySelector(`#${addPortsToPortGroupTableRows[x]}`);
                if (addSelectedPortsToPortGroup) {
                    addSelectedPortsToPortGroup.addEventListener('click', event => {
                        event.preventDefault;
                        let getCheckboxTableInputNameId = addPortsToPortGroupTableRows[x].split('-')[1]
                        let selectedPortGroup = event.target.innerText;

                        if (selectedPortGroup != "Add-Ports-To-Port-Group") {
                            let value = getSelectedCheckboxPorts(getCheckboxTableInputNameId);
                            let device = value[0]
                            let portCheckboxList = value[1]
                            addPortsToPortGroup(domain, device, selectedPortGroup, portCheckboxList);
                        }
                    })
                }
            }

            for (let x=0; x < removePortsFromPortGroupTableRows.length; x++) {
                let removeSelectedPortsToPortGroup = document.querySelector(`#${removePortsFromPortGroupTableRows[x]}`);
                if (removeSelectedPortsToPortGroup) {
                    removeSelectedPortsToPortGroup.addEventListener('click', event => {
                        let selectedPortGroup = event.target.innerText;
                        let getCheckboxTableInputNameId = removePortsFromPortGroupTableRows[x].split('-')[1]

                        if (selectedPortGroup != "Remove-Ports-From-Port-Group") {
                            let value = getSelectedCheckboxPorts(getCheckboxTableInputNameId);
                            let device = value[0]
                            let portCheckboxList = value[1]
                            removePortsFromPortGroup(domain, device, selectedPortGroup, portCheckboxList);
                        }
                    })
                }
            }

            for (let x=0; x < connectPortsToLinkDeviceTableRows.length; x++) {
                let selectConnectToLinkDevice = document.querySelector(`#${connectPortsToLinkDeviceTableRows[x]}`);
                if (selectConnectToLinkDevice) {
                    selectConnectToLinkDevice.addEventListener('click', event => {
                        let toLinkDevice = event.target.innerText;
                        let getCheckboxTableInputNameId = connectPortsToLinkDeviceTableRows[x].split('-')[1]

                        if (toLinkDevice != "Connect-Ports-To-Device") {
                            let value = getSelectedCheckboxPorts(getCheckboxTableInputNameId);
                            let device = value[0]
                            let portCheckboxList = value[1]
                            connectToLinkDevice(domain, device, portCheckboxList, toLinkDevice);
                        }
                    })
                }
            }

            for (let x=0; x < disconnectDeviceFromLinkDeviceTableRows.length; x++) {
                const disconnectPortsFromLinkDevice = document.querySelector(`#${disconnectDeviceFromLinkDeviceTableRows[x]}`);
                if (disconnectPortsFromLinkDevice) {
                    disconnectPortsFromLinkDevice.addEventListener('click', async (event) => {
                        let getCheckboxTableInputNameId = disconnectDeviceFromLinkDeviceTableRows[x].split('-')[1];
                        let value = getSelectedCheckboxPorts(getCheckboxTableInputNameId);
                        let device = value[0]
                        let portCheckboxList = value[1]
                        disconnectPorts(domain, device, portCheckboxList)
                    })
                }
            }

            // Note: The querySelector ID needs to be unique with row ID.
            //          because the domain and device are not accurate to the modal
            // AddRemoveFields Modal opened
            for (let x=0; x < addRemoveKeysTableRows.length; x++) {
                const addRemoveFieldModalClick = document.querySelector(`#${addRemoveKeysTableRows[x]}`);
                if (addRemoveFieldModalClick) {
                    addRemoveFieldModalClick.addEventListener('click', event => {
                        let device = event.target.getAttribute('device');
                        if (device != null) {
                            document.querySelector("#insertDomainForFields").innerHTML = domain;
                            document.querySelector("#insertDeviceForFields").innerHTML = device;
                            getAddRemoveKeysTable(domain, device);
                        }
                    })
                }
            }

            for (let x=0; x < refreshTableRows.length; x++) {
                const refreshTable = document.querySelector(`#${refreshTableRows[x]}`);
                if (refreshTable) {
                    refreshTable.addEventListener('click', async (event) => {
                        let device = event.target.getAttribute('device');
                        getPortConnections(device)
                    })
                }
            }

        }
    }
}

const changeAdditionalFieldValue = async (event) => {
    let device = event.target.getAttribute('device');
    let domain = event.target.getAttribute('domain');
    let field = event.target.getAttribute('field');
    let value = event.target.getAttribute('value');

    const data = await commons.postData("/api/v1/lab/inventory/changeDeviceAdditionalFieldValue",  
                    {remoteController: sessionStorage.getItem("remoteController"),
                     domain:domain, device: device, field: field, value: value})

    commons.getInstantMessages('labInventory');

    if (data.status == 'success') {
        commons.blinkSuccess();
        getInventory();
    }

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }
}

const getDevicePassword = async (device) => {
    const data = await commons.postData("/api/v1/lab/inventory/getDevicePassword",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             domain: inventoryAttributes.getAttribute('domain'),
                                             device: device})

    commons.getInstantMessages('labInventory');

    if (data.status == 'success') {
        return data.password;
    }

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }
}

const editDeviceField = async (object) => {
    /* Each field is editable
       setting deviceName=$deviceName and field=$fiel
    */

    deviceName = object.getAttribute('deviceName');
    field = object.getAttribute('field');

    // Show the field name
    document.querySelector("#insertDeviceName").innerHTML = deviceName;

    if (field == "password") {
        let password = await getDevicePassword(deviceName);
        document.querySelector("#insertDevicePassword").innerHTML = `Password:&ensp; ${password}`; 
    }

    if (field == 'deviceType') {
        unhide('.editDeviceTypeSelection')
        hide('.editConnectionProtocol')
        hide('.editDeviceLocationSelection')
        hide('.editDeviceVendorSelection')
        hide('.editDeviceIpAddress')
        hide('.editDeviceIpPort')
        hide('.editDeviceLoginName')
        hide('.editDeviceLoginPassword')
        hide('.editDeviceSerialNumber')
        hide('.editDeviceModel')
        hide('.editDeviceNotes')
        document.querySelector("#editDeviceLabel").classList.add('dropdownSizeLargeExtraHeight');

    } else if (field == 'connectionProtocol') {
        unhide('.editConnectionProtocol')
        hide('.editDeviceTypeSelection')
        hide('.editDeviceLocationSelection')
        hide('.editDeviceVendorSelection')
        hide('.editDeviceIpPort')
        hide('.editDeviceLoginName')
        hide('.editDeviceLoginPassword')
        hide('.editDeviceSerialNumber')
        hide('.editDeviceModel')
        hide('.editDeviceNotes') 
        document.querySelector("#editDeviceLabel").classList.add('dropdownSizeMedium');  
  
    } else if (field == "location") {
        unhide('.editDeviceLocationSelection')
        hide('.editConnectionProtocol')
        hide('.editDeviceTypeSelection')
        hide('.editDeviceVendorSelection')
        hide('.editDeviceIpAddress')
        hide('.editDeviceIpPort')
        hide('.editDeviceLoginName')
        hide('.editDeviceLoginPassword')
        hide('.editDeviceSerialNumber')
        hide('.editDeviceModel')
        hide('.editDeviceNotes')  
        document.querySelector("#editDeviceLabel").classList.add('dropdownSizeLargeExtraHeight');  

    } else if (field == "vendor") {
        unhide('.editDeviceVendorSelection')
        hide('.editDeviceLocationSelection')
        hide('.editConnectionProtocol')
        hide('.editDeviceTypeSelection')
        hide('.editDeviceIpPort')
        hide('.editDeviceLoginName')
        hide('.editDeviceLoginPassword')
        hide('.editDeviceSerialNumber')
        hide('.editDeviceModel')
        hide('.editDeviceNotes')  
        document.querySelector("#editDeviceLabel").classList.add('dropdownSizeLargeExtraHeight');  

    } else if (field == "ipAddress") {
        unhide('.editDeviceIpAddress')
        hide('.editDeviceVendorSelection')
        hide('.editDeviceLocationSelection')
        hide('.editConnectionProtocol')
        hide('.editDeviceTypeSelection') 
        hide('.editDeviceIpPort')
        hide('.editDeviceLoginName')
        hide('.editDeviceLoginPassword')
        hide('.editDeviceSerialNumber')
        hide('.editDeviceModel')
        hide('.editDeviceNotes') 
        document.querySelector("#editDeviceLabel").classList.add('dropdownSizeMedium');   

    } else if (field == "ipPort") {
        hide('.editDeviceIpAddress')
        hide('.editDeviceVendorSelection')
        hide('.editDeviceLocationSelection')
        hide('.editConnectionProtocol')
        hide('.editDeviceTypeSelection') 
        unhide('.editDeviceIpPort')
        hide('.editDeviceLoginName')
        hide('.editDeviceLoginPassword')
        hide('.editDeviceSerialNumber')
        hide('.editDeviceModel')
        hide('.editDeviceNotes') 
        document.querySelector("#editDeviceLabel").classList.add('dropdownSizeMedium');

    } else if (field == "loginName") {
        hide('.editDeviceIpAddress')
        hide('.editDeviceVendorSelection')
        hide('.editDeviceLocationSelection')
        hide('.editConnectionProtocol')
        hide('.editDeviceTypeSelection') 
        hide('.editDeviceIpPort')
        unhide('.editDeviceLoginName')
        hide('.editDeviceLoginPassword')
        hide('.editDeviceSerialNumber')
        hide('.editDeviceModel')
        hide('.editDeviceNotes') 
        document.querySelector("#editDeviceLabel").classList.add('dropdownSizeMedium'); 

    } else if (field == "password") {
        hide('.editDeviceIpAddress')
        hide('.editDeviceVendorSelection')
        hide('.editDeviceLocationSelection')
        hide('.editConnectionProtocol')
        hide('.editDeviceTypeSelection') 
        hide('.editDeviceIpPort')
        hide('.editDeviceLoginName')
        unhide('.editDeviceLoginPassword')
        hide('.editDeviceSerialNumber')
        hide('.editDeviceModel')
        hide('.editDeviceNotes') 
        document.querySelector("#editDeviceLabel").classList.add('dropdownSizeMedium');

    } else if (field == "serialNumber") {
        hide('.editDeviceIpAddress')
        hide('.editDeviceVendorSelection')
        hide('.editDeviceLocationSelection')
        hide('.editConnectionProtocol')
        hide('.editDeviceTypeSelection') 
        hide('.editDeviceIpPort')
        hide('.editDeviceLoginName')
        hide('.editDeviceLoginPassword')
        unhide('.editDeviceSerialNumber')
        hide('.editDeviceModel')
        hide('.editDeviceNotes') 
        document.querySelector("#editDeviceLabel").classList.add('dropdownSizeMedium'); 

    } else if (field == "model") {
        hide('.editDeviceIpAddress')
        hide('.editDeviceVendorSelection')
        hide('.editDeviceLocationSelection')
        hide('.editConnectionProtocol')
        hide('.editDeviceTypeSelection') 
        hide('.editDeviceIpPort')
        hide('.editDeviceLoginName')
        hide('.editDeviceLoginPassword')
        hide('.editDeviceSerialNumber')
        unhide('.editDeviceModel')
        hide('.editDeviceNotes')  
        document.querySelector("#editDeviceLabel").classList.add('dropdownSizeMedium');

    } else if (field == "notes") {
        hide('.editDeviceIpAddress')
        hide('.editDeviceVendorSelection')
        hide('.editDeviceLocationSelection')
        hide('.editConnectionProtocol')
        hide('.editDeviceTypeSelection') 
        hide('.editDeviceIpPort')
        hide('.editDeviceLoginName')
        hide('.editDeviceLoginPassword')
        hide('.editDeviceSerialNumber')
        hide('.editDeviceModel')
        unhide('.editDeviceNotes') 
        
        let notes = object.getAttribute('currentNotes');
        document.querySelector("#editDeviceLabel").classList.add('dropdownSizeLargeExtraHeight');
        document.querySelector("#deviceNotesTextareaId").value = notes;
    }  

    // Open the edit-device modal
    document.querySelector('#editDeviceModal').style.display = 'block';

    let excludeFields = ['name', 'deviceType', 'location', 'vendor', 'connectionProtocol']
    if (excludeFields.includes(field) == false) {
        document.querySelector(`#${field}`).innerHTML = `${commons.capitalizeWords(field)}:&emsp;`;
    }   
}


// User clicked on edit button to make changes on device internal keys
let editDevice = document.querySelector("#editDeviceButton");
if (editDevice) {
    editDevice.addEventListener('click', async event => {
        event.preventDefault;
        let domain = inventoryAttributes.getAttribute('domain')

        if (field == 'deviceType') {
            var value = selectedDeviceTypeForEdit;

        } else if (field == 'location') {
            var value = selectedDeviceLocationForEdit;

        } else if (field == 'vendor') {
            var value = selectedDeviceVendorForEdit;

        } else if (field == 'ports') {
            var value = document.querySelector('#addPortsManuallyTextAreaId').value;
            document.querySelector('#addPortsManuallyTextAreaId').value = '';
        
        } else if (field == 'connectionProtocol') {
            var value = document.querySelector('input[name=connectProtocol]:checked').value;
            document.querySelector('input[name=connectProtocol]').checked = 'ssh'; 

        } else if (field == 'ipAddress') {
            var value = document.querySelector('#ipAddressInput').value;

        } else if (field == 'ipPort') {
            var value = document.querySelector('#ipPortInput').value;
        
        } else if (field == 'loginName') {
            var value = document.querySelector('#loginNameInput').value;
    
        } else if (field == 'password') {
            var value = document.querySelector('#loginPasswordInput').value;

        } else if (field == 'serialNumber') {
            var value = document.querySelector('#serialNumberInput').value;

        } else if (field == 'notes') {
            var value = document.querySelector("#deviceNotesTextareaId").value;

        } else if (field == 'model') {
            var value = document.querySelector('#modelInput').value;
        }

        const data = await commons.postData("/api/v1/lab/inventory/editDevice",  
                {remoteController: sessionStorage.getItem("remoteController"),
                 domain:domain, deviceName: deviceName, field: field, value: value}
        )

        commons.getInstantMessages('labInventory');

        if (data.status == 'success') {
            document.querySelector('#editDeviceModal').style.display = 'none';
            commons.blinkSuccess();
            document.querySelector("#insertStatus").innertHTML = `Succcessfully modified: ${field} = ${value}`;
            resetParams();
            getInventory();
        }

        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        }
    })
}

let closeEditModal = document.querySelector("#closeEditModal");
if (closeEditModal) {
    closeEditModal.addEventListener('click', event =>  {
        document.querySelector('#editDeviceModal').style.display = 'none';
        resetParams();
        document.querySelector("#editDeviceLabel").classList.remove('dropdownSizeLargeExtraHeight');
        document.querySelector("#editDeviceLabel").classList.remove('dropdownSizeMedium');
    })
}

const deleteDevices = async (devices) => {
    const data = await commons.postData("/api/v1/lab/inventory/deleteDevices",  
            {remoteController: sessionStorage.getItem("remoteController"),
             domain: inventoryAttributes.getAttribute('domain'),
             devices: devices}
    )

    commons.getInstantMessages('labInventory');

    if (data.status == 'success') {
        commons.blinkSuccess();
        getInventory();
    }

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    }
}



/* ------  Get Port Connections Table ----- */

const getPortConnections = async (device) => {
    if (device == null) {
        return
    }

    // This json mapping gets the table row ID
    let tableId = portConnectionTableRowsJsonMapping[device];
    let setCheckboxTableInputNameId = tableId.split('-')[1]
    let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");

    const data = await commons.postData("/api/v1/portMgmt/getPortConnections",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         domain: domain,
                         deviceName: device, 
                         setCheckboxTableInputNameId: setCheckboxTableInputNameId});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        return;
    }

    if (data.portConnections) {
        document.querySelector(tableId).innerHTML = data.portConnections;

        await addPortsToPortGroupDropdown();
        await removePortsFromPortGroupDropdown();
        await getConnectPortsToLinkDeviceDropdown(device);

        // The port-connections table header row
        selectAllPortsCheckboxes = document.querySelector('#selectAllPortsCheckboxes');
        if (selectAllPortsCheckboxes) {
            selectAllPortsCheckboxes.addEventListener('change', selectAllPortsCheckbox => {
                var allPortsCheckboxes = document.querySelectorAll('.selectAllPortsClassName')
                if (selectAllPortsCheckbox.target.checked) {
                    for (var x=0; x < allPortsCheckboxes.length; x++) {
                        allPortsCheckboxes[x].checked = true;
                    }
                } else {
                    for (var x=0; x < allPortsCheckboxes.length; x++) {
                        allPortsCheckboxes[x].checked = false;
                    }
                }
            })
        }

        var table = document.querySelector("#portMgmtTable");
        //var tableHeaderRow = table.rows[0];
        //let rows = table.querySelectorAll("tr");
        //let cells = rows.querySelectorAll("td");

        // Modify additional key dropdown format values: boolean and options
        var theKeyClassNameList = document.querySelectorAll(`.additionalKeys`);
        for (var x=0; x < theKeyClassNameList.length; x++) {
            theKeyClassNameList[x].addEventListener('click', classEvent => {
                modifyPortAdditionalKeyValue(classEvent);
            })
        }

        // Add Ports
        let addPortsClasses = document.querySelectorAll('.addPortsClass');
        for (var x=0; x < addPortsClasses.length; x++) {
            addPortsClasses[x].addEventListener('click', addPortsClassEvent => {
                document.querySelector("#addPortsModal").style.display = 'block';
                document.querySelector("#insertAddPortsDomain").innerHTML = addPortsClassEvent.target.getAttribute('domain');
                document.querySelector("#insertAddPortsDevice").innerHTML = addPortsClassEvent.target.getAttribute('deviceName');
            })
        }

        let removePortsClasses = document.querySelectorAll('.removePortsClass');
        for (var x=0; x < removePortsClasses.length; x++) {
            removePortsClasses[x].addEventListener('click', removePortsClassEvent => {
                removePorts(removePortsClassEvent);
            })
        }

        let remotePortClasses = document.querySelectorAll('.remotePortDropdown');
        for (var x=0; x < remotePortClasses.length; x++) {
            remotePortClasses[x].addEventListener('click', remotePortClassEvent => {
                setRemotePort(remotePortClassEvent);
            })
        }

        let multiTenantClasses = document.querySelectorAll('.multiTenantDropdown');
        for (var x=0; x < multiTenantClasses.length; x++) {
            multiTenantClasses[x].addEventListener('click', multiTenantClassEvent => {
                setMultiTenant(multiTenantClassEvent);   
            }) 
        }

        let opticModeClasses = document.querySelectorAll('.opticModeDropdown');
        for (var x=0; x < opticModeClasses.length; x++) {
            opticModeClasses[x].addEventListener('click', opticModeClassEvent => {
                setOpticMode(opticModeClassEvent);
            })
        }

        let portSpeedClasses = document.querySelectorAll('.portSpeedDropdown');
        for (var x=0; x < portSpeedClasses.length; x++) {
            portSpeedClasses[x].addEventListener('click', portSpeedClassEvent => {
                setPortSpeed(portSpeedClassEvent);
            })
        }

        let portTypeClasses = document.querySelectorAll('.portTypeDropdown');
        for (var x=0; x < portTypeClasses.length; x++) {
            portTypeClasses[x].addEventListener('click', portTypeClassEvent => {
                setPortType(portTypeClassEvent);
            })
        }

        let selectMultiTenantForAllPorts = document.querySelectorAll('.selectMultiTenantForAllPorts');
        for (var x=0; x < selectMultiTenantForAllPorts.length; x++) {
            selectMultiTenantForAllPorts[x].addEventListener('change', selectMultiTenantAllPortsClassEvent => {
                setMultiTenantForAllPorts(selectMultiTenantAllPortsClassEvent);
            })
        }

        let selectAccessVlanIdDropdownForAllPorts = document.querySelectorAll('.selectAccessVlanIdForAllPorts');
        for (var x=0; x < selectAccessVlanIdDropdownForAllPorts.length; x++) {
            selectAccessVlanIdDropdownForAllPorts[x].addEventListener('change', accessVlanIdAllPortsClassEvent => {
                setVlanIdForAllPorts(accessVlanIdAllPortsClassEvent);
            })
        }

        let opticModeForAllPorts = document.querySelectorAll('.opticModeForAllPorts');
        for (var x=0; x < opticModeForAllPorts.length; x++) {
            opticModeForAllPorts[x].addEventListener('change', opticModeForAllPortsClassEvent => {
                setOpticModeForAllPorts(opticModeForAllPortsClassEvent);
            })
        }

        let portSpeedForAllPorts = document.querySelectorAll('.portSpeedForAllPorts');
        for (var x=0; x < portSpeedForAllPorts.length; x++) {
            portSpeedForAllPorts[x].addEventListener('change', portSpeedForAllPortsClassEvent => {
                setPortSpeedForAllPorts(portSpeedForAllPortsClassEvent);
            })
        }

        let addKeyForAllPorts = document.querySelectorAll('.addKeyForAllPorts');
        for (var x=0; x < addKeyForAllPorts.length; x++) {
            addKeyForAllPorts[x].addEventListener('change', addKeyForAllPortsClassEvent => {
                setAddedKeyValueForAllPorts(addKeyForAllPortsClassEvent);
            })
        }

        let accessVlanIdClasses = document.querySelectorAll('.selectAccessVlanIdDropdown');
        for (var x=0; x < accessVlanIdClasses.length; x++) {
            accessVlanIdClasses[x].addEventListener('click', accessVlanIdClassEvent => {
                setVlanId(accessVlanIdClassEvent);
            })
        }
        
        // Will use portRow attribute to reference the input checkboxes
        let selectVlanTrunkIDsButton = document.querySelectorAll('.selectVlanTrunkIDsButton');
        for (var x=0; x < selectVlanTrunkIDsButton.length; x++) {
            selectVlanTrunkIDsButton[x].addEventListener('click', trunkVlanIdClassEvent => {
                setVlanTrunkIDs(trunkVlanIdClassEvent);
            })
        }

        return true;
    } else {
        return false;
    }
}

// ==== Inventory additional keys starts

// Inventory: User adding a new key for a device
const inventoryAddKeyButton = document.querySelector("#inventoryAddKeyButton");
if (inventoryAddKeyButton) {
    inventoryAddKeyButton.addEventListener('click', async event => {
        let domain       = document.querySelector("#inventoryAttributes").getAttribute("domain");
        let keyName      = document.querySelector("#inventoryKeyNameInput").value;
        let keyValue     = document.querySelector("#inventoryKeyValueInput").value;
        let defaultValue = document.querySelector("#inventoryDefaultKeyValueInput").value;
        let valueType    = document.querySelector("#inventoryValueType").value;

        if (keyName == "") {
            alert(`The Key name is empty!`);
            return
        }

        if (keyName.includes(" ")) {
            alert(`The Key Name cannot have spaces: ${keyName}`);
            return
        }

        if (valueType.includes('Boolean') == false && keyValue == "") {
            alert('Please provide a key value for the key name');
            return
        }

        if (valueType == "") {
            alert(`Please select a key type for the key: value-option(s) or boolean`)
            return
        }

        const data = await commons.postData("/api/v1/lab/inventory/addKey",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     domain: domain,
                                     keyName: keyName,
                                     keyValue: keyValue,
                                     defaultValue: defaultValue,
                                     valueType:  valueType});

        commons.getInstantMessages('labInventory');

        // Reset the field type dropdown option to default
        document.querySelector("#inventoryValueType").value = "";
        document.querySelector("#inventoryValueType").selectedIndex = 0;
        document.querySelector("#inventoryKeyNameInput").value = "";
        document.querySelector("#inventoryKeyValueInput").value = "";
        document.querySelector("#inventoryDefaultKeyValueInput").value = "";

        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        } else {
            commons.blinkSuccess();
            getInventoryAddRemoveKeysTable();
            getInventory();
        }    
    })
}

const modifyInventoryAdditionalKeyValue = async (event) => {
    const data = await commons.postData("/api/v1/lab/inventory/modifyAdditionalKeyValue",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: document.querySelector("#inventoryAttributes").getAttribute("domain"),
                                 device: event.target.getAttribute("device"),
                                 key:    event.target.getAttribute("additionalKey"),
                                 value:  event.target.innerText,
                                 type:   event.target.getAttribute("valueType")
                                });

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getInventory();
    }    
}

document.querySelector("#inventoryValueType").addEventListener('change', event => {
    let valueType = event.target.value;

    if (valueType.includes('Boolean')) {
        document.querySelector("#inventoryKeyValueInput").classList.add('hideFromUser');
        document.querySelector("#inventoryDefaultKeyValueInput").classList.add('hideFromUser');
    } else {
        document.querySelector("#inventoryKeyValueInput").classList.remove('hideFromUser');
        document.querySelector("#inventoryDefaultKeyValueInput").classList.remove('hideFromUser');
    }
})

document.querySelector("#inventoryAddInventoryColumn").addEventListener('click', event => {
    getInventoryAddRemoveKeysTable();
})

const getInventoryAddRemoveKeysTable = async () => {
    var domain = document.querySelector("#inventoryAttributes").getAttribute("domain");

    const data = await commons.postData("/api/v1/lab/inventory/removeKeysTable",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain})

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#inventoryInsertDomainForFields").innerHTML = domain;
        document.querySelector("#inventoryRemoveKeyTableData").innerHTML = data.removeKeyTable;

        let addNewFieldOption = document.querySelectorAll('.addFieldOptionClass');
        for (var a=0; a < addNewFieldOption.length; a++) {
            addNewFieldOption[a].addEventListener('click', event => {
                var fieldName = event.target.getAttribute('field');
                let optionValue = document.querySelector(`#${fieldName}`).value;
                addFieldOption(fieldName, optionValue)
            })
        }

        let removeFieldsOptions = document.querySelectorAll('.removeFieldOptionsClass');
        for (var a=0; a < removeFieldsOptions.length; a++) {
            removeFieldsOptions[a].addEventListener('click', event => {
                let fieldName = event.target.getAttribute('fieldName');

                let fieldOptionRemoveCheckbox = [];
                let fieldOptionRemoveCheckboxObj = document.querySelectorAll('input[name="fieldOptionRemoveCheckbox"]')
                for (var x=0; x < fieldOptionRemoveCheckboxObj.length; x++) {
                    if (fieldOptionRemoveCheckboxObj[x].checked) {
                        let option = fieldOptionRemoveCheckboxObj[x].getAttribute("option");

                        fieldOptionRemoveCheckbox.push(option)
                        fieldOptionRemoveCheckboxObj[x].checked = false;
                    }
                }

                removeFieldOptions(fieldName, fieldOptionRemoveCheckbox)
            })
        }
    }
}

// Inventory: Get user selected remove-field checkboxes
const inventoryRemoveKeysButton = document.querySelector("#inventoryRemoveKeysButton");
if (inventoryRemoveKeysButton) {
    inventoryRemoveKeysButton.addEventListener('click', event => {
        let inventoryRemoveKeyCheckboxes = [];
        let inventoryRemoveKeyCheckboxesObj = document.querySelectorAll('input[name="inventoryRemoveKeyCheckboxes"]')

        for (var x=0; x < inventoryRemoveKeyCheckboxesObj.length; x++) {
            if (inventoryRemoveKeyCheckboxesObj[x].checked) {
                let key = inventoryRemoveKeyCheckboxesObj[x].getAttribute("key");

                inventoryRemoveKeyCheckboxes.push(key)
                inventoryRemoveKeyCheckboxesObj[x].checked = false;
            }
        }

        if (inventoryRemoveKeyCheckboxes.length > 0) {
            inventoryRemoveKeys(inventoryRemoveKeyCheckboxes);
            inventoryClearRemoveKeyCheckboxes();

        } else {
            alert('Please select 1 or more keys')
        }
    })
}

const addFieldOption = async (field, option) => {
    // Add field option to the option list

    const data = await commons.postData("/api/v1/lab/inventory/addFieldOption",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     field:field, option:option})

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getInventoryAddRemoveKeysTable();
        getInventory();
    }
}

const removeFieldOptions = async (field, options) => {
    // Add field option to the option list

    const data = await commons.postData("/api/v1/lab/inventory/removeFieldOptions",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     fieldName:field, options:options})

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getInventoryAddRemoveKeysTable();
        getInventory();
    }
}

const inventoryRemoveKeys = async (keys) => {
    let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");
    const data = await commons.postData("/api/v1/lab/inventory/removeKeys",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     domain:domain, keys:keys})

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getInventoryAddRemoveKeysTable();
        getInventory();
    }
}

const closeInventoryRemoveKeyModal = document.querySelector("#closeInventoryRemoveKeysModal");
if (closeInventoryRemoveKeyModal) {
    closeInventoryRemoveKeyModal.addEventListener('click', event => {
        inventoryClearRemoveKeyCheckboxes();
    })
}

const inventoryClearRemoveKeyCheckboxes = () => {
    let inventoryRemoveKeyCheckboxesObj = document.querySelectorAll('input[name="inventoryRemoveKeyCheckboxes"]')
    for (var x=0; x < inventoryRemoveKeyCheckboxesObj.length; x++) {
        inventoryRemoveKeyCheckboxesObj[x].checked = false;
    }
}
// ==== Inventory additional keys ends


const portMgmtAddFieldOption = async (domain, device, field, option) => {
    // Add field option to the option list

    const data = await commons.postData("/api/v1/portMgmt/portConnection/addFieldOption",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     field:field, option:option})

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getAddRemoveKeysTable(domain, device) 
    }
}

const portMgmtRemoveFieldOptions = async (domain, device, field, options) => {
    // Remove port-mgmt field options

    const data = await commons.postData("/api/v1/portMgmt/portConnection/removeFieldOptions",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     fieldName:field, options:options})

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getAddRemoveKeysTable(domain, device) 
    }
}

const modifyPortAdditionalKeyValue = async (event) => {
    /* Edit dropdown types: boolean and options */
    let device = event.target.getAttribute("device");

    const data = await commons.postData("/api/v1/portMgmt/portConnection/modifyPortAdditionalKeyValue",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: document.querySelector("#inventoryAttributes").getAttribute("domain"),
                                 device: device,
                                 port:   event.target.getAttribute("port"),
                                 key:    event.target.getAttribute("additionalKey"),
                                 value:  event.target.innerText,
                                 type:   event.target.getAttribute("valueType")});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections(device);
    }
}

const editPortAdditionalField = (event) => {
    /* Edit individual port non dropdown types: string and integer */

    document.querySelector("#editPortAdditionalFieldModal").style.display = "block";
    document.querySelector("#insertEditPortAdditionalFieldDevice").innerHTML = event.getAttribute("deviceName");
    document.querySelector("#insertEditPortAdditionalFieldPort").innerHTML = event.getAttribute("port");
    document.querySelector("#insertEditPortAdditionalFieldKey").innerHTML = event.getAttribute("additionalKey");
    document.querySelector("#insertEditPortAdditionalFieldValueType").innerHTML = event.getAttribute("valueType");
}

// User is editing individual port's additional key value.
// For non dropdown types: string and integer
const editPortConnectionAdditionalKeyValue = document.querySelector("#editPortAdditionalKeyButton");
editPortConnectionAdditionalKeyValue.addEventListener('click', async event => {
        // User clicked on individual port-connection's port to edit additional-key value
        // Get the individual port details from the modal divs provided by editPortAdditionalField

        let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");
        let device = document.querySelector("#insertEditPortAdditionalFieldDevice").innerHTML;
        let port = document.querySelector("#insertEditPortAdditionalFieldPort").innerHTML;
        let key = document.querySelector("#insertEditPortAdditionalFieldKey").innerHTML;
        let value = document.querySelector("#additionalPortKeyValueInput").value;
        let valueType =  document.querySelector("#insertEditPortAdditionalFieldValueType").innerHTML;

        const data = await commons.postData("/api/v1/portMgmt/portConnection/modifyPortAdditionalKeyValue",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain,
                                 device: device,
                                 port:   port,
                                 key:    key,
                                 value:  value,
                                 type:   valueType
                                });

        commons.getInstantMessages('labInventory');
        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        } else {
            commons.blinkSuccess();
            getPortConnections(device);
        }
})

document.querySelector("#closeEditPortAdditionalFieldModal").addEventListener('click', event => {
    document.querySelector("#editPortAdditionalFieldModal").style.display = "none";
})

const getAddRemoveKeysTable = async (domain, device) => {
    /* For additonal key field management */

    const data = await commons.postData("/api/v1/portMgmt/portConnection/removeKeysTable",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain, device: device})

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#removeKeyTableData").innerHTML = data.removeKeyTable;

        let portMgmtAddNewFieldOption = document.querySelectorAll('.portMgmtAddFieldOptionClass');
        for (var a=0; a < portMgmtAddNewFieldOption.length; a++) {
            portMgmtAddNewFieldOption[a].addEventListener('click', event => {
                var fieldName = event.target.getAttribute('field');
                let optionValue = document.querySelector(`#portMgmt-${fieldName}`).value;
                portMgmtAddFieldOption(domain, device, fieldName, optionValue)
            })
        }

        let portMgmtRemoveFieldsOptions = document.querySelectorAll('.portMgmtRemoveFieldOptionsClass');
        for (var a=0; a < portMgmtRemoveFieldsOptions.length; a++) {
            portMgmtRemoveFieldsOptions[a].addEventListener('click', event => {
                let fieldName = event.target.getAttribute('fieldName');

                let portMgmtFieldOptionRemoveCheckbox = [];
                let portMgmtFieldOptionRemoveCheckboxObj = document.querySelectorAll('input[name="portMgmtFieldOptionRemoveCheckbox"]')
                for (var x=0; x < portMgmtFieldOptionRemoveCheckboxObj.length; x++) {
                    if (portMgmtFieldOptionRemoveCheckboxObj[x].checked) {
                        let option = portMgmtFieldOptionRemoveCheckboxObj[x].getAttribute("option");

                        portMgmtFieldOptionRemoveCheckbox.push(option)
                        portMgmtFieldOptionRemoveCheckboxObj[x].checked = false;
                    }
                }

                portMgmtRemoveFieldOptions(domain, device, fieldName, portMgmtFieldOptionRemoveCheckbox)
            })
        }
    }
}


// Port-Mgmt: User adding a new key for port-connections
const addKeyButton = document.querySelector("#addKeyButton");
if (addKeyButton) {
    addKeyButton.addEventListener('click', async event => {

        let domain       = document.querySelector("#insertDomainForFields").innerHTML;
        let device       = document.querySelector("#insertDeviceForFields").innerHTML;
        let keyName      = document.querySelector("#portMgmtKeyNameInput").value;
        let keyValue     = document.querySelector("#portMgmtKeyValueInput").value;
        let defaultValue = document.querySelector("#portMgmtDefaultKeyValueInput").value;
        let valueType    = document.querySelector("#portMgmtValueType").value;

        if (keyName == "") {
            alert(`The Key name is empty`);
            return
        }

        if (keyName.includes(" ")) {
            alert(`The Key Name cannot have spaces: ${keyName}`);
            return
        }

        if (valueType.includes('Boolean') == false && keyValue == "") {
            alert('Please provide a key value for the key name');
            return
        }

        if (valueType == "") {
            alert(`Please select a key type for the key: string, integer, boolean`)
            return
        }

        const data = await commons.postData("/api/v1/portMgmt/portConnection/addKey",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     domain: domain,
                                     device: device,
                                     keyName: keyName,
                                     keyValue: keyValue,
                                     defaultValue: defaultValue,
                                     valueType:  valueType});

        commons.getInstantMessages('labInventory');
        
        // Reset the field type dropdown option to default
        document.querySelector("#portMgmtValueType").value = "";
        document.querySelector("#portMgmtValueType").selectedIndex = 0;
        document.querySelector("#portMgmtKeyNameInput").value = ""
        document.querySelector("#portMgmtKeyValueInput").value = "";
        document.querySelector("#portMgmtDefaultKeyValueInput").value = "";

        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        } else {
            commons.blinkSuccess();
            getAddRemoveKeysTable(domain, device);
            getPortConnections(device);
        }    
    })
}

// Port-Mgmt: Get user selected remove-field checkboxes
const removeKeysButton = document.querySelector("#removeKeysButton");
if (removeKeysButton) {
    removeKeysButton.addEventListener('click', event => {
        let removeKeyCheckboxes = [];
        let removeKeyCheckboxesObj = document.querySelectorAll('input[name="removeKeyCheckboxes"]')
        let domain = null;
        let device = null;

        for (var x=0; x < removeKeyCheckboxesObj.length; x++) {
            if (removeKeyCheckboxesObj[x].checked) {
                domain = removeKeyCheckboxesObj[x].getAttribute("domain") ;
                device = removeKeyCheckboxesObj[x].getAttribute("device");
                let key = removeKeyCheckboxesObj[x].getAttribute("key");

                removeKeyCheckboxes.push([domain, device, key])
                removeKeyCheckboxesObj[x].checked = false;
            }
        }

        if (removeKeyCheckboxes.length > 0) {
            removeKeys(domain, device, removeKeyCheckboxes);
            clearRemoveKeyCheckboxes();

        } else {
            alert('Please select 1 or more keys')
        }
    })
}

const removeKeys = async (domain, device, keys) => {
    const data = await commons.postData("/api/v1/portMgmt/portConnection/removeKeys",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     domain:domain, device:device, keys:keys})

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        getAddRemoveKeysTable(domain, device);
        getPortConnections(device);
    }
}

const clearRemoveKeyCheckboxes = () => {
    let removeKeyCheckboxesObj = document.querySelectorAll('input[name="removeKeyCheckboxes"]')
    for (var x=0; x < removeKeyCheckboxesObj.length; x++) {
        removeKeyCheckboxesObj[x].checked = false;
    }
}

const closeRemoveKeyModal = document.querySelector("#closeRemoveKeysModal");
if (closeRemoveKeyModal) {
    closeRemoveKeyModal.addEventListener('click', event => {
        clearRemoveKeyCheckboxes();
    })
}

const setRemotePort = async (event) => {
    /* cellValue: ${event.target.innerHTML}
       port: event.target.getAttribute("port")
    */
    if (event.target.getAttribute("srcPort") === null) {
        return
    }

    let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");
    let srcDevice = event.target.getAttribute("srcDevice");

    const data = await commons.postData("/api/v1/portMgmt/setRemotePortConnection",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain,
                                 srcDevice: srcDevice,
                                 srcPort: event.target.getAttribute("srcPort"),
                                 remoteDevice: event.target.getAttribute("remoteDevice"),
                                 remotePort: event.target.innerHTML});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections(srcDevice);
    }
}

const setMultiTenantForAllPorts = async (event) => {
    /* Uses <select> */
    let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");
    let device = event.target.getAttribute('device');
    let multiTenantValue = event.target.value;

    const data = await commons.postData("/api/v1/portMgmt/setPortMultiTenant",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain,
                                 device: device,
                                 port: 'all',
                                 multiTenantSelection: multiTenantValue});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections(device);
    }
}

const setMultiTenant = async (event) => {
    /* Uses BS Dropdown */

    if (event.target.getAttribute("port") === null) {
        return
    }

    let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");
    let device = event.target.getAttribute("device");

    const data = await commons.postData("/api/v1/portMgmt/setPortMultiTenant",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain,
                                 device: device,
                                 port: event.target.getAttribute("port"),
                                 multiTenantSelection: event.target.innerHTML});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections(device);
    }
}

const setOpticModeForAllPorts = async (event) => {
    /* Uses <select> */

    let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");
    let device = event.target.getAttribute('device');
    let opticMode = event.target.value;

    const data = await commons.postData("/api/v1/portMgmt/setOpticMode",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain,
                                 device: device,
                                 port: 'all',
                                 opticMode: opticMode});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections(device);
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

    let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");
    let device = event.target.getAttribute("device");

    const data = await commons.postData("/api/v1/portMgmt/setOpticMode",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain,
                                 device: device,
                                 port: event.target.getAttribute("port"),
                                 opticMode: event.target.innerHTML});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections(device);
    }
}

const setPortSpeedForAllPorts = async (event) => {
    /* Uses <select> */

    let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");
    let device = event.target.getAttribute('device');
    let speed = event.target.value;

    const data = await commons.postData("/api/v1/portMgmt/setPortSpeed",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain,
                                 device: device,
                                 port: 'all',
                                 speed: speed});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections(device);
    }
}

const setAddedKeyValueForAllPorts = async (event) => {
    /* Uses <select> */

    let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");
    let device = event.target.getAttribute('device');
    let field = event.target.getAttribute('field');
    let type = event.target.getAttribute('type');
    let value = event.target.value;

    const data = await commons.postData("/api/v1/portMgmt/portConnection/modifyPortAdditionalKeyValue",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain,
                                 device: device,
                                 port: 'all',
                                 key: field,
                                 type: type,
                                 value: value});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections(device);
    }
}

const inventoryChangeKeyValueForAllDevices = async (event) => {
    /* Uses <select> */

    let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");
    let field = event.target.getAttribute('field');
    let value = event.target.value;

    const data = await commons.postData("/api/v1/lab/inventory/changeDeviceAdditionalFieldValue",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain,
                                 device: 'all',
                                 field: field,
                                 value: value});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getInventory();
    }
}

const setPortSpeed = async (event) => {
    /* cellValue: ${event.target.innerHTML
       port: event.target.getAttribute("port")
       portSpeed:  event.target.innerHTML
    */

    if (event.target.getAttribute("port") === null) {
        return
    }

    let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");
    let device = event.target.getAttribute("device");

    const data = await commons.postData("/api/v1/portMgmt/setPortSpeed",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain,
                                 device: device,
                                 port: event.target.getAttribute("port"),
                                 speed: event.target.innerHTML});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections(device);
    }
}

const setPortType = async (event) => {
    /* cellValue: ${event.target.innerHTML
       port: event.target.getAttribute("port")
       portType:  event.target.innerHTML
    */

    let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");
    let device = event.target.getAttribute("device");

    const data = await commons.postData("/api/v1/portMgmt/setPortType",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain,
                                 device: device,
                                 port: event.target.getAttribute("port"),
                                 portType: event.target.innerHTML});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections(device);
    }
}

const setVlanIdForAllPorts = async (event) => {
    /* Uses <select class="selectAccessVlanIdDropdownForAllPorts mainTextColor" device="{deviceName}"> */

    let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");
    let device = event.target.getAttribute('device');
    let vlanIdList = [event.target.value];

    const data = await commons.postData("/api/v1/portMgmt/setVlanId",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain,
                                 device: device,
                                 port: 'allPorts',
                                 vlanIdList: vlanIdList});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections(device);
    }
}

const setVlanId = async (event) => {
    /* cellValue: ${event.target.innerHTML
       port: event.target.getAttribute("port")
       vlanId:  event.target.innerHTML
    */

    let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");
    let device = event.target.getAttribute("device");
    let vlanIdList = [event.target.innerHTML];

    const data = await commons.postData("/api/v1/portMgmt/setVlanId",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain,
                                 device: device,
                                 port: event.target.getAttribute("port"),
                                 vlanIdList: vlanIdList});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections(device);
    }
}

const setVlanTrunkIDs = async (event) => {
    /* cellValue: ${event.target.innerHTML
       port: event.target.getAttribute("port")
       vlanId:  event.target.innerHTML
    */

    let domain = document.querySelector("#inventoryAttributes").getAttribute("domain");
    let device = event.target.getAttribute('device');
    let port   = event.target.getAttribute("port")
    let portRowNumber = event.target.getAttribute('portRow');
    let vlanIdList = [];

    let vlanTrunkIdCheckboxes = document.querySelectorAll(`input[name="selectVlanTrunkIdCheckboxes-${portRowNumber}"]`);
    for (var x=0; x < vlanTrunkIdCheckboxes.length; x++) {
        if (vlanTrunkIdCheckboxes[x].checked) {
            vlanIdList.push(vlanTrunkIdCheckboxes[x].getAttribute('vlanId'))
        };
    }

    if (vlanIdList.length == 0) {
        alert('Please select a minimum of one Vlan ID')
        return
    }

    const data = await commons.postData("/api/v1/portMgmt/setVlanId",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 domain: domain,
                                 device: device,
                                 port: port,
                                 vlanIdList: vlanIdList});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections(device);
    }
}

const testConnection = async () => {
    let deviceAttributes = document.querySelector('#deviceAttributes');
    let device = deviceAttributes.getAttribute('profile');
    let ipAddress = deviceAttributes.getAttribute('ipAddress');
    let ipPort = deviceAttributes.getAttribute('ipPort');

    const data = await commons.postData("/api/v1/portMgmt/testConnection",  
                                {remoteController: sessionStorage.getItem("remoteController"),
                                 device: device, ipAddress: ipAddress, ipPort: ipPort});

    /*
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        document.querySelector("#insertProfileStatus").innerHTML = data.html;
    } else {
        document.querySelector("#insertProfileStatus").innerHTML = data.html;
    }
    */
}

 let addPortsButton = document.querySelector("#addPortsButton");
 addPortsButton.addEventListener('click', event => {
    let domain = document.querySelector("#insertAddPortsDomain").innerHTML;
    let device = document.querySelector("#insertAddPortsDevice").innerHTML;
    let ports = document.querySelector("#addPortsTextAreaId").value;
    addPorts(domain, device, ports)
 })

 document.querySelector("#addPortsCloseModalButton").addEventListener('click', event => {
    document.querySelector("#addPortsModal").style.display = "none";
    document.querySelector("#addPortsTextAreaId").value = '';
})

const addPorts = async (domain, device, ports) => {
    const data = await commons.postData("/api/v1/lab/inventory/addPorts",  
                            {remoteController: sessionStorage.getItem("remoteController"),
                             domain: domain, device: device, ports: ports});

    commons.getInstantMessages('labInventory');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        getPortConnections(device);
        getInventory();
    }
}

const removePorts = async (event) => {
    let domain = event.target.getAttribute('domain');
    let device = event.target.getAttribute('device');
    let selectedCheckboxes = [];
    let portCheckboxes = document.querySelectorAll('.selectAllPortsClassName');

    for (var x=0; x < portCheckboxes.length; x++) {
        if (portCheckboxes[x].checked) {
            let port = portCheckboxes[x].getAttribute('port');
            selectedCheckboxes.push(port)
            portCheckboxes[x].checked = false;
        }
    }

    if (selectedCheckboxes.length > 0) {
        const data = await commons.postData("/api/v1/lab/inventory/removePorts",  
                            {remoteController: sessionStorage.getItem("remoteController"),
                            domain: domain, device: device, ports: selectedCheckboxes});

        commons.getInstantMessages('labInventory');

        if (data.status == 'failed') {
            document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
        } else {
            commons.blinkSuccess();
            getPortConnections(device);
            getInventory();
        }
    }
}

const addPortsToPortGroupDropdown = async () => {
    // Adding ports to a port-group: PortGroup dropdown options for ports
    let domain = document.querySelector("#pageAttributes").getAttribute('domain');

    const data = await commons.postData("/api/v1/portMgmt/selectPortGroupToAddPorts",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         domain: domain});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector(`${addPortsToPortGroupId}`).innerHTML = data.portGroupOptions;
    }
}

const addPortsToPortGroup = async (domain, device, portGroup, portList) => {
    if (portList.length == 0) {
        // In case the user clicks on the dropdown without selecting ports
        return
    }

    const data = await commons.postData("/api/v1/portMgmt/addPortsToPortGroup",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         domain: domain, device: device, portGroup: portGroup, ports: portList});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        uncheckAllPorts();
        commons.blinkSuccess();
        getPortConnections(device);
    }
}

const removePortsFromPortGroupDropdown = async () => {
    // Remove ports from a port-group: PortGroup dropdown options for ports.
    let domain = document.querySelector("#pageAttributes").getAttribute('domain');
    const data = await commons.postData("/api/v1/portMgmt/selectPortGroupToRemovePorts",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         domain: domain});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector(`${removePortsFromPortGroupId}`).innerHTML = data.portGroupOptions;
    }
}

const removePortsFromPortGroup = async (domain, device, portGroup, portList) => {
    // portList format: portGroup:port
    if (portList.length == 0) {
        // In case the user clicks on the dropdown without selecting ports
        return
    }

    const data = await commons.postData("/api/v1/portMgmt/removePortsFromPortGroup",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         domain: domain, device: device, portGroup: portGroup, ports: portList});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        uncheckAllPorts();
        getPortConnections(device);
    }
}

const getConnectPortsToLinkDeviceDropdown = async (device) => {
    /* Get a dropdown menu of link switches.
       When user selects a link switch, there is an event 
       listener to get all the ports to select as out-ports.
    */
    const data = await commons.postData("/api/v1/portMgmt/getConnectPortsToLinkDeviceDropdown",  
                           {remoteController: sessionStorage.getItem("remoteController")});
   
    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector(`${connectPortsToLinkDeviceId}`).innerHTML = data.linkDevicesHtml;
    }
}

const connectToLinkDevice = async (domain, fromLinkDevice, fromPorts, toLinkDevice) => {
    const data = await commons.postData("/api/v1/portMgmt/connectToLinkDevice",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         domain: domain,
                         fromLinkDevice: fromLinkDevice,
                         ports: fromPorts,
                         toLinkDevice: toLinkDevice, 
                         });

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        uncheckAllPorts();
        getPortConnections(fromLinkDevice);
    }
}

const disconnectPorts = async (domain, device, selectedPorts) => {
    const data = await commons.postData("/api/v1/portMgmt/disconnectPorts",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         domain: domain,
                         device: device,
                         ports: selectedPorts});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        uncheckAllPorts();
        getPortConnections(device); 
    }   
}

const getSelectedDevices = () => {
    let devicesArray = [];
    let deviceCheckboxes = document.querySelectorAll('input[name="devices"]')

    for (var x=0; x < deviceCheckboxes.length; x++) {
        if (deviceCheckboxes[x].checked) {
            //let domain = deviceCheckboxes[x].getAttribute('domain');
            let deviceName = deviceCheckboxes[x].getAttribute('deviceName');
            devicesArray.push(deviceName)
            deviceCheckboxes[x].checked = false;
        }
    }

    if (devicesArray.length > 0) {
        document.querySelector('#selectAllDevicesForDelete').checked = false;
    }

    return devicesArray
}

const getSelectedDevicesAddToEnv = () => {
    /* For add-devices-to-env only */

    let devicesArray = [];
    let deviceCheckboxes = document.querySelectorAll('input[name="addSelectedDevicesToEnv"]')

    for (var x=0; x < deviceCheckboxes.length; x++) {
        if (deviceCheckboxes[x].checked) {
            let deviceName = deviceCheckboxes[x].getAttribute('deviceName');
            devicesArray.push(deviceName)
            deviceCheckboxes[x].checked = false;
        }
    }

    return devicesArray
}

document.querySelector("#addDevicesToEnv").addEventListener("click", event => {
    /* A topbar link to open a modal to add devices to Envs */

    getDomainEnvsDropdownMenu();
    getDeviceNames();
    document.querySelector("#addDevicesToEnvModal").style.display = 'block';
})

const getDomainEnvsDropdownMenu = async () => {
    /*
       - Create a new RestAPI to take in the selected devices and put them into the  env yml file
       - Update the yml file in the modal at real-time
       - The modal to split view in half: Show device checkboxes for user to remove
    */
    let domain = document.querySelector("#pageAttributes").getAttribute('domain');

    const data = await commons.postData("/api/v1/lab/inventory/getDomainEnvsDropdownMenu",  
                                          {remoteController: sessionStorage.getItem("remoteController"),
                                           domain: domain});

    commons.getInstantMessages('labInventory');

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#modifyEnvStatus").innerHTML = '';
        document.querySelector("#insertSelectEnv").innerHTML = data.envsDropdown;

        // EVENT LISTERNER: User selects an env
        let selectedEnvForAddingDevices = document.querySelector("#selectedEnvForAddingDevices");
        selectedEnvForAddingDevices.addEventListener("click", event => {
            // User selected an env from the dropdown menu in Add-Devices-To-Env link

            addDevicesToSelectedEnvFullPath = event.target.getAttribute("envFullPath");
            document.querySelector("#insertEnvForInventory").innerHTML = addDevicesToSelectedEnvFullPath;
            getFileContents(addDevicesToSelectedEnvFullPath);

            // Show devices from the curernt domain
            document.querySelector("#modifyEnvFileButton").classList.remove('hideFromUser');
            document.querySelector("#insertEnvContents").classList.remove('hideFromUser');
            document.querySelector("#addDevicesToEnvButton").classList.remove('hideFromUser');
        })
    }   
}

const getDeviceNames = async () => {
    /* Get a dropdown list of devices names for users to add to Envs */

    let domain = document.querySelector("#pageAttributes").getAttribute('domain');
    const data = await commons.postData("/api/v1/lab/inventory/getDeviceNames",  
                                         {remoteController: sessionStorage.getItem("remoteController"),
                                          domain: domain});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector("#insertDeviceNames").innerHTML = data.deviceNames;
    }
}

document.querySelector("#addDevicesToEnvButton").addEventListener('click', event => {
    // Get the selected Env
    let selectedDevices = getSelectedDevicesAddToEnv();
    if (selectedDevices.length == 0) {
        alert('Please select 1 or more devices first')
        return
    }

    addDevicesToEnv(selectedDevices);
})

const addDevicesToEnv = async (devices) => {
    /* User modified the Env Yaml file. Update the Env Yaml file. */
    document.querySelector("#addDevicesToEnvStatus").innerHTML = ''; 
    document.querySelector("#modifyEnvStatus").innerHTML = '';
    let domain = document.querySelector("#pageAttributes").getAttribute('domain');
    const data = await commons.postData("/api/v1/env/update",  
                        {remoteController: sessionStorage.getItem("remoteController"),
                         domain: domain,
                         envFullPath: addDevicesToSelectedEnvFullPath,
                         devices: devices});

    commons.getInstantMessages('labInventory');
    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        commons.blinkSuccess();
        let status = `<div class="textGreen">Successfully added devices to Env file</div>`;
        document.querySelector("#modifyEnvStatus").innerHTML = status;
        getFileContents(addDevicesToSelectedEnvFullPath);
    }   
}

const getFileContents = async (filePath) => {
    try {
        // getFileContents calls sidebar/views
        const data = await commons.postData("/api/v1/fileMgmt/getFileContents",  
                                        {remoteController: sessionStorage.getItem("remoteController"),
                                         filePath: filePath})

        document.querySelector("#insertEnvContents").innerHTML = `<textarea id="textareaId" name="${data.fullPath}" cols="75" rows="27">${data.fileContents}</textarea>`;
        
    } catch (error) {
        console.error(`Envs getFileContents: ${error.message}`);
    }
    commons.getInstantMessages('labInventory');	  
}

document.querySelector("#modifyEnvFileButton").addEventListener("click", event => {
    /* User modified the env file in add-devices-to-env.
       modifyFile() will query for textAreaId.value
    */
    document.querySelector("#addDevicesToEnvStatus").innerHTML = ''; 
    document.querySelector("#modifyEnvStatus").innerHTML = ''; 
    commons.modifyFile();
})

document.querySelector("#closeAddDevicesToEnvModal").addEventListener("click", event => {
    document.querySelector("#addDevicesToEnvModal").style.display = "none";
    document.querySelector("#modifyEnvStatus").innerHTML = '';
    document.querySelector("#insertEnvForInventory").innerHTML = '';
    document.querySelector("#insertEnvContents").innerHTML = '';

    document.querySelector("#insertEnvContents").classList.add('hideFromUser');
    document.querySelector("#modifyEnvFileButton").classList.add('hideFromUser');
    document.querySelector("#addDevicesToEnvButton").classList.add('hideFromUser');
    let newEnv = document.querySelector("#newEnvForAddDevicesToEnv").value = '';
    let envGroup = document.querySelector("#envGroupForAddDevicesToEnv").value = '';
    document.querySelector("#addDevicesToEnvStatus").innerHTML = ''; 
})

document.querySelector("#inventoryCreateEnvButton").addEventListener("click", async event => {
    try {
        let domain = document.querySelector("#pageAttributes").getAttribute('domain');
        let newEnv = document.querySelector("#newEnvForAddDevicesToEnv").value;
        let envGroup = document.querySelector("#envGroupForAddDevicesToEnv").value;
        let textArea = '';

        const data = await commons.postData("/api/v1/env/create",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             textArea: textArea, 
                                             newEnv: newEnv, 
                                             envGroup: envGroup,
                                             domain: `DOMAIN=${domain}`})

        commons.getInstantMessages('envs');

        if (data.status == "success") {
            getDomainEnvsDropdownMenu();
            let status = `<div class="textGreen">Successfully created Env: ${newEnv}</div>`;
            document.querySelector("#addDevicesToEnvStatus").innerHTML = status;
        } else {
            let status = `<div class="textRed">Failed: ${data.errorMsg}</div>`
            document.querySelector("#addDevicesToEnvStatus").innerHTML = status;           
        }
    } catch (error) {  
        console.error(`inventory:createEnv: ${error}`);
    }

    document.querySelector("#newEnvForAddDevicesToEnv").value = '';
    document.querySelector("#envGroupForAddDevicesToEnv").value = '';
})

const resetParams = () => {
    /* Add new device form */
    document.querySelector('input[id=newDeviceName]').value = '';
    document.querySelector('input[id=newDeviceModel]').value = '';
    document.querySelector('input[id=newDeviceIpAddress]').value = '';
    document.querySelector('input[id=newDeviceIpPort]').value = '';
    document.querySelector('input[id=newDeviceLoginName]').value = '';
    document.querySelector('input[id=newDevicePassword]').value = '';
    document.querySelector('input[name=connectProtocol][id=newDeviceIpSSHProtocol]').checked = 'ssh'; 
    document.querySelector('#addPortsManuallyTextAreaId').value = ''; 

    deviceName = null;
    field = null;
    document.querySelector("#insertDeviceName").innerHTML = '';
    document.querySelector("#insertSelectedDeviceLocationForEdit").innerHTML = '';
    document.querySelector("#insertSelectedDeviceTypeForEdit").innerHTML = '';
    document.querySelector("#insertSelectedDeviceVendorForEdit").innerHTML = '';
    document.querySelector("#insertSelectedDeviceType").innerHTML = '';
    document.querySelector("#insertSelectedLocation").innerHTML = '';
    document.querySelector("#insertSelectedVendor").innerHTML = '';
    document.querySelector("#insertDevicePassword").innerHTML = '';

    document.querySelector("#deviceNotesTextareaId").value = '';
    document.querySelector('#ipAddressInput').value = '';
    document.querySelector('#ipPortInput').value = '';
    document.querySelector('#modelInput').value = '';
    document.querySelector('#serialNumberInput').value = '';
    document.querySelector('#loginNameInput').value = '';
    document.querySelector('#loginPasswordInput').value = '';
}

window.getInventory = getInventory;
window.editDeviceField = editDeviceField;
window.unhidePortConnectionsRow = unhidePortConnectionsRow;
window.addPortsToPortGroupDropdown =  addPortsToPortGroupDropdown;
window.removePortsFromPortGroupDropdown =  removePortsFromPortGroupDropdown;
window.editPortAdditionalField = editPortAdditionalField;
window.modifyFile = commons.modifyFile;



