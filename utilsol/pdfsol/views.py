from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
import fitz, os, json, nltk, shutil, datetime
from nltk.corpus import wordnet
from django.conf import settings
from os import path
from shutil import make_archive
import pandas as pd
import openpyxl
from io import BytesIO

# Create your views here.
def index(request):
    # return HttpResponse('welcome')
    return render(request,'index.html')

# Fetch synonyms of the keyword
def fetch_synonyms(request):
    synresults = []
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        keywords = data.get('keywrd').split(',')
        for idx, item in enumerate(keywords,start=1):
            val = get_synonyms(item)
            if not val:
                synresults.append(item)
            else:
                synresults.append(val)
        return JsonResponse({'synonyms':synresults})

# Get synonyms of the keyword
def get_synonyms(word):
    nltk.download('wordnet')
    synonyms = []
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())
    return list(set(synonyms))

# def upload_file(request):
#     if request.method == 'POST':
#         request.upload_handlers = [TemporaryFileUploadHandler()]
#         uploaded_files = request.FILES.getlist('files')
#         file_urls = []

#         if not uploaded_files:
#             return JsonResponse({'error': 'No files uploaded'}, status=400)

#         if request.user.is_anonymous:
#             app_media_path = os.path.join(settings.MEDIA_ROOT, 'temp')
#         else:
#             app_media_path = os.path.join(settings.MEDIA_ROOT, request.user.username)

#         os.makedirs(app_media_path, exist_ok=True)
#         success = clear_folder(app_media_path)
#         if success:
#             for uploaded_file in uploaded_files:
#                 file_path = os.path.join(app_media_path, uploaded_file.name)

#                 with open(file_path, 'wb') as destination:
#                     for chunk in uploaded_file.chunks():
#                         destination.write(chunk)

#                 file_url = os.path.join(settings.MEDIA_URL, request.user.username, uploaded_file.name)
#                 file_urls.append(file_url)
#             return JsonResponse({'message': 'Files uploaded successfully', 'file_urls': file_urls})
#         else:
#             return JsonResponse({'error': f"Failed to clear folder {app_media_path}."}, status=400)
#     else:
#         return JsonResponse({'error': 'Invalid HTTP method'}, status=400)

@method_decorator(csrf_protect, name='dispatch')
class upload_file(View):
    # Set upload_handlers at the class level
    http_method_names = ['post']
    upload_handlers = [TemporaryFileUploadHandler()]

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            uploaded_files = request.FILES.getlist('files')
            file_urls = []

            if not uploaded_files:
                return JsonResponse({'error': 'No files uploaded'}, status=400)

            if request.user.is_anonymous:
                app_media_path = os.path.join(settings.MEDIA_ROOT, 'temp')
            else:
                app_media_path = os.path.join(settings.MEDIA_ROOT, request.user.username)

            os.makedirs(app_media_path, exist_ok=True)
            success = clear_folder(app_media_path)

            if success:
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(app_media_path, uploaded_file.name)

                    with open(file_path, 'wb') as destination:
                        for chunk in uploaded_file.chunks():
                            destination.write(chunk)

                    file_url = os.path.join(settings.MEDIA_URL, request.user.username, uploaded_file.name)
                    file_urls.append(file_url)

                return JsonResponse({'message': 'Files uploaded successfully', 'file_urls': file_urls})
            else:
                return JsonResponse({'error': f"Failed to clear folder {app_media_path}."}, status=400)
        else:
            return JsonResponse({'error': 'Invalid HTTP method'}, status=400)
        
def clear_folder(folder_path):
    try:
        # Iterate over all files in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            # Check if the path is a file (not a directory)
            if os.path.isfile(file_path):
                # Remove the file
                os.unlink(file_path)
            else:
                print(file_path)
                shutil.rmtree(file_path)

        return True  # Operation successful
    except Exception as e:
        #print(f"Error clearing folder {folder_path}: {e}")
        return False  # Operation failed

def highlight_and_save_pdf(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        synonyms = list(data.get('keywrd').split(','))
        output_buffer = BytesIO()
        foundkeys = []

        if request.user.is_anonymous:
            app_media_path = os.path.join(settings.MEDIA_ROOT, 'temp')
        else:
            app_media_path = os.path.join(settings.MEDIA_ROOT, request.user.username)
        
        os.makedirs(app_media_path, exist_ok=True)
        file_list = os.listdir(app_media_path)
        os.makedirs(app_media_path + r'\output', exist_ok=True)
        
        for filename in file_list:
            print('file', filename)
            file_path = os.path.join(app_media_path, filename)
            newfolder = filename[:-4].strip()
            os.makedirs(app_media_path + r'\output'+f"\{newfolder}", exist_ok=True)

            if os.path.isfile(file_path):
                pdf_document = fitz.open(file_path)

                for page_num in range(pdf_document.page_count):
                    page = pdf_document[page_num]

                    for idx, item in enumerate(synonyms,start=1):
                        quads = page.search_for(item)
                        page.add_highlight_annot(quads)
                        foundkeys.append(item+f",{str(page_num+1)},{filename}")
                
                # Close the PDF document
                pdf_document.save(output_buffer)
                pdf_document.close()

                output_image_path = os.path.join(app_media_path + r'\output'+f"\{newfolder}", f"{newfolder}_highlighted.pdf")

                with open(output_image_path, mode='wb') as f:
                    f.write(output_buffer.getbuffer())

        zipname =datetime.datetime.today().strftime("%Y%m%d%H%M%S")
        xloutput(foundkeys,app_media_path)
        if request.user.is_anonymous:
            shutil.make_archive(settings.MEDIA_ROOT+"\\"+zipname,"zip",settings.MEDIA_ROOT,"temp")
        else:
            shutil.make_archive(settings.MEDIA_ROOT+"\\"+zipname,"zip",settings.MEDIA_ROOT,request.user.username)
        
        app_media_path = str(settings.MEDIA_ROOT) + f"\{zipname}.zip"
        response = HttpResponse(open(app_media_path, 'rb').read())
        return response
    else:
        return JsonResponse({'error': 'Invalid HTTP method'}, status=400)

def xloutput(data,path):
    if data !='':
        df = pd.DataFrame([sub.split(",") for sub in data], columns=["keyword", "page num", "file name"])
        df.to_excel(excel_writer=path+'\\results.xlsx',sheet_name='data',index=False)