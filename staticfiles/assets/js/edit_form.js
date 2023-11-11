
"use strict"


const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++){
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')){
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue
}

const csrf_token = getCookie('csrftoken');

let update_form = (url, category) => {
    document.getElementById('save_update_button').addEventListener('click', event => {
        if (category === 'Bible Reading') {
            let comment = document.querySelector("#comment").value;
            let date = document.querySelector('#date').value;
            let status = document.querySelector('#status').value;

            const formData = new FormData();
            formData.append('comment', comment);
            formData.append('date', date);
            formData.append('status', status);
            formData.append('csrfmiddlewaretoken', csrf_token);
            
            const headers = new Headers();
            headers.append('Content-Type', 'application/json');
            headers.append('Origin', 'https://crm.g-lh.org');
            headers.append('X-CSRFToken', csrf_token);

            fetch(url, {
                method: 'POST',
                credentials: 'same-origin',
                headers: headers,
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    let confirm = document.querySelector('#update_successful')
                    confirm.style.display = 'block'

                    setTimeout(() => {
                            confirm.style.display = 'none';
                        }, 5000);

                //    UPDATE WEBSITES
                    document.querySelector("#display_comment").textContent = comment;
                    const date_value = new Date(date)
                    document.querySelector("#display_date").textContent = date_value.toDateString();

                    let display_status = document.querySelector("#display_status")

                    if (status === 'completed') {
                        display_status.textContent = 'Completed';
                        display_status.className = "badge rounded-pill bg-success";
                    }
                    else if (status === 'in_progress') {
                        display_status.textContent = 'In Progress';
                        display_status.className = "badge rounded-pill bg-warning";
                    }
                    else if (status === 'not_started') {
                        display_status.textContent = 'Not Started';
                        display_status.className = "badge rounded-pill bg-danger";
                    }

                //    UPDATE COUNTERS
                    update_personal_development_counters();
                })
                .catch(error => {
                    console.log(error);
                });
        }
        else if (category === 'Prayer Marathon') {
        //    PRAYER MARATHON
            let comment = document.querySelector("#comment").value;
            let date = document.querySelector('#date').value;

            const formData = new FormData();
            formData.append('comment', comment)
            formData.append('date', date);
            formData.append('csrfmiddlewaretoken', csrf_token);

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
                    let confirm = document.querySelector('#update_successful')
                    confirm.style.display = 'block'

                    setTimeout(() => {
                            confirm.style.display = 'none';
                        }, 5000);

                //    UPDATE WEBSITES
                    document.querySelector("#display_comment").textContent = comment;

                    const date_value = new Date(date)
                    document.querySelector("#display_date").textContent = date_value.toDateString();

                })
                .catch(error => {
                    console.log(error);
                });

        }
        else if (category === 'Church Work') {
        //    CHURCH WORK
            let details = document.querySelector("#details").value;
            let work_category = document.querySelector("#work_category").value;
            let hours_spent = document.querySelector("#hours_spent").value;
            let start_time = document.querySelector("#start_time").value;
            let end_time = document.querySelector("#end_time").value;
            let date = document.querySelector("#date").value;

            const formData = new FormData();
            formData.append('details', details);
            formData.append('work_category', work_category);
            formData.append('hours_spent', hours_spent);
            formData.append('start_time', start_time);
            formData.append('end_time', end_time);
            formData.append('date', date);

            const headers = new Headers();
            headers.append('Content-Type', 'application/json');
            headers.append('Origin', 'https://crm.g-lh.org');
            headers.append('X-CSRFToken', csrf_token);
            
            fetch(url, {
                method: 'POST',
                credentials: 'same-origin',
                headers: headers,
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    let confirm = document.querySelector('#update_successful');
                    confirm.style.display = 'block';

                    setTimeout(() => {
                        confirm.style.display = 'none';
                    }, 5000);

                //    UPDATE WEBSITE
                    document.querySelector('#display_detail').textContent = details;

                    work_category = work_category.split('_');

                    if (work_category.length === 2) {
                        work_category[0] = `${work_category[0].substring(0, 1).toUpperCase()}${work_category[0].substring(1)}`;
                        work_category[1] = `${work_category[1].substring(0, 1).toUpperCase()}${work_category[1].substring(1)}`
                        work_category = work_category.join(" ")
                    }
                    else if (work_category.length > 2) {
                        work_category[0] = `${work_category[0].substring(0, 1).toUpperCase()}${work_category[0].substring(1)}`;
                        work_category[1] = `${work_category[1].substring(0, 1).toUpperCase()}${work_category[1].substring(1)}`;
                        work_category[2] = `${work_category[2].substring(0, 1).toUpperCase()}${work_category[2].substring(1)}`;

                        work_category = `${work_category.slice(0, 2).join("/")} ${work_category[2]}`
                    }
                    document.querySelector("#display_category").textContent = work_category;
                    document.querySelector("#display_time").innerHTML = `Start Time: ${start_time}<br /> End Time: ${end_time}`;
                    document.querySelector("#display_hours_spent").textContent = hours_spent;

                    const date_value = new Date(date);
                    document.querySelector("#display_date").textContent = date_value.toDateString();

                })
                .catch(error => {
                    console.log(error);
                })

        }
        else if (category === 'Evangelism') {
            let field_of_visit = document.querySelector("#evangelism_field_of_visit").value;
            let hours_spent = document.querySelector("#evangelism_hours_spent").value;
            let no_led_to_christ = document.querySelector("#evangelism_no_led_to_christ").value;
            let follow_up = document.querySelector("#evangelism_follow_up").value;
            let invites = document.querySelector("#evangelism_no_of_invites").value;
            let baptism = document.querySelector("#evangelism_no_baptism").value;
            let people_prayed = document.querySelector("#evangelism_people_prayed").value;
            let prints_shared = document.querySelector("#evangelism_prints_shared").value;
            let messages = document.querySelector('#evangelism_message_shared').value;
            let snippets = document.querySelector('#evangelism_snippets').value;
            let first_date = document.querySelector('#evangelism_first_date').value;
            let last_date = document.querySelector('#evangelism_last_date').value;

            const formData = new FormData();
            formData.append('field_of_visit', field_of_visit);
            formData.append('hours_spent', hours_spent);
            formData.append('no_led_to_christ', no_led_to_christ);
            formData.append('follow_up', follow_up);
            formData.append('invites', invites);
            formData.append('baptism', baptism);
            formData.append('people_prayed', people_prayed);
            formData.append('prints_shared', prints_shared);
            formData.append('messages', messages);
            formData.append('snippets', snippets);
            formData.append('first_date', first_date);
            formData.append('last_date', last_date);
            formData.append('csrfmiddlewaretoken', csrf_token);

            const headers = new Headers();
            headers.append('Content-Type', 'application/json');
            headers.append('Origin', 'https://crm.g-lh.org');
            headers.append('X-CSRFToken', csrf_token);
            
            fetch(url, {
                method: 'POST',
                credentials: 'same-origin',
                headers: headers,
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    let confirm = document.querySelector('#update_successful')
                    confirm.style.display = 'block'

                    setTimeout(() => {
                            confirm.style.display = 'none';
                        }, 5000);

                    document.querySelector("#display_field_of_visit").textContent = field_of_visit;
                    document.querySelector("#display_hours_spent").textContent = hours_spent;
                    document.querySelector("#display_led_to_christ").textContent = no_led_to_christ;
                    document.querySelector("#display_follow_up").textContent = follow_up;
                    document.querySelector("#display_invites").textContent = invites;
                    document.querySelector("#display_holy_spirit_baptism").textContent = baptism;
                    document.querySelector("#display_people_prayed").textContent = people_prayed;
                    document.querySelector("#display_prints_shared").textContent = prints_shared;
                    document.querySelector("#display_messages").textContent = messages;
                    document.querySelector("#display_snippet").textContent = snippets;

                    document.querySelector("#display_first_date").textContent = new Date(first_date).toDateString();
                    document.querySelector("#display_last_date").textContent = new Date(last_date).toDateString();

                })
                .catch(error => {
                    console.log(error);
                })
        }
        else if (category === 'Prophetic Vision'){
        //    PROPHETIC VISION
            let description = document.querySelector("#prophetic_vision_description").value;
            let date = document.querySelector("#prophetic_vision_date").value;
            let body = document.querySelector("#prophetic_vision_body").value;

            const formData = new FormData();
            formData.append('description', description);
            formData.append('date', date);
            formData.append('body', body);

            const headers = new Headers();
            headers.append('Content-Type', 'application/json');
            headers.append('Origin', 'https://crm.g-lh.org');
            headers.append('X-CSRFToken', csrf_token);
            
            fetch(url, {
                method: 'POST',
                credentials: 'same-origin',
                headers: headers,
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    let confirm = document.querySelector("#update_successful");
                    confirm.style.display = 'block';

                    setTimeout(() => {
                        confirm.style.display = 'none';
                    }, 5000);

                //    UPDATE WEBSITE
                    document.querySelector("#display_description").textContent = description;
                    document.querySelector("#display_date").textContent = date;
                    document.querySelector("#display_body").textContent = body;
                })
                .catch(error => {
                    console.log(error);
                })
        }
        else {
            console.log("YOu are not suppose to be here! Either way I bless the Lord");
        }
    })
}


