from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


class AddPeopleForm(FlaskForm):
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    info = StringField('Информация', validators=[DataRequired()])

    submit = SubmitField('Сохранить')
