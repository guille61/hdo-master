from datetime import date
from flask import current_app
import psycopg2
from psycopg2.extras import RealDictCursor

from .forms import ModifyComputerForm
from .models import Computer


def update_computer_data(form: ModifyComputerForm, computer: Computer):
    """ Actualiza los datos del ordenador según la información indicada en el formulario de modificación.

    Args:
        form (ModifyComputerForm): Formulario de modificación de un ordenador.
        computer (Computer): Ordenador a modificar.
    """
    computer.sn = form.sn.data
    computer.hostname = form.hostname.data
    computer.pn = form.model.data
    computer.description = form.description.data
    computer.po = form.po.data
    computer.notes = form.notes.data
    computer.state_id = form.state.data
    
    match form.origin.data:
        case "is_renting":
            computer.is_external = False
            computer.is_purchase = False
        case "is_purchase":
            computer.is_external = False
            computer.is_purchase = True
        case "is_external":
            computer.is_external = True
            computer.is_purchase = False
            
    computer.update_in_db()
    
def get_suggested_hostname(computer: Computer) -> str:
    """ Sugiere un hostname para un nuevo equipo.
    Para generar el hostname utiliza el tipo del nuevo ordenador (es distinto el hostname entre una máquina de CATIA y un equipo normal), el hostname del último equipo del mismo tipo y la fecha actual (para los primeros dígitos correspondientes al año actual).

    Args:
        computer (Computer): Ordenador al cual se asignará el nuevo hostname.

    Returns:
        str: Nuevo hostname.
    """
    year = abs(date.today().year) % 100 
    
    conn = psycopg2.connect(**current_app.config["MASTER_DB"])
    cursor = conn.cursor()
    
    query = "SELECT type_name FROM computer_models WHERE pn = %(pn)s"
    cursor.execute(query, {"pn": computer.pn})
    type_name = cursor.fetchone()[0]
    
    if type_name not in current_app.config["CATIA_TYPES"]:
        where_type = "cm.type_name != 'Workstation' and cm.type_name != 'ZBook'"
    else:
        where_type = "cm.type_name = 'Workstation' or cm.type_name = 'ZBook'"
    
    if computer.is_renting:
        origin = "kostal"
        pattern = current_app.config["HOSTNAMES"][type_name][origin]["pattern"].format(year = year)
        query = f"SELECT c.hostname FROM computers c LEFT JOIN computer_models cm ON c.pn = cm.pn WHERE {where_type} AND c.hostname like %(pattern)s AND c.is_renting ORDER BY c.hostname DESC"
    elif computer.is_purchase:
        origin = "kostal"
        pattern = current_app.config["HOSTNAMES"][type_name][origin]["pattern"].format(year = year)
        query = f"SELECT c.hostname FROM computers c LEFT JOIN computer_models cm ON c.pn = cm.pn WHERE {where_type} AND c.hostname like %(pattern)s AND c.is_purchase ORDER BY c.hostname DESC"
    else:
        origin = "external"
        pattern = current_app.config["HOSTNAMES"][type_name][origin]["pattern"].format(year = year)
        query = f"SELECT c.hostname FROM computers c LEFT JOIN computer_models cm ON c.pn = cm.pn WHERE {where_type} AND c.hostname like %(pattern)s AND c.is_external ORDER BY c.hostname DESC"
    
    cursor.execute(query, {"type_name": type_name, "pattern": pattern})
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        num = str(int(result[0][-current_app.config["HOSTNAMES"][type_name][origin]["digits"]:]) + 1).zfill(current_app.config["HOSTNAMES"][type_name][origin]["digits"])
        return f"{result[0][0:-current_app.config['HOSTNAMES'][type_name][origin]['digits']]}{num}"
    
    return current_app.config["HOSTNAMES"][type_name]["kostal"]["pattern"].format(year = year).replace("%", "1".zfill(current_app.config["HOSTNAMES"][type_name]["kostal"]["digits"]))


# Modelos

def get_computer_models() -> list[any]:
    """ Devuelve un listado de todos los modelos de PC.

    Returns:
        list[any]: Lista con la información de los modelos.
    """
    conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM computer_models")
    result = cursor.fetchall()
    conn.close()
    
    return result


def get_computer_model(pn: str) -> list[any]:
    """ Devuelve la información de un modelo de PC en concreto.

    Args:
        pn (str): Product Number del modelo a buscar.

    Returns:
        list[any]: Lista con los atributos de un modelo.
    """
    conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM computer_models WHERE pn = %(pn)s", {"pn": pn})
    result = cursor.fetchone()
    conn.close()
    
    return result


def add_computer_model(pn: str, model: str, type_name: str):
    """ Introduce en el sistema un nuevo modelo de PC.

    Args:
        pn (str): Product Number del modelo.
        model (str): Nombre visual del modelo.
        type_name (str): Tipo de PC.
    """
    conn = psycopg2.connect(**current_app.config["MASTER_DB"])
    cursor = conn.cursor()
    cursor.execute("INSERT INTO computer_models (pn, model, type_name) VALUES (%(pn)s, %(model)s, %(type_name)s)", {"pn": pn, "model": model, "type_name": type_name})
    conn.commit()
    conn.close()
    