/**
 * Entity Editor JavaScript
 * Handles the UI interactions for creating and editing entities
 */
document.addEventListener('DOMContentLoaded', function() {
    // Globals
    let entities = {};
    let currentEntity = null;
    
    // DOM Elements
    const entityList = document.getElementById('entityList');
    const entityForm = document.getElementById('entityForm');
    const entityEditorCard = document.getElementById('entityEditorCard');
    const entityEditorTitle = document.getElementById('entityEditorTitle');
    const fieldsContainer = document.getElementById('fieldsContainer');
    const entityName = document.getElementById('entityName');
    const entityDescription = document.getElementById('entityDescription');
    const addEntityBtn = document.getElementById('addEntityBtn');
    const deleteEntityBtn = document.getElementById('deleteEntityBtn');
    const addFieldBtn = document.getElementById('addFieldBtn');
    const saveEntityBtn = document.getElementById('saveEntityBtn');
    const cancelEntityBtn = document.getElementById('cancelEntityBtn');
    const generateCodeBtn = document.getElementById('generateCodeBtn');
    const clearAllBtn = document.getElementById('clearAllBtn');
    
    // Bootstrap Modals
    const addEntityModal = new bootstrap.Modal(document.getElementById('addEntityModal'));
    const deleteEntityModal = new bootstrap.Modal(document.getElementById('deleteEntityModal'));
    const newEntityNameInput = document.getElementById('newEntityName');
    const confirmAddEntityBtn = document.getElementById('confirmAddEntityBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    
    // Configuration checkboxes
    const generateController = document.getElementById('generateController');
    const generateService = document.getElementById('generateService');
    const generateRepository = document.getElementById('generateRepository');
    const generateSwagger = document.getElementById('generateSwagger');
    
    // Initialize the UI
    initializeApp();
    
    // ============= Functions =============
    
    /**
     * Initialize the application
     */
    function initializeApp() {
        // Load saved entities from session storage
        loadEntities();
        
        // Set up event listeners
        setupEventListeners();
        
        // Update the entity list
        updateEntityList();
        
        // Hide the entity form initially
        hideEntityForm();
    }
    
    /**
     * Load entities from session storage
     */
    function loadEntities() {
        // Try to get entities from session storage
        const entitiesJson = sessionStorage.getItem('entities');
        if (entitiesJson) {
            entities = JSON.parse(entitiesJson);
        }
    }
    
    /**
     * Save entities to session storage
     */
    function saveEntities() {
        sessionStorage.setItem('entities', JSON.stringify(entities));
    }
    
    /**
     * Set up event listeners
     */
    function setupEventListeners() {
        // Add entity button
        addEntityBtn.addEventListener('click', function() {
            newEntityNameInput.value = '';
            addEntityModal.show();
        });
        
        // Confirm add entity button
        confirmAddEntityBtn.addEventListener('click', function() {
            const name = newEntityNameInput.value.trim();
            if (name) {
                addEntityModal.hide();
                createNewEntity(name);
            } else {
                alert('Entity name is required');
            }
        });
        
        // Delete entity button
        deleteEntityBtn.addEventListener('click', function() {
            if (currentEntity) {
                deleteEntityModal.show();
            }
        });
        
        // Confirm delete button
        confirmDeleteBtn.addEventListener('click', function() {
            if (currentEntity) {
                deleteEntity(currentEntity);
                deleteEntityModal.hide();
            }
        });
        
        // Add field button
        addFieldBtn.addEventListener('click', function() {
            addNewField();
        });
        
        // Save entity button (form submit)
        entityForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveCurrentEntity();
        });
        
        // Cancel entity button
        cancelEntityBtn.addEventListener('click', function() {
            hideEntityForm();
        });
        
        // Generate code button
        generateCodeBtn.addEventListener('click', function() {
            generateCode();
        });
        
        // Clear all button
        clearAllBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to clear all entities? This cannot be undone.')) {
                entities = {};
                saveEntities();
                updateEntityList();
                hideEntityForm();
            }
        });
    }
    
    /**
     * Update the entity list in the sidebar
     */
    function updateEntityList() {
        entityList.innerHTML = '';
        
        if (Object.keys(entities).length === 0) {
            const emptyItem = document.createElement('li');
            emptyItem.className = 'list-group-item text-center text-muted';
            emptyItem.textContent = 'No entities defined';
            entityList.appendChild(emptyItem);
            return;
        }
        
        for (const name in entities) {
            const item = document.createElement('li');
            item.className = 'list-group-item d-flex justify-content-between align-items-center';
            if (currentEntity === name) {
                item.classList.add('active');
            }
            
            const entity = entities[name];
            const fieldsCount = entity.fields ? entity.fields.length : 0;
            
            item.innerHTML = `
                <span>${name}</span>
                <span class="badge bg-primary rounded-pill">${fieldsCount}</span>
            `;
            
            item.addEventListener('click', function() {
                editEntity(name);
            });
            
            entityList.appendChild(item);
        }
    }
    
    /**
     * Show the entity form for editing
     */
    function showEntityForm() {
        entityEditorCard.style.display = 'block';
        deleteEntityBtn.style.display = 'block';
    }
    
    /**
     * Hide the entity form
     */
    function hideEntityForm() {
        entityEditorCard.style.display = 'block';
        entityForm.reset();
        fieldsContainer.innerHTML = '';
        currentEntity = null;
        entityEditorTitle.textContent = 'Entity Details';
        deleteEntityBtn.style.display = 'none';
        updateEntityList();
    }
    
    /**
     * Create a new entity
     */
    function createNewEntity(name) {
        if (entities[name]) {
            alert(`Entity '${name}' already exists`);
            return;
        }
        
        entities[name] = {
            name: name,
            description: '',
            fields: [],
            config: {
                generateController: true,
                generateService: true,
                generateRepository: true,
                generateSwagger: true
            }
        };
        
        saveEntities();
        editEntity(name);
    }
    
    /**
     * Edit an existing entity
     */
    function editEntity(name) {
        currentEntity = name;
        const entity = entities[name];
        
        // Update form fields
        entityName.value = entity.name;
        entityDescription.value = entity.description || '';
        entityEditorTitle.textContent = `Editing: ${name}`;
        
        // Load entity configuration
        generateController.checked = entity.config?.generateController !== false;
        generateService.checked = entity.config?.generateService !== false;
        generateRepository.checked = entity.config?.generateRepository !== false;
        generateSwagger.checked = entity.config?.generateSwagger !== false;
        
        // Clear existing fields
        fieldsContainer.innerHTML = '';
        
        // Add fields to the form
        if (entity.fields && entity.fields.length > 0) {
            entity.fields.forEach(field => addFieldToForm(field));
        }
        
        showEntityForm();
        updateEntityList();
    }
    
    /**
     * Delete an entity
     */
    function deleteEntity(name) {
        if (entities[name]) {
            delete entities[name];
            saveEntities();
            hideEntityForm();
            updateEntityList();
        }
    }
    
    /**
     * Save the current entity being edited
     */
    function saveCurrentEntity() {
        if (!currentEntity) return;
        
        const name = entityName.value.trim();
        if (!name) {
            alert('Entity name is required');
            return;
        }
        
        // Get all field elements
        const fieldRows = fieldsContainer.querySelectorAll('.field-row');
        const fields = [];
        
        // Collect field data
        fieldRows.forEach(row => {
            const nameInput = row.querySelector('.field-name');
            const typeSelect = row.querySelector('.field-type');
            const referenceSelect = row.querySelector('.entity-reference');
            const validationCheckboxes = row.querySelectorAll('.validation-rule input[type="checkbox"]:checked');
            
            const fieldName = nameInput.value.trim();
            if (!fieldName) return; // Skip empty fields
            
            const fieldType = typeSelect.value;
            
            const validations = [];
            validationCheckboxes.forEach(checkbox => {
                validations.push(checkbox.value);
            });
            
            const field = {
                name: fieldName,
                type: fieldType,
                validations: validations
            };
            
            // If entity reference, save the referenced entity
            if (fieldType === 'Entity' || fieldType === 'Collection') {
                field.reference = referenceSelect.value;
            }
            
            fields.push(field);
        });
        
        // Check if the entity name has changed
        if (name !== currentEntity) {
            // Create a new entity with the new name
            entities[name] = {
                name: name,
                description: entityDescription.value,
                fields: fields,
                config: {
                    generateController: generateController.checked,
                    generateService: generateService.checked,
                    generateRepository: generateRepository.checked,
                    generateSwagger: generateSwagger.checked
                }
            };
            
            // Delete the old entity
            delete entities[currentEntity];
            currentEntity = name;
        } else {
            // Update the existing entity
            entities[name] = {
                name: name,
                description: entityDescription.value,
                fields: fields,
                config: {
                    generateController: generateController.checked,
                    generateService: generateService.checked,
                    generateRepository: generateRepository.checked,
                    generateSwagger: generateSwagger.checked
                }
            };
        }
        
        saveEntities();
        updateEntityList();
        
        // Show success message
        const toast = new bootstrap.Toast(Object.assign(document.createElement('div'), {
            className: 'toast align-items-center text-bg-success border-0 position-fixed bottom-0 end-0 m-3',
            innerHTML: `
                <div class="d-flex">
                    <div class="toast-body">
                        Entity saved successfully!
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            `
        }));
        document.body.appendChild(toast.element);
        toast.show();
        
        // Remove toast element after it's hidden
        toast.element.addEventListener('hidden.bs.toast', () => {
            document.body.removeChild(toast.element);
        });
    }
    
    /**
     * Add a new field to the entity form
     */
    function addNewField(fieldData = {}) {
        addFieldToForm(fieldData);
    }
    
    /**
     * Add a field to the entity form with given data
     */
    function addFieldToForm(fieldData = {}) {
        // Clone the field template
        const template = document.getElementById('fieldRowTemplate');
        const fieldRow = template.content.cloneNode(true).querySelector('.field-row');
        
        // Get field elements
        const nameInput = fieldRow.querySelector('.field-name');
        const typeSelect = fieldRow.querySelector('.field-type');
        const entityReferenceContainer = fieldRow.querySelector('.entity-reference-container');
        const entityReferenceSelect = fieldRow.querySelector('.entity-reference');
        const deleteButton = fieldRow.querySelector('.delete-field');
        const validationCheckboxes = fieldRow.querySelectorAll('.validation-rule input[type="checkbox"]');
        
        // Set field values if provided
        nameInput.value = fieldData.name || '';
        if (fieldData.type) {
            typeSelect.value = fieldData.type;
        }
        
        // Populate entity reference dropdown
        updateEntityReferenceDropdown(entityReferenceSelect);
        
        // Show/hide entity reference based on type
        if (fieldData.type === 'Entity' || fieldData.type === 'Collection') {
            entityReferenceContainer.style.display = 'block';
            entityReferenceSelect.value = fieldData.reference || '';
        }
        
        // Set validation checkboxes
        if (fieldData.validations) {
            validationCheckboxes.forEach(checkbox => {
                if (fieldData.validations.includes(checkbox.value)) {
                    checkbox.checked = true;
                }
            });
        }
        
        // Add event listeners
        typeSelect.addEventListener('change', function() {
            if (this.value === 'Entity' || this.value === 'Collection') {
                entityReferenceContainer.style.display = 'block';
                updateEntityReferenceDropdown(entityReferenceSelect);
            } else {
                entityReferenceContainer.style.display = 'none';
            }
        });
        
        deleteButton.addEventListener('click', function() {
            fieldRow.remove();
        });
        
        // Add the field to the container
        fieldsContainer.appendChild(fieldRow);
    }
    
    /**
     * Update the entity reference dropdown with current entities
     */
    function updateEntityReferenceDropdown(dropdown) {
        dropdown.innerHTML = '';
        
        // Add empty option
        const emptyOption = document.createElement('option');
        emptyOption.value = '';
        emptyOption.textContent = '-- Select Entity --';
        dropdown.appendChild(emptyOption);
        
        // Add all entities
        for (const name in entities) {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            dropdown.appendChild(option);
        }
    }
    
    /**
     * Generate Spring Boot code from the defined entities
     */
    function generateCode() {
        if (Object.keys(entities).length === 0) {
            alert('Please define at least one entity before generating code');
            return;
        }
        
        // Save any unsaved changes
        if (currentEntity) {
            saveCurrentEntity();
        }
        
        // Send entities to the server to generate code
        fetch('/api/generate-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(entities)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Redirect to code preview page
                window.location.href = '/code-preview';
            } else {
                alert('Error generating code: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while generating the code');
        });
    }
});
