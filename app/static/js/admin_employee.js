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

function update_csrf_after_post(){

    var _csrf_token =  document.getElementById('_csrf_token');
    var _csrf_p = document.getElementById('CSRF_PARAGRAPH');
    
    fetch('/csrf_ajax/')
    .then(function(response) {
        return response.json();
      })
      .then(function(myJson) {
        console.log(JSON.stringify(myJson));
        return myJson
      })     
    .then(function(response){

        console.log(response);

        if(response.success === true){
            _csrf_token.value = response.token;
            _csrf_p.innerText = response.token;
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

    var postRequestType = document.getElementById('function_marker').value;
    var _csrf_token =  document.getElementById('_csrf_token').value;

    postData('/admin_employee/',{postMethod: postRequestType, addData: data,
        _csrf_token: _csrf_token})
        //.then(table.draw())
        .then(response => console.log(response))
        .then(response => update_csrf_after_post());
        // https://www.tjvantoll.com/2015/09/13/fetch-and-errors/
        //.catch(error => console.log(error));

}


function openModelForm(){
    document.getElementById('employee_tb-form_container_modal')
    .style.display = "block";
}


function openEmployeeFormAdd(){
    

    // reset form fields
    if ($('#function_marker').value  != "add"){

        document.getElementById('input_first_name').value = "";
        document.getElementById('input_last_name').value = "";
        document.getElementById('input_DoB').value = "";
        document.getElementById('input_username').value = "";
        document.getElementById('input_email').value = "";
        document.getElementById('input_phone').value = "";
        document.getElementById('input_em_contact').value = "";
        document.getElementById('input_em_r').value = "";
        document.getElementById('input_em_phone').value = "";
        document.getElementById('input_tfn').value = "";
        document.getElementById('input_ea').value = "";
        document.getElementById('input_skills').value = "";

    }

    document.getElementById('form_heading').innerText = "Add a new employee";
    document.getElementById('function_marker').value = "add";

    //open modal function here
    openModelForm();
    
}


function openEmployeeEditForm(table, e){

    // query the database for the employee entity
    var table_row = table.row( "#tab_id_" + e.currentTarget.dataset.id ).data();


    // input the row data into the form
    document.getElementById('input_first_name').value = "";
    document.getElementById('input_last_name').value = "";
    document.getElementById('input_DoB').value = "";
    document.getElementById('input_username').value = table_row[1];
    document.getElementById('input_email').value = table_row[2];
    document.getElementById('input_phone').value = "";
    document.getElementById('input_em_contact').value = "";
    document.getElementById('input_em_r').value = "";
    document.getElementById('input_em_phone').value = "";
    document.getElementById('input_tfn').value = "";
    document.getElementById('input_ea').value = table_row[3];
    document.getElementById('input_skills').value = "";


    document.getElementById('form_heading').innerText = "Edit existing employee";
    document.getElementById('function_marker').value = "edit";

    //form fields replaced by entry form fields

    //open modal function here
    openModelForm();
}

function tableLoader(){

    const fetchUrl = '/admin_employee_table/' 

    fetch(fetchUrl)
        .then(function(response){
            return response.json();
        })
        .then(function(jsonResponse){
            var table = $('#employee_table_container').DataTable({
                data: jsonResponse["data"],
                rowId: (a) => 'tab_id_' + a[0], //label rows 
                dom: 'Bftrip', //create button
                buttons:[{
                    text: 'Add New Employee',
                    action:() => openEmployeeFormAdd() 
                }],
                columns: [
                    {
                        data:[0],
                        render: (data) =>  '<input type="checkbox" class="table-selection" value="' + data + '"/>'
                    },
                    {"data": [0]}, // column names
                    {"data": [1]}, 
                    {"data": [2]}, 
                    {"data": [3]}, 
                    {
                        data: [0],
                        render: (data) =>  '<a class="table-edit" data-id="' + data + '">Edit</a>'
                    }
                ]
            });

            // add entry event listeners
            $('#add-employee-btn').on('click',null,openEmployeeFormAdd);

            // edit row event listener
            table.on('click', '.table-edit', function(e){
                openEmployeeEditForm(table, e);
            });

        });


    }

// before the document is ready


$( document ).ready(function(){

    $('#submitNewEmployee').on('click', null, function(){
        console.log('button pushed');
        postEmployee();
    });   
    
    
    // Get the <span> element that closes the modal
    var modal = document.getElementById('employee_tb-form_container_modal');
    var span = document.getElementsByClassName("close")[0];


    // When the user clicks on <span> (x), close the modal
    $('#modal-close-btn').on('click',null,function(){
        $('#employee_tb-form_container_modal')[0].style.display = "none";
    });

    $('#close-btn').on('click',null,function(){
        $('#employee_tb-form_container_modal')[0].style.display = "none";
    });

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }


    // load the table and its event handlers
    tableLoader();
    

})
