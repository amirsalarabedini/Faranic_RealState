#!/usr/bin/env python3
"""
Example client for the Faranic Real Estate FastAPI backend
This script demonstrates how to interact with the API endpoints
"""
import asyncio
import aiohttp
import json
import sys
import time
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"

async def check_health():
    """Check the health of the API"""
    print("🔍 Checking API health...")
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_BASE_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API is healthy: {data}")
                    return True
                else:
                    print(f"❌ API health check failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Failed to connect to API: {e}")
            return False

async def generate_report(query: str, language: str = "English") -> Dict[str, Any]:
    """Generate a report using the synchronous endpoint"""
    print(f"📊 Generating report for query: '{query}'")
    
    payload = {
        "query": query,
        "language": language,
        "report_date": None  # Will use current date
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{API_BASE_URL}/generate_report",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Report generated successfully!")
                    print(f"📄 Report ID: {data['report_id']}")
                    print(f"📝 Report length: {len(data['report'])} characters")
                    return data
                else:
                    error_data = await response.json()
                    print(f"❌ Failed to generate report: {error_data}")
                    return None
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return None

async def stream_report(query: str, language: str = "English"):
    """Generate a report using the streaming endpoint"""
    print(f"🔄 Streaming report for query: '{query}'")
    
    payload = {
        "query": query,
        "language": language,
        "report_date": None
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{API_BASE_URL}/generate_report_stream",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    print("🌊 Streaming response:")
                    async for chunk in response.content.iter_chunked(1024):
                        chunk_str = chunk.decode('utf-8')
                        if chunk_str.strip():
                            print(f"📦 Chunk: {chunk_str[:100]}...")
                    print("✅ Streaming completed")
                else:
                    error_data = await response.json()
                    print(f"❌ Failed to stream report: {error_data}")
        except Exception as e:
            print(f"❌ Error streaming report: {e}")

async def list_reports():
    """List all generated reports"""
    print("📋 Listing all reports...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_BASE_URL}/reports") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"📊 Found {data['total_count']} reports:")
                    for report in data['reports']:
                        print(f"  - ID: {report['report_id']}")
                        print(f"    Query: {report['query'][:50]}...")
                        print(f"    Language: {report['language']}")
                        print(f"    Created: {report['timestamp']}")
                        print()
                    return data
                else:
                    error_data = await response.json()
                    print(f"❌ Failed to list reports: {error_data}")
                    return None
        except Exception as e:
            print(f"❌ Error listing reports: {e}")
            return None

async def get_report(report_id: str):
    """Get a specific report by ID"""
    print(f"📄 Retrieving report: {report_id}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_BASE_URL}/reports/{report_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Report retrieved successfully!")
                    print(f"📝 Query: {data['query']}")
                    print(f"📝 Report length: {len(data['report'])} characters")
                    return data
                else:
                    error_data = await response.json()
                    print(f"❌ Failed to retrieve report: {error_data}")
                    return None
        except Exception as e:
            print(f"❌ Error retrieving report: {e}")
            return None

async def delete_report(report_id: str):
    """Delete a specific report"""
    print(f"🗑️  Deleting report: {report_id}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.delete(f"{API_BASE_URL}/reports/{report_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Report deleted successfully: {data['message']}")
                    return True
                else:
                    error_data = await response.json()
                    print(f"❌ Failed to delete report: {error_data}")
                    return False
        except Exception as e:
            print(f"❌ Error deleting report: {e}")
            return False

async def main():
    """Main function to demonstrate the API"""
    print("🏠 Faranic Real Estate API Client Example")
    print("=" * 50)
    
    # Check if API is healthy
    is_healthy = await check_health()
    if not is_healthy:
        print("❌ API is not available. Please start the server first.")
        print("Run: python run_server.py")
        return
    
    # Example queries
    queries = [
        "What are the key factors for real estate investment in Tehran?",
        "عوامل کلیدی سرمایه‌گذاری در بازار املاک تهران کدامند؟"
    ]
    
    # Generate reports
    report_ids = []
    for i, query in enumerate(queries):
        print(f"\n{'-' * 30}")
        print(f"Example {i + 1}: Generating report")
        language = "Persian" if i == 1 else "English"
        
        result = await generate_report(query, language)
        if result:
            report_ids.append(result['report_id'])
            
        # Small delay between requests
        await asyncio.sleep(2)
    
    # List all reports
    print(f"\n{'-' * 30}")
    await list_reports()
    
    # Get a specific report
    if report_ids:
        print(f"\n{'-' * 30}")
        await get_report(report_ids[0])
    
    # Demonstrate streaming (commented out to avoid long output)
    # print(f"\n{'-' * 30}")
    # await stream_report("Quick market analysis for investors")
    
    # Clean up - delete one report
    if report_ids:
        print(f"\n{'-' * 30}")
        await delete_report(report_ids[0])
    
    print(f"\n{'-' * 30}")
    print("✅ Example completed successfully!")
    print(f"📖 API Documentation: {API_BASE_URL}/docs")
    print(f"📚 ReDoc Documentation: {API_BASE_URL}/redoc")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        sys.exit(1) 