from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.fields import SubmitField

class UploadForm(FlaskForm):
    file = FileField(validators = [FileRequired(), FileAllowed(["xls"])])
    submit = SubmitField("Subir")
    