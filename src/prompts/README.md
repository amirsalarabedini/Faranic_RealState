# Prompt Template System

A comprehensive, organized system for managing reusable AI prompts in your real estate application.

## 🎯 Why Use This System?

- **Consistency**: Standardized prompts across your application
- **Maintainability**: Easy to update prompts without changing code
- **Reusability**: Write once, use everywhere
- **Organization**: Categorized templates for different use cases
- **Flexibility**: Support for variable substitution and dynamic templates

## 📁 Structure

```
src/prompts/
├── __init__.py              # Package initialization
├── prompt_manager.py        # Core PromptManager class
├── base_templates.py        # Easy-to-use template methods
├── examples.py             # Usage examples
├── README.md               # This documentation
└── templates/              # JSON template files
    ├── search.json         # Property search templates
    ├── analysis.json       # Analysis templates
    └── chat.json          # Conversational templates
```

## 🚀 Quick Start

### Method 1: Using BasePrompts (Recommended for common tasks)

```python
from src.prompts import BasePrompts

# Property search
prompt = BasePrompts.property_search(
    location="Miami, FL",
    price_range="$300K-$500K",
    property_type="Condo",
    bedrooms="2-3",
    bathrooms="2+",
    special_requirements="Ocean view"
)

# Financial analysis
prompt = BasePrompts.financial_analysis(
    property_info="2BR/2BA condo in Brickell",
    purchase_price="$450,000",
    down_payment="$90,000",
    loan_terms="30-year fixed at 6.5%",
    rental_income="$3,200/month",
    monthly_expenses="$800",
    appreciation_rate="3% annually"
)
```

### Method 2: Using PromptManager (For advanced control)

```python
from src.prompts import PromptManager

pm = PromptManager()

# List available templates
print("Categories:", pm.list_categories())
print("Search templates:", pm.list_templates('search'))

# Get a specific prompt
prompt = pm.get_prompt(
    'analysis', 'comparative_analysis',
    property_a_details="Property A details...",
    property_b_details="Property B details...",
    comparison_criteria="ROI, location, rental demand"
)

# Get template information
info = pm.get_template_info('search', 'property_search')
print("Required variables:", info['variables'])
```

## 📋 Available Templates

### Search Templates (`search.json`)
- **property_search**: Find properties based on criteria
- **market_analysis**: Analyze real estate markets
- **property_evaluation**: Evaluate individual properties

### Analysis Templates (`analysis.json`)
- **financial_analysis**: Comprehensive financial analysis
- **comparative_analysis**: Compare multiple properties
- **trend_analysis**: Market trend analysis

### Chat Templates (`chat.json`)
- **real_estate_assistant**: General assistant conversations
- **client_consultation**: Client consultation sessions
- **follow_up**: Follow-up conversations with context

## 🔧 Adding Custom Templates

### Method 1: Add via Code

```python
from src.prompts import PromptManager

pm = PromptManager()

pm.add_template(
    category='inspection',
    template_name='property_inspection',
    template="""
    Create an inspection checklist for {property_type} in {location}.
    Focus on {special_concerns}.
    """,
    description='Property inspection checklist generator',
    variables=['property_type', 'location', 'special_concerns']
)
```

### Method 2: Add via JSON File

Create a new JSON file in `src/prompts/templates/`:

```json
{
  "template_name": {
    "prompt": "Your template with {variables} here",
    "description": "What this template does",
    "variables": ["list", "of", "required", "variables"]
  }
}
```

## 💡 Best Practices

### 1. Variable Naming
- Use descriptive variable names: `{property_type}` not `{type}`
- Use snake_case: `{special_requirements}` not `{specialRequirements}`

### 2. Template Organization
- Group related templates in the same category
- Use clear, descriptive template names
- Include descriptions and variable lists

### 3. Error Handling
```python
try:
    prompt = pm.get_prompt('category', 'template', var1='value1')
except KeyError as e:
    print(f"Template error: {e}")
```

### 4. Template Design
- Make prompts specific and actionable
- Include clear instructions and expected output format
- Use consistent formatting across templates

## 🔄 Integration Examples

### With OpenAI API
```python
import openai
from src.prompts import BasePrompts

# Generate prompt
prompt = BasePrompts.property_search(
    location="Tampa, FL",
    price_range="$200K-$400K",
    property_type="Single Family",
    bedrooms="3+",
    bathrooms="2+",
    special_requirements="Good schools nearby"
)

# Use with OpenAI
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
```

### With Your Agents
```python
from src.prompts import BasePrompts
from src.agents import RealEstateAgent

agent = RealEstateAgent()

# Use template for consistent agent behavior
prompt = BasePrompts.client_consultation(
    client_profile="First-time buyer, $80K income",
    client_goals="Buy primary residence",
    budget="$300K max",
    timeline="6 months",
    preferences="Modern, low maintenance",
    topic="Mortgage pre-approval process"
)

response = agent.process(prompt)
```

## 🧪 Testing Your Templates

Run the examples to see all templates in action:

```bash
cd /path/to/your/project
python -m src.prompts.examples
```

## 📈 Benefits

1. **Consistency**: All team members use the same high-quality prompts
2. **Efficiency**: No need to write prompts from scratch each time
3. **Maintainability**: Update prompts in one place, affects entire application
4. **Quality**: Well-tested, optimized prompts for better AI responses
5. **Scalability**: Easy to add new templates as your application grows
6. **Documentation**: Self-documenting system with descriptions and variable lists

## 🔮 Future Enhancements

- Template versioning
- A/B testing for prompt effectiveness
- Template performance analytics
- Web interface for non-technical users
- Integration with prompt optimization tools

---

**Happy prompting!** 🏠✨ 