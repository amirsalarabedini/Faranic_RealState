"""
Simple test of individual agents to show functionality
"""

import asyncio
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.agents.specialists.receptionist import ReceptionistAgent

async def test_receptionist():
    """Test the receptionist agent directly"""
    print("🔍 Testing Receptionist Agent")
    print("=" * 50)
    
    receptionist = ReceptionistAgent("test_receptionist")
    
    # Test query analysis
    test_query = "I'm an investor looking to buy a 100 sqm apartment in Tehran's District 5. What's the current market price and is it a good investment opportunity?"
    
    print(f"User Query: {test_query[:80]}...")
    print()
    
    try:
        # Direct test of analysis function
        analysis = await receptionist.analyze_user_query(test_query)
        
        print("✅ Analysis completed!")
        print(f"Client Type: {analysis.get('client_type')}")
        print(f"Primary Task: {analysis.get('primary_task')}")
        print(f"Required Agents: {analysis.get('required_agents', [])}")
        print(f"Location: {analysis.get('property_specs', {}).get('location', 'Not specified')}")
        print(f"Urgency: {analysis.get('urgency_level')}")
        
        # Test work order creation
        work_order = receptionist.create_work_order(analysis, test_query)
        print(f"\n📋 Work Order Created: {work_order.order_id}")
        print(f"Status: {work_order.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def test_capabilities():
    """Test agent capabilities reporting"""
    print("\n🛠️ Testing Agent Capabilities")
    print("=" * 50)
    
    receptionist = ReceptionistAgent("test_receptionist")
    capabilities = receptionist.get_capabilities()
    
    print(f"Agent Type: {capabilities['agent_type']}")
    print(f"Primary Function: {capabilities['primary_function']}")
    print("Capabilities:")
    for cap in capabilities['capabilities'][:3]:
        print(f"  • {cap}")
    
    print(f"Supported Languages: {capabilities['languages_supported']}")

if __name__ == "__main__":
    print("🚀 Simple Agent Test")
    print("Testing individual agent functionality")
    print()
    
    # Run tests
    success1 = asyncio.run(test_receptionist())
    asyncio.run(test_capabilities())
    
    print("\n" + "=" * 50)
    if success1:
        print("✅ Receptionist Agent working correctly!")
        print("✅ LLM integration successful!")
        print("✅ Work Order creation successful!")
    else:
        print("❌ Some tests failed")
    
    print("\n🎯 This demonstrates:")
    print("• Your LLM config integration works")
    print("• Agent analysis and structured output works") 
    print("• Work Order system works")
    print("• Ready to add more agents that use your utilities!") 