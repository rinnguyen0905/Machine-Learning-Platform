from flask import Flask, render_template, jsonify, request
import requests
import json
import os
from pathlib import Path

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# API endpoint base URL - update this based on your FastAPI service
API_BASE_URL = "http://localhost:8000"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/application')
def application():
    return render_template('application.html')

@app.route('/behavior')
def behavior():
    return render_template('behavior.html')

@app.route('/collections')
def collections():
    return render_template('collections.html')

@app.route('/desertion')
def desertion():
    return render_template('desertion.html')

@app.route('/batch')
def batch():
    return render_template('batch.html')

@app.route('/api/proxy/<path:endpoint>', methods=['GET', 'POST'])
def proxy_api(endpoint):
    """Proxy requests to the FastAPI backend"""
    url = f"{API_BASE_URL}/{endpoint}"
    
    # Forward the request to the API
    if request.method == 'GET':
        response = requests.get(url, params=request.args)
    else:  # POST
        response = requests.post(url, json=request.json)
    
    # Return the API response
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs(Path(__file__).parent / 'templates', exist_ok=True)
    os.makedirs(Path(__file__).parent / 'static' / 'css', exist_ok=True)
    os.makedirs(Path(__file__).parent / 'static' / 'js', exist_ok=True)
    os.makedirs(Path(__file__).parent / 'static' / 'img', exist_ok=True)
    
    app.run(debug=True, port=5000)
