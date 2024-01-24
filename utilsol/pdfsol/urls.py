from django.urls import path
from . import views

app_name = 'pdfsolutions'
urlpatterns = [
    path('',views.index, name='index'),
    path('findsynonyms/',views.fetch_synonyms,name='fetch_synonyms'),
    path('upload/',views.upload_file.as_view(), name='upload_file'),
    path('savefiles/',views.highlight_and_save_pdf, name='savefiles'),   
]