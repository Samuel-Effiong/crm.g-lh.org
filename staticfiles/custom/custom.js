
"use strict"


// PROJECT MANAGEMENT

const __save_project = (url) => {
    const project_name = document.getElementById('project_name').value;
    const project_description = document.getElementById('project_description').value;
    const project_category = document.getElementById('project_category').value;
    const project_start_date = document.getElementById('project_start_date').value;
    const project_due_date = document.getElementById('project_due_date').value;
    const project_priority = document.getElementById('project_priority').value;
    const project_leader = document.getElementById('project_leader').value;

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
    formData.append('project_priority', project_priority);
    formData.append('project_leader', project_leader);
    formData.append('project_members', project_members);
    formData.append('project_targets', project_targets);
    formData.append('X-CSRFToken', csrf_token);

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
    let currentState = element.value;
    console.log('currentState', currentState);

    const status_badge = document.querySelector(`#pk${pk} .status`);

    if (currentState === 'Completed') {

        const completion_modal = document.querySelector('#confirm_completion #completion_detail');
        const show_modal_button = document.getElementById(`show_modal${pk}`);
        const project_target_id = document.querySelector('#confirm_completion #project_target_id');

        url = `${url}change_target_status&target_id=${pk}&state=Pending Approval`;

        completion_modal.textContent = url;
        project_target_id.textContent = pk;
        show_modal_button.click();

        return;
    }

    url = `${url}change_target_status&target_id=${pk}&state=${currentState}`;

    fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data['confirm']) {
                if (currentState === 'Completed') {
                    console.log('Darn it Escaped');
                }

                const status_badge = document.querySelector(`#pk${pk} .status`);
                console.log(status_badge);
                console.log(currentState)

                if (currentState === 'In Progress') {
                    status_badge.textContent = 'In Progress';
                    status_badge.className = 'badge badge-warning badge-pill status';
                }

                else if (currentState === 'Not Started') {
                    status_badge.textContent = 'Not Started';
                    status_badge.className = 'badge badge-danger badge-pill status';
                }
            }
        })
}


// PROJECT DETAIL
const send_approval_notification = () => {
    const target_id = document.querySelector('#confirm_completion #project_target_id').textContent;
    const completion_detail = document.querySelector('#confirm_completion #completion_detail');

    const url = completion_detail.textContent;
    completion_detail.textContent = "";

    console.log('completion detail\n\n', url);

    fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data['confirm']) {

                const outlier_pending_status_button = document.querySelector(`#outlier_pending_status_button${target_id}`);
                const completed_status_button = document.querySelector(`#completed_status_button${target_id}`);
                const target_status_select_box = document.querySelector(`#target_status_select_box${target_id}`);

                console.log(outlier_pending_status_button);
                console.log(completed_status_button);
                console.log(target_status_select_box);

                const status_span = document.querySelector(`#pk${target_id} .status`)

                outlier_pending_status_button.style.display = 'block';
                status_span.style.display = 'none'
                // completed_status_button.display = 'none';

                target_status_select_box.disabled = true;
            }
        })
}


const _target_approved_by_leader = (element, url, target_id) => {
    const pending_status_button = document.querySelector(`#pending_status_button${target_id}`);
    const leader_approval_button = document.querySelector(`#leader_approval_button${target_id}`);
    const leader_rejection_button = document.querySelector(`#leader_rejection_button${target_id}`);
    const completed_status_button = document.querySelector(`#completed_status_button${target_id}`);

    fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data['confirm']) {
                completed_status_button.style.display = 'block';
                leader_approval_button.style.display = 'none';
                leader_rejection_button.style.display = 'none'
                pending_status_button.style.display = 'none';
            }
        })
}


const _target_rejected_by_leader = (element, url, target_id) => {
    const pending_status_button = document.querySelector(`#pending_status_button${target_id}`);
    const leader_approval_button = document.querySelector(`#leader_approval_button${target_id}`);
    const leader_rejection_button = document.querySelector(`#leader_rejection_button${target_id}`);
    const completed_status_button = document.querySelector(`#completed_status_button${target_id}`);
    const outlier_not_started = document.querySelector(`#outlier_not_started${target_id}`);
    const target_status_select_box = document.querySelector(`#target_status_select_box${target_id}`);

    fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data['confirm']) {
                completed_status_button.style.display = 'none';
                leader_approval_button.style.display = 'none';
                leader_rejection_button.style.display = 'none'
                pending_status_button.style.display = 'none';

                target_status_select_box.disabled = false;
                target_status_select_box.value = "Not Started";

                outlier_not_started.style.display = 'block';
            }
        })
}


const select_status_filter = (element) => {
    const status_display = document.getElementById('filter-by-status');
    const status = element.textContent;

    status_display.textContent = ` ${status}`;
}


const select_priority_filter = (element) => {

    const priority_display = document.getElementById('filter-by-priority');
    const priority = element.textContent;

    priority_display.textContent = ` ${priority}`;
}


const filter_by_priority_and_status = () => {
    const priority = document.getElementById('filter-by-priority').textContent;
    const status = document.getElementById('filter-by-status').textContent;

    window.location.href = `?filter&status=${status.trim()}&priority=${priority.trim()}`;
}

// END OF PROJECT MANAGEMENT
