from collections import Counter
from datetime import datetime
from django.shortcuts import render
import requests
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required, permission_required
import logging

logger = logging.getLogger(__name__)

@login_required
@permission_required('dashboard.index_viewer', raise_exception=True)
# Create your views here.
def index(request):
    api_available = True
    api_error_msg = None
    posts = {}
    
    try:
        try:
            response = requests.get(settings.API_URL, timeout=5)  # URL de la API
            response.raise_for_status()  # Lanza excepción si status != 2xx
            posts = response.json()  # Convertir la respuesta a JSON
        except requests.exceptions.Timeout:
            api_available = False
            api_error_msg = "La API tardó demasiado en responder (timeout > 5s)"
            logger.warning(f"API timeout: {settings.API_URL}")
        except requests.exceptions.ConnectionError:
            api_available = False
            api_error_msg = "No se puede conectar con la API"
            logger.warning(f"API connection error: {settings.API_URL}")
        except requests.exceptions.HTTPError as e:
            api_available = False
            api_error_msg = f"Error HTTP en la API: {e.response.status_code}"
            logger.warning(f"API HTTP error {e.response.status_code}: {settings.API_URL}")
        except (requests.exceptions.RequestException, ValueError) as e:
            api_available = False
            api_error_msg = f"Error al obtener datos de la API: {str(e)}"
            logger.warning(f"API error: {str(e)}")
    except Exception as e:
        # Catch-all para cualquier error inesperado
        api_available = False
        api_error_msg = "Error inesperado al procesar datos"
        logger.exception(f"Unexpected error in index view: {str(e)}")
        posts = {}
    
    # Número total de respuestas
    total_responses = len(posts)
    servicios = []
    customer_names = []
    citas_realizadas = 0
    hoy = datetime.today().date()  # fecha actual sin hora
    citas_por_fecha = {}  # Para el gráfico
    tabla_respuestas = []
    for key, value in posts.items():
        if isinstance(value, dict):
            nombre = value.get('name', '')
            servicio = value.get('service', '')
            if nombre or servicio:
                tabla_respuestas.append({'name': nombre, 'service': servicio})

    for key, value in posts.items():
        # Verificamos que sea un dict y tenga el campo 'service'
        if isinstance(value, dict) and 'service' in value:
            servicios.append(value['service'].lower())
        if isinstance(value, dict) and 'name' in value:
            customer_names.append(value['name'])
        # Contar citas realizadas (fecha <= hoy)
        if isinstance(value, dict) and 'fecha' in value:
            try:
                fecha_cita = datetime.strptime(value['fecha'], '%Y-%m-%d').date()
                if fecha_cita <= hoy:
                    citas_realizadas += 1
                    fecha_str = fecha_cita.strftime('%Y-%m-%d')
                    citas_por_fecha[fecha_str] = citas_por_fecha.get(fecha_str, 0) + 1
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
        'mas_solicitado': mas_solicitado.upper() if mas_solicitado else "No data available",
        'mas_frecuente': mas_frecuente if mas_frecuente else "No data available",
        'citas_realizadas': citas_realizadas,
        'tabla_respuestas': tabla_respuestas,  # <-- agrega esto
        'api_available': api_available,
        'api_error_msg': api_error_msg,
    }
    return render(request, 'dashboard/index.html', data)

def datos_grafico(request):
    """Función que devuelve datos para el gráfico"""
    posts = {}
    try:
        response = requests.get(settings.API_URL, timeout=5)
        response.raise_for_status()
        posts = response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        # Retornar datos vacíos en caso de error
        logger.warning(f"API error in datos_grafico: {e}")
        return JsonResponse({
            "labels": [],
            "citas": [],
            "visitantes": [],
            "error": True
        })
    except Exception as e:
        # Catch-all general
        logger.exception(f"Unexpected error in datos_grafico: {str(e)}")
        return JsonResponse({
            "labels": [],
            "citas": [],
            "visitantes": [],
            "error": True
        })
    
    citas_por_fecha = {}
    
    # Procesar los datos igual que en index()
    for key, value in posts.items():
        if isinstance(value, dict) and 'fecha' in value:
            try:
                fecha_cita = datetime.strptime(value['fecha'], '%Y-%m-%d').date()
                fecha_str = fecha_cita.strftime('%Y-%m-%d')
                citas_por_fecha[fecha_str] = citas_por_fecha.get(fecha_str, 0) + 1
            except ValueError:
                pass
    
    # Preparar datos para el gráfico
    if citas_por_fecha:
        # Ordenar fechas
        fechas_ordenadas = sorted(citas_por_fecha.keys())
        citas_counts = [citas_por_fecha[fecha] for fecha in fechas_ordenadas]
        
        # Para visitantes, usar una estimación simple: citas * 3
        visitantes_counts = [citas * 3 for citas in citas_counts]
    else:
        fechas_ordenadas = []
        citas_counts = []
        visitantes_counts = []
    
    return JsonResponse({
        "labels": fechas_ordenadas,
        "citas": citas_counts,
        "visitantes": visitantes_counts
    })