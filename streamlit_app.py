import streamlit as st
import asyncio
from main import main as run_main_script
import os

st.title("Faranic Real Estate Investment Advisor")

user_query = st.text_area("Enter your investment query:", "عوامل کلیدی و تعیین‌کننده در شروع و پایان هر یک از اپیزودهای رونق شدید، رونق اندک، رکود اندک، رکود شدید و چرخش بازار کدامند؟")

if st.button("Generate Report"):
    with st.spinner("Generating your report, please wait..."):
        # Run the main script from main.py
        # We need to run the async main function
        asyncio.run(run_main_script(user_query))
        
        # Define the absolute path for the report
        report_path = os.path.join(os.getcwd(), "final_investment_report.md")
        
        # Read the generated report
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report_content = f.read()
            st.markdown(report_content)
        except FileNotFoundError:
            st.error(f"Error: The report file was not found at {report_path}. The report generation might have failed.")

st.markdown("---")
st.subheader("File I/O Test")

if st.button("Create Test File"):
    test_file_path = os.path.join(os.getcwd(), "test_file.txt")
    try:
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write("This is a test file created by the Streamlit app.")
        st.success(f"Test file created at: {test_file_path}")
    except Exception as e:
        st.error(f"Failed to create test file: {e}")

if st.button("Read Test File"):
    test_file_path = os.path.join(os.getcwd(), "test_file.txt")
    try:
        with open(test_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        st.info(f"Content of test file: '{content}'")
        st.success(f"Successfully read test file from: {test_file_path}")
    except FileNotFoundError:
        st.error(f"Test file not found at: {test_file_path}")
    except Exception as e:
        st.error(f"Failed to read test file: {e}") 