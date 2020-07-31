from flaskapp import db
from flaskapp.models import Eventos, Ferias, Letivos, Atividades, Tecnico, Graduacao, Calem, Campi


def exclusaoEventos(ano, modalidade, campus, conteudo):
    c = Campi.query.filter_by(cidade=campus)[0]
    if modalidade == 'graduacao':
        nivel_curso = c.graduacao[0]
        eventos = Eventos.query.filter_by(graduacao_id=str(nivel_curso))
    elif modalidade == 'tecnico':
        nivel_curso = c.tecnico[0]
        eventos = Eventos.query.filter_by(tecnico_id=str(nivel_curso))
    elif modalidade == 'calem':
        nivel_curso = c.calem[0]
        eventos = Eventos.query.filter_by(calem_id=str(nivel_curso))
    eventosAno = [e for e in eventos if e.ano == int(ano) and 
                                        e.comentario == conteudo]
    try:
        db.session.delete(eventosAno[0])
        db.session.commit()
    except:
        db.session.rollback()

def exclusaoFerias(ano, campus, conteudo):
    c = Campi.query.filter_by(cidade=campus)[0]
    ferias = c.ferias
    feriasAno = [f for f in ferias if f.ano == int(ano) and 
                                        f.comentario == conteudo]
    
    try:
        db.session.delete(feriasAno[0])
        db.session.commit()
    except:
        db.session.rollback()    
