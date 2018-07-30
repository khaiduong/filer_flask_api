#!filer/bin/python
import os
from flask import Flask, request, redirect, url_for, send_from_directory, abort, jsonify
from werkzeug import secure_filename

UPLOAD_FOLDER = os.path.abspath('storage')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'yml'])

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 6 * 1024 * 1024 #limit the maximum allowed payload to 16 megabytes


@app.route('/files')
def list_files():
    """Endpoint to list files on the server."""
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(path):
            files.append(filename)
    return jsonify({'List of Files: ': files})


def allowed_file(filename):
    """This function verify whether the given file is allowed to upload to server"""
    # name, ext = os.path.splitext(filename)
    #if not ext:
        #return True
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            app.logger.info('**found file %s' % file.filename)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # for browser, add 'redirect' function on top of 'url_for'
            return redirect(url_for('uploaded_file', filename=filename))
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    """

@app.route('/files/<filename>')
def uploaded_file(filename):
    """This function will help to display content of an uploaded file"""
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/deleteItem/<item>', methods=['GET', 'POST'])
def delete_item(item):
    """This functuon will help to remove a file by name from filer"""
    filename = os.path.join(UPLOAD_FOLDER, item)
    if os.path.exists(filename):
        app.logger.info("removing file %s" % filename)
        os.remove(filename)
    else:
        return "File %s not found" % item
    return "DELETED! File %s has been removed from filer" % item


@app.errorhandler(413)
def request_entity_too_large(e):
    return 'File Too Large', 413


@app.errorhandler(400)
def Bad_Request(error):
    return 'Please select the file before upload', 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)