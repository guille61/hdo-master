from flask import current_app
from flask_wtf import FlaskForm
from wtforms import BooleanField, SubmitField


class PreferenciasForm(FlaskForm):
    """ Formulario para la gestión de las preferencias de usuario.
    """

    sidebar_toggle = BooleanField()
    submit = SubmitField("Guardar")

    def change_values(self, sidebar_toggle: int):
        """ Actualiza los valores seleccionados del formulario.
        """
        self.sidebar_toggle.data = sidebar_toggle
