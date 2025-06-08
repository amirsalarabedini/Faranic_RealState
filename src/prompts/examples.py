"""
Examples demonstrating how to use the prompt template system.
Run this file to see the prompt templates in action.
"""

from src.prompts import PromptManager, BasePrompts


def demonstrate_basic_usage():
    """Show basic usage of the PromptManager."""
    print("=== Basic PromptManager Usage ===\n")
    
    # Initialize the prompt manager
    pm = PromptManager()
    
    # List available categories
    print("Available categories:", pm.list_categories())
    
    # List templates in a category
    print("Search templates:", pm.list_templates('search'))
    print("Analysis templates:", pm.list_templates('analysis'))
    print("Chat templates:", pm.list_templates('chat'))
    print()


def demonstrate_property_search():
    """Demonstrate property search prompt."""
    print("=== Property Search Example ===\n")
    
    # Using BasePrompts (easier)
    prompt = BasePrompts.property_search(
        location="Downtown Miami, FL",
        price_range="$300,000 - $500,000",
        property_type="Condo",
        bedrooms="2-3",
        bathrooms="2+",
        special_requirements="Ocean view, modern amenities, parking included"
    )
    
    print("Generated Prompt:")
    print("-" * 50)
    print(prompt)
    print("-" * 50)
    print()


def demonstrate_financial_analysis():
    """Demonstrate financial analysis prompt."""
    print("=== Financial Analysis Example ===\n")
    
    prompt = BasePrompts.financial_analysis(
        property_info="2BR/2BA condo in Brickell, Miami - 1,200 sq ft, built 2018",
        purchase_price="$450,000",
        down_payment="$90,000 (20%)",
        loan_terms="30-year fixed at 6.5%",
        rental_income="$3,200/month",
        monthly_expenses="$800 (HOA: $400, Insurance: $200, Property Tax: $200)",
        appreciation_rate="3% annually"
    )
    
    print("Generated Prompt:")
    print("-" * 50)
    print(prompt)
    print("-" * 50)
    print()


def demonstrate_direct_prompt_manager():
    """Show direct PromptManager usage for more control."""
    print("=== Direct PromptManager Usage ===\n")
    
    pm = PromptManager()
    
    # Get template info
    info = pm.get_template_info('analysis', 'comparative_analysis')
    print("Template Info:")
    print(f"Description: {info['description']}")
    print(f"Required Variables: {info['variables']}")
    print()
    
    # Use the template
    prompt = pm.get_prompt(
        'analysis', 'comparative_analysis',
        property_a_details="Property A: $400K, 2BR/2BA, Downtown",
        property_b_details="Property B: $380K, 2BR/1BA, Midtown", 
        property_c_details="Property C: $420K, 3BR/2BA, Suburbs",
        comparison_criteria="ROI potential, location convenience, rental demand"
    )
    
    print("Generated Comparative Analysis Prompt:")
    print("-" * 50)
    print(prompt)
    print("-" * 50)
    print()


def demonstrate_adding_custom_template():
    """Show how to add custom templates dynamically."""
    print("=== Adding Custom Template ===\n")
    
    pm = PromptManager()
    
    # Add a custom template
    custom_template = """
    Create a detailed inspection checklist for a {property_type} property.
    
    Property Details:
    - Location: {location}
    - Age: {property_age}
    - Size: {property_size}
    - Special Concerns: {special_concerns}
    
    Generate a comprehensive inspection checklist covering:
    1. Structural elements
    2. Electrical systems
    3. Plumbing
    4. HVAC
    5. Exterior condition
    6. Interior condition
    7. Safety features
    8. Property-specific items
    
    Prioritize items based on property age and type.
    Include estimated costs for common issues found.
    """
    
    pm.add_template(
        category='inspection',
        template_name='property_inspection',
        template=custom_template.strip(),
        description='Generate property inspection checklist',
        variables=['property_type', 'location', 'property_age', 'property_size', 'special_concerns']
    )
    
    print("Added custom inspection template!")
    print("Available categories now:", pm.list_categories())
    
    # Use the new template
    prompt = pm.get_prompt(
        'inspection', 'property_inspection',
        property_type='Single Family Home',
        location='Coral Gables, FL',
        property_age='25 years (built 1999)',
        property_size='2,500 sq ft, 4BR/3BA',
        special_concerns='Potential roof issues, older electrical panel'
    )
    
    print("\nGenerated Inspection Checklist Prompt:")
    print("-" * 50)
    print(prompt)
    print("-" * 50)
    print()


def demonstrate_chat_assistant():
    """Demonstrate chat assistant prompt."""
    print("=== Chat Assistant Example ===\n")
    
    prompt = BasePrompts.real_estate_assistant(
        task_type="First-time home buying guidance",
        user_context="Young professional, stable income $75K, saved $50K for down payment, looking in Tampa Bay area",
        user_question="What should I know about the home buying process and what price range should I consider?"
    )
    
    print("Generated Chat Assistant Prompt:")
    print("-" * 50)
    print(prompt)
    print("-" * 50)
    print()


if __name__ == "__main__":
    """Run all examples."""
    demonstrate_basic_usage()
    demonstrate_property_search()
    demonstrate_financial_analysis()
    demonstrate_direct_prompt_manager()
    demonstrate_adding_custom_template()
    demonstrate_chat_assistant()
    
    print("=== Summary ===")
    print("The prompt template system provides:")
    print("1. Organized, reusable prompt templates")
    print("2. Easy variable substitution")
    print("3. Multiple ways to access templates (BasePrompts vs PromptManager)")
    print("4. Dynamic template addition")
    print("5. Template metadata and documentation")
    print("6. JSON-based storage for easy editing")
    print("\nYou can now use this system throughout your real estate application!") 