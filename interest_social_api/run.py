import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import send_from_directory
from app import create_app

app = create_app()

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

@app.route('/uploads/<int:user_id>/<filename>')
def uploaded_file(user_id, filename):
    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
    return send_from_directory(user_folder, filename)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000, debug=True)
