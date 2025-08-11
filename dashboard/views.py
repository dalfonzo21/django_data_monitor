from collections import Counter
from datetime import datetime
from django.shortcuts import render
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required
# Create your views here.
def index(request):
    response = requests.get(settings.API_URL)  # URL de la API
    posts = response.json()  # Convertir la respuesta a JSON
    # Número total de respuestas
    total_responses = len(posts)
    servicios = []
    customer_names = []
    citas_realizadas = 0
    
    hoy = datetime.today().date()  # fecha actual sin hora
    for key, value in posts.items():
        # Verificamos que sea un dict y tenga el campo 'service'
        if isinstance(value, dict) and 'service' in value:
            servicios.append(value['service'].lower())
        if isinstance(value, dict) and 'name' in value:
            customer_names.append(value['name'].lower())
        # Contar citas realizadas (fecha <= hoy)
        if isinstance(value, dict) and 'fecha' in value:
            try:
                fecha_cita = datetime.strptime(value['fecha'], '%Y-%m-%d').date()
                if fecha_cita <= hoy:
                    citas_realizadas += 1
            except ValueError:
                # Si la fecha no es válida o está mal formateada, la ignoramos
                pass

    
    # Contar ocurrencias de cada servicio
    contador = Counter(servicios)
    contador_names = Counter(customer_names)
    
    # Obtener el servicio más común (más solicitado)
    if contador:
        mas_solicitado = contador.most_common(1)[0][0]  # servicio con más apariciones
    else:
        mas_solicitado = None

    if contador_names:
        mas_frecuente = contador_names.most_common(1)[0][0]
    else:
        mas_frecuente = None
    data = {
        'title': "Landing Page' Dashboard",
        'total_responses': total_responses,
        'mas_solicitado': mas_solicitado.upper() if mas_solicitado else "No data available" ,
        'mas_frecuente': mas_frecuente.upper() if mas_frecuente else "No data available",
        'citas_realizadas': citas_realizadas,
    }
    return render(request, 'dashboard/index.html', data)