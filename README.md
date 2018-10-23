# PreferenceSchedulerApplication

<h3>Todo</h3>

<ul>
    <li>[ ] Admin Shift View
        <p>
            Admin need to be able to manipulate all of the shifts. Needs to be able to add, delete and edit shifts as well as require capabilities on those shifts. The view should also include a way to see who has been assigned to said shifts, and other shift related metrics like cost.  
        </p>
        <ul>
            <li>[X] AJAX: add shift </li>
            <li>[X] AJAX: delete shift </li>
            <li>[X] AJAX: Edit shift start and end time </li>
        </ul>
        <p>
            Subsequently have gone back over the code when creating an employee page - As a result the code needs to be refactored
        </p>
        <p>[ ] Refactor Code to use better AJAX Calls</p>
    </li>
    <li>[ ] Admin Employee View
        <p>
            Admin needs to be able to add, delete, and edit employees. Use case is to add a new employee when they are hired and to edit employees to have skills as they learn new capabilities. When an employee leaves the company the admin also needs to be able to remove them from file.
        </p>
        <ul>
            <li>[X] AJAX: update CSRF token</li>
            <li>[X] AJAX: add employee </li>
            <li>[X] AJAX: delete employee </li>
            <li>[X] AJAX: Edit employee details </li>
            <li>[ ] For each employee see what periods they are assigned and to what shifts they are asigned</li>
            <li>[ ] For each employee to see the associated cost associated with the current assignment</li>
        </ul>
    </li>
    <li>
        [ ] Employee Account View
        <p>
            Employees need to be able to edit some of their own details. In particular they need to be able to edit their contact details. 
        </p>
        <ul>
            <li>[ ] AJAX: edit own detail</li>
        </ul>
    </li>
    <li>
        [ ] Employee Shift View
        <p>
            Employee needs to be able to select a preference for the possible shifts which have been created by the admin. 
        </p>
        <ul>
            <li>[ ] AJAX: Get own shift preferences</li>
            <li>[ ] AJAX: set own shift preference</li>
        </ul>
    </li>
    <li>
        [ ] Employee Roster View
        <p>
            Employee needs to be able to see the asignment proposed by the admin. Employee should be able to flag problems up the chain
        </p>
        <ul>
            <li>[ ] AJAX: Get own shift allocation</li>
            <li>[ ] AJAX: Send Problem request to Admin</li>
        </ul>
    </li>
</ul>