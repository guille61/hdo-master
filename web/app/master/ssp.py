"""
Script usado para las Datatables que tienen el procesamiento de los datos en el servidor. Construye y gestiona la query lanzada a la base de datos.

La ejecución de la librería es mediante la función ssp.

"""
import psycopg2


def get_where(search: str, columns: list[str]) -> str:
    """ Construye las condiciones del WHERE de la query a partir de los parámetros enviados por la Datatable.

    Args:
        search (str): Valor dentro de request.values con los filtros de búsqueda indicados por Datatable.
        columns (list[str]): Columnas a devolver.

    Returns:
        str: Parte correspondiente al "WHERE" que se incluirá en la query.
    """
    if not search:
        return ""
    
    where = f"{columns[0]} ILIKE '%{search}%'"
    for column in columns[1:]:
        where += f" OR {column} ILIKE '%{search}%'"

    return where

def get_order(values: dict, columns: list) -> str:
    """ Construye el ORDER BY de la query.

    Args:
        values (dict): request.values de Flask.
        columns (list): Columnas a devolver.

    Returns:
        str: Parte correspondiente al "ORDER BY" que se incluirá en la query.
    """
    return f"ORDER BY {columns[int(values['order[0][column]'])]} {values['order[0][dir]']}"

def get_pagination(values: dict) -> str:
    """ Construye el LIMIT de la query para controlar la paginación.

    Args:
        values (dict): request.values de Flask.

    Returns:
        str: Parte correspondiente al "LIMIT / OFFSET" que se incluirá en la query.
    """
    return f"LIMIT {int(values['length'])} OFFSET {int(values['start'])}"

def build_data_query(table: str, where: str, join: str, columns: list[str], values: dict) -> str:
    """ Construye la query que se lanzará contra la base de datos.

    Args:
        table (str): Nombre de la tabla.
        where (str): WHERE de la query.
        join (str): JOIN de la query.
        columns (list[str]): Columnas a devolver.
        values (dict): request.values de Flask.

    Returns:
        str: Query.
    """
    # Obtener las distintas partes de la query
    datatable_where = get_where(values["search[value]"], columns)
    order_by = get_order(values, columns)
    pagination = get_pagination(values)

    select = f"SELECT {columns[0]}"
    for column in columns[1:]:
        select += f", {column}"

    # Construir el WHERE a partir de las condiciones en la Datatable (búsqueda) y las definidas por parámetro (where)
    if where and datatable_where:
        complete_where = f"WHERE {where} AND ({datatable_where})"
    elif where:
        complete_where = f"WHERE {where}"
    elif datatable_where: 
        complete_where = f"WHERE {datatable_where}"
    else:
        complete_where = "" #NOTE: Ero Macia Modified: Añadido el caso que no venta la consulta con condición, que no añada el Where.
        
    return f"{select} FROM {table} {join} {complete_where} {order_by} {pagination};"

def build_qt_query(table: str, where: str, join: str, columns: list[str], values: dict) -> str:
    """ Construye la query que se lanzará contra la base de datos para obtener el número de filas totales.

    Args:
        table (str): Nombre de la tabla.
        where (str): WHERE de la query.
        join (str): JOIN de la query.
        columns (list[str]): Columnas a devolver.
        values (dict): request.values de Flask.

    Returns:
        str: Query.
    """
    # Obtener las distintas partes de la query
    datatable_where = get_where(values["search[value]"], columns)
    order_by = get_order(values, columns)

    # Construir el WHERE a partir de las condiciones en la Datatable (búsqueda) y las definidas por parámetro (where)
    if where and datatable_where:
        complete_where = f"WHERE {where} AND ({datatable_where})"
    elif where:
        complete_where = f"WHERE {where}"
    elif datatable_where:
        complete_where = f"WHERE {datatable_where}"
    else:
        complete_where = "" #NOTE: Ero Macia Modified: Añadido el caso que no venta la consulta con condición, que no añada el Where.

    return f"SELECT count(*) as qt FROM {table} {join} {complete_where};"


def ssp(table: str, columns: list[str], values: dict, db_host: str, db_port: str, db_name: str, db_username: str, db_password: str, where: str = "", join: str = "", total_where: str = None) -> dict[str, any]:
    """ Devuelve todos los datos de la query y la información adicional que necesita la Datatable.
    En el caso de que la query implique un JOIN, se deberá tener en cuenta a la hora de definir los valores de "table", "columns" y "join".
    
    Ejemplo de uso: 
    ssp("procedures as p", ["pl.line_view", "p.os0", "p.type_proc", "p.message", "p.fromdate_proc", "p.user_mod"], request.values, current_app.config["REWORK_DB_HOST"], current_app.config["REWORK_DB_PORT"], current_app.config["REWORK_DB_DATABASE"], current_app.config["REWORK_DB_USER"], current_app.config["REWORK_DB_PASS"], join = "JOIN prodlines as pl ON pl.id = p.prodlines_id")

    Args:
        table (str): Nombre de la tabla.
        columns (list[str]): Columnas de la base de datos a devolver. Deben incluir los nombres de las tablas en caso de que se necesite realizar un join.
        values (dict): request.values de Flask. Contiene los filtros mandados por la Datatable.
        db_host (str): Host de la base de datos.
        db_port (str): Puerto de la base de datos.
        db_name (str): Nombre de la base de datos.
        db_username (str): Usuario de acceso a la base de datos.
        db_password (str): Password de acceso a la base de datos.
        where (str, optional): Condiciones de la query.
        join (str, optional): Definición de lo(s) JOIN(s).
        join (str, optional): Condición para la query de "total". Esta query se usa para indicar el usuario el total de registros sobre los cuales se han aplicado los filtros de la Datatable.
        
    Returns:
        dict[str, any]: Diccionario con la información y el formato esperado por la Datatable.
    """    
    conn = psycopg2.connect(host = db_host, port = db_port, database = db_name, user = db_username, password = db_password)
    cursor = conn.cursor()

    # Query para obtención de datos (con paginación)
    cursor.execute(build_data_query(table, where, join, columns, values))
    results = cursor.fetchall()

    # Query para obtención de la cantidad de datos (query con los filtros aplicados)
    cursor.execute(build_qt_query(table, where, join, columns, values))
    qt_filtered = cursor.fetchone()

    # Query para obtención de la cantidad de datos totales
    if total_where:
        cursor.execute(f"SELECT count(*) as qt FROM {table} WHERE {total_where};")
    else:
        cursor.execute(f"SELECT count(*) as qt FROM {table};")
    qt = cursor.fetchone()

    conn.close()

    return {
        "data": results,
        "recordsFiltered": qt_filtered,
        "recordsTotal": qt,
        "draw": int(values["draw"])
    }
    

