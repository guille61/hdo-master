"""
Estados:
1. Nuevo
|
2. Configurado
|
3. Pendiente de entrega
|
4. En uso
|
5. Baja
|
6. Formateado
|
    7. Recompra
    8. Devuelto Econocom
    9. Devuelto Terceros
    10. Tirado
"""

from flask import current_app
import psycopg2
from psycopg2.extras import RealDictCursor, RealDictRow


class Computer:
    hostname: str
    sn: str
    pn: str
    description: str
    is_renting: bool
    is_purchase: bool
    is_external: bool
    notes: str
    state_id: int

    def __init__(self, sn: str, pn: str = None, po: int = None, hostname: str = None, description: str = None, is_renting: bool = True, is_purchase: bool = False, is_external: bool = False, notes: str = None, state_id: int = 1):
        # Si ya existe, coge los valores de la base de datos
        conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM computers WHERE sn = %(sn)s", {"sn": sn})
        result = cursor.fetchone()
        conn.close()

        if result:
            self.sn = result["sn"]
            self.pn = result["pn"]
            self.po = result["po"]
            self.hostname = result["hostname"]
            self.description = result["description"]
            self.is_renting = result["is_renting"]
            self.is_purchase = result["is_purchase"]
            self.is_external = result["is_external"]
            self.notes = result["notes"]
            self.state_id = result["state_id"]
        else:
            self.sn = sn
            self.pn = pn
            self.po = po
            self.hostname = hostname
            self.description = description
            self.is_renting = is_renting
            self.is_purchase = is_purchase
            self.is_external = is_external
            self.notes = notes
            self.state_id = state_id

    def __repr__(self):
        return self.sn
    
    def get_data(self) -> list[RealDictRow]:
        """ Obtiene toda la información del Computer (JOIN con tablas adicionales).
        """
        conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        
        query = "SELECT c.hostname, c.sn, c.pn, cm.model, cm.type_name, c.description, c.is_renting, c.is_purchase, c.is_external, c.notes, c.state_id, c.po, t.id AS tro_id, t.start_date, t.end_date, cs.name AS state_name, (CASE WHEN c.is_purchase THEN 'Compra' WHEN c.is_external THEN 'External' ELSE 'Renting' END) as origin FROM computers AS c LEFT JOIN tro AS t ON t.sn = c.sn LEFT JOIN computer_models AS cm ON cm.pn = c.pn JOIN computer_states AS cs ON cs.id = c.state_id WHERE c.sn = %(sn)s"
        cursor.execute(query, {"sn": self.sn})
        data = cursor.fetchone()
        conn.close()
        
        return data
    
    def update_in_db(self):
        """ Actualiza los valores de este Computer en la base de datos con los valores actuales.
        """
        conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
        cursor = conn.cursor()

        cursor.execute("UPDATE computers SET hostname = %(hostname)s, pn = %(pn)s, description = %(description)s, is_renting = %(is_renting)s, is_purchase = %(is_purchase)s, is_external = %(is_external)s, notes = %(notes)s, state_id = %(state_id)s WHERE sn = %(sn)s", self.__dict__)
        conn.commit()

        conn.close()
        
    def delete(self):
        """ Elimina el ordenador en la base de datos.
        """
        conn = psycopg2.connect(**current_app.config["MASTER_DB"])
        cursor = conn.cursor()

        cursor.execute("DELETE FROM computers WHERE sn = %(sn)s", {"sn": self.sn})
        conn.commit()

        conn.close()



    # Funciones relacionadas con el ciclo de vida de un ordenador

    def add(self, pn: str = None, po: int = None):
        """ Añade un nuevo Computer a la base de datos.
        """
        if not pn and not self.pn:
            raise RuntimeError("No se ha especificado un Product Number.")
        
        conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        
        if pn:
            self.pn = pn
        if po:
            self.po = po

        if po:
            cursor.execute("INSERT INTO computers (sn, pn, po, is_renting, is_purchase, is_external) VALUES (%(sn)s, %(pn)s, %(po)s, %(is_renting)s, %(is_purchase)s, %(is_external)s)", self.__dict__)
        else:
            cursor.execute("INSERT INTO computers (sn, pn, is_renting, is_purchase, is_external) VALUES (%(sn)s, %(pn)s, %(is_renting)s, %(is_purchase)s, %(is_external)s)", self.__dict__)
            
        conn.commit()
        conn.close()
    
    def configure(self, hostname: str):
        """ Añade un hostname al equipo tras realizar la configuración de este.
        """
        if not self.state_id == 1:
            raise RuntimeError(f"El estado actual del equipo no permite realizar esta acción. Estado esperado 1 - Estado actual {self.state_id}")
        
        self.hostname = hostname
        self.state_id = 2
        self.update_in_db()
    
    def assign(self, description: str):
        """ Asigna el ordenador a un usuario o posición.
        """
        if not self.state_id == 2:
            raise RuntimeError(f"El estado actual del equipo no permite realizar esta acción. Estado esperado 2 - Estado actual {self.state_id}")
        
        self.description = description
        self.state_id = 3
        self.update_in_db()

    def hand_over(self, previous_computer_sn: str = None):
        """ Marca el equipo como entregado a usuario o posición de uso.
        """
        if not self.state_id == 3:
            raise RuntimeError(f"El estado actual del equipo no permite realizar esta acción. Estado esperado 3 - Estado actual {self.state_id}")
        
        self.state_id = 4
        self.update_in_db()

        if previous_computer_sn:
            previous_computer_sn = Computer(previous_computer_sn)
            previous_computer_sn.retire()

    def retire(self):
        """ Marca el equipo como retirado (baja).
        """
        if not self.state_id == 4:
            raise RuntimeError(f"El estado actual del equipo no permite realizar esta acción. Estado esperado 4 - Estado actual {self.state_id}")
        
        self.state_id = 5
        self.update_in_db()

    def format(self):
        """ Marca el equipo como formateado.
        """
        if not self.state_id == 5:
            raise RuntimeError(f"El estado actual del equipo no permite realizar esta acción. Estado esperado 5 - Estado actual {self.state_id}")
        
        self.state_id = 6
        self.update_in_db()
        
    def repurchase(self, purchaser: str):
        """ Marca el equipo como recomprado.
        """
        if not self.state_id == 6:
            raise RuntimeError(f"El estado actual del equipo no permite realizar esta acción. Estado esperado 6 - Estado actual {self.state_id}")

        self.state_id = 7
        self.update_in_db()

        conn = psycopg2.connect(**current_app.config["MASTER_DB"])
        cursor = conn.cursor()
        cursor.execute("INSERT INTO computer_repurchase (sn, purchaser) VALUES (%(sn)s, %(purchaser)s)", {"sn": self.sn, "purchaser": purchaser})
        conn.commit()
        conn.close()

    def return_to_econocom(self):
        """ Marca el equipo como devuelto al econocom.
        """
        if self.is_purchase:
            raise RuntimeError("El equipo no se puede devolver a Econocom porque es de compra.")
        if self.is_external:
            raise RuntimeError("El equipo no se puede devolver a Econocom porque no es un equipo de KOSTAL.")
        
        if not self.state_id == 6:
            raise RuntimeError(f"El estado actual del equipo no permite realizar esta acción. Estado esperado 6 - Estado actual {self.state_id}")
        
        self.state_id = 8
        self.update_in_db()

    def return_to_thirdparty(self):
        """ Marca el equipo como devuelto a terceros.
        """
        if not self.is_external:
            raise RuntimeError("El equipo no se puede devolver a terceros porque es de KOSTAL.")
        
        if not self.state_id == 6:
            raise RuntimeError(f"El estado actual del equipo no permite realizar esta acción. Estado esperado 6 - Estado actual {self.state_id}")
        
        self.state_id = 9
        self.update_in_db()

    def throw_away(self):
        """ Marca el equipo como tirado.
        """
        if self.is_external:
            raise RuntimeError("El equipo no se puede tirar porque es de teceros.")
        if self.is_renting:
            raise RuntimeError("El equipo no se puede tirar porque es de Econocom (renting).")
        
        if not self.state_id == 6:
            raise RuntimeError(f"El estado actual del equipo no permite realizar esta acción. Estado esperado 6 - Estado actual {self.state_id}")
        
        self.state_id = 10
        self.update_in_db()
        
        
class ComputerModel():
    pn: str
    model: str
    type_name: str
    
    def __init__(self, pn: str):
        conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM computer_models WHERE pn = %(pn)s", {"pn": pn})
        result = cursor.fetchone()
        conn.close()
        
        self.pn = pn
        self.model = result["model"]
        self.type_name = result["type_name"]
        
    def get_data(self) -> list[RealDictRow]:
        """ Obtiene toda la información del Modelo.
        """
        conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        
        query = "SELECT pn, model, type_name FROM computer_models WHERE pn = %(pn)s"
        cursor.execute(query, {"pn": self.pn})
        data = cursor.fetchone()
        conn.close()
        
        return data
        
    def update_in_db(self, pn: str = None, model: str = None, type_name: str = None):
        """ Actualiza los valores de este Modelo en la base de datos con los valores actuales.
        """
        old_pn = self.pn
        if pn:
            self.pn = pn
        if model:
            self.model = model
        if type_name:
            self.type_name = type_name
        
        conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
        cursor = conn.cursor()

        cursor.execute("UPDATE computer_models SET model = %(model)s, type_name = %(type_name)s WHERE pn = %(old_pn)s", {"pn": self.pn, "model": self.model, "type_name": self.type_name, "old_pn": old_pn})
        
        conn.commit()

        conn.close()
        
    def delete(self):
        """ Elimina el ordenador en la base de datos.
        """
        conn = psycopg2.connect(**current_app.config["MASTER_DB"])
        cursor = conn.cursor()

        cursor.execute("DELETE FROM computer_models WHERE pn = %(pn)s", {"pn": self.pn})
        conn.commit()

        conn.close()
        