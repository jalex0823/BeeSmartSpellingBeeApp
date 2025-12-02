from flask import Flask, jsonify, render_template_string, url_for
import os

app = Flask(__name__)

@app.get("/health")
def health():
    return jsonify(status="ok", app="simple"), 200

@app.get("/")
def index():
    # Minimal landing with a few working links
    html = """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>Simple Flask – It works ✅</title>
      <style>
        body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; padding: 2rem; background: #111; color: #f8f8f8; }
        a { color: #ffd54f; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .box { background: #1e1e1e; border: 1px solid #333; border-radius: 10px; padding: 1rem 1.25rem; max-width: 800px; }
        code { background:#222; padding: 2px 6px; border-radius: 6px; }
      </style>
    </head>
    <body>
      <h1>Simple Flask – It works ✅</h1>
      <div class="box">
        <p>This is a minimal Flask app to verify your local environment.</p>
        <ul>
          <li>Health: <a href="{{ url_for('health') }}">/health</a></li>
          <li>Index: <a href="{{ url_for('index') }}">/</a></li>
        </ul>
        <hr>
        <p>If you want to open the main BeeSmart app, try one of these (depending on which port it picked):</p>
        <ul>
          <li><a href="http://localhost:5051/" target="_blank" rel="noopener">http://localhost:5051/</a></li>
          <li><a href="http://localhost:8080/" target="_blank" rel="noopener">http://localhost:8080/</a></li>
        </ul>
        <p style="opacity:.8">Tip: On macOS, AirPlay often owns port 5000. Our main app usually shifts to 5051 or 8080.</p>
      </div>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    port = int(os.environ.get("SIMPLE_PORT", 5500))
    # Bind explicitly to localhost to avoid conflicts with system services
    app.run(host="127.0.0.1", port=port, debug=False)
