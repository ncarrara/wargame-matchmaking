from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# Path to the folder you want to serve
FOLDER_TO_SERVE = os.path.join(os.getcwd(), 'uploads')

@app.route('/')
def index():
    return "Welcome! Go to /files/<filename> to access files."

@app.route('/uploads/<path:filename>')
def serve_file(filename):
    print(filename)
    # Safely send a file from the folder
    return send_from_directory(FOLDER_TO_SERVE, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
