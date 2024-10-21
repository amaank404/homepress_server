import mimetypes
from pathlib import Path

import homepress
import homepress.renderer
from flask import Flask, Response, jsonify, redirect, request
from werkzeug.utils import secure_filename

from . import db, utils
from .config import config

app = Flask(__name__)

manager = db.SessionsManager()

@app.route("/")
def index():
    return redirect("https://github.com/amaank404/homepress_server")

@app.route("/api/v1/session_create")
def session_create():
    # Create a session
    token = manager.add()

    # Formulate the return response
    resp = jsonify({"token": token})
    resp.status_code = 201

    return resp

@app.route("/api/v1/session_delete")
def session_delete():
    token = request.args["token"]
    manager.remove(token)

@app.route("/api/v1/sessions")
def sessions():
    resp = jsonify(manager.sessions)
    return resp

@app.route("/api/v1/file_upload", methods=["POST", "GET"])
def upload():
    ctx = manager.get_context(request.args["token"])

    # If the request might contain file data
    if request.method == 'POST':
        # Check if an attached file is there
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']

        # Browsers may attach empty files at times
        if file.filename == '':
            return Response("empty file attachment", status=400)
        
        if file:
            filename = secure_filename(file.filename)
            ext = Path(filename).suffix.strip('.')

            if ext in homepress.renderer.formats:
                fid = utils.create_safe_name()
                save_path = config.uploads_directory / fid
                file.save(save_path)

                fsize = save_path.stat().st_size
                (fmime, _) = mimetypes.guess_type(filename)

                ctx.add_file(fid, fsize, fmime, filename)
            
                return Response(status=201)
        
            else:
                return Response(f"only the following are supported: {homepress.renderer.formats!r}", status=415)
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

def run_server():
    app.run("localhost", 8001, debug=True)