from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from docxcompose.composer import Composer
from docx import Document
import tempfile
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/merge", methods=["POST"])
def merge_docx():

    files = request.files.getlist("files")

    if not files:
        return jsonify({"error": "No files provided"}), 400

    saved_files = []

    # Save uploaded files
    for file in files:
        filename = secure_filename(file.filename)

        if not filename.lower().endswith(".docx"):
            return jsonify({
                "error": f"{filename} is not a DOCX file"
            }), 400

        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)
        saved_files.append(path)

    # Sort to preserve order
    saved_files.sort()

    try:

        master = Document(saved_files[0])
        composer = Composer(master)

        for docx_path in saved_files[1:]:
            composer.append(Document(docx_path))

        merged_path = os.path.join(
            OUTPUT_FOLDER,
            "merged.docx"
        )

        composer.save(merged_path)

        return send_file(
            merged_path,
            as_attachment=True,
            download_name="merged.docx"
        )

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )