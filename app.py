import os
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from utils.code_generator import generate_spring_boot_code
from utils.code_parser import parse_spring_boot_code
from utils.templates import get_template_code

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/entity-editor')
def entity_editor():
    entity_data = session.get('entity_data', {})
    return render_template('entity_editor.html', entity_data=entity_data)

@app.route('/code-preview')
def code_preview():
    entity_data = session.get('entity_data', {})
    if not entity_data:
        flash('Please define at least one entity first', 'warning')
        return redirect(url_for('entity_editor'))
    
    return render_template('code_preview.html', entity_data=entity_data)

@app.route('/import-code')
def import_code():
    return render_template('import_code.html')

@app.route('/api/generate-code', methods=['POST'])
def api_generate_code():
    try:
        entity_data = request.json
        session['entity_data'] = entity_data
        
        generated_code = generate_spring_boot_code(entity_data)
        return jsonify({"success": True, "code": generated_code})
    except Exception as e:
        logger.error(f"Error generating code: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/parse-code', methods=['POST'])
def api_parse_code():
    try:
        code = request.json.get('code', '')
        parsed_entities = parse_spring_boot_code(code)
        session['entity_data'] = parsed_entities
        return jsonify({"success": True, "entities": parsed_entities})
    except Exception as e:
        logger.error(f"Error parsing code: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/get-template', methods=['GET'])
def api_get_template():
    template_name = request.args.get('template')
    if not template_name:
        return jsonify({"success": False, "error": "No template specified"}), 400
    
    template_code = get_template_code(template_name)
    if not template_code:
        return jsonify({"success": False, "error": f"Template {template_name} not found"}), 404
    
    return jsonify({"success": True, "code": template_code})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
