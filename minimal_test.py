#!/usr/bin/env python3
"""
Minimal Flask app to test if basic functionality works
"""
from flask import Flask, jsonify, request
import json

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask app is running!"

@app.route("/api/wordbank", methods=["GET"])
def api_get_wordbank():
    return jsonify({"words": [], "status": "working"})

@app.route("/api/upload", methods=["POST"])
def api_upload():
    return jsonify({"message": "Upload endpoint working", "data": request.get_json()})

if __name__ == "__main__":
    print("Starting minimal Flask app...")
    app.run(host="0.0.0.0", port=5001, debug=True)