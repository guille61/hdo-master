from flask import Blueprint #Importación de las funciones del espacio de trabajo

#Definir el espacio
tro = Blueprint("tro", __name__, url_prefix = "/tro")

from . import views #importa los views