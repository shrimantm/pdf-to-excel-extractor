from flask import Flask, render_template, request, send_file, redirect
from flask_cors import CORS  # Import CORS
import os
from werkzeug.utils import secure_filename
from utils.pdf_extractor import extract_data
import pandas as pd
from io import BytesIO

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'pdf_file' not in request.files:
            return redirect(request.url)
        file = request.files['pdf_file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract data from the PDF
            extracted_rows = extract_data(filepath)
            columns = ["Seat No", "Name", "Sem", "Subject Code", "Subject Name",
                       "ISE", "ESE", "TOTAL", "TW", "PR", "OR", "TUT",
                       "Tot%", "Crd", "Grd", "GP", "CP", "SGPA", "Credits"]
            df = pd.DataFrame(extracted_rows, columns=columns)
            
            # Create an Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Extracted Data')
            output.seek(0)
            
            return send_file(output, as_attachment=True, download_name='Student_Marks.xlsx')
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
