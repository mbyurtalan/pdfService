from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from docxcompose.composer import Composer
from docx import Document
import tempfile
import os
import shutil

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "DOCX merge API is running"})


@app.route("/merge", methods=["POST"])
def merge_docx():
    files = request.files.getlist("files")

    if not files:
        return jsonify({"error": "No files provided. Use form-data key: files"}), 400

    temp_dir = tempfile.mkdtemp()
    saved_files = []

    try:
        for file in files:
            filename = secure_filename(file.filename)

            if not filename:
                return jsonify({"error": "One uploaded file has an empty filename"}), 400

            if not filename.lower().endswith(".docx"):
                return jsonify({"error": f"{filename} is not a .docx file"}), 400

            file_path = os.path.join(temp_dir, filename)
            file.save(file_path)
            saved_files.append(file_path)

        saved_files.sort()

        master = Document(saved_files[0])
        composer = Composer(master)

        for docx_path in saved_files[1:]:
            composer.append(Document(docx_path))

        merged_path = os.path.join(temp_dir, "merged.docx")
        composer.save(merged_path)

        return send_file(
            merged_path,
            as_attachment=True,
            download_name="merged.docx",
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Note: cleanup happens after response handling can be tricky with send_file.
        # For small/simple usage this is usually fine locally, but Render may still need the file while streaming.
        # If you get file-not-found issues, remove this line and rely on ephemeral temp storage.
        pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)