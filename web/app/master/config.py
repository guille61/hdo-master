#Se crea una clase de configuración

app_config = {
    "VERSION": "0.1.0",
    "APP_NAME": "HDO MASTER",    

    # AD API
    "AD_API_URI": "https://esseweb005.es.kostal.int/ad-api",
    "AD_API_TOKEN_NAME": "Token",
    "AD_API_TOKEN_VALUE": "5b06eec6fc54f4f9e57d4faecdefbbe35b51b3284ef58e5d0e64b52b0aa9a3e0",
    
    # TRO
    "TRO_EXCEL_COLUMNS": {
        "type_name": 0,
        "manufacturer": 1,
        "pn": 2,
        "description": 3,
        "sn": 4,
        "invoice": 6,
        "order_num": 7,
        "end_date": 14,
        "start_date": 18,
        "price": 19,
        "status": 20,
        "period": 21,
        "id": 22
    },
    
    # Computers
    "COMPUTER_MODELS": ["Laptop", "PC", "PC Mini", "Tablet", "Workstation", "ZBook"],
    "HOSTNAMES": {
        "Laptop": {"kostal": {"pattern": "ES{year}0%", "digits": 3}, "external": {"pattern": "ES{year}09%", "digits": 2}},
        "Tablet": {"kostal": {"pattern": "ES{year}0%", "digits": 3}, "external": {"pattern": "ES{year}09%", "digits": 2}},
        "PC": {"kostal": {"pattern": "ES{year}0%", "digits": 3}, "external": {"pattern": "ES{year}09%", "digits": 2}},
        "PC Mini": {"kostal": {"pattern": "ES{year}0%", "digits": 3}, "external": {"pattern": "ES{year}09%", "digits": 2}},
        "Workstation": {"kostal": {"pattern": "ESSECAD%", "digits": 3}, "external": {"pattern": "ESSECAD9%", "digits": 2}},
        "ZBook": {"kostal": {"pattern": "ESSECAD%", "digits": 3}, "external": {"pattern": "ESSECAD9%", "digits": 2}},
    },
    "CATIA_TYPES": ["Workstation", "ZBook"]
}

app_config_dev = {
    "MASTER_DB": {
        "host": "127.0.0.1",
        "port": "5432",
        "database": "master",
        "user": "master_data",
        "password": "pwd4MASTER"
    },
    
}

app_config_prod = {
    
}

class Config:
    #Se añaden los parametros generales como la clase secreta, configuraciones de la base de datos o en configuración de correo (no necesario)
    SECRET_KEY = "Proyecto Rework 3 modulo Operator"
    SESSION_TYPE = "filesystem"

    #Se define un método estático de la inicialización de la app
    @staticmethod
    def init_app(app):
        pass
    