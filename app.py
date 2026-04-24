from flask import Flask
import os

app = Flask(__name__)



@app.route('/')
def hello():
    # Fetch an environment variable to demonstrate reading from .env
    env_var = os.environ.get('MY_CUSTOM_VAR', 'Default Variable Value')
    
    html = f"""
    <h1>Hello from Python inside Docker! 🚀</h1>
    <p>This is a small application deployed via AWS ECS / EC2.</p>
    <p><strong>Environment Variable (MY_CUSTOM_VAR):</strong> {env_var}</p>
    """
    return html

if __name__ == '__main__':
    # Run the application on port 8000
    app.run(host='0.0.0.0', port=8000)
