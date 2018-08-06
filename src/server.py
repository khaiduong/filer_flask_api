#!filer/bin/python
import os
import filecmp
import shutil
import json
from flask import Flask, request, redirect, url_for, send_from_directory, abort, jsonify, Response
from werkzeug import secure_filename

UPLOAD_FOLDER = os.path.abspath('storage')
TRASH = os.path.abspath('trash')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'yml'])

for folder in (UPLOAD_FOLDER, TRASH):
    if not os.path.exists(folder):
        os.makedirs(folder)


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TRASH'] = TRASH
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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def __CheckIdenticalFile(filename, directory):
    files = os.listdir(directory)
    isIdentical = False
    if files and os.path.exists(directory):
        for f in files:
            isIdentical |= filecmp.cmp(filename, os.path.join(directory, f))
            if isIdentical:
                return filename, f### This shoule be returned with this order
    return None



@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        temp_dir = "/tmp/tmp/"
        app.config['TMP_DIR'] = temp_dir
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        file = request.files['file']
        if file and allowed_file(file.filename):
            app.logger.info('**found file %s' % file.filename)
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['TMP_DIR'], filename))
            checkIdentical = __CheckIdenticalFile(os.path.join(app.config['TMP_DIR'], filename), app.config['UPLOAD_FOLDER'])
            if not checkIdentical:
                shutil.copyfile(os.path.join(app.config['TMP_DIR'], filename), os.path.join(app.config['UPLOAD_FOLDER'], filename))
                app.logger.info("Removing tmp file from tmp filesystem")
                os.remove(os.path.join(app.config['TMP_DIR'], filename))
                # for browser, add 'redirect' function on top of 'url_for'
                return redirect(url_for('uploaded_file', filename=filename))
            app.logger.info("removing tmp file %s" % filename)
            os.remove(os.path.join(app.config['TMP_DIR'], filename))
	    error_mess = {'message': 'CONFLICT: File %s does exist or have the same contents with file %s' % tuple(checkIdentical)}
	    response = Response(json.dumps(error_mess), status=409,  mimetype='application/json')
            #abort(409, {'message': 'CONFLICT: File %s does exist or have the same contents with file %s' % tuple(checkIdentical)})
        else:
	    error_mess ={"error": "UPLOAD ERROR: unable to upload file %s. " \
                         "Please be advised that only file with extension in %s allowed to upload to filer" \
                         %(file.filename, list(ALLOWED_EXTENSIONS))}
            response = Response(json.dumps(error_mess), status=404,  mimetype='application/json')
	return response
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


@app.route('/deleteItem/<item>', methods=['DELETE'])
def delete_item(item):
    """This functuon will help to remove a file by name from filer"""
    filename = os.path.join(UPLOAD_FOLDER, item)
    if os.path.exists(filename):
        app.logger.info("removing file %s" % filename)
        shutil.move(filename, os.path.join(app.config['TRASH'], item))
        #os.remove(filename)
        removeMsg = {'error' : "File %s has been moved to trash. To recovered the file, please contact your side administrator" % item}
        response = Response(json.dumps(removeMsg), status=202, mimetype='application/json')
        return response
    invalidFileObjectErrorMsg = {
        "error": "The file with name %s that was provided was not found, so therefor unable to delete" % item
    }
    response = Response(json.dumps(invalidFileObjectErrorMsg), status=404, mimetype='application/json')
    return  response



@app.errorhandler(413)
def request_entity_too_large(e):
    return 'File Too Large', 413


@app.errorhandler(400)
def Bad_Request(error):
    return 'Please select the file before upload', 400


@app.errorhandler(409)
def Bad_Request(error):
    response = jsonify(error.description['message'])
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
