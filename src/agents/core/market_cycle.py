from langsmith import traceable
from src.models.state import RISAState
from src.configs.llm_config import get_default_llm
import json

class MarketCycleAgent:
    """Enhanced market cycle analysis agent using both knowledge base and current data"""
    
    def __init__(self):
        self.llm = get_default_llm()
        print("✅ Market cycle agent initialized successfully")
    
    @traceable
    def analyze_cycle(self, state: RISAState) -> RISAState:
        """Enhanced market cycle analysis using both knowledge base and current data"""
        print("🔄 Enhanced Market Cycle Analysis...")
        
        # Extract comprehensive data from enhanced data_ingest
        raw_data = state.get('raw_data', {})
        book_facts = state.get('book_facts', {})
        
        # Prepare context from multiple sources
        context_parts = []
        
        # Add knowledge base insights
        if raw_data.get('knowledge_base_result'):
            kb_result = raw_data['knowledge_base_result']
            if kb_result.get('answer'):
                context_parts.append(f"Knowledge Base Analysis:\n{kb_result['answer']}")
        
        # Add current market data
        if raw_data.get('web_search_result'):
            web_result = raw_data['web_search_result']
            if web_result.get('answer'):
                context_parts.append(f"Current Market Information:\n{web_result['answer']}")
        
        # Add combined analysis
        if raw_data.get('combined_analysis'):
            combined = raw_data['combined_analysis']
            if combined.get('synthesized_answer'):
                context_parts.append(f"Synthesized Analysis:\n{combined['synthesized_answer']}")
        
        # Add extracted book facts
        if book_facts:
            try:
                facts_str = json.dumps(book_facts, ensure_ascii=False, indent=2)
                context_parts.append(f"Key Facts from Knowledge Base:\n{facts_str}")
            except:
                context_parts.append(f"Book Facts:\n{str(book_facts)}")
        
        if not context_parts:
            print("⚠️ No data available for market cycle analysis")
            state["cycle_phase"] = "unknown"
            return state
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Enhanced prompt for market cycle analysis
        prompt = f"""
        You are an expert real estate market analyst specializing in Iranian housing markets. 
        Based on the comprehensive information provided below, determine the current market cycle phase.
        
        Consider the following factors:
        1. Historical market patterns from the knowledge base
        2. Current market conditions and trends
        3. Economic indicators and government policies
        4. Supply and demand dynamics
        5. Price trends and affordability metrics
        
        Available Information:
        {context}
        
        Classify the market phase as one of: 'expansion', 'peak', 'contraction', 'trough'
        
        Provide your analysis in the following format:
        PHASE: [your classification]
        CONFIDENCE: [high/medium/low]
        REASONING: [detailed explanation of your reasoning]
        KEY_INDICATORS: [list the main indicators that support your conclusion]
        OUTLOOK: [brief outlook for the next 6-12 months]
        """
        
        try:
            response = self.llm.invoke(prompt)
            analysis = response.content
            
            # Extract phase from response
            phase = "unknown"
            confidence = "low"
            reasoning = ""
            key_indicators = []
            outlook = ""
            
            lines = analysis.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('PHASE:'):
                    phase_text = line.replace('PHASE:', '').strip().lower()
                    if "contraction" in phase_text:
                        phase = "contraction"
                    elif "peak" in phase_text:
                        phase = "peak"
                    elif "trough" in phase_text:
                        phase = "trough"
                    elif "expansion" in phase_text:
                        phase = "expansion"
                elif line.startswith('CONFIDENCE:'):
                    confidence = line.replace('CONFIDENCE:', '').strip().lower()
                elif line.startswith('REASONING:'):
                    reasoning = line.replace('REASONING:', '').strip()
                elif line.startswith('KEY_INDICATORS:'):
                    key_indicators = line.replace('KEY_INDICATORS:', '').strip()
                elif line.startswith('OUTLOOK:'):
                    outlook = line.replace('OUTLOOK:', '').strip()
            
            # Store comprehensive analysis results
            state["cycle_phase"] = phase
            state["cycle_analysis"] = {
                "phase": phase,
                "confidence": confidence,
                "reasoning": reasoning,
                "key_indicators": key_indicators,
                "outlook": outlook,
                "full_analysis": analysis,
                "data_sources": raw_data.get('sources_used', {}),
                "analysis_timestamp": raw_data.get('timestamp', '')
            }
            
            print(f"✅ Market cycle analysis completed:")
            print(f"   - Phase: {phase}")
            print(f"   - Confidence: {confidence}")
            print(f"   - Data sources: {raw_data.get('sources_used', {})}")
            
        except Exception as e:
            print(f"❌ LLM call failed: {e}")
            state["cycle_phase"] = "error"
            state["cycle_analysis"] = {
                "phase": "error",
                "error": str(e),
                "analysis_timestamp": raw_data.get('timestamp', '')
            }
            raise e
        
        return state

# Global instance
_market_cycle_agent = None

def get_market_cycle_agent() -> MarketCycleAgent:
    """Get or create the global market cycle agent instance"""
    global _market_cycle_agent
    if _market_cycle_agent is None:
        _market_cycle_agent = MarketCycleAgent()
    return _market_cycle_agent

# Backward compatibility function
@traceable
def market_cycle(state: RISAState) -> RISAState:
    """Backward compatibility wrapper for the MarketCycleAgent"""
    agent = get_market_cycle_agent()
    return agent.analyze_cycle(state) 