"""s3 URL Configuration

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
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^bios/', include('bios.urls')),
    url(r'^competitions/', include('competitions.urls')),
    url(r'^dates/', include('dates.urls')),
    url(r'^games/', include('games.urls')),
    url(r'^places/', include('places.urls')),
    url(r'^organizations/', include('organizations.urls')),
    url(r'^sources/', include('sources.urls')),
    url(r'^teams/', include('teams.urls')),
]
