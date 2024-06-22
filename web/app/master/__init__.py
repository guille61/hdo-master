import certifi
from flask import Flask, render_template # Importaciones iniciales
import os
from werkzeug.middleware.profiler import ProfilerMiddleware

from .config import Config, app_config, app_config_dev, app_config_prod # Importación de la configuración

def create_app():
    # Inicialización de la app con variabled de entrada 
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)

    # Configuraciones globales
    for key, value in app_config.items():
        app.config[key] = value

    if os.environ.get("ENV") and os.environ["ENV"] == "prod": # Configuraciones específicas de producción
        for key, value in app_config_prod.items():
            app.config[key] = value
    else: # Configuraciones específicas de desarrollo
        for key, value in app_config_dev.items():
            app.config[key] = value

    # Inclusión del certificado para la API de LC
    cas_file = certifi.where()
    with open(f"{app.root_path}/static/esseweb005.pem", "rb") as f:
        kostal_ca = f.read()
    with open(cas_file, "ab") as f:
        f.write(kostal_ca)

    # Inicializaciones de las importaciones
    from .auth.views import login_manager
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Por favor, inicia sesión para ver esta página"
    login_manager.login_message_category = "info" # Color Bootstrap del mensaje
    login_manager.init_app(app)    

    ## Inclusión de los Blueprints (espacios de trabajo) y su registro. De esta manera se dispone de una applicación modular
    # Módulo de autenticación
    from .auth import auth as bp
    app.register_blueprint(bp)
    
    # Módulo principal
    from .main import main as bp
    app.register_blueprint(bp)
    
    # Módulo de TRO
    from .tro import tro as bp
    app.register_blueprint(bp)
    
    # Módulo de Computers
    from .computers import computers as bp
    app.register_blueprint(bp)

    # app = ProfilerMiddleware(app, restrictions=[5]) # Para debugar el tiempo de ejecución de los procesos

    return app