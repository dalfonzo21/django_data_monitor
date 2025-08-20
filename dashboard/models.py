from django.db import models

class DashboardModel(models.Model):

  class Meta:
     permissions = [
           ("index_viewer", "Can show to index view (function-based)"),
     ]