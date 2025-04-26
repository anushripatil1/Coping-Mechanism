from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_suggestion', methods=['POST'])
def get_suggestion():
    data = request.json
    stressor = data.get('stressor')
    emotion = data.get('emotion')

    query = f"respond({emotion}, {stressor}, Suggestion), writeln(Suggestion)."

    result = subprocess.run(
        ['C:\\Program Files\\swipl\\bin\\swipl.exe', '-s', 'coping_bot.pl', '-g', query, '-t', 'halt'],
        capture_output=True, text=True
    )

    output = result.stdout.strip()
    print(f"Prolog output: {output}")  # <--- ADD this for debugging

    return jsonify({'suggestion': output})

if __name__ == '__main__':
    app.run(port=5000)
