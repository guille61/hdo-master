from flask import current_app
from flask_login import UserMixin
import ldap
import psycopg2
from psycopg2.extras import RealDictCursor

from .config import LDAP_HOST, LDAP_BASE, LDAP_BIND_USER_DN, LDAP_BIND_USER_PASSWORD, READ_GROUP, WRITE_GROUP

class User(UserMixin):
    username = None
    dn = None
    email = None
    name = None
    surname = None

    def __init__(self, username):
        try:
            conn = ldap.initialize(LDAP_HOST)
        except ldap.SERVER_DOWN as e:
            raise Exception
        
        conn.set_option(ldap.OPT_REFERRALS, 0)

        try:
            conn.simple_bind_s(f"kostales\\{LDAP_BIND_USER_DN}", LDAP_BIND_USER_PASSWORD)
        except ldap.INVALID_CREDENTIALS:
            raise Exception
        
        result = conn.search_s(base = LDAP_BASE, scope = ldap.SCOPE_SUBTREE, filterstr = f"name={username}", attrlist = ["name", "distinguishedName", "givenName", "sn", "mail", "memberof"])
        if not result:
            raise Exception
        
        memberof = [x.decode("utf-8") for x in result[0][1]["memberOf"]]

        self.username = username
        self.dn = result[0][1]["distinguishedName"]
        self.email = result[0][1]["mail"][0].decode("UTF-8")
        self.name = result[0][1]["givenName"][0].decode("UTF-8")
        self.surname = result[0][1]["sn"][0].decode("UTF-8")        

    def get_id(self):
        """ Función usada por Flask-Login.
        """
        return self.username    
    

    # Obtención de datos
    
    def __repr__(self):
        """ Representación del objeto User.
        """
        return f"{self.name} {self.surname}"

    def get_name(self):
        """ Devuelve el nombre completo (nombre y apellido).
        """
        return f"{self.name} {self.surname}"
    

    # Preferencias

    def get_sidebar_toggled(self):
        """ Obtener la preferencia del menú lateral.
        """
        conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
        cursor = conn.cursor()

        cursor.execute("SELECT sidebar_toggled FROM user_preferences WHERE username = %s", [self.username])
        data = cursor.fetchone()

        # Si el usuario aún no ha definido sus preferencias, se envía un valor por defecto
        return data["sidebar_toggled"] if data else 0

    def get_preferences(self):
        """ Obtener las preferencias del usuario.
        """
        conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
        cursor = conn.cursor()

        cursor.execute("SELECT u.sidebar_toggled FROM user_preferences AS u WHERE username = %s", [self.username])
        data = cursor.fetchone()

        # Si el usuario aún no ha definido sus preferencias, se envía un valor por defecto
        sidebar_toggled = data["sidebar_toggled"] if data else 0

        return {"sidebar_toggled": sidebar_toggled}

    def update_preferences(self, sidebar_toggled: bool):
        """ Actualiza las preferencias del usuario.
        """
        conn = psycopg2.connect(**current_app.config["MASTER_DB"])
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO user_preferences (username, sidebar_toggled) VALUES (%(user)s, %(sidebar_toggled)s) ON CONFLICT(username) DO UPDATE SET sidebar_toggled = %(sidebar_toggled)s", {"user": self.username, "sidebar_toggled": sidebar_toggled})
        conn.commit()

        conn.close()
