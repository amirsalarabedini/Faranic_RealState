import sys
import os
from flask import Flask, request, jsonify
import asyncio
import json

# Add the project root to the Python path to allow imports from src/
# Assuming backend/app.py is at Faranic_RealState/backend/app.py
# and main.py is at Faranic_RealState/main.py
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the main orchestrator function
from main import main as run_main_script

app = Flask(__name__)

@app.route('/generate_report', methods=['POST'])
async def generate_report():
    data = request.get_json()
    user_query = data.get('query')

    if not user_query:
        return jsonify({"error": "Missing 'query' in request"}), 400

    full_report_chunks = []
    try:
        # Run the async generator and collect all chunks
        async for chunk in run_main_script(user_query):
            full_report_chunks.append(chunk)
        
        final_report = "".join(full_report_chunks)
        return jsonify({"status": "success", "report": final_report}), 200

    except Exception as e:
        # Log the exception for server-side debugging
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e), "traceback": traceback.format_exc()}), 500

if __name__ == '__main__':
    # You can run this with `python backend/app.py` or `flask run`
    # For production, use a WSGI server like Gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True) 