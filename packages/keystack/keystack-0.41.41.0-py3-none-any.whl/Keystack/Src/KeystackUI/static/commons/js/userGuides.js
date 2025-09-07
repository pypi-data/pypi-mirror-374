import * as commons from './commons.js';

document.addEventListener("DOMContentLoaded", function() {
    commons.getServerTime();
    getUserGuideMenu();
})

const getUserGuideMenu = async () => {
    // For sidebar menu
    const data = await commons.postData("/api/v1/userGuides/getMenu",  
                                    {remoteController: sessionStorage.getItem("remoteController")});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertUserGuides').innerHTML = data.userGuidesMenu;

        /* Loop through all dropdown buttons to toggle between hiding and showing its dropdown content - 
        This allows the user to have multiple dropdowns without any conflict */
        var dropdown = document.getElementsByClassName("dropdown-btn");
        for (var i = 0; i < dropdown.length; i++) {
            dropdown[i].addEventListener("click", function() {
                this.classList.toggle("active");
                var dropdownContent = this.nextElementSibling;
                if (dropdownContent.style.display === "block") {
                    dropdownContent.style.display = "none";
                } else {
                    dropdownContent.style.display = "block";
                }
            });
        }
    }
}

const getUserGuide = async (object) => {
    // For sidebar menu
    let userGuide = object.getAttribute('userGuide');
    const data = await commons.postData("/api/v1/userGuides/getUserGuide",  
                                    {remoteController: sessionStorage.getItem("remoteController"),
                                     userGuide: userGuide});

    if (data.status == 'failed') {
        document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
    } else {
        document.querySelector('#insertUserGuideContents').innerHTML = data.userGuideContents;
    }
}

window.getUserGuideMenu = getUserGuideMenu;
window.getUserGuide = getUserGuide;