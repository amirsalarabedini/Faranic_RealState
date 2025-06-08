from langsmith import traceable
from typing import Dict, Any
from datetime import datetime
import json
from langchain_core.messages import HumanMessage, SystemMessage
from src.config import get_llm
from ...models.state import RISAState

class GenerateReportAgent:
    """Final analysis report generation agent"""
    
    def __init__(self):
        self.model = get_llm()
        print("✅ Generate report agent initialized successfully")
    
    @traceable
    def process_query(self, state: RISAState) -> RISAState:
        """Generate comprehensive real estate analysis report"""
        print("📋 Generate Report Agent Starting...")
        
        try:
            # Extract all available data from state
            user_query = state.get('user_query', '')
            raw_data = state.get('raw_data', {})
            book_facts = state.get('book_facts', {})
            market_analysis = state.get('market_analysis', {})
            
            # Generate comprehensive report
            report = self._generate_comprehensive_report(
                user_query, raw_data, book_facts, market_analysis
            )
            
            # Update state with final report
            state['final_report'] = report
            state['report_timestamp'] = datetime.now().isoformat()
            
            print("✅ Final report generated successfully")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            state['final_report'] = f"Error generating report: {e}"
            state['report_timestamp'] = datetime.now().isoformat()
        
        return state
    
    @traceable
    def _generate_comprehensive_report(self, query: str, raw_data: Dict[str, Any], 
                                     book_facts: Dict[str, Any], market_analysis: Dict[str, Any]) -> str:
        """Generate a comprehensive real estate analysis report"""
        
        # Prepare context for report generation
        context_data = {
            'query': query,
            'raw_data': raw_data,
            'book_facts': book_facts,
            'market_analysis': market_analysis
        }
        
        report_messages = [
            SystemMessage(content="""You are an expert real estate analyst creating a comprehensive report.
            Generate a detailed, professional analysis report based on the provided data.
            
            Structure your report with:
            1. Executive Summary
            2. Market Analysis
            3. Key Findings
            4. Investment Recommendations
            5. Risk Assessment
            6. Conclusion
            
            Use Persian language when appropriate and include relevant statistics and insights."""),
            HumanMessage(content=f"""
            Generate a comprehensive real estate analysis report based on:
            
            User Query: {query}
            
            Available Data:
            {json.dumps(context_data, ensure_ascii=False, indent=2)}
            
            Create a professional, actionable report.
            """)
        ]
        
        try:
            response = self.model.invoke(report_messages)
            return response.content.strip()
            
        except Exception as e:
            return f"Error generating report content: {e}"
    
    def as_langgraph_node(self):
        """Convert to LangGraph node function"""
        def node_function(state: Dict[str, Any]) -> Dict[str, Any]:
            # Convert dict state to RISAState for compatibility
            risa_state = RISAState(**state) if isinstance(state, dict) else state
            result_state = self.process_query(risa_state)
            return dict(result_state)
        
        return node_function


def get_generate_report_agent() -> GenerateReportAgent:
    """Factory function to create a generate report agent instance"""
    return GenerateReportAgent()


@traceable
def generate_report(state: RISAState) -> RISAState:
    """Backward compatibility function for report generation"""
    agent = get_generate_report_agent()
    return agent.process_query(state)
 