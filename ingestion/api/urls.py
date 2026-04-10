from django.urls import path
from .views import UploadView
from .views import UploadView, PdfToMarkdownView
from .views import ChunkMarkdownView
from .views import EmbedChunksView
from .views import CheckFileStatusView

urlpatterns=[
    path('upload/', UploadView.as_view(), name='upload'),
    path('convert/pdf/',PdfToMarkdownView.as_view()),
    path('chunk/markdown/',ChunkMarkdownView.as_view()),
    path('embed/chunks/',EmbedChunksView.as_view()),
    path('check-status/', CheckFileStatusView.as_view()),
]