import * as commons from './commons.js';

// Default to get last 31 days of usage for all envs
var selectedEnvList = new Array();
var days = 31;
var barChartObj = null;

document.addEventListener("DOMContentLoaded", function() {
    showEnvUsage({userSelectedDays:days, getUtilization:true});
    commons.getServerTime();
});

const collectSelectedEnvs = () => {
    // Collect all the selected checkboxes and close the dropdown menu
    var checkboxArray = document.querySelectorAll('input[name=envCheckboxes]:checked');
    selectedEnvList = [];

    for (let x=0; x < checkboxArray.length; x++) {
        let env = checkboxArray[x].getAttribute('value');
        selectedEnvList.push(env);
    }

    if (selectedEnvList.indexOf('allEnvs') >= 0) {
        selectedEnvList = ['allEnvs'];
    }

    if (selectedEnvList.length == 0) {
        selectedEnvList = ['allEnvs'];
    }
}

const clearEnvSelections = () => {
    const envSelections = document.getElementsByName('envCheckboxes');
    envSelections.forEach(checkbox => {
        checkbox.checked = false;
    })
}

// Don't close the dropdown-menu when clicking inside
document.querySelector('#envDropdownMenu').addEventListener('click', function(event) {
    event.stopPropagation();
})

// Reset the selectedEnvList if user clicks on the dropdown menu
document.querySelector('#getEnvSelections').addEventListener('change', function(event) {
    var selectedEnvList = [];
    clearEnvSelections();
})

const closeEnvDropdown = () => {
    document.querySelector('#getEnvSelections').click();
}

const go = (object=null) => {
    /* User clicked on "get utilization" or showEnvUsage */
    showEnvUsage({userSelectedDays:object, getUtilization:true});
}

/* I left off here. object is not working */
//const showEnvUsage = async (object=null, getUtilization=false) => {
async function showEnvUsage({userSelectedDays=null, getUtilization=true}) {
    if (userSelectedDays) {
        // Default days=31
        days = userSelectedDays;
    }

    collectSelectedEnvs();
    document.querySelector("#insertDays").innerHTML = `Last ${days} days`;

    if (getUtilization) {
        let userPieCharts = document.querySelectorAll('.userPieChartClass');
        userPieCharts.forEach(divClass => {
            if (divClass) {
                divClass.remove();
            }
        });

        const envData = await commons.postData("/api/v1/utilization/envsBarChart",  
                                                {remoteController: sessionStorage.getItem("remoteController"),
                                                 selectedEnvs: selectedEnvList, 
                                                 lastNumberOfDays: days});

        if (envData.envs == "") {
            document.querySelector('#barChart').innerHTML = `Envs were not used in the last ${days} days`;
        } else {
            //var xValues = ["Italy", "France", "Spain", "USA", "Argentina"];
            //var yValues = [55, 49, 44, 24, 15];
            //var barColors = ["red", "green","blue","orange","brown"];

            // show:  
            let barChartDiv = document.querySelector("#barChart");
            barChartDiv.style.display = "block";

            // Hide
            let userChartDiv = document.querySelector("#userChart");
            userChartDiv.style.display = "none";

            if (barChartObj == null) {
                barChartObj = new Chart("barChart", {
                    type: "bar",
                    data: {
                        labels: envData.envs,
                        datasets: [{backgroundColor: envData.colors, data: envData.trackUtilization}]
                    },
                    options: {
                        title: {
                        display: true,
                        text: "ENVs"
                        },
                        legend: {
                        display: false
                        },
                        scales: {
                        yAxes: [{ticks: {beginAtZero:true}}]
                        }
                    }
                })
            } else {
                barChartObj.clear();
                barChartObj.data.datasets = [{backgroundColor: envData.colors, data: envData.trackUtilization}];
                barChartObj.data.labels = envData.envs;
                barChartObj.update();
            }
        }
    }
}

const showUserUsage = async (object=null) => {
    /* dropdown menu selection will call this function */
    // {'timestamp': datetime.datetime(2022, 11, 19, 16, 15, 48, 425000), 
    //  'meta': {'env': 'pythonSample', 'user': 'Hubert Gee'}}
    if (object) {
        userDefinedDays = object.getAttribute("value");
        if (userDefinedDays == 'today') {
            days = 1;
        } else if (userDefinedDays == 'yesterday') {
            days = 2;
        } else {
            days = userDefinedDays;
        }
    }

    // Clear everything
    let userPieCharts = document.querySelectorAll('.userPieChartClass');
    userPieCharts.forEach(divClass => {
        divClass.remove();
    });

    let barChartDiv = document.querySelector('#barChart');
    barChart.innerHTML = "";
    if (typeof(barChartDiv) != "undefined"  && barChartDiv != 'null') {
        if (barChartDiv) {
            // Hide
            barChartDiv.style.display = "none";
        }
    }

    collectSelectedEnvs();

    const envData = await commons.postData("/api/v1/utilization/usersBarChart",  
                                            {remoteController: sessionStorage.getItem("remoteController"),
                                             selectedEnvs: selectedEnvList,
                                             lastNumberOfDays: days});

    if (envData.envs == "") {
        document.querySelector('#userChart').innerHTML = `Envs were not used in the last ${days} days`;  
    } else {
        var userChartDiv = document.querySelector("#userChart");

        // Create a new div for each env and put the pie chart in the new divs
        envData.envs.forEach(env => {
            /* 
            envs: [['loadcoreSample', [['Hubert Gee', 2, 'darkorange'], ['hgee', 43, 'darkred']]], ['pythonSample', [['Hubert Gee', 1, 'darkorchid'], ['hgee', 77, 'darkslategray']]], ['hubert', [['Hubert Gee', 3, 'darkturquoise'], ['hgee', 50, 'blue']]], ['global', [['Hubert Gee', 1, 'red']]]]
            */

            var newDiv = document.createElement("canvas");
            newDiv.className = 'userPieChartClass';
            newDiv.id = env[0];
            newDiv.style = "width:1300px; height:300px; margin-bottom:50px;";

            let currentEnvUsers = new Array();
            let currentEnvUserCounter = new Array();
            let currentEnvUserColor = new Array();

            env[1].forEach(user => {
                currentEnvUsers.push(user[0]);
                currentEnvUserCounter.push(user[1]);
                currentEnvUserColor.push(user[2]);
            })

            userChartDiv.parentNode.appendChild(newDiv, userChartDiv.nextSibling);

            let userChartObj = new Chart(newDiv, {
                type: "bar",
                data: {
                labels: currentEnvUsers,
                datasets: [{backgroundColor: currentEnvUserColor, data: currentEnvUserCounter}]
                },
                options: {
                    responsive: false,
                    maintainAspectRatio: true,
                    title: {
                        display: true,
                        text: `ENV: ${env[0]}`
                    },
                    legend: {
                        display: false
                    },
                    scales: {
                        yAxes: [{ticks: {beginAtZero:true}}]
                    }
                }
            });
        })
    }
}

const showUserTimestamp = async (object=null) => {
    /* dropdown menu selection will call this function */
    // {'timestamp': datetime.datetime(2022, 11, 19, 16, 15, 48, 425000), 
    //  'meta': {'env': 'pythonSample', 'user': 'Hubert Gee'}}
    if (object == null) {
        if (days == null) {
            days = 7;
        }

        selectedEnvList = ['allEnvs']
    } else {
        days = object.getAttribute("value");
        if (days == 'today') {
            days = 1
        }

        if (days == 'yesterday') {
            days = 2
        }
    }

    // Clear everything
    document.querySelector('#barChart').innerHTML = '';
    collectSelectedEnvs();

    const envData = await commons.postData("/api/v1/utilization/envsBarChart",  
                                            {selectedEnvs:selectedEnvList, lastNumberOfDays:days});

    if (envData.envBarChartList == "") {
        document.querySelector('#userUsageTimestamps').innerHTML = `Envs were not used in the last ${days} days`;  
    } else {
        // user pie chart
        document.querySelector("#userUsageTimestamps").innerHTML = envData.userUsageTimestamps;
    }
}

window.clearEnvSelections = clearEnvSelections;
window.closeEnvDropdown = closeEnvDropdown;
window.go = go;
window.showUserUsage = showUserUsage;
window.showEnvUsage = showEnvUsage;







