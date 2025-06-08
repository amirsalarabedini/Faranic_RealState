from langsmith import traceable
from ...models.state import RISAState
from ...config.llm_config import get_default_llm

class QueryUnderstandingAgent:
    """Query understanding and intent analysis agent"""
    
    def __init__(self):
        self.llm = get_default_llm()
        print("✅ Query understanding agent initialized successfully")
    
    @traceable
    def understand_query(self, state: RISAState) -> RISAState:
        """Understand and categorize user queries to guide the analysis workflow"""
        print("🔄 Query Understanding and Intent Analysis...")
        
        # Use LLM to understand user intent
        prompt = f"""
        Analyze this real estate query from an Iranian user:
        
        Query: {state['user_query']}
        
        Determine:
        1. User type (investor, homebuyer, renter, developer, government)
        2. Primary intent (buy, sell, rent, invest, analyze market, policy impact)
        3. Information needs (price, location, timing, strategy, risk assessment)
        4. Urgency level (immediate, planning, research)
        5. Expertise level (beginner, intermediate, expert)
        6. Specific requirements or constraints
        
        Categorize the query and suggest which analysis modules are most relevant.
        Respond in structured format.
        """
        
        try:
            response = self.llm.invoke(prompt)
            
            # Extract intent from query keywords
            query_lower = state['user_query'].lower()
            
            # Determine user type
            user_type = "investor"  # default
            if any(word in query_lower for word in ['خرید خانه', 'مسکن اول', 'سکونت']):
                user_type = "homebuyer"
            elif any(word in query_lower for word in ['اجاره', 'رهن', 'مستأجر']):
                user_type = "renter"
            elif any(word in query_lower for word in ['سازنده', 'پروژه', 'ساخت']):
                user_type = "developer"
            elif any(word in query_lower for word in ['سیاست', 'دولت', 'وزارت']):
                user_type = "government"
            elif any(word in query_lower for word in ['سرمایه', 'بازدهی', 'سود']):
                user_type = "investor"
            
            # Determine primary intent
            intent = "analyze"  # default
            if any(word in query_lower for word in ['خرید', 'بخرم']):
                intent = "buy"
            elif any(word in query_lower for word in ['فروش', 'بفروشم']):
                intent = "sell"
            elif any(word in query_lower for word in ['اجاره', 'رهن']):
                intent = "rent"
            elif any(word in query_lower for word in ['سرمایه', 'invest']):
                intent = "invest"
            elif any(word in query_lower for word in ['تحلیل', 'بررسی', 'وضعیت']):
                intent = "analyze"
            
            # Determine information needs
            info_needs = []
            if any(word in query_lower for word in ['قیمت', 'ارزش', 'price']):
                info_needs.append("pricing")
            if any(word in query_lower for word in ['منطقه', 'محله', 'location']):
                info_needs.append("location")
            if any(word in query_lower for word in ['زمان', 'کی', 'timing']):
                info_needs.append("timing")
            if any(word in query_lower for word in ['استراتژی', 'روش', 'strategy']):
                info_needs.append("strategy")
            if any(word in query_lower for word in ['ریسک', 'خطر', 'risk']):
                info_needs.append("risk")
            
            # Determine expertise level
            expertise = "beginner"
            if any(word in query_lower for word in ['تحلیل تکنیکال', 'dcf', 'cap rate']):
                expertise = "expert"
            elif any(word in query_lower for word in ['استراتژی', 'پورتفولیو', 'diversify']):
                expertise = "intermediate"
            
            # Suggest relevant analysis modules
            relevant_modules = []
            if intent in ['buy', 'invest']:
                relevant_modules.extend(['market_cycle', 'valuation_analysis', 'investment_strategy'])
            if intent == 'rent' or user_type == 'renter':
                relevant_modules.append('rental_market')
            if user_type == 'government' or 'سیاست' in query_lower:
                relevant_modules.append('policy_simulation')
            if 'اقتصاد' in query_lower or 'کلان' in query_lower:
                relevant_modules.append('macro_analysis')
            if expertise == 'beginner':
                relevant_modules.append('educational_advisor')
            
            state["query_intent"] = {
                "user_type": user_type,
                "primary_intent": intent,
                "information_needs": info_needs,
                "urgency_level": "planning",  # default
                "expertise_level": expertise,
                "relevant_modules": list(set(relevant_modules)),  # remove duplicates
                "llm_analysis": response.content,
                "confidence_score": 0.8,
                "key_topics": [
                    topic for topic in ['قیمت', 'منطقه', 'زمان', 'ریسک', 'بازدهی'] 
                    if topic in query_lower
                ],
                "personalization_factors": {
                    "risk_tolerance": "moderate",  # default
                    "investment_horizon": "medium_term",  # default
                    "budget_range": "not_specified",
                    "preferred_locations": "not_specified"
                }
            }
            
        except Exception as e:
            print(f"LLM call failed: {e}")
            raise e
        
        print(f"✅ Query understood - User: {state['query_intent']['user_type']}, Intent: {state['query_intent']['primary_intent']}")
        return state

# Global instance
_query_understanding_agent = None

def get_query_understanding_agent() -> QueryUnderstandingAgent:
    """Get or create the global query understanding agent instance"""
    global _query_understanding_agent
    if _query_understanding_agent is None:
        _query_understanding_agent = QueryUnderstandingAgent()
    return _query_understanding_agent

# Backward compatibility function
@traceable
def query_understanding(state: RISAState) -> RISAState:
    """Backward compatibility wrapper for the QueryUnderstandingAgent"""
    agent = get_query_understanding_agent()
    return agent.understand_query(state)

if __name__ == "__main__":
    state = RISAState(
        user_query="من یک سرمایه‌گذار هستم و می‌خواهم بدانم که آیا امروز یک خانه خریداری کنم یا خیر."
    )
    result = query_understanding(state)
    print(result)

