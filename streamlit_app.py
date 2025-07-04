import streamlit as st
import asyncio
from main import main as run_main_script
import os
import re
import nest_asyncio

nest_asyncio.apply()

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

# Initialize session state for the report
if 'full_report' not in st.session_state:
    st.session_state.full_report = []

# Apply custom CSS if the query is in Persian
if is_persian(user_query):
    st.markdown(persian_css, unsafe_allow_html=True)

if st.button("Generate Report"):
    st.session_state.full_report = [] # Clear previous report
    st.subheader("Live Report Generation")
    report_container = st.empty()
    
    # Run the async generator and display the results in a streaming fashion
    with st.spinner("Generating your report, please wait..."):
        try:
            async def stream_report():
                async for chunk in run_main_script(user_query):
                    st.session_state.full_report.append(chunk)
                    report_container.markdown("".join(st.session_state.full_report))
            
            asyncio.run(stream_report())

        except Exception as e:
            st.error(f"An error occurred during report generation: {e}")

    st.success("Report generation complete!")
    # Display final report outside the spinner
    st.markdown("".join(st.session_state.full_report)) 