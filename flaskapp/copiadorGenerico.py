from flaskapp import db
from flaskapp.models import Eventos, Ferias, Letivos, Atividades

def copiadorEventos(anoBdd, anoNovo):
    listaAtual = [e for e in Eventos.query.all() if e.ano == anoBdd]
    listaProximo = [i for i in Eventos.query.all() if i.ano == anoNovo]
    if not listaProximo:
        for ev in listaAtual:
            
            try:
                db.session.add(Eventos(id=(Eventos.query.all()[-1].id+1), dia=ev.dia, mes=ev.mes, comentario=ev.comentario,
                tecnico_id=ev.tecnico_id, calem_id=ev.calem_id, graduacao_id=ev.graduacao_id, ano=anoNovo, flag=ev.flag))
                db.session.commit()
            except:
                db.session.rollback()
                break
        return False
    else:
        return True

    

def copiadorFerias(anoBdd, anoNovo):
    listaAtual = [e for e in Ferias.query.all() if e.ano == anoBdd]
    listaProximo = [i for i in Ferias.query.all() if i.ano == anoNovo]
    if not listaProximo:
        for fe in listaAtual:
            try:
                db.session.add(Ferias(id=(Ferias.query.all()[-1].id+1), dia=fe.dia, mes=fe.mes, comentario=fe.comentario,
                cidade_id=fe.cidade_id, ano=anoNovo, flag=fe.flag))
                db.session.commit()
            except:
                db.session.rollback()
                break
        return False
    else:
        return True


def copiadorAtividades(anoBdd, anoNovo):
    listaAtual = [e for e in Atividades.query.all() if e.ano == anoBdd]
    listaProximo = [i for i in Atividades.query.all() if i.ano == anoNovo]
    if not listaProximo:
        for atv in listaAtual:
            
            try:
                db.session.add(Atividades(id=(Atividades.query.all()[-1].id+1), dia_inicio=atv.dia_inicio, dia_final=atv.dia_final, mes=atv.mes,
                comentario=atv.comentario, cidade_id=atv.cidade_id, ano=anoNovo, flag=atv.flag))
                db.session.commit()
            except:
                db.session.rollback()
                break
        return False
    else:
        return True

def copiadorLetivo(anoBdd, anoNovo):
    listaAtual = [e for e in Letivos.query.all() if e.ano == anoBdd]
    listaProximo = [i for i in Letivos.query.all() if i.ano == anoNovo]
    if not listaProximo:
        for atv in listaAtual:
            
            try:
                db.session.add(Letivos(id=(Letivos.query.all()[-1].id+1), dia=atv.dia, mes=atv.mes, tecnico_id=atv.tecnico_id,
                calem_id=atv.calem_id, graduacao_id=atv.graduacao_id, ano=anoNovo))
                db.session.commit()
            except:
                db.session.rollback()
                break
        return False
    else:
        return True