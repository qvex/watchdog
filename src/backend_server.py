from flask import Flask, request, jsonify
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.hint_service import CodeContext, generate_code_hint
from src.effects import Success, Failure

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/hint', methods=['POST'])
def generate_hint():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No JSON data"}), 400

        context = CodeContext(
            file_path=data.get('file_path', ''),
            code_snippet=data.get('code_snippet', ''),
            change_type=data.get('change_type', 'modification'),
            language=data.get('language', 'python')
        )

        result = generate_code_hint(context)

        match result:
            case Success(hint):
                return jsonify({"success": True, "hint": hint}), 200
            case Failure(error, context_msg):
                return jsonify({"success": False, "error": str(error)}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, nargs='?', default=5555)
    args = parser.parse_args()

    print(f"Starting Watchdog backend server on port {args.port}")
    app.run(host='localhost', port=args.port, debug=False)
