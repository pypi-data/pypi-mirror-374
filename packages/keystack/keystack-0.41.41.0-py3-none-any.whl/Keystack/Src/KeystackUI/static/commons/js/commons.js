export const getCookie = async (name) => {
  let cookieValue = null;

  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();

          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));

              break;
          }
      }
  }

  return cookieValue;
}

export const getData = async (url) => {
  /* url: /path/to/somewhere
     csrftoken: The django generated token
     method: GET | DELETE
  */

  //console.log(`GET: ${url}`)

  try {
    // http://172.16.1.16:8000/GlobalVariables/getGlobalVariables
    // body: JSON.stringify({'filePath': filePath.value}),
    // application/x-www-form-urlencoded;
    const response = await fetch(url, {
      method: 'GET',
      mode: 'same-origin',
      credentials: 'include',
      redirect: 'follow',
      headers: {
        "Accept": "application/json, text/plain, */*",
        "X-CSRFToken": getCookie('csrftoken'),
        'Access-Control-Allow-Origin': '*',
      }
    });

    const data = await response.json();
    //console.info('getData() returning data: ' + data.file)
    return data;
  } catch (error) {
    console.error("getData() error: " + error)
  };
}


export const postData = async (url, jsonBody) => {
  /* url: /path/to/somewhere
     csrftoken: The django generated token
     method: POST
     jsonBody: {'data': 'value'}
  */

  //console.info(`POST: ${url}  ${JSON.stringify(jsonBody)}`)

  try {
    // http://172.16.1.16:8000/GlobalVariables/getGlobalVariables
    // body: JSON.stringify({'filePath': filePath.value}),
    // application/x-www-form-urlencoded;
    const response = await fetch(url, {
      method: 'POST',
      mode: 'same-origin',
      credentials: 'include',
      redirect: 'follow',
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "X-CSRFToken": getCookie('csrftoken'),
        'Access-Control-Allow-Origin': '*',
      },
      body: JSON.stringify(jsonBody),
    });

    const data = await response.json();
    return data;

  } catch (error) {
    console.error(`postData() error: ${error}`)
    return error
  };
}


export const deleteData = async (url, jsonBody) => {
  /* url: /path/to/somewhere
     csrftoken: The django generated token
     method: POST
     jsonBody: {'data': 'value'}
  */

  //console.info(`DELETE: ${url}  ${jsonBody}`)

  try {
    // http://172.16.1.16:8000/GlobalVariables/getGlobalVariables
    // body: JSON.stringify({'filePath': filePath.value}),
    // application/x-www-form-urlencoded;
    const response = await fetch(url, {
      method: 'DELETE',
      mode: 'same-origin',
      credentials: 'include',
      redirect: 'follow',
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "X-CSRFToken": getCookie('csrftoken'),
        'Access-Control-Allow-Origin': '*',
      },
      body: JSON.stringify(jsonBody),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("postData() error: " + error)
    return error
  };
}


export const sortTable = async ({tableId=null, columnIndex=null}) => {
  var table, rows, switching, i, x, y, shouldSwitch;
  table = document.querySelector(tableId);

  switching = true;
  /* Make a loop that continue until
     no switching has been done:
  */

  while (switching) {
    //start by saying: no switching is done:
    switching = false;
    rows = table.rows;

    /* Loop through all table rows (except the
       first and last row, which contains table headers and an empty last row
       to support the tableFixHead2 height:0)
    */
    for (i = 1; i < (rows.length - 2); i++) {
      //start by saying there should be no switching:
      shouldSwitch = false;

      /* Get the two elements you want to compare,
         one from current row and one from the next:
         TD[1] == column index
      */
      x = rows[i].getElementsByTagName("TD")[columnIndex];
      y = rows[i + 1].getElementsByTagName("TD")[columnIndex];
      //check if the two rows should switch place:
      if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
        //if so, mark as a switch and break the loop:
        shouldSwitch = true;
        break;
      }
    }

    if (shouldSwitch) {
      /* If a switch has been marked, make the switch
        and mark that a switch has been done:*/
      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
      switching = true;
    }
  }
}


export const search = async ({searchInputId=null, tableId=null, columnIndex=null}) => {
  var input, filter, table, tr, td, i, txtValue;
  input = document.querySelector(searchInputId);
  filter = input.value.toUpperCase();
  table = document.querySelector(tableId);
  tr = table.getElementsByTagName("tr");

  for (i = 0; i < tr.length; i++) {
    // [2] is the Playbook Group column
    td = tr[i].getElementsByTagName("td")[columnIndex];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}


export const getInstantMessages = async (webpage) => {
  const data = await postData("/api/v1/system/getInstantMessages",  
                    {remoteController:sessionStorage.getItem("remoteController"),
                     webPage: webpage})
  document.querySelector('#messageTable').innerHTML = data.instantMessages;
}


export const blinkSuccess = () => {
  /* Blink success for 3 seconds */
  document.querySelector("#flashingError").innerHTML = '<strong>Success</strong>';
  setTimeout(() => {
      document.querySelector("#flashingError").innerHTML = '';
  }, 3000);
}

export const sleep = async (sleepTime) => {
    await new Promise(resolve => setTimeout(resolve, sleepTime));
}

export const getServerTime = async () => {
  /* getServerTime() is in sessionMgmt */

  const data = await postData("/api/v1/system/serverTime",  
                      {remoteController: sessionStorage.getItem("remoteController")});

  if (data.name == "TypeError") {
    return data
  } else {
    document.querySelector('#insertServerTime').innerHTML = data.serverTime;
  }

  // Call itself recursively every 10 seconds instead of using setInterval
  setTimeout(getServerTime, 10000);
}


export const modifyFile = async () => {
  /* Modify existing env */

  try {
      const textarea = document.querySelector('#textareaId').value
      const filePath = document.querySelector('#textareaId').name

      const data = await postData("/api/v1/fileMgmt/modifyFile",  
                         {remoteController: sessionStorage.getItem("remoteController"),
                          textarea: textarea,
                          filePath: filePath})

      if (data.status == "success") {
          const status = `<div style='color:green'>Successfully modified Env file</div>`;
          document.querySelector("#modifyEnvStatus").innerHTML = status;
      } else {
          const status = `<div style='color:red'>Failed: ${data.errorMsg}</div>`;
          //document.querySelector("#flashingError").innerHTML = '<strong>Error</strong>';
          document.querySelector("#modifyEnvStatus").innerHTML = status;
      }

  } catch (error) {    
      console.error("modifyFile() error: " + error)
  }
}

export const capitalizeWords = (str) => {
    if (str && typeof(str) === "string") {
        str = str.split(" ");    
        for (var i = 0, x = str.length; i < x; i++) {
            if (str[i]) {
                str[i] = str[i][0].toUpperCase() + str[i].substr(1);
            }
        }
        return str.join(" ");
    } else {
        return str;
    }
}  