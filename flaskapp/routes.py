from flask import render_template, url_for, flash, redirect, request, session, escape, send_from_directory
import hashlib
import os
import datetime
from flaskapp import app, db
from flaskapp.latexHTML import latex_to_html
from flaskapp.models import Campi, Ferias, Atividades, Letivos, Calem, Graduacao, Tecnico, Eventos

calendario ={
	'1' : 'Janeiro',
	'2' : 'Fevereiro',
	'3' : 'Março',
	'4' : 'Abril',
	'5' : 'Maio',
	'6' : 'Junho',
	'7' : 'Julho',
	'8' : 'Agosto',
	'9' : 'Setembro',
	'10': 'Outubro',
	'11': 'Novembro',
	'12': 'Dezembro'
}
simplificador_nomes = {
	'campo mourão' : 'mourao',
	'cornélio procópio' : 'procopio',
	'dois vizinhos' : 'vizinhos',
	'francisco beltrão' : 'beltrao',
	'pato branco' : 'branco',
	'ponta grossa' : 'pgrossa',
	'santa helena' : 'helena'
}

encrypted = dict([(record.cidade, record.senha) for record in Campi.query.all()])

@app.route('/', methods=['POST', 'GET'])
def home():
	session.clear()
	if request.method=='POST':
		log = request.form['login']
		sen = request.form['senha']
		if log in encrypted:
			if hashlib.md5(sen.encode()).hexdigest() == encrypted[log]:
				session['login'] = log
				return redirect(url_for('controle'))
		return redirect(url_for('tentativa')) #atualizar html para erros
	return render_template('home.html')

@app.route('/controle', methods=['POST', 'GET'])
def controle():
	if 'login' in session:
		session.pop('tabela', None)
		log = session['login']
		data_atual = datetime.datetime.today()
		from collections import namedtuple
		Data = namedtuple('Data', 'dia mes ano')
		hoje = Data(dia=data_atual.day, mes=calendario['{}'.format(data_atual.month)], ano=data_atual.year)
		
		try:
			if request.method == 'POST':
				session.pop('tecnico', None)
				session.pop('graduacao', None)
				session.pop('calem', None)
				session['login'] = log
				if request.form.get('diasletivos0'):
					session['tabela'] = 'tecnico' 
					return redirect(url_for('dias'))
				elif request.form.get('definirdatas0'):
					session['tabela'] = 'tecnico'
					return redirect(url_for('valores'))

				elif request.form.get('tabelasimportantes0'):
					session['tabela'] = 'tecnico'
					return redirect(url_for('tectable'))

				elif request.form.get('diasletivos1'):
					session['tabela'] = 'graduacao'
					return redirect(url_for('dias'))

				elif request.form.get('definirdatas1'):
					session['tabela'] = 'graduacao'
					return redirect(url_for('valores'))

				elif request.form.get('tabelasimportantes1'):
					session['tabela'] = 'graduacao'
					return redirect(url_for('gradtable'))

				elif request.form.get('diasletivos2'):
					session['tabela'] = 'calem'
					return redirect(url_for('dias'))

				elif request.form.get('definirdatas2'):
					session['tabela'] = 'calem'
					return redirect(url_for('valores'))

				elif request.form.get('tabelasimportantes2'):
					session['tabela'] = 'calem'
					return redirect(url_for('tectable'))

				elif request.form.get('logout'):
					session.pop('login',None)
					session.clear()
					return redirect(url_for('home'))

				elif request.form.get('atividades'):
					session['tabela'] = "atividades"
					return redirect(url_for('atividades'))

				elif request.form.get('feriados'):
					session['tabela'] = "feriados"
					return redirect(url_for('atividades'))

				elif request.form.get('submitpdf'):
					if request.form.get('input1'):
						session['tecnico'] = True
					if request.form.get('input2'):
						session['graduacao'] = True
					if request.form.get('input3'):
						session['calem'] = True
					return redirect(url_for('download'))
			
			return render_template('controle.html', log=log.upper(), dia=hoje.dia, mes=hoje.mes, ano=hoje.ano, calemMsg="Informações sobre datas CALEM entrar em contato com a coordenação", feriados=False)
		except:
			return redirect(url_for('home'))
	else:
		return redirect(url_for('home'))

@app.route('/controle/download', methods=['POST', 'GET'])
def download():
	if 'login' in session:
		log = session['login']
		try:
			filename = str(simplificador_nomes[log]) + '.pdf'
			log = str(simplificador_nomes[log])
		except:
			filename = str(log) + '.pdf'
		try:
			paths = os.path.join(app.root_path, 'latex', str(log)+'.tex')
			path_fake = os.path.join(app.root_path, 'latexvisual', str(log)+'.tex')
			data_atual = datetime.datetime.today()
			ano = data_atual.year
			
			city = Campi.query.filter_by(cidade=session['login'])[0]
			with open(paths, 'wb') as w:
				string = r"""
\documentclass[thesis]{hmcposter}
\usepackage{graphicx}
\usepackage{natbib}
\usepackage{booktabs}
\usepackage{subfig}
\usepackage{amsmath}
\usepackage{textcomp}
\usepackage{longtable}
\usepackage{url}
\posteryear{%s}
\author{ } 
\title{%s}
\class{Calendário Acadêmico %s}
\pagestyle{fancy}
\usepackage{setspace}
\onehalfspacing
\begin{document}
\begin{poster}
\normalsize""" %(ano, str(session['login']).upper(), ano)

				if 'tecnico' in session:
					string+= r"\section{\color{hmcorange}Técnico Integrado}"
					tec = city.tecnico[0]
					atividades_ordenadas = sorted([eventos_atuais for eventos_atuais in tec.atividades if eventos_atuais.ano == ano])
					if len([ativids for ativids in atividades_ordenadas if ativids.mes < 5]) < 9:
						corte_vertical = 5
					else:
						corte_vertical = 4

					if len([ativids for ativids in atividades_ordenadas if (ativids.mes >= 8 and ativids.mes < 10)]) < 9:
						corte_vertical2 = 11
					else:
						corte_vertical2 = 10
					
					for letivos in tec.dias:
						if letivos.mes > 1:
							if letivos.dia == 0:
								continue

							elif letivos.mes == corte_vertical:
								string+= r"""\vfill\null
\columnbreak
\section{\hfill \color{hmcorange}1º Semestre}
"""
							elif letivos.mes == 8:
								string+= r"""\newpage
\section{\color{hmcorange}Técnico}"""
							elif letivos.mes == corte_vertical2:
								string+= r"""\vfill\null
\columnbreak
\section{\hfill \color{hmcorange}2º Semestre}
"""
							string+= r"\subsection{%s \hfill %s dias letivos}" % (calendario[str(letivos.mes)], letivos.dia)
							substring = [ativ for ativ in atividades_ordenadas if ativ.mes == letivos.mes]
							for i in substring:
								string += str(i)
					tabelax = tec.tabela1 + tec.tabela2
					tup2 = tuple(tabelax.split(';')[:-1])
					string+= r"""\newpage
~
\vfill
\begin{center}
\large \textbf{DIAS LETIVOS DO CURSO TÉCNICO INTEGRADO}
\newline
\null
\newline
\begin{table}
\centering
\resizebox{0.7\columnwidth}{!}{
\begin{tabular}{|c|c|c|c|c|c|c|}
\hline
\textbf{SEMESTRE} & \textbf{SEG} & \textbf{TER} & \textbf{QUA} & \textbf{QUI} & \textbf{SEX} & \textbf{SÁB} \\ \hline
1º & %s & %s & %s & %s & %s & %s \\ \hline
2º & %s & %s & %s & %s & %s & %s \\ \hline
\multicolumn{6}{|c|}{\small \textbf{Total de dias efetivos de atividades acadêmicas:}}              & %s            \\ \hline
\end{tabular}
}
\end{table}
\newline
\null
\newline
\end{center}
\vfill
\null
\columnbreak
~
\vfill
\begin{center}
\large \textbf{DIAS LETIVOS DO CURSO TÉCNICO INTEGRADO}
\newline
\null
\newline
\begin{table}
\centering
\resizebox{0.9\columnwidth}{!}{
\begin{tabular}{|c|c|c|c|c|}
\hline
\textbf{SEMESTRE} & \textbf{\begin{tabular}[c]{@{}c@{}}1ª NOTA\\ BIMESTRAL\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}2ª NOTA \\ BIMESTRAL\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}RESULTADOS\\ FINAIS\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}DIÁRIOS DE\\ CLASSE - DERAC\end{tabular}} \\ \hline
1º & %s & %s & %s & %s \\ \hline
2º & %s & %s & %s & %s \\ \hline
\end{tabular}
}
\end{table}
\newline
\null
\newline
\end{center}
\vfill
\null
\newpage""" % tup2 
				if 'graduacao' in session:
					string+= r"\section{\color{hmcorange}Graduação}"
					grad = city.graduacao[0]
					atividades_ordenadas = sorted([eventos_atuais for eventos_atuais in grad.atividades if eventos_atuais.ano == ano])
					if len([ativids for ativids in atividades_ordenadas if ativids.mes < 5]) < 9:
						corte_vertical = 5
					else:
						corte_vertical = 4
					if len([ativids for ativids in atividades_ordenadas if (ativids.mes >= 8 and ativids.mes < 10)]) < 9:
						corte_vertical2 = 11
					else:
						corte_vertical2 = 10
					for letivos in grad.dias:
						if letivos.mes > 1:
							if letivos.dia == 0:
								continue

							elif letivos.mes == corte_vertical:
								string+= r"""\vfill\null
\columnbreak
\section{\hfill \color{hmcorange}1º Semestre}
"""
							elif letivos.mes == 8:
								string+= r"""\newpage
\section{\color{hmcorange}Graduação}"""
							elif letivos.mes == corte_vertical2:
								string+= r"""\vfill\null
\columnbreak
\section{\hfill \color{hmcorange}2º Semestre}
"""
							string+= r"\subsection{%s \hfill %s dias letivos}" % (calendario[str(letivos.mes)], letivos.dia)
							substring = [ativ for ativ in atividades_ordenadas if ativ.mes == letivos.mes]
							for i in substring:
								string += str(i)
					tabelax = grad.tabela1 + grad.tabela2
					tup2 = tuple(tabelax.split(';')[:-1])
					string+= r"""\newpage
~
\vfill
\begin{center}
\large \textbf{DIAS LETIVOS DOS CURSOS DE GRADUAÇÃO}
\newline
\null
\newline
\begin{table}
\centering
\resizebox{0.7\columnwidth}{!}{
\begin{tabular}{|c|c|c|c|c|c|c|}
\hline
\textbf{SEMESTRE} & \textbf{SEG} & \textbf{TER} & \textbf{QUA} & \textbf{QUI} & \textbf{SEX} & \textbf{SÁB} \\ \hline
1º & %s & %s & %s & %s & %s & %s \\ \hline
2º & %s & %s & %s & %s & %s & %s \\ \hline
\multicolumn{6}{|c|}{\small \textbf{Total de dias efetivos de atividades acadêmicas:}}              & %s            \\ \hline
\end{tabular}
}
\end{table}
\null
\end{center}
\vfill
\null
\columnbreak
~
\vfill
\begin{center}
\large \textbf{DATAS IMPORTANTES PARA OS CURSOS DE GRADUAÇÃO}
\newline
\null
\newline
\begin{table}
\centering
\resizebox{0.75\columnwidth}{!}{
\begin{tabular}{|c|c|c|}
\hline
\textbf{SEMESTRE} & \textbf{\begin{tabular}[c]{@{}c@{}}TÉRMINO\\ DO SEMESTRE\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}RESULTADOS\\ FINAIS\end{tabular}} \\ \hline
1º & %s & %s \\ \hline
2º & %s & %s \\ \hline
\end{tabular}
}
\end{table}
\newline
\null
\newline
Os cronogramas de matrícula serão divulgados em instrução própria e publicados no portal dos alunos
\end{center}
\vfill
\null
\newpage""" % tup2
				string+= r"\section{\color{hmcorange}Calem}"
				if 'calem' in session:
					
					cal = city.calem[0]
					atividades_ordenadas = sorted([eventos_atuais for eventos_atuais in cal.atividades if eventos_atuais.ano == ano])
					if len([ativids for ativids in atividades_ordenadas if ativids.mes < 5]) < 9:
						corte_vertical = 5
					else:
						corte_vertical = 4

					if len([ativids for ativids in atividades_ordenadas if (ativids.mes >= 8 and ativids.mes < 10)]) < 9:
						corte_vertical2 = 11
					else:
						corte_vertical2 = 10

					for letivos in cal.dias:
						if letivos.mes > 1:
							if letivos.dia == 0:
								continue

							elif letivos.mes == corte_vertical:
								string+= r"""\vfill\null
\columnbreak
\section{\hfill \color{hmcorange}1º Semestre}
								"""
							elif letivos.mes == 8:
								string+= r"""\newpage
\section{\color{hmcorange}Calem}"""
							elif letivos.mes == corte_vertical2:
								string+= r"""\vfill\null
\columnbreak
\section{\hfill \color{hmcorange}2º Semestre}
							"""
							string+= r"\subsection{%s \hfill %s dias letivos}" % (calendario[str(letivos.mes)], letivos.dia)
							substring = [ativ for ativ in atividades_ordenadas if ativ.mes == letivos.mes]
							flag = 0
							
							for i in substring:
								string += str(i)
					tabelax = cal.tabela1 + cal.tabela2
					tup2 = tuple(tabelax.split(';')[:-1])
					string+= r"""\newpage
~
\vfill
\begin{center}
\large \textbf{DIAS LETIVOS DOS CURSOS DO CALEM}
\newline
\null
\newline
\begin{table}
\centering
\resizebox{0.7\columnwidth}{!}{
\begin{tabular}{|c|c|c|c|c|c|c|}
\hline
\textbf{SEMESTRE} & \textbf{SEG} & \textbf{TER} & \textbf{QUA} & \textbf{QUI} & \textbf{SEX} & \textbf{SÁB} \\ \hline
1º & %s & %s & %s & %s & %s & %s \\ \hline
2º & %s & %s & %s & %s & %s & %s \\ \hline
\multicolumn{6}{|c|}{\small \textbf{Total de dias efetivos de atividades acadêmicas:}}              & %s            \\ \hline
\end{tabular}
}
\end{table}
\newline
\null
\newline
\end{center}
\vfill
\null
\columnbreak
~
\vfill
\begin{center}
\large \textbf{DATAS IMPORTANTES PARA OS CURSOS DO CALEM}
\newline
\null
\newline
\begin{table}
\centering
\resizebox{0.9\columnwidth}{!}{
\begin{tabular}{|c|c|c|c|c|}
\hline
\textbf{SEMESTRE} & \textbf{\begin{tabular}[c]{@{}c@{}}1ª NOTA\\ BIMESTRAL\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}2ª NOTA \\ BIMESTRAL\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}RESULTADOS\\ FINAIS\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}DIÁRIOS DE\\ CLASSE - DERAC\end{tabular}} \\ \hline
1º & %s & %s & %s & %s \\ \hline
2º & %s & %s & %s & %s \\ \hline
\end{tabular}
}
\end{table}
\newline
\null
\newline
\end{center}
\vfill
\null
\newpage""" % tup2
				else:
					string+= r"\textbf{Informações sobre datas Calem entrar em contato com a coordenação} \newpage"

				string+= r"\onespacing \section{\color{hmcorange}Feriados, Recessos e Férias}"
				try:
					ordenados = sorted([feriados for feriados in city.ferias if feriados.ano == ano])
					mes_atual = 0
					
					for it in ordenados:
						if it.mes > mes_atual:
							string+= r"\subsection{%s}" %(calendario[str(it.mes)])
							mes_atual = it.mes
						string+= str(it)
				except:
					pass
				string+= r"""\newpage
\section{\color{hmcorange}Atividades E Eventos}"""	
				try:
					ordenados = sorted([ativis for ativis in city.atividades if ativis.ano == ano])
					mes_atual = 0
					for it in ordenados:
						if it.mes > mes_atual:
							string+= r"\subsection{%s}" %(calendario[str(it.mes)])
							mes_atual = it.mes
						string+= str(it)
				except:
					pass
				string+= r"""\end{poster}
\end{document}"""
				w.write(string.encode('utf-8'))
			
			os.chdir('flaskapp')
			os.chdir('latex') 
			os.system("pdflatex --interaction=nonstopmode {}.tex".format(log))
			os.replace(paths, path_fake)
			os.chdir('..')
			os.chdir('latexvisual')
			os.system("pdflatex --interaction=nonstopmode {}.tex".format(log))
			os.chdir('..')
			try:
				os.remove('{}.aux'.format(log))
				os.remove('{}.log'.format(log))
			except:
				pass
			
			os.chdir('..')
			return send_from_directory(directory='latexvisual', filename=filename, as_attachment=True)
		except:
			return redirect(url_for('controle'))

	else:
		return redirect(url_for('home'))

@app.route('/reenvio', methods=['POST', 'GET'])
def reenvio():
	if request.method == 'POST':
		return redirect(url_for('home'))
	return render_template('reenvio.html')

@app.route('/tentativa', methods=['POST', 'GET'])
def tentativa():
	if request.method == 'POST':
		log = request.form['login']
		sen = request.form['senha']
		if  log in encrypted:
			if hashlib.md5(sen.encode()).hexdigest() == encrypted[log]:
				session['login'] = log
				return redirect(url_for('controle'))
		return redirect(url_for('tentativa')) 
	return render_template('fail.html')

@app.route('/tectable', methods=['POST','GET'])
def tectable():
	if 'login' in session:
		city = Campi.query.filter_by(cidade=session['login'])[0]
		if session['tabela'] == 'tecnico':
			nivel_curso = city.tecnico[0]
			titulo = None
			
		else:
			nivel_curso = city.calem[0]
			titulo = 'Tabela Calem'
		
		tabelax = nivel_curso.tabela1 + nivel_curso.tabela2
		tup2 = tuple(tabelax.split(';')[:-1])
		if request.method == 'POST':
			dic = request.form.to_dict()
			string_table = ""
			for key in range(0, 13):
				keys = 'e' + str(key)
				string_table += str(dic[keys]) + ';'
			nivel_curso.tabela1 = string_table

			string_table2 = ""
			for key in range(0, 8):
				keys = 'a' + str(key)
				string_table2 += str(dic[keys]) + ';'
			nivel_curso.tabela2 = string_table2
			try:
				db.session.commit()
			except:
				db.session.rollback()
			return redirect(url_for('controle'))

		return render_template('tecnico_table.html', title=titulo, tup=tup2)
	else:
		return redirect(url_for('home'))

@app.route('/gradtable', methods=['POST','GET'])
def gradtable():
	if 'login' in session:
		city = Campi.query.filter_by(cidade=session['login'])[0]
		nivel_curso = city.graduacao[0]
		tabelax = nivel_curso.tabela1 + nivel_curso.tabela2
		tup2 = tuple(tabelax.split(';')[:-1])
		if request.method == 'POST':
			dic = request.form.to_dict()
			string_table = ""
			for key in range(0, 13):
				keys = 'e' + str(key)
				string_table += str(dic[keys]) + ';'
			nivel_curso.tabela1 = string_table

			string_table2 = ""
			for key in range(0, 4):
				keys = 'a' + str(key)
				string_table2 += str(dic[keys]) + ';'
			nivel_curso.tabela2 = string_table2
			try:
				db.session.commit()
			except:
				db.session.rollback()
			return redirect(url_for('controle'))

		return render_template('graduacao_table.html', tup=tup2)
	else:
		return redirect(url_for('home'))
	


@app.route('/atividades_academicas', methods=['POST', 'GET'])
def atividades_academicas():
	if 'login' in session:
		html_name = "child_ativ_acad"
		try:
			html_name+= str(simplificador_nomes[str(session['login'])])
		except:
			html_name += str(session['login'])
		html_name += ".html"
		paths = os.path.join(app.root_path, 'templates', html_name)
		city = Campi.query.filter_by(cidade=session['login'])[0]
		data_atual = datetime.datetime.today()
		if 'tabela' in session:
			tab = session['tabela']
			if tab == 'atividades':
				nivel_curso = city.atividades
			else:
				return redirect(url_for('controle'))

			if request.method == 'POST':
				if request.form.get('atualizarbdd'):
				
					for ativ in nivel_curso:
						db.session.delete(ativ)
					try:
						db.session.commit()
					except:
						db.session.rollback()
					dic = request.form.to_dict()
					for number in range(0, (len(dic)//3)+2):
						strnumber = str(number)
						nam = "name" + strnumber
						diaini = "diaini" + strnumber
						diafin = "diafin" + strnumber
						desc = "desc" + strnumber
						des = "des" + strnumber
						
						try:
							d1 = request.form[diaini]
							d2 = request.form[diafin]
							m = request.form[nam]
							try:
								c = str(request.form[desc])
								z = False
							except:
								c = str(request.form.get(des))
								z = True
						except:
							continue
						if ((d1 == '') or (d2 == '') or (m == '') or (c == '')):
							continue

						try:
							
							idd = Atividades.query.all()[-1].id + 1
						
						except:
							idd = 1
						var_dic = {'id':idd, 'dia_inicio':d1, 'dia_final': d2, 'mes':m, 'comentario':c, 'cidade_id':str(city), 'ano': data_atual.year, 'flag': z}
						
						db.session.add(Atividades(**var_dic))
						
					try:
						db.session.commit()
					except:
						db.session.rollback()
				else:
					dic = request.form.to_dict()

					for idx in range(1,len(dic)):
						key = "del" + str(idx)
						try:
							dic[key]
							db.session.delete(sorted(nivel_curso)[idx-1])
						except:
							pass
					try:
						db.session.commit()
						return redirect(url_for('controle'))
					except:
						db.session.rollback()

				return redirect(url_for('controle'))
			nivel_curso = Campi.query.filter_by(cidade=session['login'])[0].atividades
			atividades_ordenadas = [eventos_ordenados for eventos_ordenados in sorted(nivel_curso) if eventos_ordenados.ano == data_atual.year]
			with open(paths, 'wb') as w:
				string = r"""
					{% extends "atividades_academicas.html" %}
					{% block content %}
						<tr id='addr0' data-id="0" class="hidden" align="center">
		                                  
		                                <td data-name="name">
		                                    <select name="name0">
		                                        <option value="">Mês</option>
		                                        {% for mes in data %}
		                                            <option value= "{{ mes }}">{{ data[mes] }}</option>
		                                        {% endfor %}
		                                    </select>
		                                </td>
		                                <td data-name="diaini">
							<select name="diaini0">
								<option value="">Dia Inicial</option>
								{% for dia in dias %}
									<option value= "{{ dia }}">{{ dia }}</option>
								{% endfor %}
							</select>
						</td>
						<td data-name="diafin">
							<select name="diafin0">
								<option value="">Dia Final</option>
								{% for dia in dias %}
									<option value= "{{ dia }}">{{ dia }}</option>
								{% endfor %}
							</select>
						</td>
		                                <td data-name="desc">
		                                    <textarea name="desc0" placeholder="Descrição" class="form-control" cols="25" maxlength="800"></textarea>
		                                </td>                     
		                                <td data-name="del">
		                                    <button name="del0" class='btn btn-danger glyphicon glyphicon-remove row-remove'><span aria-hidden="true">&times;</span></button>
		                                </td>

	                    </tr>"""

				for i, evento in enumerate(atividades_ordenadas, 1):
					month = calendario[str(evento.mes)]

					string +=r"""
						<tr id='addr%s' data-id="%s" class="hidden" align="center">

							<td data-name="name">
								<select name="name%s">
								<option value="%s" selected>%s</option>
								{%% for mes in data %%}
									<option value= "{{ mes }}">{{ data[mes] }}</option>
								{%% endfor %%}
								</select>
							</td>
							<td data-name="diaini">
								<select name="diaini%s">
									<option value="%s" selected>%s</option>
									{%% for dia in dias %%}
										<option value= "{{ dia }}">{{ dia }}</option>
									{%% endfor %%}
								</select>
							</td>
							<td data-name="diafin">
								<select name="diafin%s">
									<option value="%s" selected>%s</option>
									{%% for dia in dias %%}
										<option value= "{{ dia }}">{{ dia }}</option>
									{%% endfor %%}
								</select>
							</td>"""%(i,i,i,str(evento.mes), month,i, evento.dia_inicio, evento.dia_inicio, i, evento.dia_final, evento.dia_final)
					if evento.flag:
						a = latex_to_html(pat=r'\\textbf{([\s\w_]+)}', sentence=evento.comentario)
						b = latex_to_html(pat=r'\\underline{([\s\w_]+)}', sentence=a)
						html_string = latex_to_html(pat=r'\\textit{([\s\w_]+)}', sentence=b)

						string+= r"""
							<td data-name="des">
								<input type="hidden" name="des%s" value="%s" id="des%s">
								%s
							</td>
						"""%(i, evento.comentario, i, html_string)

					else:
						string+=r"""
							<td data-name="desc">
								<textarea name="desc%s" placeholder="Descrição" class="form-control" cols="25" maxlength="800">%s</textarea>
							</td>"""%(i, evento.comentario)

					string+= r"""	                     
							<td data-name="del">
							
								<input type="submit" class="btn btn-danger" value="x" name="del%s">
							
							</td>
						</tr>""" %(i)
				string+= r"{% endblock %}"
				w.write(string.encode('utf-8'))
			
			return render_template(html_name, boler=True, data = calendario, dias=range(1,32))

		else:
			return redirect(url_for('controle'))
	else:
		return redirect(url_for('home'))

@app.route('/atividades', methods=['POST', 'GET'])
def atividades():
	if 'login' in session:
		paths = os.path.join(app.root_path, 'templates', 'child_ativ.html')
		city = Campi.query.filter_by(cidade=session['login'])[0]
		data_atual = datetime.datetime.today()
		if 'tabela' in session:
			tab = session['tabela']
			if tab == 'atividades':
				return redirect(url_for('atividades_academicas'))
			elif tab == 'feriados':
				nivel_curso = city.ferias

			if request.method == 'POST':
				if request.form.get('atualizarbdd'):
					try:
						for ativ in nivel_curso:
							db.session.delete(ativ)
						db.session.commit()
					except:
						db.session.rollback()
					dic = request.form.to_dict()
					for number in range(0, (len(dic)//3)+2):
						strnumber = str(number)
						nam = "name" + strnumber
						dia = "dia" + strnumber
						desc = "desc" + strnumber
						des = "des" + strnumber
						
						try:
							d = str(request.form[dia])
							m = request.form[nam]
							try:
								c = str(request.form[desc])
								z = False
							except:
								c = str(request.form.get(des))
								z = True
						except:
							continue
						if ((d == '') or (m == '') or (c == '')):
							continue

						try:
							idd = Ferias.query.all()[-1].id + 1
						except:
							idd = 1
						var_dic = {'id':idd, 'dia':d, 'mes':m, 'comentario':c, 'cidade_id':str(city), 'ano': data_atual.year, 'flag': z}
						try:
							db.session.add(Ferias(**var_dic))
						except:
							db.session.rollback()
						
					try:
						db.session.commit()
					except:
						db.session.rollback()
				else:
					dic = request.form.to_dict()

					for idx in range(1,len(dic)):
						key = "del" + str(idx)
						try:
							dic[key]
							db.session.delete(sorted(nivel_curso)[idx-1])
						except:
							pass
					try:
						db.session.commit()
						return redirect(url_for('controle'))
					except:
						db.session.rollback()

				return redirect(url_for('controle'))
			try:
				atividades_ordenadas = [eventos_ordenados for eventos_ordenados in sorted(nivel_curso) if eventos_ordenados.ano == data_atual.year]
				with open(paths, 'wb') as w:
					string = r"""
						{% extends "atividades.html" %}
						{% block content %}
							<tr id='addr0' data-id="0" class="hidden" align="center">
			                                  
			                                <td data-name="name">
			                                    <select name="name0">
			                                        <option value="">Mês</option>
			                                        {% for mes in data %}
			                                            <option value= "{{ mes }}">{{ data[mes] }}</option>
			                                        {% endfor %}
			                                    </select>
			                                </td>
			                                <td data-name="dia">
			                                    <textarea name="dia0" placeholder="Dias" class="form-control" cols="7" maxlength="7"></textarea>
			                                </td>
			                                <td data-name="desc">
			                                    <textarea name="desc0" placeholder="Descrição" class="form-control" cols="25" maxlength="800"></textarea>
			                                </td>                     
			                                <td data-name="del">
			                                    <button name="del0" class='btn btn-danger glyphicon glyphicon-remove row-remove'><span aria-hidden="true">&times;</span></button>
			                                </td>

		                    </tr>"""

					for i, evento in enumerate(atividades_ordenadas, 1):
						month = calendario[str(evento.mes)]

						string +=r"""
							<tr id='addr%s' data-id="%s" class="hidden" align="center">

								<td data-name="name">
									<select name="name%s">
									<option value="%s" selected>%s</option>
									{%% for mes in data %%}
										<option value= "{{ mes }}">{{ data[mes] }}</option>
									{%% endfor %%}
									</select>
								</td>
								<td data-name="dia">
									<textarea name="dia%s" placeholder="Dias" class="form-control" cols="7" maxlength="7">%s</textarea>
								</td>"""%(i,i,i,str(evento.mes), month,i,evento.dia)
						if evento.flag:
							a = latex_to_html(pat=r'\\textbf{([\s\w_]+)}', sentence=evento.comentario)
							b = latex_to_html(pat=r'\\underline{([\s\w_]+)}', sentence=a)
							html_string = latex_to_html(pat=r'\\textit{([\s\w_]+)}', sentence=b)

							string+= r"""
								<td data-name="des">
									<input type="hidden" name="des%s" value="%s" id="des%s">
									%s
								</td>
							"""%(i, evento.comentario, i, html_string)

						else:
							string+=r"""
								<td data-name="desc">
									<textarea name="desc%s" placeholder="Descrição" class="form-control" cols="25" maxlength="800">%s</textarea>
								</td>"""%(i, evento.comentario)

						string+= r"""	                     
								<td data-name="del">
								
									<input type="submit" class="btn btn-danger" value="x" name="del%s">
								
								</td>
							</tr>""" %(i)
					string+= r"{% endblock %}"
					w.write(string.encode('utf-8'))
				return render_template('child_ativ.html', boler=True, data = calendario)

			except:
				return render_template('atividades.html', data = calendario)
		else:
			return redirect(url_for('controle'))
	else:
		return redirect(url_for('home'))

@app.route('/dias', methods=['POST', 'GET'])
def dias():
	if 'login' in session:
		city = Campi.query.filter_by(cidade=session['login'])[0]
		data_atual = datetime.datetime.today()
		if 'tabela' in session:
			tab = session['tabela']
			if tab == 'graduacao':
				nivel_curso = city.graduacao[0]
			elif tab == 'tecnico':
				nivel_curso = city.tecnico[0]
			elif tab == 'calem':
				nivel_curso = city.calem[0]
				
			try:
				dias_letivos = sorted(nivel_curso.dias)
			except:
				return redirect(url_for('controle'))
			try:
				if request.method == 'POST':
					if request.form.get('atualizarbdd'):
						for ativ in dias_letivos:
							db.session.delete(ativ)
						try:
							db.session.commit()
						except:
							db.session.rollback()
						try:
							for idx in range(1, 13):
								d = "dia" + str(idx)
								
								d = request.form.get(d)
								try:
									idd = Letivos.query.all()[-1].id + 1
								except:
									idd = 1
								

								var_dic = {'id':idd, 'dia':d, 'mes':idx}
								if tab == 'graduacao':
									var_dic.update({'graduacao_id': str(nivel_curso)})
								elif tab == 'tecnico':
									var_dic.update({'tecnico_id': str(nivel_curso)})
								elif tab == 'calem':
									var_dic.update({'calem_id': str(nivel_curso)})
								var_dic.update({'ano':data_atual.year})
							
								db.session.add(Letivos(**var_dic))
								try:
									db.session.commit()
								except:
									pass
							return redirect(url_for('controle'))
						except:
							db.session.rollback()
				mydic = {item.mes:item.dia for item in dias_letivos}
				
				return render_template('dias.html', days=range(0,32), quantidade=range(1,13), meses=mydic, conv=calendario)
			except:
				return redirect(url_for('controle'))
		
		else:
			return redirect(url_for('controle'))
	else:
		return redirect(url_for('home'))

@app.route('/valores', methods=['POST', 'GET'])
def valores():
	if 'login' in session:
		html_name = "child-"
		try:
			html_name+= str(simplificador_nomes[str(session['login'])])
		except:
			html_name += str(session['login'])
		city = Campi.query.filter_by(cidade=session['login'])[0]
		data_atual = datetime.datetime.today()

		if 'tabela' in session:
			
			tab = session['tabela']
			if tab == 'graduacao':
				nivel_curso = city.graduacao[0]
				html_name += "-graduacao.html"
			elif tab == 'tecnico':
				nivel_curso = city.tecnico[0]
				html_name += "-tecnico.html"
			elif tab == 'calem':
				nivel_curso = city.calem[0]
				html_name += "-calem.html"
			paths = os.path.join(app.root_path, 'templates', html_name)

			if request.method == 'POST':
				if request.form.get('atualizarbdd'):
					for ativ in nivel_curso.atividades:
						if ativ.ano == data_atual.year:
							db.session.delete(ativ)
					try:
						db.session.commit()
					except:
						db.session.rollback()
						
					dic = request.form.to_dict()
					for number in range(0, (len(dic)//3)+2):
						strnumber = str(number)
						nam = "name" + strnumber
						dia = "dia" + strnumber
						desc = "desc" + strnumber
						des = "des" + strnumber
						try:
							d = request.form[dia]
							m = request.form.get(nam)
							try:
								c = str(request.form[desc])
								z = False
							except:
								c = str(request.form.get(des))
								z = True
						except:
							continue
						if ((d == '') or (m == '') or (c == '')):
							continue
						try:
							idd = Eventos.query.all()[-1].id + 1
						except:
							idd = 1
						var_dic = {'id':idd, 'dia':d, 'mes':m, 'comentario':c}
						if tab == 'graduacao':
							nivel_curso = city.graduacao[0]
							var_dic.update({'graduacao_id': str(nivel_curso)})
						elif tab == 'tecnico':
							nivel_curso = city.tecnico[0]
							var_dic.update({'tecnico_id': str(nivel_curso)})
						elif tab == 'calem':
							nivel_curso = city.calem[0]
							var_dic.update({'calem_id': str(nivel_curso)})
						var_dic.update({'ano':data_atual.year, 'flag': z})
						db.session.add(Eventos(**var_dic))
					try:	
						db.session.commit()
					except:
						db.session.rollback()
				else:
					dic = request.form.to_dict()

					for idx in range(1,len(dic)):
						key = "del" + str(idx)
						try:
							dic[key]
							db.session.delete([eventos_organizados for eventos_organizados in sorted(nivel_curso.atividades) if eventos_organizados.ano == data_atual.year][idx-1])
						except:
							pass
					try:
						db.session.commit()
					except:
						db.session.rollback()
				return redirect(url_for('controle'))
			city = Campi.query.filter_by(cidade=session['login'])[0]
			if tab == 'graduacao':
				nivel_curso = city.graduacao[0]
			elif tab == 'tecnico':
				nivel_curso = city.tecnico[0]
			elif tab == 'calem':
				nivel_curso = city.calem[0]
			atividades_ordenadas = sorted(nivel_curso.atividades)	
			with open(paths, 'wb') as w:
				string = r"""
					{% extends "valores.html" %}
					{% block content %}
						<tr id='addr0' data-id="0" class="hidden" align="center">
		                                  
		                                <td data-name="name">
		                                    <select name="name0">
		                                        <option value="">Mês</option>
		                                        {% for mes in data %}
		                                            <option value= "{{ mes }}">{{ data[mes] }}</option>
		                                        {% endfor %}
		                                    </select>
		                                </td>
		                                <td data-name="dia">
		                                    <select name="dia0">
		                                        <option value="">Dia</option>
		                                        {% for dia in dias %}
		                                            <option value= "{{ dia }}">{{ dia }}</option>
		                                        {% endfor %}
		                                    </select>
		                                </td>
		                                <td data-name="desc">
		                                    <textarea name="desc0" placeholder="Descrição" class="form-control" cols="25" maxlength="800"></textarea>
		                                </td>                     
		                                <td data-name="del">
		                                    <button name="del0" class='btn btn-danger glyphicon glyphicon-remove row-remove'><span aria-hidden="true">&times;</span></button>
		                                </td>

	                    </tr>"""

				for i, evento in enumerate(atividades_ordenadas, 1):
					month = calendario[str(evento.mes)]
					string +=r"""
						<tr id='addr%s' data-id="%s" class="hidden" align="center">

							<td data-name="name">
								<select name="name%s">
								<option value="%s" selected>%s</option>
								{%% for mes in data %%}
									<option value= "{{ mes }}">{{ data[mes] }}</option>
								{%% endfor %%}
								</select>
							</td>
							<td data-name="dia">
								<select name="dia%s">
								<option value="%s" selected>%s</option>
								{%% for dia in dias %%}
									<option value= "{{ dia }}">{{ dia }}</option>
								{%% endfor %%}
								</select>
							</td>""" %(i,i,i,str(evento.mes), month,i,evento.dia,evento.dia)
					if evento.flag:
						a = latex_to_html(pat=r'\\textbf{([\s\w_]+)}', sentence=evento.comentario)
						b = latex_to_html(pat=r'\\underline{([\s\w_]+)}', sentence=a)
						html_string = latex_to_html(pat=r'\\textit{([\s\w_]+)}', sentence=b)
						string+= r"""
							<td data-name="des">
								<input type="hidden" name="des%s" value="%s" id="des%s">
								%s
							</td>
						"""%(i, evento.comentario, i, html_string)

					else:
						string += r"""
							<td data-name="desc">
								<textarea name="desc%s" placeholder="Descrição" class="form-control" cols="25" maxlength="800">%s</textarea>
							</td>""" %(i,evento.comentario)

					string += r"""                     
							<td data-name="del">
								<input type="submit" class="btn btn-danger" value="x" name="del%s">
							</td>
						</tr>""" %(i)

				string+= r"{% endblock %}"
				w.write(string.encode('utf-8'))
			return render_template(html_name, boler=True, data = calendario, dias=range(1, 32))	
			
		else:
			return redirect(url_for('controle'))
	else:
		return redirect(url_for('home'))
