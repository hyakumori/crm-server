from django.urls import path

from .restful import *

url_patterns = [
    path("setup", setup)
]
