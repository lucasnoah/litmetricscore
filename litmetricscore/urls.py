"""litmetricscore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from core.views import TextFileViewSet, CorpusItemViewSet, CorpusItemCollectionViewset, WordTokenViewSet, \
    CorpusItemFilterViewSet
from topic_modeling.views import TopicModelViewSet



router = routers.DefaultRouter()
router.register(r'texts', TextFileViewSet)
router.register(r'corpusitems', CorpusItemViewSet)
router.register(r'collections', CorpusItemCollectionViewset)
router.register(r'tokens', WordTokenViewSet)
router.register(r'filters', CorpusItemFilterViewSet)
router.register('models', TopicModelViewSet)


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^auth/', include('djoser.urls.authtoken')),
]

urlpatterns = urlpatterns + router.urls