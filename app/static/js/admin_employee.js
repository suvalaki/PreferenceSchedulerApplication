// https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
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



function checkPostFormRequest(jsonResponse){
    // update the datatable to show the new employee
    var table = $('#table_id').DataTable();

    if (jsonResponse.post_status === true) {
        // the server executed the 'add' successfully
        table.draw();
    } else {
        // the server has failed to execure the 'add'
        alert('The server encountered an error adding this item');

    }
}


function postEmployee(){
    // post a new employee to the server

    //var table = $('#table_id').DataTable();

    var data = {
        first_name: document.getElementById('input_first_name').value,
        last_name : document.getElementById('input_last_name').value,
        gender    : document.getElementById('gener_input').value,
        dob       : document.getElementById('input_DoB').value,
        username  : document.getElementById('input_username').value,
        email     : document.getElementById('input_email').value,
        phone     : document.getElementById('input_phone').value,
        em_contact: document.getElementById('input_em_contact').value,
        em_rel    : document.getElementById('input_em_r').value,
        em_phone  : document.getElementById('input_em_phone').value,
        fin_tfn   : document.getElementById('input_tfn').value,
        ea        : document.getElementById('input_ea').value,
        // https://stackoverflow.com/questions/11821261/how-to-get-all-selected-values-from-select-multiple-multiple
        skills    : $('#input_skills').val(),
    };

    var postRequestType = "add";
    var _csrf_token =  document.getElementById('_csrf_token').value;

    postData('/admin_employee/',{postMethod: postRequestType, adddData: data,
        _csrf_token: _csrf_token})
        //.then(table.draw())
        .then(response => console.log(response))
        // https://www.tjvantoll.com/2015/09/13/fetch-and-errors/
        .catch(error => console.log(error));


}


$( document ).ready(function(){

    $('#submitNewEmployee').on('click', null, function(){
        console.log('button pushed');
        postEmployee();
    });    

})
