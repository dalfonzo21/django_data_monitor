from django.db import models

# Create your models here.
#define configuracion de la aplicacion, establece modelo que en py son clases.

class DashboardModel(models.Model):

  class Meta:
     permissions = [
           ("index_viewer", "Can show to index view (function-based)"), #nombre /descripcion del permiso 
     ]