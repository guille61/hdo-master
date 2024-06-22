from flask import render_template, current_app, request, g, session, redirect, url_for, flash
from flask_login import login_required
from markupsafe import Markup
import os
from werkzeug.utils import secure_filename

from . import tro
from .forms import UploadForm
from .functions import import_tro, deactivate_old_registries, is_most_recent_tro
from ..ssp import ssp

@tro.route("", methods = ["GET", "POST"])
@login_required
def home():
    g.active = "section-tro"
    form = UploadForm()
    
    if form.validate_on_submit():
        f = form.file.data
        filename = secure_filename(f.filename)
        
        if not is_most_recent_tro(filename):
            flash(Markup("La información en el sistema es más reciente o igual que la del fichero indicado."), "danger")
            return redirect(url_for("tro.home"))
        
        f.save(os.path.join(current_app.root_path, "tro/uploads", filename))
        
        # Importar nuevas filas y desactivar las que no se encuentran en el TRO actual
        try:
            new, total = import_tro(os.path.join(current_app.root_path, "tro/uploads", filename), "Estado del Portfolio")
            deactivated = deactivate_old_registries(os.path.join(current_app.root_path, "tro/uploads", filename), "Estado del Portfolio")
        except Exception as e:
            os.remove(os.path.join(current_app.root_path, "tro/uploads", filename))
            flash(Markup(f"Error durante la importación. Verificar logs de la aplicación."), "danger")
            return redirect(url_for("tro.home"))
        
        flash(Markup(f"Importadas <strong>{new}</strong> filas de <strong>{total}</strong>.<br/>Desactivados <strong>{deactivated}</strong> registros."), "success")
        return redirect(url_for("tro.home"))
    
    return render_template("tro/tro.html", form = form)

@tro.route("/data", methods = ["POST"])
@login_required
def tro_data():
    table = "tro"
    columns = ["CAST(id as TEXT)", "type_name", "manufacturer", "pn", "description", "sn", "invoice", "order_num", "TO_CHAR(start_date, 'yyyy-mm-dd')", "TO_CHAR(end_date, 'yyyy-mm-dd')", "CAST(price as TEXT)", "status", "CAST(period as TEXT)"]
    where = "is_active"
    total_where = "is_active"

    return ssp(table, columns, request.values, current_app.config["MASTER_DB"]["host"], current_app.config["MASTER_DB"]["port"], current_app.config["MASTER_DB"]["database"], current_app.config["MASTER_DB"]["user"], current_app.config["MASTER_DB"]["password"], where = where, total_where = total_where)
