let count = 1;
let field_names = "";


function buildTable(table_id) {
    let tableBody = document.getElementById(table_id),
        firstRow = tableBody.firstElementChild,
        cloneRow = firstRow.cloneNode(true);

    tableBody.append(cloneRow);
    refreshTable(tableBody.firstElementChild); //refresh table on each add

    document.getElementById('field_id').value += ` ${count}`;
}

function refreshTable(firstRow) {
    let children = firstRow.children;

    children = Array.isArray(children) ? children : Object.values(children); //array check

    count++;
    children.forEach(x => {
        let element = x.firstElementChild.firstElementChild;

        if (element.tagName.toLowerCase() === 'input'){
            element.setAttribute('name', `field_name_${count}`);
            element.setAttribute('required', '');
            element.value = "";
        }
        else if (element.tagName.toLowerCase() === 'select') {
            element.setAttribute('name',`field_type_${count}`)
        }
    });
}

function removeRow(row) {
    if (row.closest('tbody').childElementCount === 1) {
        alert("This row can't be deleted");
    } else {
        row.closest('tr').remove();
    }
}