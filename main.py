#!/usr/bin/env python3
"""
RISA - Real Estate Intelligence System & Analysis
Main entry point for the application
"""

import os
import sys
from typing import Optional

# Add src to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.routing.orchestrator import orchestrator
from src.models.state import RISAState
from src.configs.llm_config import get_current_config


def main():
    """Main function to run RISA analysis"""
    
    print("🏠 Welcome to RISA - Real Estate Intelligence System & Analysis")
    print("=" * 60)
    
    # Display current configuration
    config = get_current_config()
    print(f"🔧 Current LLM: {config['provider']} - {config['model']}")
    print()
    
    # Get user query
    query = input("💬 Enter your real estate analysis query: ")
    
    if not query.strip():
        print("❌ Please provide a valid query.")
        return
    
    try:
        # Initialize state
        print("\n🚀 Initializing RISA analysis...")
        state = RISAState(user_query=query)
        
        print("\n🎯 Running RISA Analysis...")
        result = orchestrator(state)
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 ANALYSIS COMPLETE")
        print("=" * 60)
        
        if result.get('final_report'):
            print("\n📋 Final Report:")
            print("-" * 40)
            print(result['final_report'])
        
        # Save results if requested
        save_results = input("\n💾 Save results to file? (y/N): ").lower().strip()
        if save_results == 'y':
            filename = f"output/reports/risa_analysis_{hash(query) % 10000}.md"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# RISA Analysis Report\n\n")
                f.write(f"**Query:** {query}\n\n")
                f.write(f"**Analysis Date:** {result.get('timestamp', 'N/A')}\n\n")
                f.write(f"## Results\n\n{result.get('final_report', 'No report generated')}\n")
            
            print(f"✅ Results saved to: {filename}")
    
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        print("Please check your configuration and try again.")
    
    print("\n👋 Thank you for using RISA!")


def run_example():
    """Run an example analysis"""
    
    print("🏠 RISA Example Analysis")
    print("=" * 40)
    
    example_query = "Analyze the Tehran real estate market trends and provide investment recommendations"
    
    print(f"📝 Example Query: {example_query}")
    print("\n🚀 Running analysis...")
    
    try:
        state = RISAState(user_query=example_query)
        result = orchestrator(state)
        
        print("\n📊 Example Analysis Complete!")
        if result.get('final_report'):
            print("\n📋 Report Summary:")
            print("-" * 30)
            print(result['final_report'][:500] + "..." if len(result.get('final_report', '')) > 500 else result.get('final_report', 'No report generated'))
    
    except Exception as e:
        print(f"❌ Example failed: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="RISA - Real Estate Intelligence System")
    parser.add_argument("--example", action="store_true", help="Run example analysis")
    parser.add_argument("--query", type=str, help="Direct query for analysis")
    
    args = parser.parse_args()
    
    if args.example:
        run_example()
    elif args.query:
        try:
            state = RISAState(user_query=args.query)
            result = orchestrator(state)
            print(result.get('final_report', 'Analysis completed'))
        except Exception as e:
            print(f"Error: {e}")
    else:
        main() 