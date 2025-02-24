/* JavaScript specific to the log entry view page goes here. */

// Get the array of hidden columns from local storage or set to empty array
let hiddenLogTblColumns = JSON.parse((localStorage.getItem('hiddenLogTblColumns') !== null ? localStorage.getItem('hiddenLogTblColumns') : JSON.stringify([])));

// Assemble the array of column information for the table
let columnInfo = []
columnInfo = [
    // [checkBoxID, columnClass, Pretty Name, name_in_json, toHtmlFunc (default `jsescape`), shownByDefault (default true)]
    ['identifierCheckBox', 'identifierColumn', 'Identifier', 'entry_identifier', undefined, false],
    ['startDateCheckBox', 'startDateColumn', 'Start Date', 'start_date', entry => jsEscape(entry).replace(/\.\d+/, "").replace("Z", "").replace("T", " ")],
    ['endDateCheckbox', 'endDateColumn', 'End Date', 'end_date', entry => jsEscape(entry).replace(/\.\d+/, "").replace("Z", "").replace("T", " ")],
    ['sourceIPCheckbox', 'sourceIPColumn', 'Source', 'source_ip'],
    ['destIPCheckbox', 'destIPColumn', 'Destination', 'dest_ip'],
    ['toolNameCheckbox', 'toolNameColumn', 'Tool Name', 'tool'],
    ['userContextCheckbox', 'userContextColumn', 'User Context', 'user_context'],
    ['commandCheckbox', 'commandColumn', 'Command', 'command'],
    ['descriptionCheckbox', 'descriptionColumn', 'Description', 'description'],
    ['outputCheckbox', 'outputColumn', 'Output', 'output'],
    ['commentsCheckbox', 'commentsColumn', 'Comments', 'comments'],
    ['operatorCheckbox', 'operatorColumn', 'Operator', 'operator_name'],
    ['tagsCheckbox', 'tagsColumn', 'Tags', 'tags', entry => stylizeTags(jsEscape(entry))],
    ['optionsCheckbox', 'optionsColumn', 'Options', ''],
]

// Generate a table row based on a log entry
function generateTableHeaders() {
    let out = "";
    columnInfo.forEach(column => {
        out += `<th class="${column[1]} align-middle">${column[2]}</th>`
    });
    return out;
}

// Convert a table row to JSON and copy it to the clipboard
function convertRowToJSON(row_id) {
    let $row = document.getElementById(row_id);
    let header = [];
    let rows = [];

    $('#oplogTable > thead > th').each(function () {
        header.push($(this).text())
    })

    for (let j = 0; j < $row.cells.length - 1; j++) {
        $row[header[j]] = $row.cells[j].innerText;
    }
    rows.push($row);

    // Convert the array of row values to JSON
    let rawJson = JSON.stringify(rows[0])
    let jsonObj = JSON.parse(rawJson)
    delete jsonObj["Identifier"]
    let json = JSON.stringify(jsonObj, null, 2)

    // Create a temporary input element to copy the JSON to the clipboard
    let $temp = $('<input>');
    $('body').append($temp);
    $temp.val(json).select();
    // If Clipboard API is unavailable, use the deprecated `execCommand`
    if (!navigator.clipboard) {
        document.execCommand('copy');
    // Otherwise, use the Clipboard API
    } else {
        navigator.clipboard.writeText(json).then(
            function () {
                console.log('Copied row JSON to clipboard')
                displayToastTop({
                    type: 'success',
                    string: 'Copied the row to the clipboard as JSON.',
                    title: 'Row Copied'
                });
            })
            .catch(
                function () {
                    console.log('Failed to copy row JSON to clipboard')
                });
    }
    $temp.remove();
}

// Generate a table row based on a log entry
function generateRow(entry) {
    let out = `<tr id="${entry["id"]}" class="editableRow">`;
    columnInfo.forEach(column => {
        if(column[0] == "optionsCheckbox") {
            out += `<td class="${column[1]} align-middle">
                <button class="btn" data-toggle="tooltip" data-placement="left" title="Create a copy of this log entry" onClick="copyEntry(this);" entry-id="${entry['id']}"><i class="fa fa-copy"></i></button>
                <button class="btn" data-toggle="tooltip" data-placement="left" title="Copy this entry to your clipboard as JSON" onClick="convertRowToJSON(${entry["id"]});"><i class="fas fa-clipboard"></i></button>
                <button class="btn danger" data-toggle="tooltip" data-placement="left" title="Delete this log entry" onClick="deleteEntry(this);" entry-id="${entry['id']}"><i class="fa fa-trash"></i></button>
            </td>`
        } else {
            let value = entry[column[3]];
            let filter = column[4] ?? jsEscape;
            out += `<td class="${column[1]} align-middle">${filter(value)}</td>`;
        }
    });
    return out + "</tr>";
}

// Add a placeholder row that spans the entire table
function addPlaceholderRow($table) {
    console.log('adding placeholder row')
    $table.prepend(`<tr id="oplogTableNoEntries"><td colspan="100%">No entries to display</td></tr>`)
}

// Remove the placeholder row that spans the entire table
function removePlaceholderRow($table) {
    $table.find('#oplogTableNoEntries').remove()
}

// Match checkboxes and column IDs to show or hide columns based on the checkbox state
function coupleCheckboxColumn(checkboxId, columnClass) {
    $(checkboxId).change(function () {
        if (!this.checked) {
            $(columnClass).hide()
            // Add column to hiddenLogTblColumns
            hiddenLogTblColumns.push(columnClass)
        } else {
            $(columnClass).show()
            // Remove column from hiddenLogTblColumns
            hiddenLogTblColumns = hiddenLogTblColumns.filter(function (value, _, _) {
                return value != columnClass;
            });
        }
        // Save hiddenLogTblColumns to localStorage
        localStorage.setItem('hiddenLogTblColumns', JSON.stringify(hiddenLogTblColumns));
        // Update classes to round corners of first and last header columns
        columnInfo.forEach(function (value, _, _) {
            let $col = $('.' + value[1])
            if ($col.hasClass('first-col')) {
                $col.removeClass('first-col')
            }
            if ($col.hasClass('last-col')) {
                $col.removeClass('last-col')
            }
        })
        let firstCol = $('th').filter(':visible').first()
        let lastCol = $('th').filter(':visible').last()
        if (!firstCol.hasClass('first-col')) {
            firstCol.addClass('first-col')
        }
        if (!lastCol.hasClass('last-col')) {
            lastCol.addClass('last-col')
        }
    });
}

// Build the column show/hide checkboxes
function buildColumnsCheckboxes() {
    columnInfo.forEach(function (value, _, _) {
        let checked = (value[5] === undefined || value[5]) ? "checked" : "";
        let checkboxEntry = `
        <div class="form-check-inline">
        <div class="custom-control custom-switch">
        <input type="checkbox" id="${value[0]}" class="form-check-input custom-control-input" ${checked}/>
        <label class="form-check-label custom-control-label" for="${value[0]}">${value[2]}</label>
        </div>
        </div>
        `
        $checkboxList.append(checkboxEntry)
        let headerColumn = `
        <th class="${value[1]} align-middle">${value[2]}</th>
        `
        $tableHeader.append(headerColumn)
        coupleCheckboxColumn('#' + value[0], '.' + value[1])

        if (hiddenLogTblColumns.includes('.' + value[1])) {
            $('#' + value[0]).prop('checked', false)
        }
    })
}

// Hide columns based on the "Select Columns" checkboxes
function hideColumns() {
    columnInfo.forEach(function (value, _, _) {
        $checkbox = $('#' + value[0])
        if (!$checkbox.prop('checked')) {
            $('.' + value[1]).hide()
        }
    })
}

// Update an existing row with new data from the server
function updateRow($existingRow, newRow) {
    $(newRow).children().each(function () {
        let className = $(this).attr('class').split(' ')[0]
        $existingRow.find('.' + className).html($(this).html())
    });
}

// Create a new entry when the create button is clicked
function createEntry(id) {
    socket.send(JSON.stringify({
        'action': 'create',
        'oplog_id': id
    }))
    displayToastTop({type: 'success', string: 'Successfully added a log entry.', title: 'Oplog Update'});
}

// Delete an entry when the delete button is clicked
function deleteEntry($ele) {
    let id = $($ele).attr('entry-id')
    socket.send(JSON.stringify({
        'action': 'delete',
        'oplogEntryId': id
    }))
    displayToastTop({type: 'success', string: 'Successfully deleted a log entry.', title: 'Oplog Update'});
}

// Create a copy of an entry when the copy button is clicked
function copyEntry($ele) {
    let id = $($ele).attr('entry-id')
    socket.send(JSON.stringify({
        'action': 'copy',
        'oplogEntryId': id
    }))
    displayToastTop({type: 'success', string: 'Successfully cloned a log entry.', title: 'Oplog Update'});
}

// Stylize the tags for display in the table
function stylizeTags(tagString) {
    let tags = tagString.split(',')
    let tagHtml = ''
    for (tag of tags) {
        if (tag == '') {
            continue
        }
        // Check for escaped version of `att&ck` to style the label
        if (tag.toUpperCase().includes("ATT&AMP;CK") || tag.toUpperCase().includes("ATTACK") || tag.toUpperCase().includes("MITRE") || tag.toUpperCase().includes("TTP")) {
            tagHtml += `<span class="badge badge-danger">${tag}</span>`
        } else if (tag.toUpperCase().includes("CREDS") || tag.toUpperCase().includes("CREDENTIALS")) {
            tagHtml += `<span class="badge badge-warning">${tag}</span>`
        } else if (tag.toUpperCase().includes("VULN")) {
            tagHtml += `<span class="badge badge-success">${tag}</span>`
        } else if (tag.toUpperCase().includes("DETECT")) {
            tagHtml += `<span class="badge badge-info">${tag}</span>`
        } else if (tag.toUpperCase().includes("OBJECTIVE")) {
            tagHtml += `<span class="badge badge-primary">${tag}</span>`
        } else {
            tagHtml += `<span class="badge badge-secondary">${tag}</span>`
        }
    }
    return tagHtml
}
