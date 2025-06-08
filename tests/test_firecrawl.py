# # from firecrawl import FirecrawlApp
# # import json
# # api_key = "fc-301f7bfd5e2946529a697036077a00d0"

# # # Initialize the client
# # firecrawl = FirecrawlApp(api_key=api_key)


# # # Start research with real-time updates
# # def on_activity(activity):
# #     print(f"[{activity['type']}] {activity['message']}")

# # # Run deep research
# # results = firecrawl.deep_research(
# #     query="میانگین اجاره ‍ملک در تهران چقدر است؟",
# #     max_depth=5,
# #     time_limit=180,
# #     max_urls=15,
# #     on_activity=on_activity
# # )

# # # Access research findings.
# # print(f"Final Analysis: {results['data']['finalAnalysis']}")

# # print(f"Sources: {len(results['data']['sources'])} references")

# # #save results to json file
# # with open('results.json', 'w') as f:
# #     json.dump(results, f)

# # Install with pip install firecrawl-py
# import asyncio
# from firecrawl import AsyncFirecrawlApp
# from pydantic import BaseModel, Field
# from typing import Any, Optional, List
# import json

# class NestedModel1(BaseModel):
#     location: str
#     average_price: float
#     currency: str
#     date: str = None

# class ExtractSchema(BaseModel):
#     real_estate_prices: list[NestedModel1]

# async def main():
#     app = AsyncFirecrawlApp(api_key='fc-301f7bfd5e2946529a697036077a00d0')
#     response = await app.extract(
#         urls=[
#             "https://amar.org.ir/*",
#             "https://cbi.ir/*",
#             "https://mrud.ir/*",
#             "https://iranamlaak.ir/*",
#             "https://tejaratefarda.com/*",
#             "https://donya-e-eqtesad.com/*"
#         ],
#         prompt='Research the real estate prices in Iran, focusing on different locations, average prices, and the currency used. Include the date of the data if available.',
#         schema=ExtractSchema.model_json_schema(),
#         # system_prompt='You are a real estate expert. You are given a list of URLs. You need to extract the real estate prices in Iran, focusing on different locations, average prices, and the currency used. Include the date of the data if available.',
#         show_sources=True,
#         enable_web_search=True,
#         allow_external_links=True,
 
#     )
#     print(response)
#     #save the response to json file
#     with open('response.json', 'w') as f:
#         json.dump(response, f)

# asyncio.run(main())
# Install with pip install firecrawl-py
import asyncio
from firecrawl import AsyncFirecrawlApp
from pydantic import BaseModel, Field
from typing import Any, Optional, List, Dict, Union
import json

class NestedModel1(BaseModel):
    location: str
    average_price: float
    currency: str
    date: Optional[str] = None

class ExtractSchema(BaseModel):
    real_estate_prices: list[NestedModel1]

async def main():
    app = AsyncFirecrawlApp(api_key='fc-301f7bfd5e2946529a697036077a00d0')
    response = await app.extract(
        urls=[
            "https://amar.org.ir/*",
            "https://cbi.ir/*",
            "https://mrud.ir/*",
            "https://iranamlaak.ir/*",
            "https://tejaratefarda.com/*",
            "https://donya-e-eqtesad.com/*"
        ],
        prompt='Research the real estate prices in Iran, focusing on different locations, average prices, and the currency used. Include the date of the data if available.',
        schema=ExtractSchema.model_json_schema(),
        enable_web_search=True,
        allow_external_links=True,
    )
    
    # Print the response for debugging
    print(f"Response type: {type(response)}")
    print(response)
    
    # Extract data and save to JSON file
    if hasattr(response, 'data'):
        # Create a serializable dictionary
        serializable_data = {
            'id': response.id,
            'status': response.status,
            'expiresAt': str(response.expiresAt) if response.expiresAt else None,
            'success': response.success,
            'data': response.data,
            'error': response.error,
            'warning': response.warning,
            # Handle sources specially since it might not be JSON serializable
            'sources': {} if response.sources is None else response.sources
        }
        
        # Save to a JSON file
        with open('response.json', 'w') as f:
            json.dump(serializable_data, f, default=str)
        
        print("Data successfully saved to response.json")
    else:
        print("Unexpected response format, cannot extract data")

asyncio.run(main())
