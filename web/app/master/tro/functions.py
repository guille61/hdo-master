from datetime import datetime
from flask import current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.errors import InvalidTextRepresentation
from typing import Tuple
import xlrd
from xlrd.biffh import XLRDError


def is_most_recent_tro(filename: str) -> bool:
    """ Comprueba que el fichero de TRO adjunto no sea más antiguo que alguno de los ficheros importados anteriormente.

    Args:
        filename (str): Nombre del fichero adjunto.

    Returns:
        bool: Indica si el fichero es válido o no para importarlo.
    """
    file_date = datetime.strptime(filename.split("_")[-1].split(".")[0], "%Y%m%d")
    
    conn = psycopg2.connect(**current_app.config["MASTER_DB"])
    cursor = conn.cursor()
    cursor.execute("SELECT file_date FROM tro_import WHERE file_date >= %(date)s", {"date": file_date})
    result = cursor.fetchall()
    conn.close()
    
    if result:
        return False
    
    return True
    

def import_tro(filename: str, sheetname: str) -> Tuple[int, int]:
    """ Importa los datos del fichero de TRO.
    """
    # Abrir fichero
    workbook = xlrd.open_workbook(filename)
    try:
        sheet = workbook.sheet_by_name(sheetname)
    except XLRDError as e:
        raise ValueError(str(e))
    
    if sheet.ncols != 23:
        raise RuntimeError("El fichero no tiene el número de columnas esperadas (23)")


    # Obtener IDs de Econocom que ya se encuentran en la base de datos
    try:
        conn = psycopg2.connect(**current_app.config["MASTER_DB"])
    except psycopg2.OperationalError:
        raise RuntimeError("Base de datos no accesible")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM tro WHERE is_active")
    db_ids = [x[0] for x in cursor.fetchall()]


    # Importar los registros del fichero
    count = 0
    query = "INSERT INTO tro (id, manufacturer, pn, description, sn, invoice, order_num, start_date, end_date, price, period, status, type_name) VALUES (%(id)s, %(manufacturer)s, %(pn)s, %(description)s, %(sn)s, %(invoice)s, %(order_num)s, %(start_date)s, %(end_date)s, %(price)s, %(period)s, %(status)s, %(type_name)s);"
    for row in range(1, sheet.nrows):
        # Si ya existe en base de datos, pasar al siguiente ID
        if sheet.cell_value(row, current_app.config["TRO_EXCEL_COLUMNS"]["id"]) in db_ids:
            continue

        values = {}
        for key, index in current_app.config["TRO_EXCEL_COLUMNS"].items():
            # Para los campos correspondiente a las fechas, se debe transformar a objeto "datetime"
            if key == "start_date" or key == "end_date":
                try:
                    values[key] = xlrd.xldate_as_datetime(sheet.cell_value(row, index), workbook.datemode)
                except TypeError as e:
                    values[key] = None
                continue
            values[key] = sheet.cell_value(row, index)
        
        try:
            cursor.execute(query, values)
            count += 1
        except InvalidTextRepresentation as e:
            raise ValueError(f"Error en INSERT: {str(e)}")
        
    # Guardar log de importación
    file_date = datetime.strptime(filename.split("_")[-1].split(".")[0], "%Y%m%d")
    cursor.execute("INSERT INTO tro_import (file_name, file_date) VALUES (%(file_name)s, %(file_date)s)", {"file_name": filename.split("/")[-1], "file_date": file_date})

    conn.commit()
    conn.close()
    
    return count, (sheet.nrows - 1)


def deactivate_old_registries(filename: str, sheetname: str) -> int:
    """ Desactiva los registros en la base de datos que ya no aparecen el fichero importado.
    """
    workbook = xlrd.open_workbook(filename)
    try:
        sheet = workbook.sheet_by_name(sheetname)
    except XLRDError as e:
        raise ValueError(str(e))

    if sheet.ncols != 23:
        raise RuntimeError("El fichero no tiene el número de columnas esperadas (23)")
    
    # Obtener los IDs en el fichero
    file_ids = []
    for row in range(1, sheet.nrows):
        file_ids.append(sheet.cell_value(row, current_app.config["TRO_EXCEL_COLUMNS"]["id"]))


    # Consultar registros en base de datos que no aparecen en el fichero
    try:
        conn = psycopg2.connect(**current_app.config["MASTER_DB"])
    except psycopg2.OperationalError:
        raise RuntimeError("Base de datos no accesible")
    cursor = conn.cursor()

    count = 0
    cursor.execute("SELECT id FROM tro WHERE is_active")
    for id in [x[0] for x in cursor.fetchall()]:
        if id not in file_ids:
            cursor.execute("UPDATE tro SET is_active = false WHERE id = %(id)s", {"id": id})
            count += 1

    conn.commit()
    conn.close()
    
    return count
