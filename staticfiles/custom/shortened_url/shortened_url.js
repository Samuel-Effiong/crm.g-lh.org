"use strict"

let currentPage = 1;
const itemsPerPage = 5;
let urlData = []

const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++ ) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrf_token = getCookie('csrftoken');


// TOAST NOTIFICATION JS

function showToast(message, toast_container, color, duration = 5000) {
    const toastContainer = document.getElementById(toast_container);

    // Create a new toast element
    const toast = document.createElement('div');
    toast.classList.add('toast');
    toast.style.backgroundColor = color

    toast.textContent = message;

    // Add the toast to the container
    toastContainer.appendChild(toast);

    // Show the toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    // Hide and remove the toast after the specified duration
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 500);
    }, duration);
}

// Example usage when an error occurs
function handleUrlError(errorMessage, toast_container) {
    showToast(errorMessage, toast_container, '#f44336');
}

function handleUrlSuccess(successMessage, toast_container) {
    showToast(successMessage, toast_container, '#28a745')
}

// Call handleAddUrlError() when an error happens during adding a new URL
// Example: handleAddUrlError('Failed to add the URL. Please try again.');


const fetch_data = (url) => {
    fetch(url)
    .then(response => response.json())
    .then(data => {
        urlData = data.urls;
        renderTable(urlData);
        updatePagination(urlData)
    })
    .catch(error => {
        console.log("Error fetching URL data: ", error)
    })
}

document.addEventListener('DOMContentLoaded', function() {
    fetch_data('/pastoring/shorten-url/?api=true')
});

function renderTable(data) {
    const urlList = document.getElementById('urlList');
    urlList.innerHTML = '';

    const start = (currentPage - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const paginatedData = data.slice(start, end);

    paginatedData.forEach((url, index) => {
        const row = document.createElement('tr');

        const originalCell = document.createElement('td');
        originalCell.textContent = url.original;

        const shortCell = document.createElement('td');
        const shortLink = document.createElement('a');
        shortLink.href = url.short;
        shortLink.textContent = url.short;
        shortLink.target = '_blank';
        shortCell.appendChild(shortLink);

        const dateCell = document.createElement('td');
        dateCell.textContent = url.date;

        const actionsCell = document.createElement('td');
        actionsCell.classList.add('actions');

        const copyButton = document.createElement('button');
        copyButton.textContent = 'Copy';
        copyButton.addEventListener('click', () => {
            navigator.clipboard.writeText(url.short).then(() => {
                alert('Short URL copied to clipboard!');
            });
        });

        const editButton = document.createElement('button');
        editButton.textContent = 'Edit';
        editButton.addEventListener('click', () => {
            openEditModal(index, url);
        });

        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.addEventListener('click', () => {
            fetch(`/pastoring/shorten-url/?delete=${url.original}`)
                .then(response => response.json())
                .then(data => {
                    let confirmation = data['confirmation']
                    console.log(confirmation)
                    
                    if (confirmation) {
                        deleteURL(index);
                    }
                    else {
                        let error_message = data['error_message']
                        handleUrlError(error_message, 'toast-container-failed')
                    }
                })
        });

        actionsCell.appendChild(copyButton);
        actionsCell.appendChild(editButton);
        actionsCell.appendChild(deleteButton);

        row.appendChild(originalCell);
        row.appendChild(shortCell);
        row.appendChild(dateCell);
        row.appendChild(actionsCell);

        urlList.appendChild(row); 
    });
}

function updatePagination(data) {
    const totalPages = Math.ceil(data.length / itemsPerPage);
    const pageInfo = document.getElementById('pageInfo');
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;

    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');

    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        // const urlData = getFilteredData();
        renderTable(urlData);
        updatePagination(urlData);
    }
}

function nextPage() {
    // const urlData = getFilteredData();
    const totalPages = Math.ceil(urlData.length / itemsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        renderTable(urlData);
        updatePagination(urlData);
    }
}

function searchURLs() {
    currentPage = 1;
    const urlData = getFilteredData();
    renderTable(urlData);
    updatePagination(urlData);
}

function sortURLs() {
    currentPage = 1;
    const urlData = getFilteredData();
    renderTable(urlData);
    updatePagination(urlData);
}

function getFilteredData() {
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const sortSelect = document.getElementById('sortSelect').value;

    urlData = urlData.filter(url =>
        url.original.toLowerCase().includes(searchInput) ||
        url.short.toLowerCase().includes(searchInput)
    );

    if (sortSelect === 'date') {
        urlData.sort((a, b) => new Date(b.date) - new Date(a.date));
    } else if (sortSelect === 'original') {
        urlData.sort((a, b) => a.original.localeCompare(b.original));
    } else if (sortSelect === 'short') {
        urlData.sort((a, b) => a.short.localeCompare(b.short));
    }

    return urlData;
}

function openEditModal(index, url) {
    const modal = document.getElementById('editModal');
    modal.style.display = 'flex';

    document.getElementById('editOriginalUrl').value = url.original;
    document.getElementById('editShortUrl').value = url.short;

    document.getElementById('editForm').onsubmit = (e) => {
        e.preventDefault();

        let original_url = document.getElementById('editOriginalUrl').value;
        let short_url = document.getElementById('editShortUrl').value;

        const formData = new FormData();
        formData.append('url_id', url.id);
        formData.append('original_url', original_url);
        formData.append('short_url', short_url)

        fetch('/pastoring/shorten-url/?edit=true', {
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

                if (confirmation) {
                    saveChanges(index);
                }
                else {
                    let error_message = data['error_message']?data['error_message']:'Love God with all your heart'
                    handleUrlError(error_message, 'toast-container-edit-modal')
                    console.log(error_message)
                }
            })
    };
}

function openAddModal() {
    const modal = document.getElementById('addModal');
    modal.style.display = 'flex';

    document.getElementById('addForm').onsubmit = (e) => {
        e.preventDefault();
        addNewURL();
    };
}

function closeModal() {
    const editModal = document.getElementById('editModal');
    const addModal = document.getElementById('addModal');
    editModal.style.display = 'none';
    addModal.style.display = 'none';
}

function saveChanges(index) {
    const urlData = getFilteredData();
    urlData[index].original = document.getElementById('editOriginalUrl').value;
    urlData[index].short = document.getElementById('editShortUrl').value;

    renderTable(urlData);
    updatePagination(urlData);
    closeModal();

    handleUrlSuccess("Url successfully changed", 'toast-container-success')
}

function addNewURL() {
    const newOriginalUrl = document.getElementById('addOriginalUrl').value;
    const newShortUrl = document.getElementById('addShortUrl').value;

    const headers = new Headers();
    headers.append('Content-Type', 'application/json');
    headers.append('X-CRSFToken', csrf_token)
    
    fetch('/pastoring/shorten-url/?api=true&method=add', {
        method: 'POST',
        credentials: 'same-origin',
        headers: headers,
        body: FormData
    })


    const newUrl = { original: newOriginalUrl, short: newShortUrl, date: new Date().toISOString().split('T')[0] };

    urlData = getFilteredData();
    urlData.push(newUrl);

    renderTable(urlData);
    updatePagination(urlData);
    closeModal();
}


function deleteURL(index) {
    let urlData = getFilteredData(); 
    urlData.splice(index, 1);

    renderTable(urlData);
    updatePagination(urlData);

    handleUrlSuccess(`url successfully deleted`, 'toast-container-success')
}


