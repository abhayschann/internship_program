from app import db
import json
from datetime import datetime

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    entities = db.relationship('Entity', backref='project', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Project {self.name}>'

class Entity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    config = db.Column(db.Text)  # JSON string for configuration
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    fields = db.relationship('Field', backref='entity', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Entity {self.name}>'
    
    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'config': json.loads(self.config) if self.config else {},
            'fields': [field.to_dict() for field in self.fields]
        }

class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    validations = db.Column(db.Text)  # JSON string for validations
    reference = db.Column(db.String(100))  # For entity references
    entity_id = db.Column(db.Integer, db.ForeignKey('entity.id'), nullable=False)
    
    def __repr__(self):
        return f'<Field {self.name}>'
    
    def to_dict(self):
        return {
            'name': self.name,
            'type': self.type,
            'validations': json.loads(self.validations) if self.validations else [],
            'reference': self.reference
        }

class GeneratedCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    project = db.relationship('Project', backref=db.backref('generated_files', lazy=True, cascade="all, delete-orphan"))
    
    def __repr__(self):
        return f'<GeneratedCode {self.filename}>'