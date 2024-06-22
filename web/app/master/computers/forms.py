from flask import current_app
from flask_wtf import FlaskForm
import psycopg2
from psycopg2.extras import RealDictCursor
from wtforms import StringField, SubmitField, SelectField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, ValidationError

class DeleteComputerForm(FlaskForm):
    delete_submit = SubmitField("Sí")

class ModifyComputerForm(FlaskForm):
    sn = StringField("Serial Number", validators = [DataRequired()], render_kw = {"readonly": True})
    hostname = StringField("Hostname", render_kw = {"readonly": True})
    model = SelectField("Modelo", validators = [DataRequired()])
    description = StringField("Descripción", render_kw = {"readonly": True})
    state = SelectField("Estado", coerce = int)
    origin = SelectField("Origen")
    po = StringField("PO", render_kw = {"readonly": True})
    notes = TextAreaField("Notas", render_kw = {"readonly": True})
    
    modify_submit = SubmitField("Guardar")
    
    def __init__(self):
        super().__init__()
        
        conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        
        # Modelos disponibles
        cursor.execute("SELECT pn, model, type_name FROM computer_models ORDER BY model ASC")
        self.model.choices = [(x["pn"], x["model"]) for x in cursor.fetchall()]
        
        # Estados
        cursor.execute("SELECT id, name FROM computer_states ORDER BY id ASC")
        self.state.choices = [(x["id"], x["name"]) for x in cursor.fetchall()]
        
        conn.close()
        
        # Origen
        self.origin.choices = [("is_renting", "Renting"), ("is_purchase", "Compra"), ("is_external", "Externo")]
        
    def validate_modify_submit(form, field):
        if not field.data:
            raise ValidationError()
            
    def populate(self, **kwargs):        
        self.sn.data = kwargs.pop("sn")
        self.hostname.data = kwargs.pop("hostname")
        self.description.data = kwargs.pop("description")
        self.model.data = kwargs.pop("pn")
        self.state.data = kwargs.pop("state_id")
        self.notes.data = kwargs.pop("notes")
        # Origen
        if kwargs.pop("is_purchase"):
            self.origin.data = "is_purchase"
        elif kwargs.pop("is_external"):
            self.origin.data = "is_external"
        else:
            self.origin.data = "is_renting"
        
        
"""
    Formularios de gestión del ciclo de vida de un ordenador.
"""

class AddComputerForm(FlaskForm):
    sn = StringField("Serial Number", validators = [DataRequired()], render_kw = {"placeholder": "Serial Number"})
    pn = StringField("Product Number", validators = [DataRequired()], render_kw = {"placeholder": "Product Number"})
    po = StringField("Customer PO", render_kw = {"placeholder": "Customer PO"})
    is_renting = BooleanField("Econocom")
    is_purchase = BooleanField("Compra")
    is_external = BooleanField("Externo")
    
    model = StringField("Modelo", render_kw = {"placeholder": "Modelo"})
    type_name = SelectField("Tipo")
    
    submitbtn = SubmitField("Añadir")
    
    def __init__(self):
        super().__init__()        
        self.type_name.choices = current_app.config["COMPUTER_MODELS"]
        
    def validate_sn(self, field):
        """ Comprueba si el Serial Number introducido ya existe en el sistema.
        """
        conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        cursor.execute("SELECT sn FROM computers WHERE sn = %(sn)s", {"sn": self.sn.data})
        result = cursor.fetchall()
        conn.close()
        
        if result:
            raise ValidationError("Este Serial Number ya existe en el sistema.")
        
    def validate_pn(self, field):
        """ Comprueba si el Product Number introducido ya existe en el sistema.
        Si no existe, este campo pasará a ser requerido.
        """
        conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        cursor.execute("SELECT pn FROM computer_models WHERE pn = %(pn)s", {"pn": self.pn.data})
        result = cursor.fetchall()
        conn.close()
        
        if not result and not self.model.data:
            raise ValidationError("No se ha indicado un Nombre para el nuevo modelo.")
        if not result and not self.type_name.data:
            raise ValidationError("No se ha indicado un Tipo para el nuevo modelo.")
    
    
class ConfigureForm(FlaskForm):
    hostname = StringField("Hostname", validators = [DataRequired()], render_kw = {"placeholder": "Hostname"})
    submitbtn = SubmitField("Sí")
    
    def __init__(self, suggested_hostname: str = None):
        super().__init__()
        if suggested_hostname:
            self.hostname.data = suggested_hostname
    
    
class AssignForm(FlaskForm):
    description = StringField("Descripcion", validators = [DataRequired()], render_kw = {"placeholder": "Usuario / posición"})
    submitbtn = SubmitField("Sí")
    

class HandOverForm(FlaskForm):
    previous_computer = SelectField("Ordenador anterior")
    submitbtn = SubmitField("Sí")
    
    def __init__(self, hostname: str, description: str):
        super().__init__()
        
        conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        cursor.execute("SELECT hostname, sn FROM computers WHERE state_id = 4 AND description = %(description)s AND hostname != %(hostname)s", {"description": description, "hostname": hostname})
        results = [(x["sn"], x["hostname"]) for x in cursor.fetchall()]
        results.insert(0, ("", "---"))
        conn.close()
                
        self.previous_computer.choices = results
        
        if not self.previous_computer.data:
            self.previous_computer.data = ""
    
    
class RetireForm(FlaskForm):
    submitbtn = SubmitField("Sí")


class FormatForm(FlaskForm):
    format_submit = SubmitField("Sí")
   
    
class ReturnToEconocomOrRepurchaseForm(FlaskForm):
    repurchase_submit = SubmitField("Sí")
    submitbtn = SubmitField("Sí")
    
    
class ReturnToThirdPartyForm(FlaskForm):
    submitbtn = SubmitField("Sí")
   
    
class ThrowAwayOrRepurchaseForm(FlaskForm):
    repurchase_submit = SubmitField("Sí")
    submitbtn = SubmitField("Sí")



#######

class DeleteComputerModelForm(FlaskForm):
    pn = StringField("Product Number")
    delete_submit = SubmitField("Sí")
    
    def __init__(self, pn: str):
        super().__init__()
        self.pn.data = pn
    
    def validate_pn(form, field):        
        conn = psycopg2.connect(**current_app.config["MASTER_DB"], cursor_factory = RealDictCursor)
        cursor = conn.cursor()
        
        cursor.execute("SELECT c.sn, cm.pn FROM computers AS c LEFT JOIN computer_models AS cm ON c.pn = cm.pn WHERE cm.pn = %(pn)s", {"pn": field.data})
        results = cursor.fetchall()
        
        conn.close()
        
        if results:
            raise ValidationError("No se puede borrar este Product Number porque está asociado a algún ordenador.")

class ModifyComputerModelForm(FlaskForm):
    pn = StringField("Product Number", validators = [DataRequired()], render_kw = {"placeholder": "Product Number", "readonly": True})
    model = StringField("Modelo", validators = [DataRequired()], render_kw = {"placeholder": "Modelo", "readonly": True})
    type_name = SelectField("Tipo", validators = [DataRequired()], render_kw = {"readonly": True})
    
    modify_submit = SubmitField("Guardar")
    
    def __init__(self):
        super().__init__()        
        self.type_name.choices = [(x, x) for x in current_app.config["COMPUTER_MODELS"]]
        
    def populate(self, **kwargs):        
        self.pn.data = kwargs.pop("pn")
        self.model.data = kwargs.pop("model")
        self.type_name.data = kwargs.pop("type_name")
        