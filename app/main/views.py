from flask import render_template, session, redirect, url_for, current_app, \
	flash, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from sqlalchemy.sql import text

from .. import db
from ..models import TipoConta, Conta, Lancamento
from . import main
from .forms import TipoContaForm, ContaForm, LancamentoForm


@main.app_template_filter()
def format_currency(value):
    value = float(value)
    return ("R$ {:.2f}".format(value)).replace(".", ",")


@main.app_template_filter()
def teste_currency(value):
    value = float(value)
    return value


@main.app_template_filter()
def format_datetime(value, format="%d/%m/%Y"):
    """Format a date time to (Default): d Mon YYYY HH:MM P"""
    if value is None:
        return ""
    return value.strftime(format)


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@main.route('/tipos', methods=['GET', 'POST'])
def tipos():
    form = TipoContaForm()
    if form.validate_on_submit():
        tipo = TipoConta(nome=form.nome.data)
        try:
            db.session.add(tipo)
            db.session.commit()
            flash('Cadastro do tipo efetuado com sucesso!')
            return redirect(url_for('.tipos'))
        except IntegrityError:
            db.session.rollback()
            flash('Atenção. Este tipo já existe!')
            return redirect(request.url)
    page = request.args.get('page', 1, type=int)
    pagination = TipoConta.query.order_by(TipoConta.nome.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    tipos = pagination.items
    count = TipoConta.query.count()
    
    return render_template('tipos.html',
                            form=form,
                            tipos=tipos,
                            pagination=pagination,
                            count=count,
                            titulo='Tipos')


@main.route('/tipo/<int:id>')
def deleta_tipo(id):
    tipo = TipoConta.query.filter_by(id=id).first()
    try:
        db.session.delete(tipo)
        db.session.commit()
        flash('Tipo de conta deletada com sucesso!')
        return redirect(url_for('.tipos'))
    except IntegrityError:
        db.session.rollback()
        flash('Não é possível deletar o tipo de conta!')
        return redirect(url_for('.tipos'))


@main.route('/contas', methods=['GET', 'POST'])
def contas():
    form = ContaForm()
    tipo = [(t.id, t.nome) for t in TipoConta.query.all()]
    form.tipo.choices = tipo
    if form.validate_on_submit():
        conta = Conta(
        	nome=form.nome.data,
        	saldo=float(str(form.saldo.data).replace(',','.')),
            tipo_id = form.tipo.data)                
        try:
            db.session.add(conta)
            db.session.commit()
            flash('Cadastro da conta efetuado com sucesso!')
            return redirect(url_for('.contas'))
        except IntegrityError:
            db.session.rollback()
            flash('Atenção. Esta conta já existe!')
            return redirect(request.url)
    page = request.args.get('page', 1, type=int)
    pagination = Conta.query.order_by(Conta.tipo_id).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    contas = pagination.items
    count = Conta.query.count()
    return render_template('contas.html',
                            form=form,
                            contas=contas,
                            pagination=pagination,
                            count=count,
                            titulo='Contas')


@main.route('/conta/<int:id>')
def deleta_conta(id):
    conta = Conta.query.filter_by(id=id).first()
    try:
        db.session.delete(conta)
        db.session.commit()
        flash('Conta deletada com sucesso!')
        return redirect(url_for('.contas'))
    except IntegrityError:
        db.session.rollback()
        flash('Não é possível deletar a conta!')
        return redirect(url_for('.contas'))


@main.route('/lancamentos', methods=['GET', 'POST'])
def lancamentos():
    form = LancamentoForm()
    conta_deb = [(cd.id, cd.nome) for cd in Conta.query.all()]
    form.conta_deb.choices = conta_deb
    conta_cre = [(cc.id, cc.nome) for cc in Conta.query.all()]
    form.conta_cre.choices = conta_cre
    
    if form.validate_on_submit():
        lancamento = Lancamento(
            descricao=form.descricao.data,
            data_lanc=form.data_lanc.data,
            valor=float(str(form.valor.data).replace(',','.')),  
            debito_id=form.conta_deb.data,
            credito_id=form.conta_cre.data)
        try:
            db.session.add(lancamento)
            db.session.commit()
            flash('Cadastro do lancamento efetuado com sucesso!')
            
            conta_crd = form.conta_cre.data
            conta_dbt = form.conta_deb.data
            valor_lanc = float(str(form.valor.data).replace(',','.'))

            saldo_conta_crd = db.engine.execute("SELECT saldo FROM contas WHERE id=%s", conta_crd).scalar()
            novo_saldo_conta_crd = float(saldo_conta_crd) + valor_lanc
            c = Conta.query.get(conta_crd)
            c.saldo = float(novo_saldo_conta_crd)
    
            saldo_conta_dbt = db.engine.execute("SELECT saldo FROM contas WHERE id=%s", conta_dbt).scalar()
            novo_saldo_conta_dbt = float(saldo_conta_dbt)  - valor_lanc
            d = Conta.query.get(conta_dbt)
            d.saldo = float(novo_saldo_conta_dbt)
    
            db.session.commit()

            return redirect(url_for('.lancamentos'))
        except IntegrityError:
            db.session.rollback()
            flash('Algo deu errado!')
            return redirect(request.url)

    page = request.args.get('page', 1, type=int)
    pagination = Lancamento.query.order_by(Lancamento.data_lanc.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    lancamentos = pagination.items
    count = Lancamento.query.count()
   
    #session['valor'] = 0
    
    return render_template('lancamentos.html',
                            form=form,
                            lancamentos=lancamentos,
                            pagination=pagination,
                            count=count,
                            titulo='Lançamentos')


@main.route('/lancamento/<int:id>')
def deleta_lancamento(id):
    lancamento = Lancamento.query.filter_by(id=id).first()
    try:
        db.session.delete(lancamento)
        db.session.commit()
        flash('Lançamento deletado!')

        conta_crd = lancamento.credito_id
        conta_dbt = lancamento.debito_id
        valor_lanc = float(str(lancamento.valor).replace(',','.'))

        saldo_conta_crd = db.engine.execute("SELECT saldo FROM contas WHERE id=%s", conta_crd).scalar()
        novo_saldo_conta_crd = float(saldo_conta_crd) - valor_lanc
        c = Conta.query.get(conta_crd)
        c.saldo = float(novo_saldo_conta_crd)
    
        saldo_conta_dbt = db.engine.execute("SELECT saldo FROM contas WHERE id=%s", conta_dbt).scalar()
        novo_saldo_conta_dbt = float(saldo_conta_dbt) + valor_lanc
        d = Conta.query.get(conta_dbt)
        d.saldo = float(novo_saldo_conta_dbt)
    
        db.session.commit()  

        return redirect(url_for('.lancamentos'))
    except IntegrityError:
        db.session.rollback()
        flash('Não é possível deletar!')
        return redirect(url_for('.lancamentos'))


@main.route('/lista_tipo/<int:id>')
def lista_tipo(id):
    tipo = TipoConta.query.filter_by(id=id).first()
    page = request.args.get('page', 1, type=int)
    pagination = Conta.query.filter_by(tipo_id=id).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    contas = pagination.items
    total = db.engine.execute("SELECT SUM(saldo) FROM contas WHERE tipo_id=%s", id).scalar()
    return render_template('lista_tipo.html',
                            pagination=pagination,
                            tipo=tipo,
                            contas=contas,
                            total=total)


@main.route('/teste/<int:id>', methods=['GET', 'POST'])
def teste(id):
    result = db.session.query(func.sum(Lancamento.valor)).scalar()
    count = Lancamento.query.count()
    t = db.engine.execute("""SELECT SUM(VALOR) FROM lancamentos WHERE credito_id=?""", id).scalar()
    return render_template('teste.html', result=result, count=count, t=t)




