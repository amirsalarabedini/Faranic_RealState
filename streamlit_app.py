import streamlit as st
import asyncio
from main import main as run_main_script
import os
import re

def is_persian(text: str) -> bool:
    """Checks if the text contains Persian characters."""
    return bool(re.search('[\u0600-\u06FF]', text))

# --- CSS for RTL and Vazirmatn Font ---
persian_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100..900&display=swap');
    
    .stApp {
        direction: rtl;
    }
    
    html, body, [class*="st-"], button, input, textarea, h1, h2, h3, h4, h5, h6 {
        font-family: 'Vazirmatn', sans-serif !important;
    }
</style>
"""

st.title("Faranic Real Estate Investment Advisor")

user_query = st.text_area("Enter your investment query:", "عوامل کلیدی و تعیین‌کننده در شروع و پایان هر یک از اپیزودهای رونق شدید، رونق اندک، رکود اندک، رکود شدید و چرخش بازار کدامند؟")

# Apply custom CSS if the query is in Persian
if is_persian(user_query):
    st.markdown(persian_css, unsafe_allow_html=True)

if st.button("Generate Report"):
    st.subheader("Live Report Generation")
    report_container = st.empty()
    
    # Run the async generator and display the results in a streaming fashion
    with st.spinner("Generating your report, please wait..."):
        try:
            full_report = []
            # asyncio.run() is not directly compatible with async generators in this context.
            # We need to get the event loop and run the async generator to completion.
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def stream_report():
                async for chunk in run_main_script(user_query):
                    full_report.append(chunk)
                    report_container.markdown("".join(full_report))
            
            loop.run_until_complete(stream_report())

        except Exception as e:
            st.error(f"An error occurred during report generation: {e}")

    st.success("Report generation complete!") 