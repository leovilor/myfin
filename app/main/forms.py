from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired


class TipoContaForm(FlaskForm):
    nome = StringField('Tipo:', validators=[DataRequired()])
    submit = SubmitField('Gravar')


class ContaForm(FlaskForm):
    nome = StringField('Conta:', validators=[DataRequired()])
    tipo = SelectField('Tipo:', coerce=int)
    saldo = StringField('Valor:', validators=[DataRequired()])
    submit = SubmitField('Gravar')


class LancamentoForm(FlaskForm):
    descricao = StringField('Descrição do Lançamento:', validators=[DataRequired()])
    data_lanc = DateField('Data:', validators=[DataRequired()], format='%d/%m/%Y')
    valor = StringField('Valor:', validators=[DataRequired()])
    conta_deb = SelectField('Débito:', coerce=int)
    conta_cre = SelectField('Crédito:', coerce=int)
    submit = SubmitField('Gravar')
