from flask import Blueprint #Importación de las funciones del espacio de trabajo

#Definir el espacio
main = Blueprint("main", __name__, url_prefix = "/")

from . import views #importa los views
