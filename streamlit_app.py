import streamlit as st
import asyncio
# import asyncio # No longer needed, as Flask handles async
# from main import main as run_main_script # No longer needed, calling via API
import os
import re
import nest_asyncio
import traceback
import httpx # New import for making HTTP requests

nest_asyncio.apply()

# Define the Flask backend URL
FLASK_BACKEND_URL = "http://localhost:5000" # Change this if your Flask app is on a different host/port

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

# Initialize session state variables
if 'full_report' not in st.session_state:
    st.session_state.full_report = []
if 'report_generated' not in st.session_state:
    st.session_state.report_generated = False
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'generation_error' not in st.session_state:
    st.session_state.generation_error = None

user_query = st.text_area("Enter your investment query:", "عوامل کلیدی و تعیین‌کننده در شروع و پایان هر یک از اپیزودهای رونق شدید، رونق اندک، رکود اندک، رکود شدید و چرخش بازار کدامند؟")

# Apply custom CSS if the query is in Persian
if is_persian(user_query):
    st.markdown(persian_css, unsafe_allow_html=True)

# Check if we need to reset the report (new query)
if user_query != st.session_state.last_query:
    print(f"DEBUG: Query changed detected! Old: '{st.session_state.last_query}', New: '{user_query}'")
    st.session_state.report_generated = False
    st.session_state.full_report = []
    st.session_state.generation_error = None
    st.session_state.last_query = user_query

# Show the generate button only if no report is currently generated or if query changed
if not st.session_state.report_generated:
    if st.button("Generate Report"):
        st.session_state.full_report = []  # Clear previous report
        st.session_state.generation_error = None
        st.subheader("Live Report Generation")
        report_container = st.empty()
        
        # Run the async generator and display the results in a streaming fashion
        with st.spinner("Generating your report, please wait..."):
            try:
                # Make an async HTTP POST request to the Flask backend
                async def call_backend_and_stream():
                    async with httpx.AsyncClient() as client:
                        response = await client.post(
                            f"{FLASK_BACKEND_URL}/generate_report",
                            json={"query": user_query},
                            timeout=None # Important for potentially long-running reports
                        )
                        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
                        
                        response_data = response.json()
                        
                        if response_data.get("status") == "success":
                            st.session_state.full_report = [response_data.get("report", "")]
                            report_container.markdown("".join(st.session_state.full_report))
                        else:
                            error_message = response_data.get("message", "Unknown error from backend")
                            backend_traceback = response_data.get("traceback", "No traceback available.")
                            raise Exception(f"Backend Error: {error_message}\nTraceback:\n{backend_traceback}")

                # Use Streamlit's experimental_fragment to run asyncio code
                # Or use nest_asyncio.apply() as already done
                asyncio.run(call_backend_and_stream())

                st.session_state.report_generated = True
                st.success("Report generation complete!")
                
            except httpx.RequestError as e:
                error_msg = f"Network or HTTP error: {str(e)}"
                st.error(error_msg)
                st.session_state.generation_error = error_msg
                st.text("Full error traceback:")
                st.code(traceback.format_exc())
            except httpx.HTTPStatusError as e:
                error_msg = f"HTTP status error: {e.response.status_code} - {e.response.text}"
                st.error(error_msg)
                st.session_state.generation_error = error_msg
                st.text("Full error traceback:")
                st.code(traceback.format_exc())
            except Exception as e:
                error_msg = f"An error occurred during report generation: {str(e)}"
                st.error(error_msg)
                st.session_state.generation_error = error_msg
                # Print full traceback for debugging
                st.text("Full error traceback:")
                st.code(traceback.format_exc())

# Display the report if it exists
if st.session_state.report_generated and st.session_state.full_report:
    st.subheader("Generated Report")
    st.markdown("".join(st.session_state.full_report))
    
    # Add a button to generate a new report
    if st.button("Generate New Report"):
        st.session_state.report_generated = False
        st.session_state.full_report = []
        st.session_state.generation_error = None
        st.rerun()

# Display error if there was one
if st.session_state.generation_error:
    st.error(st.session_state.generation_error)
    if st.button("Try Again"):
        st.session_state.generation_error = None
        st.session_state.report_generated = False
        st.rerun() 