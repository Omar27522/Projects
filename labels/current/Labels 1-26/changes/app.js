// Global variables
let entryCounter = 2; // Start from 2 since we have one example entry
let yamlFileHandle = null;

/**
 * Handle errors consistently
 * @param {Error} error - The error object
 * @param {string} context - Contextual information about where the error occurred
 */
function handleError(error, context) {
    console.error(`${context}:`, error);
    alert(`An error occurred while ${context}. Please try again.`);
}

/**
 * Get file handle with user permission
 * @returns {Promise<FileSystemFileHandle>} The file handle for the YAML file
 */
async function getYamlFileHandle() {
    if (!yamlFileHandle) {
        try {
            const handles = await window.showOpenFilePicker({
                types: [{
                    description: 'YAML files',
                    accept: {
                        'text/yaml': ['.yaml', '.yml']
                    }
                }],
                multiple: false
            });
            yamlFileHandle = handles[0];
        } catch (error) {
            handleError(error, 'getting file handle');
            throw error;
        }
    }
    return yamlFileHandle;
}

/**
 * Read and parse the YAML file
 * @returns {Promise<Object>} Parsed YAML data
 */
async function readYamlFile() {
    try {
        const fileHandle = await getYamlFileHandle();
        const file = await fileHandle.getFile();
        const content = await file.text();
        return jsyaml.load(content) || { entries: [] };
    } catch (error) {
        handleError(error, 'reading YAML file');
        return { entries: [] };
    }
}

/**
 * Save changes to YAML file
 * @param {Object} entry - The entry to save
 * @returns {Promise<void>}
 */
async function saveToYAML(entry) {
    try {
        const fileHandle = await getYamlFileHandle();
        const data = await readYamlFile();
        
        // Update or add entry
        const entryIndex = data.entries.findIndex(e => e.id === entry.id);
        if (entryIndex !== -1) {
            data.entries[entryIndex] = entry;
        } else {
            data.entries.push(entry);
        }
        
        // Generate YAML content with proper formatting
        const newYaml = jsyaml.dump(data, { 
            indent: 2,
            lineWidth: -1,
            noRefs: true 
        });

        // Write to file
        const writable = await fileHandle.createWritable();
        await writable.write(newYaml);
        await writable.close();
        
        console.log('Changes saved successfully to YAML file');
    } catch (error) {
        handleError(error, 'saving to YAML');
        alert('Failed to save changes. Please try again and make sure you have write permission.');
    }
}

/**
 * Load and display existing entries
 * @returns {Promise<void>}
 */
async function loadExistingEntries() {
    try {
        const data = await readYamlFile();
        // TODO: Update UI with existing entries
        console.log('Loaded entries:', data.entries);
    } catch (error) {
        handleError(error, 'loading entries');
    }
}

/**
 * Handle edit action
 * @param {HTMLElement} entryElement - The entry element to edit
 */
function handleEdit(entryElement) {
    const viewContent = entryElement.querySelector('.view-content');
    const editForm = entryElement.querySelector('.edit-form');
    
    // Populate form with current values
    const title = viewContent.querySelector('h2').textContent;
    const date = viewContent.querySelector('.change-date').textContent.replace('Added: ', '');
    const description = viewContent.querySelector('.change-description').innerHTML;
    const tags = Array.from(viewContent.querySelectorAll('.tag'))
        .map(tag => tag.textContent)
        .join(', ');
    const status = viewContent.querySelector('.status').classList[1];

    editForm.querySelector('.title-input').value = title;
    editForm.querySelector('.date-input').value = date;
    editForm.querySelector('.description-input').value = description;
    editForm.querySelector('.tag-input').value = tags;
    editForm.querySelector('.status-input').value = status;

    viewContent.classList.add('hidden');
    editForm.classList.add('active');
}

/**
 * Handle save action
 * @param {HTMLElement} entryElement - The entry element to save
 * @returns {Promise<void>}
 */
async function handleSave(entryElement) {
    const viewContent = entryElement.querySelector('.view-content');
    const editForm = entryElement.querySelector('.edit-form');
    
    // Get values from form
    const title = editForm.querySelector('.title-input').value;
    const date = editForm.querySelector('.date-input').value;
    const description = editForm.querySelector('.description-input').value;
    const tags = editForm.querySelector('.tag-input').value
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag); // Remove empty tags
    const status = editForm.querySelector('.status-input').value;

    // Create entry object
    const entry = {
        id: entryElement.dataset.id || Date.now(),
        title,
        date,
        description,
        tags,
        status
    };

    // Save to YAML file
    await saveToYAML(entry);

    // Update view content
    viewContent.querySelector('h2').textContent = title;
    viewContent.querySelector('.change-date').textContent = `Added: ${date}`;
    viewContent.querySelector('.change-description').innerHTML = description;
    
    // Update tags
    const tagContainer = viewContent.querySelector('.tags-container');
    const tagElements = tags.map(tag => 
        `<span class="tag">${tag}</span>`
    ).join('');
    
    tagContainer.innerHTML = tagElements + 
        `<span class="status ${status}">${status.replace('-', ' ')}</span>`;

    // Hide edit form and show view content
    viewContent.classList.remove('hidden');
    editForm.classList.remove('active');
}

/**
 * Handle cancel action
 * @param {HTMLElement} entryElement - The entry element to cancel editing
 */
function handleCancel(entryElement) {
    const viewContent = entryElement.querySelector('.view-content');
    const editForm = entryElement.querySelector('.edit-form');
    
    viewContent.classList.remove('hidden');
    editForm.classList.remove('active');
}

/**
 * Handle delete action
 * @param {HTMLElement} entryElement - The entry element to delete
 */
function handleDelete(entryElement) {
    if (confirm('Are you sure you want to delete this entry?')) {
        entryElement.remove();
        // TODO: Update YAML file after deletion
    }
}

/**
 * Handle add new entry action
 */
async function handleAddEntry() {
    try {
        if (!yamlFileHandle) {
            await getYamlFileHandle();
        }
        const currentDate = new Date().toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });

        const newEntryHtml = `
            <div class="change-entry" data-id="${entryCounter++}">
                <div class="view-content">
                    <div class="action-buttons">
                        <button class="edit-btn" data-action="edit" title="Edit">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="delete-btn" data-action="delete" title="Delete">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                    <h2>New Feature</h2>
                    <div class="change-date">Added: ${currentDate}</div>
                    <div class="change-description">
                        <p>Description goes here</p>
                    </div>
                    <div class="tags-container">
                        <span class="tag">New</span>
                        <span class="status planned">Planned</span>
                    </div>
                </div>
                <div class="edit-form">
                    <div class="form-group">
                        <input type="text" class="title-input" placeholder="Enter title">
                    </div>
                    <div class="form-group">
                        <input type="text" class="date-input" placeholder="Enter date">
                    </div>
                    <div class="form-group">
                        <textarea class="description-input" placeholder="Enter description (HTML supported)"></textarea>
                    </div>
                    <div class="form-group">
                        <input type="text" class="tag-input" placeholder="Enter tags (comma-separated)">
                    </div>
                    <div class="form-group">
                        <select class="status-input">
                            <option value="planned">Planned</option>
                            <option value="in-progress">In Progress</option>
                            <option value="completed">Completed</option>
                        </select>
                    </div>
                    <div class="form-actions">
                        <button class="save-btn" data-action="save">Save</button>
                        <button class="cancel-btn" data-action="cancel">Cancel</button>
                    </div>
                </div>
            </div>
        `;

        const entriesContainer = document.getElementById('entries-container');
        entriesContainer.insertAdjacentHTML('afterbegin', newEntryHtml);
        
        // Automatically open the edit form for the new entry
        const newEntry = entriesContainer.firstElementChild;
        handleEdit(newEntry);
    } catch (error) {
        handleError(error, 'adding new entry');
    }
}

// Event delegation for all button actions
document.addEventListener('click', (event) => {
    const target = event.target.closest('[data-action]');
    if (!target) return;

    const action = target.dataset.action;
    switch (action) {
        case 'add-entry':
            handleAddEntry();
            break;
        case 'edit':
            handleEdit(target.closest('.change-entry'));
            break;
        case 'save':
            handleSave(target.closest('.change-entry'));
            break;
        case 'cancel':
            handleCancel(target.closest('.change-entry'));
            break;
        case 'delete':
            handleDelete(target.closest('.change-entry'));
            break;
        default:
            console.warn(`Unknown action: ${action}`);
    }
});

// Initialize file access when page loads
window.addEventListener('load', async () => {
    try {
        await loadExistingEntries();
    } catch (error) {
        handleError(error, 'initializing file access');
    }
});
