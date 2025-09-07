import * as commons from './commons.js';
//import {SwaggerUIBundle} from './swagger-ui/dist/SwaggerUIBundle.js';

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

    document.querySelector("#mainBodyDiv").style.height = "100vh";
    document.querySelector("#mainBodyDiv").style.marginTop = "15px";
    commons.getServerTime();
})


// schema-swagger-ui | restAPI
const ui = SwaggerUIBundle({
    url: "/api/v1/restAPI/docs/",
    dom_id: '#swagger-ui',
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
    ],
    layout: "BaseLayout",
    requestInterceptor: (request) => {
        request.headers['X-CSRFToken'] = commons.getCookie('csrftoken')
        return request;
    }
})
