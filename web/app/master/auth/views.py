""" Contiene los recursos (rutas) para la Blueprint 'auth'.
"""
from flask import render_template, redirect, url_for, request, session
from flask_login import login_user, logout_user, LoginManager, current_user
from urllib.parse import urlparse

from . import auth
from .forms import LoginForm
from .models import User

login_manager = LoginManager() 

""" Funciones requeridas para el manejo de sesión.
"""
@login_manager.user_loader
def load_user(id):
    return User(id)

""" Página de inicio de sesión.
"""
@auth.route("/login", methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form  = LoginForm()
    if form.validate_on_submit():
        user = User(form.username.data)
        login_user(user)
        
        # Quitar los mensajes "flash" que se han podido generar al intentar entrar en una página protegida por login
        if "_flashes" in session:
            session["_flashes"].clear()
        
        # Mirar si se debe hacer un redirect a alguna página en concreto o mandar a la página de inicio
        next_page = request.args.get("next")
        if not next_page or urlparse(next_page).netloc != "":
            next_page = url_for("main.home")
        return redirect(next_page)

    return render_template("auth/login.html", form = form)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
