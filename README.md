**PDF Highlighter**
This Django project provides a web application for highlighting keywords in PDF files, extracting synonyms, and generating a results Excel file.

Install the required dependencies:
pip install -r requirements.txt

Run the development server:
python manage.py runserver

The application should now be running locally. Access it through your web browser at http://localhost:8000/.

**Usage**
1. Visit the home page:
Open your web browser and navigate to http://localhost:8000/. You should see the home page with the option to upload files and highlight keywords.

2. Upload Files:
Use the file upload feature to upload PDF files for keyword highlighting.

3. Highlight Keywords:
Enter keywords separated by commas to highlight them in the uploaded PDF files. The results will be saved in a new PDF file and an Excel file.

4. Download Results:
Download the highlighted PDF files and the results Excel file from the provided links.

**Dependencies**
Django
PyMuPDF (fitz)
NLTK
Pandas
Openpyxl
