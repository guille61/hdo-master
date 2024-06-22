from flask import Blueprint #Importación de las funciones del espacio de trabajo

#Definir el espacio
computers = Blueprint("computers", __name__, url_prefix = "/computers")

from . import views #importa los views
