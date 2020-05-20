"""mydj1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from importDB import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', views.homepage),
    path('', views.home, name = 'home'),
    # path('', include('importDB.urls')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('showdbsql/', views.showdbsql),
    path('showdboracle/', views.showdbOracle),
    path('rodreport/', views.rodReport),
    path('prpmdump/',views.prpmdump), 
    path('prpmdump/prpmdumpResults',views.dump),
    path('dQueryReports/',views.dQueryReports),
    path('dQueryReports/queryDumpResults',views.dQuery),
    path('revenues/',views.pageRevenues),
    path('exFund/',views.pageExFund),
    path('ranking/',views.pageRanking),
    path('revenues/graph', views.revenues_graph)
    # path('revenues/showrevenues',views.pageRevenues),
    # path('revenues/?',views.pageRevenues),
]
