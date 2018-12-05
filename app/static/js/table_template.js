function postData(url = ``, data = {}) {
    // Default options are marked with *
    return fetch(url, {
        method: "POST", // *GET, POST, PUT, DELETE, etc.
        mode: "cors", // no-cors, cors, *same-origin
        cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
        credentials: "same-origin", // include, same-origin, *omit
        headers: {
            "Content-Type": "application/json; charset=utf-8",
            // "Content-Type": "application/x-www-form-urlencoded",
        },
        redirect: "follow", // manual, *follow, error
        referrer: "no-referrer", // no-referrer, *client
        body: JSON.stringify(data), // body data type must match "Content-Type" header
    })
    .then(response => response.json()); // parses response to JSON
}

function update_csrf_after_post(csrf_token_id = '_csrf_token', 
                                    csrf_ajax_update_route = '/csrf_ajax/'){

    var _csrf_token =  document.getElementById(csrf_token_id);
    
    fetch(csrf_ajax_update_route)
    .then(function(response) {
        return response.json();
      })
      .then(function(myJson) {
        //console.log(JSON.stringify(myJson));
        return myJson
      })     
    .then(function(response){

        //console.log(response);
        if(response.success === true){
            _csrf_token.value = response.token;
        }

    });

}

function checkPostFormRequest(jsonResponse){
    // update the datatable to show the new employee
    var table = $('#table_id').DataTable();

    if (jsonResponse.post_status === true) {
        // check the response for validation errors

        // the server executed the 'add' successfully
        table.draw();
    } else {
        // the server has failed to execure the 'add'
        alert('The server encountered an error adding this item');

    }
}

function columnDefinitions(data){
    var coldef = [];

    coldef.push({
        data:[0],
        render: (data) =>  '<input type="checkbox" class="table-selection" name="selected_id" value="' + data + '"/>'
    });

    var lenArr = data.length;
    for (var len = lenArr; len > 0; len--){
        //dostuff
        coldef.push({"data": [len]});
    }

    coldef.push({
        data: [0],
        render: (data) =>  '<a href="#" class="table-edit" data-id="' + data + '">Edit</a>'
    });

    return(coldef);

}

function generateEditForm(data){

    example_data = {group_1}

}