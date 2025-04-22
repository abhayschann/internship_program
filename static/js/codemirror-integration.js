/**
 * CodeMirror Integration
 * Helper functions for CodeMirror integration
 */

/**
 * Create a CodeMirror instance for Java code
 */
function createJavaEditor(elementId, readOnly = false) {
    return CodeMirror(document.getElementById(elementId), {
        mode: 'text/x-java',
        theme: 'darcula',
        lineNumbers: true,
        indentWithTabs: true,
        tabSize: 4,
        lineWrapping: true,
        matchBrackets: true,
        autoCloseBrackets: true,
        readOnly: readOnly,
        viewportMargin: Infinity
    });
}

/**
 * Create a CodeMirror instance for XML code
 */
function createXmlEditor(elementId, readOnly = false) {
    return CodeMirror(document.getElementById(elementId), {
        mode: 'application/xml',
        theme: 'darcula',
        lineNumbers: true,
        indentWithTabs: true,
        tabSize: 4,
        lineWrapping: true,
        matchBrackets: true,
        autoCloseBrackets: true,
        readOnly: readOnly,
        viewportMargin: Infinity
    });
}

/**
 * Set the appropriate mode for CodeMirror based on file extension
 */
function setEditorModeByFilename(editor, filename) {
    let mode = 'text/x-java';
    
    if (filename.endsWith('.xml') || filename.endsWith('.pom')) {
        mode = 'application/xml';
    } else if (filename.endsWith('.properties')) {
        mode = 'text/plain';
    } else if (filename.endsWith('.md')) {
        mode = 'text/markdown';
    } else if (filename.endsWith('.html')) {
        mode = 'text/html';
    } else if (filename.endsWith('.yml') || filename.endsWith('.yaml')) {
        mode = 'text/x-yaml';
    }
    
    editor.setOption('mode', mode);
}

/**
 * Format code in a CodeMirror editor
 */
function formatCode(editor) {
    // This is a very basic implementation
    // A more sophisticated approach would use language-specific formatters
    const totalLines = editor.lineCount();
    const totalChars = editor.getTextArea().value.length;
    
    editor.autoFormatRange({ line: 0, ch: 0 }, { line: totalLines, ch: totalChars });
}

/**
 * Auto format range for CodeMirror
 * This extends CodeMirror with a basic auto-formatting capability
 */
CodeMirror.defineExtension("autoFormatRange", function(from, to) {
    const cm = this;
    const mode = cm.getOption("mode");
    
    // Different formatting logic based on the mode
    if (mode === "text/x-java" || mode === "application/xml") {
        // Indent each line
        for (let i = from.line; i <= to.line; i++) {
            cm.indentLine(i);
        }
    }
});
