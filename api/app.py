import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS
from pipeline.verify import verify_hcp
from summariser.report import generate_report

app = Flask(__name__)
CORS(app)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "running",
        "service": "HCP Compliance Checker API",
        "version": "1.0"
    })

@app.route("/verify", methods=["POST"])
def verify():
    data = request.get_json()
    
    if not data or "npi" not in data:
        return jsonify({
            "error": "NPI number required",
            "example": {"npi": "1003000126"}
        }), 400
    
    npi = data["npi"].strip()
    
    if len(npi) != 10 or not npi.isdigit():
        return jsonify({
            "error": "Invalid NPI number — must be exactly 10 digits"
        }), 400
    
    try:
        verification_result = verify_hcp(npi)
        report = generate_report(verification_result)
        return jsonify(report)
    except Exception as e:
        return jsonify({
            "error": "Verification failed",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)