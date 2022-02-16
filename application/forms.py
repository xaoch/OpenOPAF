from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DecimalField, BooleanField
from wtforms.validators import DataRequired, Email
from flask_wtf.file import FileField, FileRequired, FileAllowed


class NewPresentationForm(FlaskForm):
    duration = DecimalField("Presentation Length (minutes): ", places=0, validators=[DataRequired()],default=5)
    includePresentation = BooleanField("Includes Presentation?: ", default=True)
    presentationFile = FileField(validators=[FileAllowed(['pptx'], 'PowerPoint files only')])
    submit = SubmitField("Submit")

class PresentationFileForm(FlaskForm):
    presentationFile = FileField(validators=[FileRequired(),FileAllowed(['pptx'], 'PowerPoint files only')])
    submit = SubmitField("Submit")

class StopForm(FlaskForm):
    stop = SubmitField("Stop")
