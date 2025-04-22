/**
 * Main JavaScript file for the Spring Boot REST API Generator
 * Contains shared utilities and initialization code
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Handle flash messages auto-dismiss
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(function(flash) {
        setTimeout(function() {
            const closeButton = flash.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000); // Auto-dismiss after 5 seconds
    });

    // Utility functions for entity data management
    window.entityUtils = {
        /**
         * Save entity data to session storage
         * @param {Object} entities - The entities to save
         */
        saveEntities: function(entities) {
            sessionStorage.setItem('entities', JSON.stringify(entities));
        },

        /**
         * Load entity data from session storage
         * @returns {Object} The loaded entities or an empty object
         */
        loadEntities: function() {
            const entitiesJson = sessionStorage.getItem('entities');
            return entitiesJson ? JSON.parse(entitiesJson) : {};
        },

        /**
         * Clear all entity data from session storage
         */
        clearEntities: function() {
            sessionStorage.removeItem('entities');
        },

        /**
         * Validate entity name (PascalCase)
         * @param {string} name - The entity name to validate
         * @returns {boolean} True if valid, false otherwise
         */
        isValidEntityName: function(name) {
            return /^[A-Z][a-zA-Z0-9]*$/.test(name);
        },

        /**
         * Validate field name (camelCase)
         * @param {string} name - The field name to validate
         * @returns {boolean} True if valid, false otherwise
         */
        isValidFieldName: function(name) {
            return /^[a-z][a-zA-Z0-9]*$/.test(name);
        },

        /**
         * Convert string to PascalCase
         * @param {string} str - The string to convert
         * @returns {string} The PascalCase string
         */
        toPascalCase: function(str) {
            return str.replace(/\w+/g, function(w) {
                return w[0].toUpperCase() + w.slice(1).toLowerCase();
            });
        },

        /**
         * Convert string to camelCase
         * @param {string} str - The string to convert
         * @returns {string} The camelCase string
         */
        toCamelCase: function(str) {
            str = this.toPascalCase(str);
            return str.charAt(0).toLowerCase() + str.slice(1);
        },

        /**
         * Convert string to plural form
         * @param {string} str - The string to convert
         * @returns {string} The plural form
         */
        pluralize: function(str) {
            // Very basic pluralization
            if (str.endsWith('y')) {
                return str.slice(0, -1) + 'ies';
            } else if (str.endsWith('s') || str.endsWith('x') || str.endsWith('z') || 
                       str.endsWith('ch') || str.endsWith('sh')) {
                return str + 'es';
            } else {
                return str + 's';
            }
        }
    };

    // API utilities
    window.apiUtils = {
        /**
         * Generate code from entity data
         * @param {Object} entityData - The entity data
         * @returns {Promise} A promise that resolves to the generated code
         */
        generateCode: function(entityData) {
            return fetch('/api/generate-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(entityData)
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    throw new Error(data.error || 'Failed to generate code');
                }
                return data.code;
            });
        },

        /**
         * Parse Spring Boot code
         * @param {string} code - The code to parse
         * @returns {Promise} A promise that resolves to the parsed entities
         */
        parseCode: function(code) {
            return fetch('/api/parse-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ code: code })
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    throw new Error(data.error || 'Failed to parse code');
                }
                return data.entities;
            });
        },

        /**
         * Get template code
         * @param {string} templateName - The name of the template
         * @returns {Promise} A promise that resolves to the template code
         */
        getTemplate: function(templateName) {
            return fetch(`/api/get-template?template=${templateName}`)
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    throw new Error(data.error || 'Failed to get template');
                }
                return data.code;
            });
        }
    };

    // DOM utilities
    window.domUtils = {
        /**
         * Create an element with attributes and children
         * @param {string} tag - The tag name
         * @param {Object} attrs - The attributes
         * @param {Array|string} children - The children
         * @returns {HTMLElement} The created element
         */
        createElement: function(tag, attrs = {}, children = []) {
            const element = document.createElement(tag);
            
            // Set attributes
            for (const [key, value] of Object.entries(attrs)) {
                if (key === 'className') {
                    element.className = value;
                } else if (key === 'innerHTML') {
                    element.innerHTML = value;
                } else {
                    element.setAttribute(key, value);
                }
            }
            
            // Append children
            if (typeof children === 'string') {
                element.textContent = children;
            } else if (Array.isArray(children)) {
                children.forEach(child => {
                    if (typeof child === 'string') {
                        element.appendChild(document.createTextNode(child));
                    } else if (child instanceof Node) {
                        element.appendChild(child);
                    }
                });
            }
            
            return element;
        },

        /**
         * Show an alert message
         * @param {string} message - The message to show
         * @param {string} type - The alert type (success, danger, warning, info)
         * @param {number} duration - The duration in milliseconds
         */
        showAlert: function(message, type = 'info', duration = 5000) {
            const alertContainer = document.createElement('div');
            alertContainer.className = 'position-fixed top-0 start-50 translate-middle-x p-3';
            alertContainer.style.zIndex = '9999';
            
            const alertEl = document.createElement('div');
            alertEl.className = `alert alert-${type} alert-dismissible fade show`;
            alertEl.setAttribute('role', 'alert');
            alertEl.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            alertContainer.appendChild(alertEl);
            document.body.appendChild(alertContainer);
            
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alertEl);
                bsAlert.close();
                // Remove from DOM after animation
                alertEl.addEventListener('closed.bs.alert', () => {
                    document.body.removeChild(alertContainer);
                });
            }, duration);
        }
    };
});
