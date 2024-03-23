
//
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
    return cookieValue;
}
//
const csrf_token = getCookie('csrftoken');
let change_password = (url) => {
//
    document.getElementById('password_form').addEventListener('submit', event => {
        event.preventDefault();

        let current_password = document.querySelector('#currentPassword').value;
        let new_password = document.querySelector("#newPassword").value;

        const formData = new FormData();
        formData.append('current', current_password);
        formData.append('new', new_password);
        formData.append('form_name', 'password');
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
                let confirmation = data['confirm']
                const password_successful = document.querySelector('#password_successful')
                const password_failed = document.querySelector('#password_failed')
                if (confirmation) {
                    password_failed.style.display = 'none';
                    password_successful.style.display = 'block';
                    setTimeout(() => {
                        window.location.reload();
                    }, 5000);
                }
                else {
                    password_failed.style.display = 'block';
                    password_successful.style.display = 'none';

                    setTimeout(() => {
                        password_failed.style.display = 'none';
                    }, 5000);
                }
            })
            .catch(error => {
                const password_error = document.querySelector('#password_error')
                    password_error.style.display = 'block'

                    setTimeout(() => {
                        password_error.style.display = 'none';
                    }, 5000);
            });
    })
}

// RENDER PASSWORD SUBMIT BUTTON INVALID WHILE THE PASSWORDS DO NOT MATCH

const password_validation = () => {
    const current_password = document.querySelector('#currentPassword');
    const new_password = document.querySelector('#newPassword');
    const confirm_password = document.querySelector('#confirmPassword');

    const password_button = document.querySelector('#password_submit_button');

    const checker = () => {
        let current_value = current_password.value;
        let new_value = new_password.value;
        let confirm_value = confirm_password.value;

        if (current_value.length < 1 || new_value.length < 1 || confirm_value.length < 1) {
            password_button.disabled = true;
        }
        else if (current_value && new_value && confirm_value) {
            if (new_value !== confirm_value) {
                password_button.disabled = true;         }
            else {
                password_button.disabled = false;
            }
        }
    }

    current_password.addEventListener('keyup', checker);
    new_password.addEventListener('keyup', checker);
    confirm_password.addEventListener('keyup', checker);
}

let edit_profile = (url) => {
    document.getElementById('profile_form').addEventListener('submit', event => {
        // alert("Love you God")
        event.preventDefault();

        const files = document.querySelector('#profilePic').files;

        // BIO DATA
        let first_name = document.querySelector('#firstName').value;
        let surname = document.querySelector('#surname').value;

        let gender = document.getElementsByName('gender');
        if (gender[0].checked){
            gender = gender[0].value;
        }
        else {
            gender = gender[1].value;
        }
        let date_of_birth = document.querySelector('#date_of_birth').value;
        let about = document.querySelector('#about').value;

        // PERSONAL DATA
        let phone_number = document.querySelector('#phoneNumber').value;
        let email = document.querySelector('#email').value;
        let occupation = document.querySelector('#occupation').value;
        let address = document.querySelector('#address').value;
        let skills = document.querySelector('#skills').value;

        let blood_group = document.querySelector('#blood_group').value;
        let genotype = document.querySelector('#genotype').value;
        let chronic_illness = document.querySelector('#chronic_illness').value;

        // RESIDENTIAL INFORMATION
        let lga = document.querySelector('#lga').value;
        let state = document.querySelector('#state').value;
        let country = document.querySelector('#country').value;
        let church_outpost = document.querySelector('#church_outpost').value;

        // SCHOOL INFORMATION
        let course_of_study = document.querySelector('#course_of_study').value;
        let years_of_study = document.querySelector('#years_of_study').value;
        let current_year_of_study = document.querySelector('#current_year_of_study').value;
        let final_year_status = document.querySelector('#final_year_status').value;
        let graduate_status = document.querySelector('#graduate_status').value;

        // NEXT OF KIN INFORMATION
        let next_of_kin_full_name = document.querySelector('#next_of_kin_full_name').value;
        let next_of_kin_relationship = document.querySelector('#next_of_kin_relationship').value;
        let next_of_kin_phone_number = document.querySelector('#next_of_kin_phone_number').value;
        let next_of_kin_address = document.querySelector('#next_of_kin_address').value;

        // SPIRITUAL INFORMATION
        let gift_graces = document.querySelector('#gift_graces').value;

        // ADDITIONAL INFORMATION
        let unit_of_work = document.querySelector('#unit_of_work').value;
        let shepherd = document.querySelector('#shepherd').value;
        let sub_shepherd = document.querySelector('#sub_shepherd').value;

        // SPECIAL KNOWLEDGE
        let shoe_size = document.querySelector('#shoe_size').value;
        let cloth_size = document.querySelector('#cloth_size').value;


        const formData = new FormData();
        formData.append('form_name', 'profile');

        // BIO DATA
        formData.append('first_name', first_name);
        formData.append('surname', surname);
        formData.append('gender', gender);
        formData.append('date_of_birth', date_of_birth);
        formData.append('about', about);

        // PERSONAL DATA
        formData.append('phone_number', phone_number);
        formData.append('email', email);
        formData.append('occupation', occupation);
        formData.append('address', address);
        formData.append('skills', skills);

        // BASIC MEDICAL INFORMATION
        formData.append('blood_group', blood_group);
        formData.append('genotype', genotype);
        formData.append('chronic_illness', chronic_illness);

        // RESIDENTIAL INFORMATION
        formData.append('lga', lga);
        formData.append('state', state);
        formData.append('country', country);
        formData.append('church_outpost', church_outpost);

        // SCHOOL INFORMATION
        formData.append('course_of_study', course_of_study);
        formData.append('years_of_study', years_of_study);
        formData.append('current_year_of_study', current_year_of_study);
        formData.append('final_year_status', final_year_status);
        formData.append('graduate_status', graduate_status);

        // NEXT OF KIN INFORMATION
        formData.append('next_of_kin_full_name', next_of_kin_full_name);
        formData.append('next_of_kin_relationship', next_of_kin_relationship);
        formData.append('next_of_kin_phone_number', next_of_kin_phone_number);
        formData.append('next_of_kin_address', next_of_kin_address);

        // SPIRITUAL INFORMATION
        formData.append('gift_graces', gift_graces);

        // ADDITIONAL INFORMATION
        formData.append('unit_of_work', unit_of_work);
        formData.append('shepherd', shepherd);
        formData.append('sub_shepherd', sub_shepherd);

        // SPECIAL KNOWLEDGE
        formData.append('shoe_size', shoe_size);
        formData.append('cloth_size', cloth_size);

        formData.append('csrfmiddlewaretoken', csrf_token);

        formData.append('profile_pic', files.length > 0 ? files[0]: 'none');

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
                if ('error' in data){
                    const display = document.querySelector('#profile_update_failed');
                    const display_span = document.querySelector('#profile_update_failed #message')
                    display_span.textContent = data['error'];
                    display.style.display = 'block';
                }
                else {
                    const display = document.querySelector('#profile_update_successful');
                    const display_span = document.querySelector('#profile_update_successful #message')
                    display_span.textContent = "Update successful, well done!";
                    display.style.display = 'block';

                    //    UPDATE THE WEBSITE WITH THE UPLOADED INFORMATION
                    // BIO DATA
                    for (let i=1; i <= 2; i++) {
                        if (files.length > 0) {
                            document.querySelector('#displayProfilePic' + String(i)).src = URL.createObjectURL(files[0])
                        }
                    }
                    for (let i=1; i <= 2; i++) {
                        document.querySelector('#displayFullName' + String(i)).textContent = first_name + ' ' + surname;
                    }

                    document.querySelector('#displayGender').textContent = gender === 'M'? 'Male': 'Female';
                    document.querySelector('#displayDateOfBirth').textContent = date_of_birth;
                    document.querySelector('#displayAbout').textContent = about;

                    // PERSONAL DATA
                    document.querySelector('#displayPhoneNumber').textContent = phone_number;
                    document.querySelector('#displayEmail').textContent = email;
                    document.querySelector('#displayOccupation').textContent = occupation
                    document.querySelector('#displayAddress').textContent = address;
                    document.querySelector('#displaySkills').textContent = skills;

                    // BASIC MEDIC INFO
                    document.querySelector('#displayBloodGroup').textContent = blood_group;
                    document.querySelector('#displayGenotype').textContent = genotype;
                    document.querySelector('#displayChronicIllness').textContent = chronic_illness

                    // RESIDENTIAL INFORMATION
                    document.querySelector('#displayLga').textContent = lga;
                    document.querySelector('#displayState').textContent = state;
                    document.querySelector('#displayCountry').textContent = country;
                    document.querySelector('#displayChurchOutpost').textContent = church_outpost;

                    // SCHOOL INFORMATION
                    document.querySelector('#displayCourseOfStudy').textContent = course_of_study;
                    document.querySelector('#displayYearsOfStudy').textContent = years_of_study;
                    document.querySelector('#displayCurrentYearOfStudy').textContent = current_year_of_study;
                    document.querySelector('#displayFinalYearStatus').textContent = final_year_status;
                    document.querySelector('#displayGraduateStatus').textContent = graduate_status;

                    // NEXT OF KIN INFORMATION
                    document.querySelector('#displayNextOfKinFullName').textContent = next_of_kin_full_name;
                    document.querySelector('#displayNextOfKinRelationship').textContent = next_of_kin_relationship;
                    document.querySelector('#displayNextOfKinPhoneNumber').textContent = next_of_kin_phone_number;
                    document.querySelector('#displayNextOfKinAddress').textContent = next_of_kin_address;

                    // SPIRITUAL INFORMATION
                    document.querySelector('#displayGiftGraces').textContent = gift_graces

                    // ADDITIONAL INFORMATION
                    document.querySelector("#displayUnitOfWork").textContent = unit_of_work;
                    document.querySelector('#displayShepherd').textContent = shepherd;
                    document.querySelector('#displaySubShepherd').textContent = sub_shepherd;

                    // SPECIAL KNOWLEDGE
                    document.querySelector('#displayShoeSize').textContent = shoe_size;
                    document.querySelector('#displayClothSize').textContent = cloth_size;

                    setTimeout(()=>{display.style.display = 'none'}, 5000)
                }

            })
            .catch(error => {
                console.log(error)
            })
    })
}

let preview_image = () => {
    // Preview uploaded image before uploading it
    const profile_pic = document.querySelector('#profilePic');
    const preview_image = document.querySelector('#preview');

    profile_pic.addEventListener('change', event => {
        let file = profile_pic.files
        file = file.length > 0 ? file[0] : '';

        if (file) {
            preview_image.src = URL.createObjectURL(file);
        }
    })
}


let remove_profile_pic = (default_image) => {
    const remove_button = document.querySelector('#removeProfilePic');
    const preview_img = document.querySelector('#preview');

    remove_button.addEventListener('click', event => {
        preview_img.className = "bi person-circle";
        preview_img.removeAttribute('src');
    })
}

const _load_celeb_image = (id, profile_pic) => {
    document.getElementById(id).src = profile_pic
}

async function load_celeb_image(id, profile_pic) {
    await _load_celeb_image(id, profile_pic)
}

let birthday_pop_box = (full_name, username, about, gender, sender_username, profile_pic) => {

    const message_input = document.getElementById('message_input_form');
    message_input.style.display = 'block';

    const container = document.getElementById('birthday_reply_container');
    container.style.display = 'none';

    document.getElementsByClassName('birthday_intro')[0].textContent = `Say Hi to your ${gender == 'F'?'Sister': 'Brother'}!`;
    document.getElementById('celebrant_full_name').textContent = full_name;
    document.getElementById('celebrant_nickname').textContent = ` @${username}`;
    document.getElementById('celebrant_about').textContent = about;
    load_celeb_image('celebrant_image', profile_pic);
    document.getElementById('birthdayMessageInput').value = "";

    check_if_user_has_already_sent_celebrant_message(sender_username, username);
}

const check_if_user_has_already_sent_celebrant_message = (sender, receiver) => {
    let birthday_url = document.getElementById('birthday_url').value.trim();
    birthday_url = `${birthday_url}?check_birthday_message=True&sender=${sender}&receiver=${receiver}`;

    const message_present = document.getElementById('message_sent_already');
    const success_container = document.getElementById('message_delivered');
    const failure_container = document.getElementById('message_failed');

    message_present.style.display = 'none !important';
    success_container.style.display = 'none !important';
    failure_container.style.display = 'none !important';

    fetch(birthday_url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            const confirmation = data['confirm']

            const message_input = document.getElementById('message_input_form');
            const container = document.getElementById('birthday_reply_container');

            if (confirmation) {
                message_present.style.display = 'block';
                container.style.display = 'block';

                success_container.style.display = 'none !important';
                failure_container.style.display = 'none !important';

                message_input.style.display = 'none';

            }
            else {
                // the User hasn't sent birthday message to celebrant
                // Open the text box and close the alert widgets

                container.style.display = 'none';
                message_present.style.display = 'none !important';

                success_container.style.display = 'none !important';
                failure_container.style.display = 'none !important';

                message_input.style.display = 'block';
            }
        })
        .then(error => {
            console.log(error)
        })
}

let send_birthday_message = (event, sender_username) => {
    // event.preventDefault();
    let celebrant_username = document.getElementById('celebrant_nickname').textContent;
    celebrant_username = celebrant_username.replace('@', '').trim();

    let message = document.getElementById('birthdayMessageInput').value;
    
    let birthday_url = document.getElementById('birthday_url').value.trim();
    birthday_url = `${birthday_url}?birthday_message=True&sender=${sender_username}&receiver=${celebrant_username}&message=${message}`;


    const message_present = document.getElementById('message_sent_already');
    const success_container = document.getElementById('message_delivered');
    const failure_container = document.getElementById('message_failed');

    message_present.style.display = 'none !important';
    success_container.style.display = 'none !important';
    failure_container.style.display = 'none !important';

    fetch(birthday_url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
        },
    })
        .then(response => response.json())
        .then(data => {
            const confirmation = data['confirm'];

            const container = document.getElementById('birthday_reply_container');

            const success_container = document.getElementById('message_delivered');
            const failure_container = document.getElementById('message_failed');
            const message_already_delivered = document.getElementById('message_sent_already');

            container.style.display = 'block';
            // message_already_delivered.style.display = 'block';

            const input_container = document.getElementById('message_input_form');
            input_container.style.display = 'none';

            if (confirmation) {
                success_container.style.display = 'block';

                failure_container.style.display = 'none !important';
                message_already_delivered.style.display = 'none !important';

            }
            else {
                failure_container.style.display = 'block';

                success_container.style.display = 'none !important';
                message_already_delivered.style.display = 'none !important';
            }
        })
        .then(error => {
            console.log(error);
        })
}

let display_list = (url, field, value) => {

    fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {

            let gender_list_content = document.getElementById('list_content');

            let table_rows = ""

            for (let i=0; i < data.length; i++) {
                let person = data[i];

                let content = `
                <tr>
                    <td><a href="${person.chief_shepherd_access_profile_url}">${person.full_name}</a></td>
                    <td>${person.age !== null?person.age: '-'}</td>
                </tr>      
     
                `

                table_rows += content;
            }

            let list_title = document.getElementById('list_title');

            if (field === 'gender') {
                list_title.textContent = value === 'M'? 'Male': 'Female';
            }
            else if (field === 'skills') {
                list_title.textContent = value === 'None'? 'No skills Yet': value;
            }
            else {
                list_title.textContent = value;
            }

            gender_list_content.innerHTML = `
<table class="table table-striped">
    <thead>
        <tr>
            <th>Name</th>
            <th>Age</th>
        </tr>
    </thead>       
    <tbody>
        ${table_rows}
    </tbody>     
</table>
            `
        })

    // for (let item in gender_list) {
    //     console.log(item)
    // }

}


const validate_suggestion_complaint_message_dialog = () => {
    const title = document.getElementById('suggestion_complaint_title').value;
    const message = document.getElementById('suggestion_complaint_message').value;
    const button = document.getElementById('suggestion_complaint_submit_button');

    if (title && message) {
        button.removeAttribute('disabled');
    }
    else {
        button.setAttribute('disabled', 'true');
    }
}

const clear_suggestion_complaint_message_dialog_inputs = () => {
    document.getElementById('suggestion_complaint_title').value = "";
    document.getElementById('suggestion_complaint_message').value = "";
    document.getElementById('suggestion_complaint_submit_button').setAttribute('disabled', 'true');
    document.getElementById('suggestion_complaint_anonymous').checked = false;
}

const send_suggestion_complaint_message = (url) => {
//    Retrieve the details from the suggestion or complaint dialog box
//    and send it to the server for storage

//    Retrieve details from the dialog box
    const title = document.getElementById('suggestion_complaint_title').value;
    const category = document.getElementById('suggestion_complaint_category').value;
    const level_of_urgency = document.getElementById('suggestion_complaint_level_of_urgency').value;
    const message = document.getElementById('suggestion_complaint_message').value;
    let is_anonymous = document.getElementById('suggestion_complaint_anonymous').checked;
    console.log(url)
    url = `${url}?title=${title}&category=${category}&level_of_urgency=${level_of_urgency}&message=${message}&is_anonymous=${is_anonymous}`;

    fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
        }
    })
        .then(response => response.json())
        .then(data => {
            const confirmation = data['confirm']

            if (confirmation) {
                const status = document.getElementById('suggestion_complaint_success_status');
                status.style.display = 'block';

                setTimeout(() => {
                    status.style.display = 'none';
                }, 3000);
            }
            else {
                const status = document.getElementById('suggestion_complaint_error_status');
                status.style.display = 'block';

                setTimeout(() => {
                    status.style.display = 'none';
                }, 3000)
            }
        })
        .then(error => {
            console.log(error);
        })
}


const notification_is_activated = (url, notification_id) => {
    /*
        send a signal to the server notifying it that the user has 
        clicked on a particular notification and that it should be deactivated
        and possibly deleted from the database
    */
   
    fetch(url , {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'Accept': 'application/json',
        }
    })

}
