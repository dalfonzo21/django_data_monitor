from django.urls import path
from . import views

urlpatterns = [
   path("", views.index, name="index"),
   path('datos-grafico/', views.datos_grafico, name='datos_grafico'),

]