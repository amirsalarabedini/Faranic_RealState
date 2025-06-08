from .prompt_manager import prompt_manager


class BasePrompts:
    """
    Easy-to-use interface for common prompt templates.
    Provides methods for frequently used prompts without needing to remember
    category and template names.
    """
    
    @staticmethod
    def property_search(location: str, price_range: str, property_type: str, 
                       bedrooms: str, bathrooms: str, special_requirements: str = "None"):
        """Get a property search prompt."""
        return prompt_manager.get_prompt(
            'search', 'property_search',
            location=location,
            price_range=price_range,
            property_type=property_type,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            special_requirements=special_requirements
        )
    
    @staticmethod
    def market_analysis(location: str, time_period: str, property_types: str, price_range: str):
        """Get a market analysis prompt."""
        return prompt_manager.get_prompt(
            'search', 'market_analysis',
            location=location,
            time_period=time_period,
            property_types=property_types,
            price_range=price_range
        )
    
    @staticmethod
    def property_evaluation(property_details: str, location: str, asking_price: str,
                          property_type: str, year_built: str, condition: str):
        """Get a property evaluation prompt."""
        return prompt_manager.get_prompt(
            'search', 'property_evaluation',
            property_details=property_details,
            location=location,
            asking_price=asking_price,
            property_type=property_type,
            year_built=year_built,
            condition=condition
        )
    
    @staticmethod
    def financial_analysis(property_info: str, purchase_price: str, down_payment: str,
                          loan_terms: str, rental_income: str, monthly_expenses: str,
                          appreciation_rate: str):
        """Get a financial analysis prompt."""
        return prompt_manager.get_prompt(
            'analysis', 'financial_analysis',
            property_info=property_info,
            purchase_price=purchase_price,
            down_payment=down_payment,
            loan_terms=loan_terms,
            rental_income=rental_income,
            monthly_expenses=monthly_expenses,
            appreciation_rate=appreciation_rate
        )
    
    @staticmethod
    def comparative_analysis(property_a_details: str, property_b_details: str,
                           comparison_criteria: str, property_c_details: str = "N/A"):
        """Get a comparative analysis prompt."""
        return prompt_manager.get_prompt(
            'analysis', 'comparative_analysis',
            property_a_details=property_a_details,
            property_b_details=property_b_details,
            property_c_details=property_c_details,
            comparison_criteria=comparison_criteria
        )
    
    @staticmethod
    def real_estate_assistant(task_type: str, user_context: str, user_question: str):
        """Get a general real estate assistant prompt."""
        return prompt_manager.get_prompt(
            'chat', 'real_estate_assistant',
            task_type=task_type,
            user_context=user_context,
            user_question=user_question
        )
    
    @staticmethod
    def client_consultation(client_profile: str, client_goals: str, budget: str,
                          timeline: str, preferences: str, topic: str):
        """Get a client consultation prompt."""
        return prompt_manager.get_prompt(
            'chat', 'client_consultation',
            client_profile=client_profile,
            client_goals=client_goals,
            budget=budget,
            timeline=timeline,
            preferences=preferences,
            topic=topic
        )
    
    @staticmethod
    def trend_analysis(market_location: str, time_frame: str, property_segment: str, data_points: str):
        """Get a trend analysis prompt."""
        return prompt_manager.get_prompt(
            'analysis', 'trend_analysis',
            market_location=market_location,
            time_frame=time_frame,
            property_segment=property_segment,
            data_points=data_points
        ) 