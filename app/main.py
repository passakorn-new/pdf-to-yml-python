from flask import Flask, request, after_this_request, send_file, flash, redirect
import logging, secrets, PyPDF2, yaml, os, re

app = Flask(__name__)

@app.route("/uploader", methods=["POST"])
def uploader():
    input_filename = request.files['pdf_file'].filename
    input_content_type = request.files['pdf_file'].content_type
    
    if str(input_content_type) != 'application/pdf':
        flash('File is not PDF')
        return redirect(request.url)

    temp_filename = write_yaml_file(request.files['pdf_file'])
    file_path = f'{os.path.abspath(os.getcwd())}/{temp_filename}.yml'
    @after_this_request
    def remove_file(response):
        try:
            os.remove(file_path)
        except Exception:
             logging.exception("Error removing or closing downloaded file handle")
        return response
    return send_file(file_path, attachment_filename = f'{re.sub(".pdf", "", input_filename)}.yml', as_attachment = True)

def write_yaml_file(pdf_file):
    pdfReader = PyPDF2.PdfFileReader(pdf_file)
    temp_filename = secrets.token_hex(10)

    dict_file = {}
    field_default = {
      "fill_in": "{var}",
      "prefix": "",
      "province": "",
      "type": str("normal")
    }
    
    for key in pdfReader.getFields().keys():
      dict_file[str(key)] = dict(field_default)

    with open(f'{os.path.abspath(os.getcwd())}/{temp_filename}.yml', 'w') as file:
       yaml.dump(dict_file, file)

    return temp_filename