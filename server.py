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
    physical = data.get('physical', 'none')
    time = data.get('time', 'afternoon')
    support = data.get('support', 'unavailable')
    environment = data.get('environment', 'home')
    preference = data.get('preference', 'passive')

    query = f"respond('{emotion}', '{stressor}', '{physical}', '{time}', '{support}', '{environment}', '{preference}', Suggestion), writeln(Suggestion)."

    result = subprocess.run(
        ['C:\\Program Files\\swipl\\bin\\swipl.exe', '-s', 'coping_bot.pl', '-g', query, '-t', 'halt'],
        capture_output=True, text=True
    )

    output = result.stdout.strip()
    print(f"Prolog output: {output}")

    return jsonify({
        'suggestion': output,
        'parameters': {
            'emotion': emotion,
            'stressor': stressor,
            'physical': physical,
            'time': time,
            'support': support,
            'environment': environment,
            'preference': preference
        }
    })

if __name__ == '__main__':
    app.run(port=5000)
