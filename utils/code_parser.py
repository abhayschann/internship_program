"""
Code Parser Module
Parses Spring Boot code to extract entity definitions
"""

import re
import logging

logger = logging.getLogger(__name__)

def parse_spring_boot_code(code):
    """
    Parse Spring Boot code to extract entity definitions
    
    Args:
        code (str): Java code containing entity classes
        
    Returns:
        dict: Dictionary of entity definitions
    """
    try:
        entities = {}
        
        # Extract entity classes
        entity_pattern = r'@Entity\s+(?:@Table\s*\([^)]*\)\s*)?public\s+class\s+(\w+)(?:\s+extends\s+\w+)?\s*\{([\s\S]*?)(?:public\s+class|\Z)'
        entity_matches = re.finditer(entity_pattern, code, re.MULTILINE)
        
        for entity_match in entity_matches:
            entity_name = entity_match.group(1)
            entity_body = entity_match.group(2)
            
            # Extract description from comments
            description = ""
            description_pattern = r'/\*\*([\s\S]*?)\*/'
            description_match = re.search(description_pattern, code, re.MULTILINE)
            if description_match:
                description = description_match.group(1).strip()
                description = re.sub(r'^\s*\*\s*', '', description, flags=re.MULTILINE)
                description = description.strip()
            
            # Initialize entity
            entities[entity_name] = {
                'name': entity_name,
                'description': description,
                'fields': [],
                'config': {
                    'generateController': True,
                    'generateService': True,
                    'generateRepository': True,
                    'generateSwagger': True
                }
            }
            
            # Extract fields
            field_pattern = r'(?:@[^;]+\s+)*private\s+(\w+(?:<\w+>)?)\s+(\w+)\s*;'
            field_matches = re.finditer(field_pattern, entity_body, re.MULTILINE)
            
            for field_match in field_matches:
                field_type = field_match.group(1)
                field_name = field_match.group(2)
                
                # Skip id field as it will be added automatically
                if field_name == 'id':
                    continue
                
                field_def = {
                    'name': field_name,
                    'type': field_type,
                    'validations': []
                }
                
                # Check for validations/annotations in the field declaration
                field_pos = entity_body.find(field_match.group(0))
                field_start = max(0, field_pos - 200)  # Look back up to 200 chars
                field_context = entity_body[field_start:field_pos + len(field_match.group(0))]
                
                # Check for common validations
                if '@NotNull' in field_context or 'nullable\s*=\s*false' in field_context:
                    field_def['validations'].append('required')
                
                if '@Column' in field_context and 'unique\s*=\s*true' in field_context:
                    field_def['validations'].append('unique')
                
                # Check for entity relationships
                if '@ManyToOne' in field_context or '@OneToOne' in field_context:
                    field_def['type'] = 'Entity'
                    # Try to extract the referenced entity
                    if '.' in field_type:
                        # Handle fully qualified type names
                        field_def['reference'] = field_type.split('.')[-1]
                    else:
                        field_def['reference'] = field_type
                
                if '@OneToMany' in field_context or '@ManyToMany' in field_context:
                    field_def['type'] = 'Collection'
                    # Try to extract the referenced entity from generic type
                    if '<' in field_type and '>' in field_type:
                        generic_type = field_type[field_type.index('<')+1:field_type.index('>')]
                        if '.' in generic_type:
                            # Handle fully qualified type names
                            field_def['reference'] = generic_type.split('.')[-1]
                        else:
                            field_def['reference'] = generic_type
                
                entities[entity_name]['fields'].append(field_def)
        
        return entities
    except Exception as e:
        logger.error(f"Error parsing Spring Boot code: {str(e)}")
        raise
