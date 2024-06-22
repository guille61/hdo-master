from flask import render_template, g
from flask_login import current_user, login_required

from . import main
from .forms import PreferenciasForm

@main.route("", methods = ["GET"])
@login_required
def home():
    g.active = "section-home"
    return render_template("main/home.html")

@main.route("/about", methods = ["GET"])
@login_required
def about():
    return render_template("main/about.html")


@main.route("/preferences", methods = ["GET", "POST"])
@login_required
def preferences():
    form = PreferenciasForm()

    if form.validate_on_submit():
        current_user.update_preferences(form.sidebar_toggle.data)

    # Actualizar el formulario con las configuraciones preferidas del usuario
    user_preferences = current_user.get_preferences()
    form.change_values(user_preferences["sidebar_toggled"])

    return render_template("main/preferences.html", form = form)
