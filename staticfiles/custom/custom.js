
"use strict"

const __save_project = (url) => {
    console.log(url);
    const project_name = document.getElementById('project_name').value;
    const project_description = document.getElementById('project_description').value;
    const project_category = document.getElementById('project_category').value;
    const project_start_date = document.getElementById('project_start_date').value;
    const project_due_date = document.getElementById('project_due_date').value;

    let project_members = document.getElementById('project_members');
    let members_options = project_members.options;

    let result = [];
    for (let i = 0; i < members_options.length; i++) {
        if (members_options[i].selected) {
            result.push(members_options[i].value);
        }
    }
    project_members = result.join('~ ');

    let project_targets = [];
    let project_targets_list = document.querySelectorAll('.project_targets');
    for (let i=0; i < project_targets_list.length; i++) {
        project_targets.push(project_targets_list[i].textContent);
    }
    project_targets = project_targets.join('~ ');

    const csrf_token = document.querySelector('input[name=csrfmiddlewaretoken]').value;

    const formData = new FormData();
    formData.append('project_name', project_name);
    formData.append('project_description', project_description);
    formData.append('project_category', project_category);
    formData.append('project_start_date', project_start_date);
    formData.append('project_due_date', project_due_date);
    formData.append('project_members', project_members);
    formData.append('project_targets', project_targets);
    formData.append('X-CSRFToken', csrf_token);

    console.log(url)

    fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
            'X-CSRFToken': csrf_token,
        },
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            const confirm = data['confirm'];

            if (confirm) {
                document.querySelector('#submit_button').style.disabled = true;
                window.location.reload();
            }
        })
}


const __toggle_target = (element, url, pk) => {
    let currentState = element.getAttribute('data-state');
    console.log('currentState', currentState);
    console.log('element', element);

    url = `${url}change_target_status&target_id=${pk}`;
    // url = `${url}&state=${ currentState === 'Pending' ? 'Completed' : currentState === 'Pending' ? 'Pending' : 'Not Started'}`;


    if (currentState === 'Pending') {
    //     Indeterminate == Pending
        element.setAttribute('data-state', 'Completed');
        element.indeterminate = false;
        element.checked = true;

        url = `${url}&state=Completed`;

    } else if (currentState === 'Not Started') {
    //     unchecked == Not Started
        element.setAttribute('data-state', 'Pending');
        element.indeterminate = true;
        element.checked = false;

        url = `${url}&state=Pending`;
    }
    else if (currentState === 'Completed') {
    //     checked == Completed
        element.setAttribute('date-state', 'Not Started');
        element.indeterminate = false;
        element.checked = false;

        url = `${url}&state=Not Started`;

    }
    console.log('url', url);

    // fetch(url, {
    //     method: 'GET',
    //     credentials: 'same-origin',
    //     headers: {
    //         'Accept': 'application/json',
    //     }
    // })
    //     .then(response => response.json())
    //     .then(data => {
    //         if (data['confirm']) {
    //             const status_badge = document.querySelector(`#pk${pk} .status`);
    //             currentState = element.getAttribute('date-state');
    //
    //             if (currentState === 'Completed') {
    //
    //                 status_badge.textContent = 'Completed';
    //                 status_badge.className = 'badge badge-success badge-pill status';
    //             }
    //             else if (currentState === 'Pending') {
    //
    //                 status_badge.textContent = 'Pending';
    //                 status_badge.className = 'badge badge-warning badge-pill status';
    //             }
    //             else if (currentState === 'Not Started') {
    //
    //                 status_badge.textContent = 'Not Started';
    //                 status_badge.className = 'badge badge-danger badge-pill status';
    //             }
    //         }
    //     })
}
