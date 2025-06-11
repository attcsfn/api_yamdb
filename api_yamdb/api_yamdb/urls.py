from django.conf.urls import include
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from rest_framework.routers import DefaultRouter  #  код для удаления
from api.views import CommentViewSet  #  код для удаления

router = DefaultRouter()  #  код для удаления
router.register(r'comments', CommentViewSet)  #  код для удаления

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
]
