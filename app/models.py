from . import db


class TipoConta(db.Model):
    __tablename__ = 'tipo_contas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True, nullable=False)
    contas = db.relationship('Conta', backref='tipoconta', lazy='dynamic', passive_deletes=True)
    

class Conta(db.Model):
    __tablename__ = 'contas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True, nullable=False)
    saldo = db.Column(db.String(20), nullable=False)
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipo_contas.id'))
    creditos = db.relationship('Lancamento', backref='credito', lazy='dynamic',
        foreign_keys ='Lancamento.credito_id', passive_deletes=True)
    debitos = db.relationship('Lancamento', backref='debito', lazy='dynamic',
        foreign_keys ='Lancamento.debito_id', passive_deletes=True)


class Lancamento(db.Model):
    __tablename__ = 'lancamentos'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(64), nullable=False)
    data_lanc = db.Column(db.DateTime, nullable=False)
    valor = db.Column(db.String(20), nullable=False)
    debito_id = db.Column(db.Integer, db.ForeignKey('contas.id'))
    credito_id = db.Column(db.Integer, db.ForeignKey('contas.id'))


