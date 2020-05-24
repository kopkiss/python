from django.urls import path, include
from . import views  # . คือ อยู่ใน folder เดียวกัน


urlpatterns = [
    path('', views.home, name = 'home'),
    # path('django_plotly_dash/', include('django_plotly_dash.urls')),
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
]