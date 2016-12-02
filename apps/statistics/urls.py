from django.conf.urls import url
from apps.statistics import views

urlpatterns = [
    url(r'^dashboard_graphs', views.dashboard_graphs, name='statistics-graphs'),
    url(r'^feedback_table', views.feedback_table, name='feedback-table'),
]
