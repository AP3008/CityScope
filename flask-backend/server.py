from flask import Flask, jsonify, request
from flask_cors import CORS
from database import getAllSummaries, getSummaryByDocumentId, getRecentSummaries

app = Flask(__name__)
CORS(app)

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
    return jsonify({
        "status": "healthy",
        "service": "CityScope API"
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)