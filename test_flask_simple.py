from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Flask is working!'

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'Simple Flask test server'}

if __name__ == '__main__':
    print("Starting simple Flask test server on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
