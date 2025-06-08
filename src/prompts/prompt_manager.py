import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class PromptManager:
    """
    A comprehensive prompt template manager for handling reusable prompts
    with variable substitution and template organization.
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the PromptManager.
        
        Args:
            templates_dir: Directory containing prompt templates. 
                          Defaults to the templates folder in this module.
        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent / "templates"
        
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize template categories
        self._templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all templates from the templates directory."""
        if not self.templates_dir.exists():
            return
        
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    category = template_file.stem
                    self._templates[category] = template_data
            except Exception as e:
                print(f"Warning: Could not load template {template_file}: {e}")
    
    def get_prompt(self, category: str, template_name: str, **kwargs) -> str:
        """
        Get a formatted prompt template.
        
        Args:
            category: Template category (e.g., 'search', 'analysis', 'chat')
            template_name: Name of the specific template
            **kwargs: Variables to substitute in the template
            
        Returns:
            Formatted prompt string
            
        Raises:
            KeyError: If category or template_name doesn't exist
        """
        if category not in self._templates:
            raise KeyError(f"Template category '{category}' not found. Available categories: {list(self._templates.keys())}")
        
        if template_name not in self._templates[category]:
            available_templates = list(self._templates[category].keys())
            raise KeyError(f"Template '{template_name}' not found in category '{category}'. Available templates: {available_templates}")
        
        template = self._templates[category][template_name]
        
        # Handle both string templates and dict templates with metadata
        if isinstance(template, dict):
            prompt_text = template.get('prompt', template.get('text', ''))
        else:
            prompt_text = template
        
        try:
            return prompt_text.format(**kwargs)
        except KeyError as e:
            raise KeyError(f"Missing required variable {e} for template '{category}.{template_name}'")
    
    def list_categories(self) -> list:
        """Get all available template categories."""
        return list(self._templates.keys())
    
    def list_templates(self, category: str) -> list:
        """Get all templates in a specific category."""
        if category not in self._templates:
            return []
        return list(self._templates[category].keys())
    
    def add_template(self, category: str, template_name: str, template: str, 
                    description: str = "", variables: list = None):
        """
        Add a new template dynamically.
        
        Args:
            category: Template category
            template_name: Name for the template
            template: The template string with {variable} placeholders
            description: Optional description of the template
            variables: List of expected variable names
        """
        if category not in self._templates:
            self._templates[category] = {}
        
        template_data = {
            'prompt': template,
            'description': description,
            'variables': variables or []
        }
        
        self._templates[category][template_name] = template_data
        
        # Save to file
        self._save_template_category(category)
    
    def _save_template_category(self, category: str):
        """Save a template category to its JSON file."""
        template_file = self.templates_dir / f"{category}.json"
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(self._templates[category], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save template category {category}: {e}")
    
    def get_template_info(self, category: str, template_name: str) -> Dict[str, Any]:
        """
        Get metadata about a template.
        
        Returns:
            Dictionary with template info including description and variables
        """
        if category not in self._templates or template_name not in self._templates[category]:
            return {}
        
        template = self._templates[category][template_name]
        if isinstance(template, dict):
            return {
                'description': template.get('description', ''),
                'variables': template.get('variables', []),
                'prompt': template.get('prompt', template.get('text', ''))
            }
        else:
            return {'prompt': template, 'description': '', 'variables': []}


# Global instance for easy access
prompt_manager = PromptManager() 