/**
 * Code Generator JavaScript
 * Handles the UI interactions for code preview and download
 */
document.addEventListener('DOMContentLoaded', function() {
    // Globals
    let generatedFiles = {};
    let currentFile = null;
    let codeEditor = null;
    
    // DOM Elements
    const fileList = document.getElementById('fileList');
    const currentFileName = document.getElementById('currentFileName');
    const refreshCodeBtn = document.getElementById('refreshCodeBtn');
    const downloadCodeBtn = document.getElementById('downloadCodeBtn');
    const downloadFileBtn = document.getElementById('downloadFileBtn');
    const copyCodeBtn = document.getElementById('copyCodeBtn');
    
    // Initialize the UI
    initializeCodePreview();
    
    // ============= Functions =============
    
    /**
     * Initialize the code preview
     */
    function initializeCodePreview() {
        // Initialize CodeMirror editor
        initializeCodeEditor();
        
        // Set up event listeners
        setupEventListeners();
        
        // Generate or load code
        generateOrLoadCode();
    }
    
    /**
     * Initialize the CodeMirror editor
     */
    function initializeCodeEditor() {
        const editorElement = document.getElementById('codeEditor');
        
        codeEditor = CodeMirror(editorElement, {
            mode: 'text/x-java',
            theme: 'darcula',
            lineNumbers: true,
            readOnly: true,
            matchBrackets: true,
            autoCloseBrackets: true,
            indentWithTabs: true,
            tabSize: 4,
            lineWrapping: true,
            viewportMargin: Infinity
        });
        
        // Resize editor to fill container
        codeEditor.setSize('100%', '500px');
    }
    
    /**
     * Set up event listeners
     */
    function setupEventListeners() {
        // Refresh code button
        refreshCodeBtn.addEventListener('click', function() {
            generateOrLoadCode();
        });
        
        // Download all button
        downloadCodeBtn.addEventListener('click', function() {
            downloadAllFiles();
        });
        
        // Download single file button
        downloadFileBtn.addEventListener('click', function() {
            if (currentFile) {
                downloadSingleFile(currentFile, generatedFiles[currentFile]);
            }
        });
        
        // Copy code button
        copyCodeBtn.addEventListener('click', function() {
            if (currentFile) {
                copyToClipboard(generatedFiles[currentFile]);
            }
        });
    }
    
    /**
     * Generate or load code from the server
     */
    function generateOrLoadCode() {
        // Show loading state
        fileList.innerHTML = '<div class="p-3 text-center"><div class="spinner-border text-primary" role="status"></div><div class="mt-2">Generating code...</div></div>';
        currentFileName.textContent = 'Generating...';
        
        // Fetch generated code from the server
        fetch('/api/generate-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(getEntitiesFromSession())
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                generatedFiles = data.code;
                updateFileList();
                
                // Select the first file by default
                const firstFile = Object.keys(generatedFiles)[0];
                if (firstFile) {
                    selectFile(firstFile);
                }
            } else {
                showError('Error generating code: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('An error occurred while generating the code');
        });
    }
    
    /**
     * Get entities from session storage
     */
    function getEntitiesFromSession() {
        const entitiesJson = sessionStorage.getItem('entities');
        return entitiesJson ? JSON.parse(entitiesJson) : {};
    }
    
    /**
     * Update the file list in the sidebar
     */
    function updateFileList() {
        fileList.innerHTML = '';
        
        if (Object.keys(generatedFiles).length === 0) {
            fileList.innerHTML = '<div class="p-3 text-center text-muted">No files generated</div>';
            return;
        }
        
        // Group files by folder
        const filesByFolder = {};
        
        for (const filePath in generatedFiles) {
            const parts = filePath.split('/');
            const folder = parts.length > 1 ? parts.slice(0, -1).join('/') : '';
            const fileName = parts[parts.length - 1];
            
            if (!filesByFolder[folder]) {
                filesByFolder[folder] = [];
            }
            
            filesByFolder[folder].push({
                path: filePath,
                name: fileName
            });
        }
        
        // Create file list items grouped by folder
        for (const folder in filesByFolder) {
            // Add folder header if it's not the root
            if (folder) {
                const folderItem = document.createElement('div');
                folderItem.className = 'list-group-item list-group-item-secondary d-flex align-items-center';
                folderItem.innerHTML = `
                    <i class="fa-solid fa-folder me-2"></i>
                    <small>${folder}</small>
                `;
                fileList.appendChild(folderItem);
            }
            
            // Add files in this folder
            filesByFolder[folder].forEach(file => {
                const item = document.createElement('a');
                item.href = '#';
                item.className = 'list-group-item list-group-item-action d-flex align-items-center';
                
                if (currentFile === file.path) {
                    item.classList.add('active');
                }
                
                // Choose icon based on file extension
                let icon = 'fa-file-code';
                if (file.name.endsWith('.java')) {
                    icon = 'fa-brands fa-java';
                } else if (file.name.endsWith('.xml')) {
                    icon = 'fa-file-code';
                } else if (file.name.endsWith('.properties')) {
                    icon = 'fa-file-lines';
                }
                
                item.innerHTML = `
                    <i class="fa-solid ${icon} me-2"></i>
                    <span>${file.name}</span>
                `;
                
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    selectFile(file.path);
                });
                
                fileList.appendChild(item);
            });
        }
    }
    
    /**
     * Select a file to display in the editor
     */
    function selectFile(filePath) {
        currentFile = filePath;
        currentFileName.textContent = filePath;
        
        // Update file list selection
        const items = fileList.querySelectorAll('.list-group-item-action');
        items.forEach(item => item.classList.remove('active'));
        
        const selectedItem = Array.from(items).find(item => item.textContent.trim() === filePath.split('/').pop());
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        // Set the file content in the editor
        const content = generatedFiles[filePath] || '';
        
        // Set the appropriate mode based on file extension
        let mode = 'text/x-java';
        if (filePath.endsWith('.xml')) {
            mode = 'application/xml';
        } else if (filePath.endsWith('.properties')) {
            mode = 'text/plain';
        }
        
        codeEditor.setOption('mode', mode);
        codeEditor.setValue(content);
        
        // Format code
        setTimeout(() => {
            codeEditor.refresh();
        }, 10);
    }
    
    /**
     * Download all generated files as a zip
     */
    function downloadAllFiles() {
        // Check if files were generated
        if (Object.keys(generatedFiles).length === 0) {
            alert('No files to download');
            return;
        }
        
        // In a real implementation, this would create a ZIP file
        // Since we don't have access to ZIP libraries in this example,
        // we'll just show an alert that would trigger a server-side download
        
        alert('In a real implementation, this would download a ZIP file with all generated code. For now, please use the "Download" button for individual files.');
    }
    
    /**
     * Download a single file
     */
    function downloadSingleFile(filename, content) {
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
        element.setAttribute('download', filename.split('/').pop());
        
        element.style.display = 'none';
        document.body.appendChild(element);
        
        element.click();
        
        document.body.removeChild(element);
    }
    
    /**
     * Copy content to clipboard
     */
    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(
            function() {
                // Show a temporary success message
                const originalText = copyCodeBtn.innerHTML;
                copyCodeBtn.innerHTML = '<i class="fa-solid fa-check me-1"></i>Copied!';
                
                setTimeout(() => {
                    copyCodeBtn.innerHTML = originalText;
                }, 2000);
            },
            function(err) {
                console.error('Could not copy text: ', err);
                alert('Failed to copy to clipboard');
            }
        );
    }
    
    /**
     * Show an error message
     */
    function showError(message) {
        fileList.innerHTML = `<div class="p-3 text-center text-danger">${message}</div>`;
        currentFileName.textContent = 'Error';
        codeEditor.setValue('// An error occurred while generating the code');
    }
});
