from flask import render_template, request, redirect, url_for, current_app, g
from flask_login import login_required

from . import computers
from .forms import AddComputerForm, ConfigureForm, AssignForm, HandOverForm, RetireForm, FormatForm, ReturnToEconocomOrRepurchaseForm, ReturnToThirdPartyForm, ThrowAwayOrRepurchaseForm, ModifyComputerForm, DeleteComputerForm, DeleteComputerModelForm, ModifyComputerModelForm
from .functions import get_computer_model, add_computer_model, update_computer_data, get_suggested_hostname
from .models import Computer, ComputerModel
from ..ssp import ssp

# Ordenadores

@computers.route("", methods = ["GET"])
@login_required
def active_computers():
    """ Vista de todos los ordenadores del sistema.
    """
    g.active = "section-active-computers"
    return render_template("computers/computers.html", title = "Ordenadores", state_ids = [1, 2, 3, 4])


@computers.route("/to-format", methods = ["GET"])
@login_required
def to_format_computers():
    """ Vista de todos los ordenadores del sistema.
    """
    g.active = "section-to-format-computers"
    return render_template("computers/computers.html", title = "Ordenadores", state_ids = [5])

@computers.route("/to-return", methods = ["GET"])
@login_required
def to_return_computers():
    """ Vista de todos los ordenadores del sistema.
    """
    g.active = "section-to-return-computers"
    return render_template("computers/computers.html", title = "Ordenadores", state_ids = [6])

@computers.route("/data", methods = ["POST"])
@login_required
def computers_data() -> dict[str, any]:
    """ Devuelve los datos a mostrar en la tabla de ordenadores según los filtros aplicados.

    Returns:
        dict[str, any]: Diccionario con la siguiente estructura.
            {
                "data": (list[str, any]) Datos a mostrar en la tabla,
                "recordsFiltered": (int) Número de filas mostradas (tras aplicar filtros),
                "recordsTotal": (int) Número total de filas en la tabla,
                "draw": Valor usado por Datatable)
            }
    """    
    table = "computers as c"
    columns = ["c.hostname", "c.sn", "c.pn", "cm.model", "cm.type_name", "c.description", "(CASE WHEN c.is_purchase THEN 'Compra' WHEN c.is_external THEN 'External' ELSE 'Renting' END)", "cs.name", "c.notes"]
    
    # Filtraje por estado
    if "state_ids[]" in request.form:
        state_ids = dict(request.form.lists())["state_ids[]"]
        
        where = f"(c.state_id = {state_ids[0]}"
        for state_id in state_ids[1:]:
            where += f" OR c.state_id = {state_id}"
        where += ")"
        
    else:
        where = None
        
    join = "LEFT JOIN tro AS t ON t.sn = c.sn LEFT JOIN computer_models AS cm ON cm.pn = c.pn JOIN computer_states as cs ON cs.id = c.state_id"
    return ssp(table, columns, request.values, current_app.config["MASTER_DB"]["host"], current_app.config["MASTER_DB"]["port"], current_app.config["MASTER_DB"]["database"], current_app.config["MASTER_DB"]["user"], current_app.config["MASTER_DB"]["password"], join = join, where = where, total_where = where)


@computers.route("/<sn>", methods = ["GET"])
@login_required
def computer(sn: str):
    """ Detalle de un ordenador.

    Args:
        sn (str): Serial Number del equipo a mostrar.
    """
    c = Computer(sn)
    modify_form = ModifyComputerForm()
    modify_form.populate(**c.get_data())
    delete_form = DeleteComputerForm()
        
    # Cambia el formulario de estado a mostrar según el estado del equipo
    match c.state_id:
        case 1:
            state_form = ConfigureForm(suggested_hostname = get_suggested_hostname(c))
        case 2:
            state_form = AssignForm()
        case 3:
            state_form = HandOverForm(hostname = c.sn, description = c.description)
        case 4:
            state_form = RetireForm()        
        case 5:
            state_form = FormatForm()
        case 6:
            if c.is_external:
                state_form = ReturnToThirdPartyForm()
            elif c.is_purchase:
                state_form = ThrowAwayOrRepurchaseForm()
            else:
                state_form = ReturnToEconocomOrRepurchaseForm()
        case _:
            state_form = None
    
    return render_template("computers/computer.html", computer = c.get_data(), state_form = state_form, modify_form = modify_form, delete_form = delete_form)


@computers.route("/<sn>/change_state", methods = ["POST"])
@login_required
def computer_change_state(sn: str):
    """ Lógica del cambio de estado de un ordenador.

    Args:
        sn (str): Serial Number del equipo.
    """
    c = Computer(sn)
    
    match c.state_id:
        case 1:
            state_form = ConfigureForm()
            if state_form.validate_on_submit():
                c.configure(state_form.hostname.data)
        case 2:
            state_form = AssignForm()
            if state_form.validate_on_submit():
                c.assign(state_form.description.data)
        case 3:
            state_form = HandOverForm(hostname = c.sn, description = c.description)
            if state_form.validate_on_submit():
                c.hand_over(previous_computer_sn = state_form.previous_computer.data)
        case 4:
            state_form = RetireForm()
            if state_form.validate_on_submit():
                c.retire()
        case 5:
            state_form = FormatForm()
            if state_form.validate_on_submit():
                c.format()
        case 6:
            if c.is_external:
                state_form = ReturnToThirdPartyForm()
                if state_form.validate_on_submit():
                    c.return_to_thirdparty()
            elif c.is_purchase:
                state_form = ThrowAwayOrRepurchaseForm()
                if state_form.validate_on_submit():
                    if state_form.repurchase_submit.data:
                        c.repurchase("TEST")
                    else:
                        c.throw_away()
            else:
                state_form = ReturnToEconocomOrRepurchaseForm()
                if state_form.validate_on_submit():
                    if state_form.repurchase_submit.data:
                        c.repurchase("TEST")
                    else:
                        c.return_to_econocom()
                        
    return redirect(url_for("computers.computer", sn = sn))


@computers.route("/<sn>/modify", methods = ["POST"])
@login_required
def computer_modify(sn: str):
    """ Modifica la información de un ordenador.

    Args:
        sn (str): Serial Number del equipo.
    """
    c = Computer(sn)
    modify_form = ModifyComputerForm()
    if modify_form.validate_on_submit():
        # Guardar cambios del ordenador
        update_computer_data(modify_form, c)
        modify_form.populate(**c.get_data())
                
    return redirect(url_for("computers.computer", sn = sn))


@computers.route("/<sn>/delete", methods = ["POST"])
@login_required
def computer_delete(sn: str):
    """ Elimina un ordenador.

    Args:
        sn (str): Serial Number del equipo.
    """
    c = Computer(sn)
    delete_form = DeleteComputerForm()
    if delete_form.validate_on_submit():
        # Borrar equipo
        c.delete()
                
    return redirect(url_for("computers.active_computers"))
    

@computers.route("/add", methods = ["GET", "POST"])
@login_required
def computer_add():
    """ Vista para añadir un nuevo ordenador al sistema.
    """
    form = AddComputerForm()
    
    if form.validate_on_submit():
        # Si no existía el Modelo en el sistema, se añade
        if form.model.data:
            add_computer_model(form.pn.data, form.model.data, form.type_name.data)
        
        # Añadir nuevo Computer
        computer = Computer(sn = form.sn.data, pn = form.pn.data, po = form.po.data, is_renting = form.is_renting.data, is_purchase = form.is_purchase.data, is_external = form.is_external.data)
        computer.add()

        return redirect(url_for("computers.computer", sn = computer.sn))
        
    form.model.data = ""
    form.is_renting.data = True
    return render_template("computers/add_computer.html", form = form)
       
    
    
# Modelos

@computers.route("/models", methods = ["GET", "POST"])
@login_required
def computer_models():
    """ Vista para mostrar todos los modelos de ordenadordisponibles.
    """
    g.active = "section-computer-models"
    
    # Para comprobar si un modelo ya existe
    if request.method == "POST":
        data = get_computer_model(request.json["pn"])
        if not data:
            return "", 404
        return data, 200

    # GET
    return render_template("computers/computer_models.html")


@computers.route("/models/data", methods = ["POST"])
@login_required
def models_data():
    """ Devuelve los datos a mostrar en la tabla de modelos según los filtros aplicados.

    Returns:
        dict[str, any]: Diccionario con la siguiente estructura.
            {
                "data": (list[str, any]) Datos a mostrar en la tabla,
                "recordsFiltered": (int) Número de filas mostradas (tras aplicar filtros),
                "recordsTotal": (int) Número total de filas en la tabla,
                "draw": Valor usado por Datatable
            }
    """
    table = "computer_models"
    columns = ["pn", "model", "type_name"]

    return ssp(table, columns, request.values, current_app.config["MASTER_DB"]["host"], current_app.config["MASTER_DB"]["port"], current_app.config["MASTER_DB"]["database"], current_app.config["MASTER_DB"]["user"], current_app.config["MASTER_DB"]["password"])


@computers.route("/models/<pn>", methods = ["GET"])
@login_required
def computer_model(pn: str):
    """ Vista para el detalle de un modelo de ordenador.

    Args:
        pn (str): Product Number del modelo.
    """
    g.active = "section-computer-models"
    
    cm = ComputerModel(pn)
    modify_form = ModifyComputerModelForm()
    modify_form.populate(**cm.get_data())
    delete_form = DeleteComputerModelForm(pn)
    
    return render_template("computers/computer_model.html", modify_form = modify_form, delete_form = delete_form, pn = cm.pn)

@computers.route("/models/<pn>/modify", methods = ["POST"])
@login_required
def computer_model_modify(pn: str):
    """ Modifica la información de un modelo de ordenador.

    Args:
        pn (str): Product Number del modelo.
    """
    modify_form = ModifyComputerModelForm()
    cm = ComputerModel(pn)
    
    if modify_form.validate_on_submit():
        cm.update_in_db(modify_form.pn.data, modify_form.model.data, modify_form.type_name.data)
    
    return redirect(url_for("computers.computer_model", pn = cm.pn))

@computers.route("/models/<pn>/delete", methods = ["POST"])
@login_required
def computer_model_delete(pn: str):
    """ Vista para el detalle de un modelo de ordenador.

    Args:
        pn (str): Product Number del modelo.
    """
    delete_form = DeleteComputerModelForm(pn)
    cm = ComputerModel(pn)
    
    if delete_form.validate_on_submit():
        cm.delete()
    
    return redirect(url_for("computers.computer_models"))
