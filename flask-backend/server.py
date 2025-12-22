from flask import Flask, jsonify, request
from flask_cors import CORS
from services.database import getAllSummaries, getSummaryByDocumentId, getRecentSummaries

app = Flask(__name__)
CORS(app)  # Enable CORS for your React frontend

@app.route('/')
def home():
    return jsonify({
        "message": "CityScope API",
        "version": "1.0",
        "endpoints": {
            "/summaries": "Get all meeting summaries",
            "/summaries/<document_id>": "Get specific summary",
            "/summaries/recent": "Get recent summaries (last 30 days)"
        }
    })

@app.route('/summaries', methods=['GET'])
def get_summaries():
    """
    Get all summaries with optional limit
    Query params:
        - limit: Number of results to return (default: 30)
    """
    try:
        limit = request.args.get('limit', default=30, type=int)
        summaries = getAllSummaries(limit=limit)
        
        return jsonify({
            "success": True,
            "count": len(summaries),
            "data": summaries
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/summaries/<document_id>', methods=['GET'])
def get_summary(document_id):
    """
    Get a specific summary by document ID
    """
    try:
        summary = getSummaryByDocumentId(document_id)
        
        if summary:
            return jsonify({
                "success": True,
                "data": summary
            })
        else:
            return jsonify({
                "success": False,
                "error": "Summary not found"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/summaries/recent', methods=['GET'])
def get_recent_summaries():
    """
    Get summaries from the last N days
    Query params:
        - days: Number of days to look back (default: 30)
    """
    try:
        days = request.args.get('days', default=30, type=int)
        summaries = getRecentSummaries(days=days)
        
        return jsonify({
            "success": True,
            "count": len(summaries),
            "days": days,
            "data": summaries
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    """
    return jsonify({
        "status": "healthy",
        "service": "CityScope API"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)