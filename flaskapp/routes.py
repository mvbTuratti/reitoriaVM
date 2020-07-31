from flask import render_template, url_for, flash, redirect, request, session, escape, send_from_directory
import hashlib
import os
import datetime
#import de direto acesso ao banco de dados
from flaskapp import app, db
from flaskapp.latexHTML import latex_to_html
#esse é o import para manuseio das tabelas SQL, cada tabela pode ser encarada como uma classe no python, cheque os comentários de models.py para 
# mais informações
from flaskapp.models import Campi, Ferias, Atividades, Letivos, Calem, Graduacao, Tecnico, Eventos

#dict criado para facilitar futuramente a conversão de um número para o nome de um mês por extenso e vice-versa
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

# dict para criar arquivos que tem nome com base o nome do campus, o problema é o uso de espaço entre palavras para criação de um arquivo
simplificador_nomes = {
	'campo mourão' : 'mourao',
	'cornélio procópio' : 'procopio',
	'dois vizinhos' : 'vizinhos',
	'francisco beltrão' : 'beltrao',
	'pato branco' : 'branco',
	'ponta grossa' : 'pgrossa',
	'santa helena' : 'helena'
}

#dict comprehension de todos os campus com login e senha HASHEADA dentro da tabela Campi do banco de dados
#encrypted = dict([(record.cidade, record.senha) for record in Campi.query.all()])
#inicialmente era em escala 'global' na aplicação, mas isso causa problemas porque algumas alterações não ficam associadas aos objetos já
#carregados! Query precisa ser refeita para puxar atualizações na tabela!

"""
	* Rota inicial do site, a primeira linha limpa todos e qualquer cookies salvos na sessão, ou seja, caso a pessoa volte para a url inicial
	* as informações como por exemplo 'campus apucarana ativou as tabelas de técnico integrado', para saber quais cookies são utilizados veja ref [a definir]
"""
@app.route('/', methods=['POST', 'GET'])
def home():
	session.clear()
	#dict comprehension de todos os campus com login e senha HASHEADA dentro da tabela Campi do banco de dados
	encrypted = dict([(record.cidade, record.senha) for record in Campi.query.all()])
	#caso seja clicado no botão do site o site recebe um form request que valida esse if, do contrário é exposto ao usuário o arquivo home.html
	#no primeiro acesso à página não há form request, portanto é falso e só será aberto o html
	if request.method=='POST':
		#associado a esse request estarão informações coletadas pelos campos que receberam nome de login e senha dentro de home.html
		log = request.form['login']
		sen = request.form['senha']
		#checa se o login está dentro do banco de dados, na tabela Campi através do dicionário previamente preenchido
		if log in encrypted:
			#caso esteja dentro, a senha fornecida pelo usuário será obviamente uma não hasheada, e a senha salva é uma hasheada, portanto
			#é necessário decriptografar a senha do dict utilizando o mesmo método que é feito na hora da criptografia, veja ref[ a definir ]
			if hashlib.md5(sen.encode()).hexdigest() == encrypted[log]:
				#adiciona aos cookies qual é o campus logado
				session['login'] = log
				if log == "adm":
					return redirect(url_for('adm'))
				#sai do método e é redirecionado para controle
				return redirect(url_for('controle'))
		#caso login ou senha estejam incorretos a pessoa é redirecionada para o método 'tentativa' isso foi uma gafe da minha parte,
		#usualmente o erro seria tratado com condicionais Jinja2 dentro do html, porém eu utilizei uma animação em home.html que devido
		#ao desconhecimento na hora não soube tratar, contornei o problema com um .html separado que carrega uma tela com uma mensagem de erro
		#e evita as animações css estilizadas 
		return redirect(url_for('tentativa'))
	return render_template('home.html')

"""
	* Método da página de controle, aqui ficam os paineis de seleção de todas as opções, a ideia é que os checkmarks da parte esquerda sejam 
	* salvos como cookies
"""
@app.route('/controle', methods=['POST', 'GET'])
def controle():
	# Caso o usuário tenha ativado o cookie de login através da tela de login, proceda, caso contrário, jogue-o para a página de login
	if 'login' in session:
		#Remove os cookies salvos de tabelas
		session.pop('tabela', None)
		#salva aqui o login do campus, a ideia é manter os campus como nome de usuários, facilita na hora da impressão e diferenciar
		#os tratamentos entre campus (por exemplo: usar nomes para identificar quais tem técnico anual e qual é semestral para os if's)
		log = session['login']
		if (log == "adm"):
			return redirect(url_for('adm'))
		#aqui o python recolhe a data em que está sendo utilizado o site, para fins conforme ref [a definir]
		data_atual = datetime.datetime.today()
		from collections import namedtuple
		Data = namedtuple('Data', 'dia mes ano')
		#facilita a identificação visual no futuro para chamada por nomes de dia, mês e ano
		hoje = Data(dia=data_atual.day, mes=calendario['{}'.format(data_atual.month)], ano=data_atual.year)
		
		#abordagem de tentar presumindo que não haverá falha, caso falhe algo é redirecionado para página controle, usualmente aqui
		#seria anexado uma mensagem de erro, mas tendo em vista a escala do projeto e a quantidade de usuários, os problemas possíveis
		#são poucos, o objetivo é evitar o crash do flask para não precisar um macro que checa se o server está ativo ou inativo
		try:
			#caso seja feito um pedido de form request, trata-o devidamente (botão sendo clicado), caso contrário apenas carregue a página 
			#inicial de login, porque assim evidencia que algo ocorreu de errado.
			if request.method == 'POST':
				#limpa os checkboxs ativos anteriormente, caso alguém vá por um botão de retorno para controle, todos estarão desativados
				session.pop('tecnico', None)
				session.pop('graduacao', None)
				session.pop('calem', None)
				session['login'] = log
				
				#Tratamento individual de cada botão, os nomes são sugestivos com o número definindo a linha, 0 sendo a linha de técnico
				#1 a de graduação e 2 a do calem
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

				#botão de logout, limpa todos os cookies e joga o usuário para tela de login.
				elif request.form.get('logout'):
					session.pop('login',None)
					session.clear()
					return redirect(url_for('home'))

				#botão de atividades e feriados, caso seja desejável omitir algum deles não precisa comentar essa parte do código
				#o que havia sido definido até a data inicial do projeto é que apenas feriados deveriam ser omitidos para os campus
				#tendo em vista isso eu fiz um sistema de flag que ativa ou desativa o botão de feriados, mais detalhes na chamada do método
				elif request.form.get('atividades'):
					session['tabela'] = "atividades"
					return redirect(url_for('atividades'))

				elif request.form.get('feriados'):
					session['tabela'] = "feriados"
					return redirect(url_for('atividades'))

				#aqui é setado como cookies os checkbox's marcados antes de clicar em gerar pdf.
				elif request.form.get('submitpdf'):
					if request.form.get('input1'):
						session['tecnico'] = True
					if request.form.get('input2'):
						session['graduacao'] = True
					if request.form.get('input3'):
						session['calem'] = True
					if request.form.get('semCalem'):
						session['seminf'] = True
					return redirect(url_for('download'))
			#calemMsg é a mensagem que será impressa quando o usuário selecionar que não há informações disponíveis para o Calem
			#feriados é a flag que determina a aparição ou não do botão que redireciona para controle de feriados
			return render_template('controle.html', log=log.upper(), dia=hoje.dia, mes=hoje.mes, ano=hoje.ano, calemMsg="Informações sobre datas CALEM entrar em contato com a coordenação", feriados=False)
		except:
			return redirect(url_for('home'))
	else:
		return redirect(url_for('home'))


"""
	* Método que gera o pdf, conforme ref [a definir].
	* Sinceramente, caso deseje alterar algo graficamente no pdf você provavelmente terá que refatorar todo esse método, pois ele
	* é extremamente fixo na estética previamente definida. Aqui ocorre um carregamento numa variável chamada 'string', essa variável é 
	* constantemente concatenada de forma estruturada, o banco de dados é visitado e conforme os cookies ativos as condicionais de if 
	* são ativadas e o 'string' é atualizado com novas informações, a 'string' final é o texto que gerará o arquivo latex que posteriormente
	* será transformado em pdf, conforme a referência citada.
"""
@app.route('/controle/download', methods=['POST', 'GET'])
def download():
	#verifica qual o login salvo nos cookies, sem cookies tentando acessar esse site n faz sentido, portanto redireciona para o login
	if 'login' in session:
		#salva o nome do campus como variável 'log'
		log = session['login']
		try:
			#assume que é um dos campus que tem nome separado por vírgula, usa a dic para usar o nome novo, só por garantia de tipagem
			#filtra como 'str', atualiza o 'log' como o nome abreviado
			filename = str(simplificador_nomes[log]) + '.pdf'
			log = str(simplificador_nomes[log])

		except:
			#caso não passe pelo filtro, assuma o nome do campus como nome do arquivo e deixe a variável 'log' como ela está
			filename = str(log) + '.pdf'
		try:
			#uso do import os para garantir funcionabilidade do código em sistemas linux e windows (os dois sistemas tem formas / e \ respectivamente
			# para separar diretórios). Para entender o fluxo de file manegment use ref [a definir]
			paths = os.path.join(app.root_path, 'latex', str(log)+'.tex')
			path_fake = os.path.join(app.root_path, 'latexvisual', str(log)+'.tex')
			data_atual = datetime.datetime.today()
			ano = data_atual.year
			
			#query que traz acesso ao objeto cidade (conforme ref [a definir])
			city = Campi.query.filter_by(cidade=session['login'])[0]

			#aberto uma thread para escrever em um arquivo, string raw pois uso de \ é constante
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

				#tem técnico ativado nos cookies? Caso sim:
				if 'tecnico' in session:
					#técnico dividido entre anual e semestral, sendo anual esses dois campus
					lista_tecnico_anual = ['campo mourão', 'pato branco']
					#criando um novo log, pois ambos foram sobrescritos em 'log' (ambos tem nome composto)
					log2 = session['login']
					if log2 in lista_tecnico_anual:
						string+= r"\section{\color{hmcorange}Técnico Integrado Anual}"
						#acesso ao objeto que pertence a tabela Tecnico, essa query retorna uma lista, por isso é necessário [0], mesmo sendo
						#apenas um objeto dentro da lista
						tec = city.tecnico[0]
						#list comprehension ordenado dos eventos do ano em que está sendo acessado o site, conforme ref [a definir]
						atividades_ordenadas = sorted([eventos_atuais for eventos_atuais in tec.atividades if eventos_atuais.ano == ano])
						
						#Isso aqui seria uma forma de dividir melhor as colunas de forma estética, porém a forma mais eficiente seria
						#contagem iterativa, mas visto número 'n' de eventos esperados em um ano ser baixo isso não é problemático
						if len([ativids for ativids in atividades_ordenadas if ativids.mes < 5]) < 8:
							corte_vertical = 5
						else:
							corte_vertical = 4

						if len([ativids for ativids in atividades_ordenadas if (ativids.mes >= 8 and ativids.mes < 10)]) < 9:
							corte_vertical2 = 11
						else:
							corte_vertical2 = 10
						#loop que itera pelos eventos da tabela tecnico, .dias é a chave estrangeira que acessa a tabela Eventos
						for letivos in tec.dias:
							#Como não vai ter eventos em janeiro, já pula.
							if letivos.mes > 1:
								#flags para separar cortes de coluna e de página, esses valores representam os meses, definidos anteriormente
								if letivos.mes == corte_vertical:
									string+= r"""\vfill\null
\columnbreak
\section{\hfill \color{hmcorange}1º Semestre}
"""	
								#divisão de semestres é sempre no mesmo mês de julho que acaba e agosto começa um novo, caso precise
								#mudar é aqui o valor numérico de 8 a ser alterado
								elif letivos.mes == 8:
									string+= r"""\newpage
\section{\color{hmcorange}Técnico}"""
								elif letivos.mes == corte_vertical2:
									string+= r"""\vfill\null
\columnbreak
\section{\hfill \color{hmcorange}2º Semestre}
"""
								#cria um subtítulo que representa o mês com o número de dias contidos
								string+= r"\subsection{%s \hfill %s dias letivos}" % (calendario[str(letivos.mes)], letivos.dia)
								#list comprehension do subconjunto de eventos que percente ao mês atual
								substring = [ativ for ativ in atividades_ordenadas if ativ.mes == letivos.mes]
								#Se não há eventos em um mês, eu quero que o mês seja separados por uma linha extra, que melhora visualmente
								#a apresentação, caso haja eventos, isso é dispensado
								if substring:
									#loop de todos os itens
									for i in substring:
										string += str(i)
									# último item peço que anule o comando \newline (-8 caracteres) para que a separação entre meses seja menor e caiba mais
									# eventos numa única página	
									string = string[:-8]
								else:
									string += r' \null \newline '
						# Para entender o sistema que fiz aqui é melhor checar a ref[ a definir]
						# para sumarizar: é uma string, que dividi entre ';' para criar uma tupla, facilitando na hora de atribuir
						# à raw string os '%s' invocados ao longo do texto
						tabelax = tec.tabela1 + tec.tabela2
						tup2 = tuple(tabelax.split(';')[:-1])
						string+= r"""\newpage
~
\vfill
\begin{center}
\large \textbf{DIAS LETIVOS DO CURSO TÉCNICO INTEGRADO ANUAL}
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
\end{center}
\begin{center}
    \large \textbf{ANUAL}
\end{center}
\null
\begin{center}
\begin{table}
\centering
\resizebox{0.9\columnwidth}{!}{
\begin{tabular}{|c|c|c|c|c|c|}
\hline
\textbf{\begin{tabular}[c]{@{}c@{}}1ª NOTA\\ BIMESTRAL\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}2ª NOTA \\ BIMESTRAL\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}3ª NOTA \\ BIMESTRAL\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}4ª NOTA \\ BIMESTRAL\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}TÉRMINO DO \\ANO LETIVO\end{tabular}} & \textbf{\begin{tabular}[c]{@{}c@{}}RESULTADOS\\ FINAIS\end{tabular}} \\ \hline
%s & %s & %s & %s & %s & %s \\ \hline
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
					# aqui é o else referente a técnico anual/semestral, é basicamente o mesmo sistema em tudo, a exceção aqui é 
					# a omissão do termo anual e a forma com que as tabelas são estruturadas, como é algo estritamente estético
					# foi necessário criação de algo que é essencialmente copy/paste
					else:
						string+= r"\section{\color{hmcorange}Técnico Integrado}"
						tec = city.tecnico[0]
						atividades_ordenadas = sorted([eventos_atuais for eventos_atuais in tec.atividades if eventos_atuais.ano == ano])
						if len([ativids for ativids in atividades_ordenadas if ativids.mes < 5]) < 8:
							corte_vertical = 5
						else:
							corte_vertical = 4

						if len([ativids for ativids in atividades_ordenadas if (ativids.mes >= 8 and ativids.mes < 10)]) < 9:
							corte_vertical2 = 11
						else:
							corte_vertical2 = 10
						
						for letivos in tec.dias:
							if letivos.mes > 1:
								

								if letivos.mes == corte_vertical:
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
								if substring:
									for index, i in enumerate(substring):
										
										string += str(i)
										
									string = string[:-8]
								else:
									string += r' \null \newline '
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
				
				#Sistema de graduação, caso esteja ativo o cookie do mesmo ele entra nesse if
				if 'graduacao' in session:
					#adiciona o título
					string+= r"\section{\color{hmcorange}Graduação}"
					#salva na variável 'grad' o acesso da tabela Graduação que é direcionado pela chave externa do campus ativo no cookie,
					#como essa query retorna uma lista é necessário [0], para acessar ao primeiro item da lista
					grad = city.graduacao[0]
					#list comprehension ordenada que é contido no ano atual do pedido de download, ref [a definir]
					atividades_ordenadas = sorted([eventos_atuais for eventos_atuais in grad.atividades if eventos_atuais.ano == ano])
					#checa se tem menos que 8 itens nos eventos de graduação até o mês de maio (mês 5), caso tenha menos que 8, define o
					#corte vertical da página no mês de maio, caso contrário o corte fica em abril
					if len([ativids for ativids in atividades_ordenadas if ativids.mes < 5]) < 8:
						corte_vertical = 5
					else:
						corte_vertical = 4
					#sistema semelhante ao anterior, porém refere-se ao segundo semestre (entre meses 8 e 12)
					if len([ativids for ativids in atividades_ordenadas if (ativids.mes >= 8 and ativids.mes < 10)]) < 9:
						corte_vertical2 = 11
					else:
						corte_vertical2 = 10
					for letivos in grad.dias:
						#if que evita o mês de Janeiro ser computado.
						if letivos.mes > 1:
							#condicionais que definem corte de páginas e cortes verticais
							if letivos.mes == corte_vertical:
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
							#list comprehension dos eventos referentes ao mês atual para listá-los no 'for', caso não haja nenhum membro
							#na lista, apenas é pulado uma linha com \newline para espaçamento estético
							substring = [ativ for ativ in atividades_ordenadas if ativ.mes == letivos.mes]
							if substring:
								for index, i in enumerate(substring):
									string += str(i)
								#retira o último \newline para fins estéticos	
								string = string[:-8]
							else:
								string += r' \null \newline '
					tabelax = grad.tabela1 + grad.tabela2
					#tabela é uma string dividida por ; que é transformado em tuplas para facilitar no preenchimento com %s da raw string
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
				#Esse fragmento é muito semelhante ao anterior de graduação, não foi generalizado devidamente por problemas de deadline
				if 'calem' in session:
					string+= r"\section{\color{hmcorange}Calem}"
					if 'seminf' in session:
						string+= r"\textbf{Informações sobre datas Calem entrar em contato com a coordenação} \newpage"
					else:
						cal = city.calem[0]
						atividades_ordenadas = sorted([eventos_atuais for eventos_atuais in cal.atividades if eventos_atuais.ano == ano])
						if len([ativids for ativids in atividades_ordenadas if ativids.mes < 5]) < 8:
							corte_vertical = 5
						else:
							corte_vertical = 4

						if len([ativids for ativids in atividades_ordenadas if (ativids.mes >= 8 and ativids.mes < 10)]) < 9:
							corte_vertical2 = 11
						else:
							corte_vertical2 = 10

						for letivos in cal.dias:
							if letivos.mes > 1:
								

								if letivos.mes == corte_vertical:
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
								
								if substring:
									for index, i in enumerate(substring):
										string += str(i)
										
									string = string[:-8]
								else:
									string += r' \null \newline '
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
				#aqui começa o método de Feriados, cercado por um bloco de try só para evitar a quebra do servidor
				try:
					#list comprehension ordenada que garante ser eventos do ano selecionado para download, ref [a definir]
					ordenados = sorted([feriados for feriados in city.ferias if feriados.ano == ano])
					mes_atual = 0
					flag_first = False
					for it in ordenados:
						#caso seja um mês diferente do atual é necessário adicionar uma nova subsection que nomeia o novo mês
						if it.mes > mes_atual:
							#caso não seja o primeiro mês, remova \newline por finalidades estéticas.
							if flag_first:
								string = string[:-8]
							string += r"\subsection{%s}" %(calendario[str(it.mes)])
							#atualiza o mês
							mes_atual = it.mes
							#atualiza a flag para garantir que entre no condicional 
							flag_first = True
						string+= str(it)
				except:
					pass
				
				#página de atividades e eventos, cercado por um try/catch só por via das dúvidas
				string+= r"""\newpage
\section{\color{hmcorange}Atividades E Eventos}"""	
				try:
					#bem similar ao fragmento de atividades, checar ele caso haja dúvidas
					ordenados = sorted([ativis for ativis in city.atividades if ativis.ano == ano])
					mes_atual = 0
					flag_first = False
					for it in ordenados:
						if it.mes > mes_atual:
							if flag_first:
								string = string[:-8]
							string += r"\subsection{%s}" %(calendario[str(it.mes)])
							mes_atual = it.mes
							flag_first = True
						string+= str(it)
				except:
					pass
				""" código comentado que cria um pequeno rodapé de data de criação, caso seja necessário no futuro """
				#data_atual = datetime.datetime.today()
				#string+= r""" ~ \vfill \hfill \small \color{hmcorange}Gerado em %s de %s """ %(data_atual.day, calendario[str(data_atual.month)])
				
				string+= r"""\end{poster}
\end{document}"""
				#aqui toda a variável 'string' é escrita no documento aberto, seria possível também ir escrevendo aos poucos, mas como
				#o documento nunca será grande o suficiente para ter problemas com isso, é confiável guardar tudo numa variável e escrevê-la
				#em sua integridade posteriormente
				w.write(string.encode('utf-8'))
			
			#manuseio de diretórios para criar os arquivos com base no texto .tex formado, conforme ref [a definir]
			#o fluxo funciona em ambos Linux/Windows.
			os.chdir('flaskapp')
			os.chdir('latex') 
			os.system("pdflatex --interaction=nonstopmode {}.tex".format(log))
			os.replace(paths, path_fake)
			os.chdir('..')
			os.chdir('latexvisual')
			os.system("pdflatex --interaction=nonstopmode {}.tex".format(log))
			os.chdir('..')
			#remove os arquivos .aux e .log gerados, porque depois complica para encontrar e lota a pasta.
			try:
				os.remove('{}.aux'.format(log))
				os.remove('{}.log'.format(log))
			except:
				pass
			
			os.chdir('..')
			#retorna a minuta gerada como arquivo para download
			return send_from_directory(directory='latexvisual', filename=filename, as_attachment=True)
		except:
			return redirect(url_for('controle'))

	else:
		return redirect(url_for('home'))

""" 
	* Módulo de reenvio de senha, 
	* TO-DO
	* Complicado de setar variáveis de e-mail na máquina virtual
	
@app.route('/reenvio', methods=['POST', 'GET'])
def reenvio():
	if request.method == 'POST':
		return redirect(url_for('home'))
	return render_template('reenvio.html')"""

"""
	* Método que trata quando uma tentativa de login da errado, é extremamente similar ao padrão, porém carrega uma .html que não tem efeito
	* estilizado na tela de login
"""
@app.route('/tentativa', methods=['POST', 'GET'])
def tentativa():
	#dict comprehension de todos os campus com login e senha HASHEADA dentro da tabela Campi do banco de dados
	encrypted = dict([(record.cidade, record.senha) for record in Campi.query.all()])

	if request.method == 'POST':
		log = request.form['login']
		sen = request.form['senha']
		if  log in encrypted:
			if hashlib.md5(sen.encode()).hexdigest() == encrypted[log]:
				session['login'] = log
				if log == "adm":
					return redirect(url_for('adm'))
				return redirect(url_for('controle'))
		return redirect(url_for('tentativa')) 
	return render_template('fail.html')

"""
	* Função de criação dos .html de tabelas, conforme ref [ a definir ], existem duas funções para criação de tabela, pois há pequenas modificações
	* na forma de acesso do banco de dados e de formas de verificação, dentro dessa função existe uma subdivisão entre tabelas semestrais e anuais
	* a tabela .html é coletada como string e diferentes campos são separados por ';', posteriormente a string é passada por um filtro de ';' que os separam.
"""
@app.route('/tectable', methods=['POST','GET'])
def tectable():
	#checa se tem cookies de login
	if 'login' in session:
		#faz uma query de objeto com o cookie fornecido, armazenando-o na variável city
		city = Campi.query.filter_by(cidade=session['login'])[0]
		#esse if-else serve para ambas as tabelas de calem e técnico (número de colunas e linhas idênticas)
		if session['tabela'] == 'tecnico':
			#caso seja um cookie de acesso via técnico, faz acessa ao primeiro item da lista de técnicos atribuído a esse campus
			#a variável 'titulo' é apenas um diferenciador para o título da página html
			nivel_curso = city.tecnico[0]
			titulo = None
			
		else:
			#caso seja cookie de calem, faz acesso ao primeiro item da lista de calem atribuído a esse campus
			nivel_curso = city.calem[0]
			titulo = 'Tabela Calem'
		#acessa a string de texto que representam os itens da tabela ordenados e separados por ';'
		tabelax = nivel_curso.tabela1 + nivel_curso.tabela2
		#cria uma tupla e atribui separadamente os itens, com a flag de separação sendo ';'
		tup2 = tuple(tabelax.split(';')[:-1])
		#pequena lista em que os membros são os campus de técnico anual 
		lista_tecnico_anual = ['campo mourão', 'pato branco']
		log = session['login']
		#checa se o cookie de login é equivalente a um dos itens que representam técnico anual
		if log in lista_tecnico_anual:
			# caso sim, retorne o html correspondente, caso receba um comando de POST no formulário (o html em questão só fornece 1 botão que o faz,
			# o de salvar mudanças) caso ele tenha vindo pela aba de controle, carregue apenas o html, com informações extraídas e armazenadas na tupla
			# anteriormente.
			if request.method == 'POST':
				
				#recebe todos os itens do dicionário de formulário, para receber múltiplos itens simultâneamente 
				dic = request.form.to_dict()
				string_table = ""
				#processo inverso para preenchimento da tabela, passa nos itens coletando-os, e une tudo numa string separando-os com ';'
				for key in range(0, 13):
					#'e' é apenas uma convenção que escolhi para separar entre as tabelas
					keys = 'e' + str(key)
					string_table += str(dic[keys]) + ';'
				nivel_curso.tabela1 = string_table

				string_table2 = ""
				for key in range(0, 6):
					keys = 'a' + str(key)
					string_table2 += str(dic[keys]) + ';'
				#atualiza os itens do banco de dados da tabela1 e tabela2
				nivel_curso.tabela2 = string_table2
				#tenta atualizar, caso de problemas faça um rollback para evitar queda do site
				try:
					db.session.commit()
				except:
					db.session.rollback()
				#redireciona para controle
				return redirect(url_for('controle'))

			return render_template('tecnico_anual_table.html', title=titulo, tup=tup2)
		#sistema similar ao anterior, a diferença é a quantidade de itens de colunas e linhas, portanto é necessário um html diferenciado
		else:
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

# sistema similar ao anterior, porém com acessos diferenciados de objetos para graduação (número de colunas e linhas diferentes para html e loop de preenchimento
# no banco de dados)
@app.route('/gradtable', methods=['POST','GET'])
def gradtable():
	#checa se o cookie está preenchido
	if 'login' in session:
		#acessa o objeto campus
		city = Campi.query.filter_by(cidade=session['login'])[0]
		#acessa o primeiro item da lista de graduações associados a esse campus
		nivel_curso = city.graduacao[0]
		#recupera as tabelas gravadas até então
		tabelax = nivel_curso.tabela1 + nivel_curso.tabela2
		#transforma de string para tupla
		tup2 = tuple(tabelax.split(';')[:-1])
		if request.method == 'POST':
			#caso o site receba um formulário de postagem, recupera o dicionário do html (que tem salvo objetos com nomes e valores, sendo
			# esses valores previamente editados pelo usuário)
			dic = request.form.to_dict()
			#dois loops para preenchimento com base nos valores recuperados do dicionário recebido
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
	
"""
	* Esse método trata as Atividades salvas, o tratamento no geral é bem semelhante a tabela de Eventos, a diferença principal é que
	* Atividades podem durar mais que um dia, portanto o tratamento em alguns casos é diferentes, pois o .html é diferente nas opções 
	* de item por linha (por exemplo, ao invés de uma coluna para dias, são duas, uma de início e outra de término).
	* Como é diferenciado as atividades de um dia para as de múltiplos? Isso é feito em models.py através de dunder methods, sempre que 
	* uma instância de objeto da classe Atividades é solicitada como string, ele checa se o dia final é menor ou igual ao dia inicial
	* e dependendo desse controle lógico é retornado a string apropriada.
	* Esse método é encarregado de apresentar a página de edição de Atividades, ou seja, toda a manipulação do usuário para deletar, criar
	* e editar as Atividades no banco de dados, o programa só permite alterações nas Atividades do ano que está sendo usado o software, 
	* para as informações dos anos anteriores serem persistentes no banco de dados. 
	* Para mais informações referentes ao fluxo no geral dessa página, consulte ref [a definir]
"""
@app.route('/atividades_academicas', methods=['POST', 'GET'])
def atividades_academicas():
	#checa cookies de login do campus
	if 'login' in session:
		#prefixo de nome que é constante
		html_name = "child_ativ_acad"
		#alguns campus precisam passar pelo simplificador de nome, para remover espaço de nomes compostos
		try:
			html_name+= str(simplificador_nomes[str(session['login'])])
		except:
			html_name += str(session['login'])
		#todos terminam com .html
		html_name += ".html"
		#encontra a string que localiza a pasta de htmls com base em caminho absoluto, funciona em ambos windows e linux
		paths = os.path.join(app.root_path, 'templates', html_name)
		#query para acesso ao objeto referente ao campus acessado
		city = Campi.query.filter_by(cidade=session['login'])[0]
		#recolhe a data atual do uso do software para usar o ano de uso como filtro para pesquisas, assim só é carregado os itens
		# do ano, porém todos fica registrado tudo feito até então
		data_atual = datetime.datetime.today()
		#garante a existência do cookie de tabelas, ou seja, força que esse link seja acessado somente através do botão dentro da página de controle
		#caso o usuário tente acessar o link manualmente ele será redirecionado para aba de controles
		if 'tabela' in session:
			tab = session['tabela']
			#acessa os itens de atividades dos campus, conforme ref [a definir]
			if tab == 'atividades':
				#acha as atividades que pertencem ao ano consultado
				nivel_curso = [ativ for ativ in city.atividades if ativ.ano == data_atual.year]
			else:
				#caso aconteça algum erro imprevisto de cookies incorretos, ele leva para página de controle
				return redirect(url_for('controle'))

			if request.method == 'POST':
				#dividido em dois tipos de atividades de request, um deles é deletar um item antigo do banco de dados, o outro é apenas acesso
				#botões de excluir itens novos são resolvidos por javascript sem recarregar a página, botões de itens antigos, deletam o item 
				#jogam para a página de controle, isso é feito assim por falta de conhecimento em javascript da minha parte
				
				#caso seja o botão de confirmar mudanças
				if request.form.get('atualizarbdd'):
					#deleta todos os itens da tabela de atividades que pertencem a esse campus atual e com a flag do ano da consulta
					for ativ in nivel_curso:
						db.session.delete(ativ)
					try:
						db.session.commit()
					except:
						db.session.rollback()
					#carrega todos os itens preenchidos no dicionário da página html
					dic = request.form.to_dict()
					#uma aproximação de itens que vai sempre percorrer todos os itens, eles são ordenados mas tem multiplos campos
					#então ao invés de carregar o comprimento do dicionário da para pegar por uma divisão do número de campos em cada 'linha'
					#pois a linha tem pelo menos três itens garantidos, de dia, mês e comentário
					for number in range(0, (len(dic)//3)+2):
						#como eu escolhi numeros ordenados para chamar os campos do html, é só percorrer um loop que incrementa um inteiro
						#e acrescentar ele ao nome das variáveis, após isso checa se ele existe, caso não exista é porque percorreu todos os itens
						strnumber = str(number)
						nam = "name" + strnumber
						diaini = "diaini" + strnumber
						diafin = "diafin" + strnumber
						desc = "desc" + strnumber
						des = "des" + strnumber
						
						#checa se existe, pois essa tabela pode ou não ser uma atividade acadêmica de múltiplos dias
						try:
							d1 = request.form[diaini]
							d2 = request.form[diafin]
							m = request.form[nam]
							#tem dois tipos de itens, os adicionados pela DIREGEA ou criados por usuário, os que são criados pela DIREGEA possuem uma flag e são
							# proibidos de edição, os que são criados por usuários do site são editáveis, os que são editaveis tem flag de False e são consultados
							# por esse uso de API do flask, caso não exista, assume que é o outro cenário, coleta o item 'des' e seta a flag como verdadeira 
							try:
								c = str(request.form[desc])
								z = False
							except:
								c = str(request.form.get(des))
								z = True
						#são duas condicionais que checam, caso não exista ou esteja vazio um dos itens das colunas pula uma iteração do loop
						except:
							continue
						if ((d1 == '') or (d2 == '') or (m == '') or (c == '')):
							continue

						try:
							#tenta consultar o a chave única do último item de atividade da tabela e adiciona +1 a ele, garantindo uma chave única
							idd = Atividades.query.all()[-1].id + 1
						
						except:
							#caso não exista nenhum item, esse é o primeiro, portanto chave = 1
							idd = 1
						#caso passe em todas as condições necessárias, guarda o item como dicionário
						var_dic = {'id':idd, 'dia_inicio':d1, 'dia_final': d2, 'mes':m, 'comentario':c, 'cidade_id':str(city), 'ano': data_atual.year, 'flag': z}
						#cria um objeto Atividades com parâmetros do dicionário e anexa esse objeto a sessão para adicionar no banco de dados
						db.session.add(Atividades(**var_dic))
					#tenta adicionar os itens no banco de dados	
					try:
						db.session.commit()
					except:
						db.session.rollback()
				#aqui é o caso de tentativa de deletar um dos itens, ou seja, foi clicado num botão 'X' de itens antigos.
				else:
					#coleta todos os itens existentes num grande dicionário
					dic = request.form.to_dict()
					#o item X que foi selecionado vai estar associado a um número inteiro de sufixo e vai ser possível checar qual é o inteiro 
					#associado ao botão ativado com base no inteiro coletado, para isso, percorre todos os itens do dicionário
					for idx in range(1,len(dic)):
						key = "del" + str(idx)
						#checa se existe o item com o inteiro de sufixo dessa vez
						try:
							dic[key]
							#caso exista, ordena a lista de atividades do ano do curso carregada, e através do item indexado deleta o item da tabela, ignora o primeiro item, pois
							#o item 0 é sempre um item novo gerado no html
							db.session.delete(sorted(nivel_curso)[idx-1])
							#sai do loop, pois achou 
							break
						except:
							#caso não exista, não precisa fazer nada, pois é o fim dessa iteração do loop 
							pass
					try:
						#atualiza sem o item deletado e retorna para controle
						db.session.commit()
						return redirect(url_for('controle'))
					except:
						db.session.rollback()

				return redirect(url_for('controle'))
			#Caso não seja um request de botão de atualizar ou deletar é porque a página está sendo carregada pela primeira vez
			#carrega as atividades filtradas pelo campus e ano de acesso
			nivel_curso = Campi.query.filter_by(cidade=session['login'])[0].atividades
			atividades_ordenadas = sorted([eventos_ordenados for eventos_ordenados in nivel_curso if eventos_ordenados.ano == data_atual.year])
			#o html é mutável com base em novos itens, aqui é carregado os itens salvos anteriormente, itens novos são tratados com javascript
			#abre um arquivo na pasta de htmls
			with open(paths, 'wb') as w:
				#primeiro item associado a 0 é sempre limpo sem nenhuma informação, pois serve de base para cópia do javascript na geração
				#de novos itens
				#o HTML recebe dicionários que facilitam através de macros do Jinja2, ai, ao invés de fazer uma option para cada dia e mês
				#ele itera através de um loop que colocará todas as opções de numeros inteiros e meses do ano
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
				#aqui é o miolo do html, o responsável por preencher com as informações até então salvas no banco de dados, o loop itera
				#pela lista de atividades previamente ordenadas, começa a partir do item 1, pois item 0 foi feito anteriormente
				for i, evento in enumerate(atividades_ordenadas, 1):
					#o mês é salvo como inteiro de 1 a 12, passa esse valor como chave string de um dicionário, para ter o nome do mês por extenso
					month = calendario[str(evento.mes)]
					#todo o valor gravado fica na tag de <option value="%s" selected>%s</option>, porém é preciso apresentar as outras opções
					#caso o usuário do programa queira atualizar o seu valor. Mas o default das opções na página será o que tinha sido salvo
					#previamente
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
					#esse é o item referente ao bloco de texto, os salvos pelo estagiário (eu) precisam de uma formatação específica, aqui foi
					#passado um desfiltro para estilizar de latex para html, ref [a definir]. Todos os eventos salvos por mim foram setados
					#com essa flag verdadeira, contudo, novos eventos criados pelo usuário serão salvos apenas como falso, pois há a possibilidade
					#de eles editarem posteriormente.
					#caso seja um evento criado pela DIREGEA e não seja editável ele é salvo com a tag 'des%s' e esse tipo é um input hidden
					if evento.flag:
						a = latex_to_html(pat=r'\\textbf{(.*?)}', sentence=evento.comentario)
						b = latex_to_html(pat=r'\\underline{(.*?)}', sentence=a)
						html_string = latex_to_html(pat=r'\\textit{(.*?)}', sentence=b)

						string+= r"""
							<td data-name="des">
								<input type="hidden" name="des%s" value="%s" id="des%s">
								%s
							</td>
						"""%(i, evento.comentario, i, html_string)
					#aqui é caso a flag seja falsa, ou seja, um evento criado durante um acesso por usuários do site, neste caso a tag será
					#'desc' e o item é textarea com um default salvo previamente pelo banco de dados.
					else:
						string+=r"""
							<td data-name="desc">
								<textarea name="desc%s" placeholder="Descrição" class="form-control" cols="25" maxlength="800">%s</textarea>
							</td>"""%(i, evento.comentario)
					#ambos tem um botão de delete, portanto aqui é gerado
					string+= r"""	                     
							<td data-name="del">
							
								<input type="submit" class="btn btn-danger" value="x" name="del%s">
							
							</td>
						</tr>""" %(i)
				#após o término do loop, o arquivo é finalizado e assim é gerado o fragmento de código que será inserido no .html dinâmico
				string+= r"{% endblock %}"
				w.write(string.encode('utf-8'))
			#aqui é o acesso ao site, o nome do .html é dinâmico conforme o campus, portanto é passado uma variável de 'html_name', boler 
			#é uma variável para o controle lógico do Jinja2, e fora isso é passado o dicionário de calendario que contém nomes de meses
			#por extenso e passo também uma lista de números inteiros de 1 até 31 (range é não inclusivo do último valor)
			return render_template(html_name, boler=True, data = calendario, dias=range(1,32))
		
		else:
			return redirect(url_for('controle'))
	else:
		return redirect(url_for('home'))

"""
	* Esse é o método de tratamento de itens de Feriados, originalmente ele tratava Feriados e Atividades, isso porquê a abordagem de 
	* tratamento para atividades de múltiplos dias era escrever num campo de texto '01 a 02' ou '01' como dia, porém a DIREGEA mudou de
	* ideia e achou que tinha muita margem para erro de usuário deixar um campo de texto, portanto esse estilo ficou disponível apenas
	* para itens de Feriados, pois apenas os estagiários terão acesso a esse controle, tendo em vista que Feriados são eventos predefinidos
	* que podem ser consultados em calendários incompletos. 
	* Portanto este método trata toda a página de edição de Feriados, similar a de Eventos e Atividades, mais informações são encontradas em
	* ref [a definir] 
"""
@app.route('/atividades', methods=['POST', 'GET'])
def atividades():
	#checa se cookie de login está ativo
	if 'login' in session:
		#coleta a string de diretórios para criar um arquivo .html no local correto, conforme ref [a definir]
		paths = os.path.join(app.root_path, 'templates', 'child_ativ.html')
		#coleta uma instância de objeto referente ao campus acessado, index [0], pois essa query retorna uma lista com possíveis múltiplos itens
		#que passam por esse filtro, nos casos de campus serão itens únicos, tendo em vista que é uma chave única
		city = Campi.query.filter_by(cidade=session['login'])[0]
		#define o dia, mês e ano de acesso do site
		data_atual = datetime.datetime.today()
		#checa se o usuário entrou através do clique do botão de tabelas no site
		if 'tabela' in session:
			#checa um possível erro improvável, mas caso haja ele é redirecionado para Atividades
			tab = session['tabela']
			if tab == 'atividades':
				return redirect(url_for('atividades_academicas'))
			elif tab == 'feriados':
				#coleta os itens da tabela de Feriados que pertencem a esse campus acessado e ao ano de acesso do site
				nivel_curso = [fer for fer in city.ferias if fer.ano == data_atual.year]
			else:
				return redirect(url_for('controle'))
			#condicional que será ativa somente quando um botão na página de Feriados seja clicada, caso contrário é um acesso
			#através da página 'controle' e esse if será falso
			if request.method == 'POST':
				#confirma que houve um clique de botão, agora checa se é um botão de delete de um item salvo previamente ou se é um botão
				#para salvar todos os dados, pois houve uma alteração, ref [a definir] 
				#esse é o caso de ser uma solicitação para alteração.
				if request.form.get('atualizarbdd'):
					#como será salvo todos os itens salvos no dicionário 'dic' criado mais abaixo, todos os feriados do campus acessado
					#no ano do acesso serão sobrescritos, portanto, todos os itens que já existem que atendem as verificações são excluidos
					#do banco de dados para que sejam criados os novos itens
					try:
						#loop para deletar todos os itens
						for ativ in nivel_curso:
							db.session.delete(ativ)
						db.session.commit()
					except:
						db.session.rollback()
					#dicionário com todos os itens da página html
					dic = request.form.to_dict()
					#mesmo sistema de Atividades, um loop que garante iteração para todos os itens 
					for number in range(0, (len(dic)//3)+2):
						#conforme o padrão, cada linha possui um sufixo numérico, para iterar entre os possíveis itens é necessário apenas
						#avançar em +1 no valor final
						strnumber = str(number)
						nam = "name" + strnumber
						dia = "dia" + strnumber
						desc = "desc" + strnumber
						des = "des" + strnumber
						#sistema que checa se é um item criado por estagiário com flag que garante que não seja editável o campo de texto
						#ou se foi um evento criado pelo usuário do site. Isso para que a qualidade de edição ou não de acessos futuros 
						#seja presenvada
						try:
							#tenta recolher os itens de dia e mês, caso não exista essa linha não será incluído no dicionário
							#e um erro ocorrerá, levando a pulada de iteração, conforme ref [a definir]
							d = str(request.form[dia])
							m = request.form[nam]
							try:
								#aqui checa se é feito pelo usuário
								c = str(request.form[desc])
								z = False
							except:
								#caso não seja, foi um Feriado criado pelo estagiário, portanto é não editável
								c = str(request.form.get(des))
								z = True
						except:
							continue
						#caso alguns dos itens estajam vazios, descarte ele e pule para próxima iteração do loop
						if ((d == '') or (m == '') or (c == '')):
							continue
						#tente acessar o último Feriado salvo na tabela e recupere a chave única dele, adicione + 1, para gerar uma nova
						#chave única
						try:
							idd = Ferias.query.all()[-1].id + 1
						except:
							#caso não haja itens de Feriados, é o primeiro item na tabela, portanto índice 1.
							idd = 1
						#cria um dicionário com todos os valores coletados
						var_dic = {'id':idd, 'dia':d, 'mes':m, 'comentario':c, 'cidade_id':str(city), 'ano': data_atual.year, 'flag': z}
						try:
							#crie uma instância de objeto com os parâmetros salvos no dicionário, adicione essa instância de objeto 
							#para o banco de dados
							db.session.add(Ferias(**var_dic))
						except:
							db.session.rollback()
					#confirme a adição, caso de problemas dê rollback
					try:
						db.session.commit()
					except:
						db.session.rollback()
				#esse é o caso em que foi selecionado um botão que exclui um item já salvo previamente no banco de dados
				#novos itens são tratados via javascript, itens antigos com flask, conforme ref [a definir]
				else:
					#recupera todas as informações do html em forma de dicionário
					dic = request.form.to_dict()
					#itera por todo o dicionário procurando qual o sufixo int que acompanha o botão 'del'
					for idx in range(1,len(dic)):
						key = "del" + str(idx)
						try:
							#existe esse 'del' + sufixo? caso sim, encontre o índice na lista ordenada e delete esse membro
							dic[key]
							db.session.delete(sorted(nivel_curso)[idx-1])
						except:
							#caso não exista no dicionário, pule a iteração
							pass
					try:
						db.session.commit()
						return redirect(url_for('controle'))
					except:
						db.session.rollback()

				return redirect(url_for('controle'))
			#caso não tenha sido acessado através de um botão, a página será carregada normalmente, .html gerado dinamicamente
			try:
				#recolhe as atividades com base no campus e no ano de acesso, filtra e ordena
				atividades_ordenadas = sorted([eventos_ordenados for eventos_ordenados in nivel_curso if eventos_ordenados.ano == data_atual.year])
				#abre um arquivo de texto para criar o .html a ser carregado pela página
				with open(paths, 'wb') as w:
					#carrega o início que será inserido num block herdado de atividades.html
					#o início são opções default que serão copiadas via javascript caso o usuário tente criar novos itens na página
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
					#itera os itens recuperados de atividades filtradas por campus e ano de acesso
					for i, evento in enumerate(atividades_ordenadas, 1):
						#usa o dicionário criado para transformar valores inteiros em meses por extenso
						month = calendario[str(evento.mes)]
						#todo o valor gravado fica na tag de <option value="%s" selected>%s</option>, porém é preciso apresentar as outras opções
						#caso o usuário do programa queira atualizar o seu valor. Mas o default das opções na página será o que tinha sido salvo
						#previamente

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
						#esse é o item referente ao bloco de texto, os salvos pelo estagiário (eu) precisam de uma formatação específica, aqui foi
						#passado um desfiltro para estilizar de latex para html, ref [a definir]. Todos os eventos salvos por mim foram setados
						#com essa flag verdadeira, contudo, novos eventos criados pelo usuário serão salvos apenas como falso, pois há a possibilidade
						#de eles editarem posteriormente.
						#caso seja um evento criado pela DIREGEA e não seja editável ele é salvo com a tag 'des%s' e esse tipo é um input hidden
						if evento.flag:
							a = latex_to_html(pat=r'\\textbf{(.*?)}', sentence=evento.comentario)
							b = latex_to_html(pat=r'\\underline{(.*?)}', sentence=a)
							html_string = latex_to_html(pat=r'\\textit{(.*?)}', sentence=b)

							string+= r"""
								<td data-name="des">
									<input type="hidden" name="des%s" value="%s" id="des%s">
									%s
								</td>
							"""%(i, evento.comentario, i, html_string)
						#caso em que foi criado por usuários num acesso prévio ao site, esse campo ficará editável
						else:
							string+=r"""
								<td data-name="desc">
									<textarea name="desc%s" placeholder="Descrição" class="form-control" cols="25" maxlength="800">%s</textarea>
								</td>"""%(i, evento.comentario)
						#todos eles criam um botão de delete
						string+= r"""	                     
								<td data-name="del">
								
									<input type="submit" class="btn btn-danger" value="x" name="del%s">
								
								</td>
							</tr>""" %(i)
					string+= r"{% endblock %}"
					#finaliza a criação do arquivo .html
					w.write(string.encode('utf-8'))
				#carrega o arquivo .html criado pelo método e passa a ele variáveis que serão usadas pelo Jinja2
				return render_template('child_ativ.html', boler=True, data = calendario)
			#erro que ocorrerá quando não houver nenhum item no banco de dados, portanto é necessário carregar apenas o .html original
			#que sem a flag 'boler' vai rodar normalmente com apenas um item default que permite criação de multiplos novos itens 
			#com javascript, ref [a definir]
			except:
				return render_template('atividades.html', data = calendario)
		else:
			return redirect(url_for('controle'))
	else:
		return redirect(url_for('home'))

"""
	* Método que trata das tabelas de edições de quantidade de dias de atividade acadêmica, conforme ref [a definir].
	* Na página carregada só é carregado uma tabela de duas colunas e 12 linhas, referentes a associação de mês com um número de dias (máximo 31)
"""	
@app.route('/dias', methods=['POST', 'GET'])
def dias():
	#checa se está logado através de cookies coletados
	if 'login' in session:
		#cria uma instância de objeto que é a do campus logado
		city = Campi.query.filter_by(cidade=session['login'])[0]
		#coleta a data atual
		data_atual = datetime.datetime.today()
		#esse método é usado pelas três modalidades existentes num campus, aqui filtra através de cookies qual foi selecionado no botão da página 'controle'
		if 'tabela' in session:
			tab = session['tabela']
			if tab == 'graduacao':
				nivel_curso = city.graduacao[0]
			elif tab == 'tecnico':
				nivel_curso = city.tecnico[0]
			elif tab == 'calem':
				nivel_curso = city.calem[0]
			#filtra com base no ano do acesso do site	
			try:
				dias_letivos = sorted([dia for dia in nivel_curso.dias if dia.ano == data_atual.year])
			except:
				return redirect(url_for('controle'))
			try:
				#aqui trata o caso em que uma mudança está sendo feita nas informações já carregadas pela página, isso só ocorre quando o botão
				#de atualizar informações é ativo
				if request.method == 'POST':
					#confirma que o botão foi selecionado
					if request.form.get('atualizarbdd'):
						#todos os itens filtrados previamente são excluídos, pois os novos estão atualmente carregados no dicionário do flask
						#obtidos na página .html, portanto deleta todos os itens desatualizados resgatados no início do acesso da página
						for ativ in dias_letivos:
							db.session.delete(ativ)
						try:
							db.session.commit()
						except:
							db.session.rollback()
						try:
							#com base nos itens recolhidos pelo dicionário, serão preenchidas as novas informações
							for idx in range(1, 13):
								d = "dia" + str(idx)
								
								d = request.form.get(d)
								#para criar uma nova chave única para a tabela, cheque o último valor numérico salvo até então e some 1 a ele
								try:
									idd = Letivos.query.all()[-1].id + 1
								#caso não tenha é porquê não há itens na tabela, portanto é o primeiro item de valor 1.
								except:
									idd = 1
								#cria um dicionário com as informações recolhidas até então

								var_dic = {'id':idd, 'dia':d, 'mes':idx}
								#checa qual é o cookie usado para adicionar ao dicionário o campo de chave externa adequado
								if tab == 'graduacao':
									var_dic.update({'graduacao_id': str(nivel_curso)})
								elif tab == 'tecnico':
									var_dic.update({'tecnico_id': str(nivel_curso)})
								elif tab == 'calem':
									var_dic.update({'calem_id': str(nivel_curso)})
								#finaliza com a informação do ano atual de acesso
								var_dic.update({'ano':data_atual.year})
								#com todas as informações coletadas no dicionário, use-o para criar uma instância de objeto Letivo
								#e adicione-o na fila para updates no banco de dados
								db.session.add(Letivos(**var_dic))
								try:
									#como é um loop e podem ter multiplos acessos, já faz o commit aqui para garantir que não haja conflito de informações
									#como número de chave única
									db.session.commit()
								except:
									pass
							#após a atualização volta para controle
							return redirect(url_for('controle'))
						except:
							db.session.rollback()
				#dict comprehension para enviar as informações resgatadas no banco de dados de forma compacta para o Jinja2 no .html
				#sendo esse dicionário utilizado como opções de default
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
							db.session.delete(sorted([eventos_organizados for eventos_organizados in nivel_curso.atividades if eventos_organizados.ano == data_atual.year])[idx-1])
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
			atividades_ordenadas = sorted([atividadesAtuais for atividadesAtuais in nivel_curso.atividades if atividadesAtuais.ano == data_atual.year])	
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
						a = latex_to_html(pat=r'\\textbf{(.*?)}', sentence=evento.comentario)
						b = latex_to_html(pat=r'\\underline{(.*?)}', sentence=a)
						html_string = latex_to_html(pat=r'\\textit{(.*?)}', sentence=b)
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


@app.route('/adm', methods=['POST', 'GET'])
def adm():
	if 'login' in session:
		if session['login'] != "adm":
			return redirect(url_for('controle'))

		data_atual = datetime.datetime.today()
		campus = [str(c) for c in Campi.query.all()]
		if request.method == 'POST':
			campus = [str(c) for c in Campi.query.all()]
			dic = request.form.to_dict()
			print(dic)
			if "nomeDoBotao" in dic:
				if dic["nomeDoBotao"] == "mudarSenha":
					campi = Campi.query.filter_by(cidade=dic["campusId"])[0]
					senhaNova = hashlib.md5(dic["novaSenha"].encode()).hexdigest()
					campi.senha = senhaNova
					try:
						db.session.commit()
					except:
						db.session.rollback()
						return render_template("adm.html", campus=campus, semSenha=True, anoOcupado=False, dias=[*range(1,32)], meses=calendario, erroEventoNovo=False, excluirGenerico=False, excluirFerias=False, excluirAtividades=False)
				
				if dic["nomeDoBotao"] == "criarEvento":
					campusQuery = Campi.query.all()
					if dic["campusId"] == "adm":
						campi = [c for c in campusQuery if c.cidade != "adm"]
					else:
						campi = [c for c in campusQuery if c.cidade == dic["campusId"]]
					for c in campi:
						var_dic = {'id':(Eventos.query.all()[-1].id+1), 'dia':dic["dia"], 'mes':dic["mes"], 'comentario':dic["novoComentario"]}
						modalidade = dic["modalidade"]
						if modalidade == 'graduacao':
							nivel_curso = c.graduacao[0]
							var_dic.update({'graduacao_id': str(nivel_curso)})
						elif modalidade == 'tecnico':
							nivel_curso = c.tecnico[0]
							var_dic.update({'tecnico_id': str(nivel_curso)})
						elif modalidade == 'calem':
							nivel_curso = c.calem[0]
							var_dic.update({'calem_id': str(nivel_curso)})
						var_dic.update({'ano':data_atual.year, 'flag': True})
						
						try:
							db.session.add(Eventos(**var_dic))
							db.session.commit()
						except:
							db.session.rollback()
							return render_template("adm.html", campus=campus, semSenha=False, anoOcupado=False, dias=[*range(1,32)], meses=calendario, erroEventoNovo="Eventos", excluirGenerico=False, excluirFerias=False, excluirAtividades=False)
				if dic["nomeDoBotao"] == "criarFerias":
					campi = Campi.query.all()
					if dic["campusId"] == "adm":
						campi = [c for c in campi if c.cidade != "adm"]
					else:
						campi = [c for c in campi if c.cidade == dic["campusId"]]
					for c in campi:
						var_dic = {'id':(Ferias.query.all()[-1].id+1), 'dia':dic["dia"], 'mes':dic["mes"], 'comentario':dic["novoComentario"],'cidade_id':str(c), 'ano':data_atual.year, 'flag': True}
						try:
							db.session.add(Ferias(**var_dic))
							db.session.commit()
						except:
							db.session.rollback()
							return render_template("adm.html", campus=campus, semSenha=False, anoOcupado=False, dias=[*range(1,32)], meses=calendario, erroEventoNovo="Ferias", excluirGenerico=False, excluirFerias=False, excluirAtividades=False)
				if dic["nomeDoBotao"] == "criarAtividades":
					campi = Campi.query.all()
					if dic["campusId"] == "adm":
						campi = [c for c in campi if c.cidade != "adm"]
					else:
						campi = [c for c in campi if c.cidade == dic["campusId"]]
					for c in campi:
						var_dic = {'id':(Atividades.query.all()[-1].id+1), 'dia_inicio':dic["dia"], 'dia_final':dic["diafinal"], 'mes':dic["mes"], 'comentario':dic["novoComentario"], 'cidade_id':str(c), 'ano':data_atual.year, 'flag': True}
						
						try:
							
							db.session.add(Atividades(**var_dic))
							db.session.commit()
						except:
							db.session.rollback()
							return render_template("adm.html", campus=campus, semSenha=False, anoOcupado=False, dias=[*range(1,32)], meses=calendario, erroEventoNovo="Atividades", excluirGenerico=False, excluirFerias=False, excluirAtividades=False)
			
			if "viradaDeAno" in dic:
				anoAtual = data_atual.year
				
				from flaskapp.copiadorGenerico import copiadorEventos, copiadorAtividades, copiadorFerias, copiadorLetivo
				anoOcupado = [False,False,False,False]
				if dic["viradaDeAno"] == "proximoAno":
					anoOcupado[0] = copiadorEventos(anoAtual, (anoAtual+1))
					anoOcupado[1] = copiadorAtividades(anoAtual,(anoAtual+1))
					anoOcupado[2] = copiadorFerias(anoAtual,(anoAtual+1))
					anoOcupado[3] = copiadorLetivo(anoAtual,(anoAtual+1))

				elif dic["viradaDeAno"] == "atualAno":
					anoOcupado[0] = copiadorEventos((anoAtual-1), anoAtual)
					anoOcupado[1] = copiadorAtividades((anoAtual-1), anoAtual)
					anoOcupado[2] = copiadorFerias((anoAtual-1), anoAtual)
					anoOcupado[3] = copiadorLetivo((anoAtual-1), anoAtual)

				return render_template("adm.html", campus=campus, semSenha=False, anoOcupado=anoOcupado, dias=[*range(1,32)], meses=calendario, erroEventoNovo=False, excluirGenerico=False, excluirFerias=False, excluirAtividades=False)
			
			if "excluirEvento" in dic:
				listas = []
				c = Campi.query.filter_by(cidade=dic["excluirEvento"])[0]
				modalidade = dic["modalidade"]

				if modalidade == 'graduacao':
					nivel_curso = c.graduacao[0]
					eventos = Eventos.query.filter_by(graduacao_id=str(nivel_curso))
				elif modalidade == 'tecnico':
					nivel_curso = c.tecnico[0]
					eventos = Eventos.query.filter_by(tecnico_id=str(nivel_curso))
				elif modalidade == 'calem':
					nivel_curso = c.calem[0]
					eventos = Eventos.query.filter_by(calem_id=str(nivel_curso))
				try:
					anoTarget = int(dic["ano"])
					eventosDesseAno = [e.comentario for e in eventos if e.ano == anoTarget]
					if not eventosDesseAno:
						raise
					listas.append(eventosDesseAno)
					listas.append([anoTarget, modalidade, dic["excluirEvento"]])
				except:
					listas.append([])
					listas.append([])
				return render_template("adm.html", campus=campus, semSenha=False, anoOcupado=False, dias=[*range(1,32)], meses=calendario, erroEventoNovo=False, excluirGenerico=listas, excluirFerias=False, excluirAtividades=False)
			
			if "excluirFerias" in dic:
				listas = []
				c = Campi.query.filter_by(cidade=dic["excluirFerias"])[0]
				fer = c.ferias
				try:
					anoTarget = int(dic["ano"])
					feriasDesseAno = [f.comentario for f in fer if f.ano == anoTarget]
					if not feriasDesseAno:
						raise
					listas.append(feriasDesseAno)
					listas.append([anoTarget, dic["excluirFerias"]])
				except:
					listas.append([])
					listas.append([])
				return render_template("adm.html", campus=campus, semSenha=False, anoOcupado=False, dias=[*range(1,32)], meses=calendario, erroEventoNovo=False, excluirGenerico=False, excluirFerias=listas, excluirAtividades=False)	

			if "excluirAtividades" in dic:
				listas = []
				c = Campi.query.filter_by(cidade=dic["excluirAtividades"])[0]
				atividadesTodas = c.atividades
				try:
					anoTarget = int(dic["ano"])
					atividadesDesseAno = [ativ.comentario for ativ in atividadesTodas if ativ.ano == anoTarget]
					if not atividadesDesseAno:
						raise
					listas.append(atividadesDesseAno)
					listas.append([anoTarget, dic["excluirAtividades"]])
				except:
					listas.append([])
					listas.append([])
				return render_template("adm.html", campus=campus, semSenha=False, anoOcupado=False, dias=[*range(1,32)], meses=calendario, erroEventoNovo=False, excluirGenerico=False, excluirFerias=False, excluirAtividades=listas)	
			
			if "modelExclusao" in dic:
				from flaskapp.exclusaoGenerica import exclusaoEventos, exclusaoFerias, exclusaoAtividades
				
				if dic["modelExclusao"] == "excluirEventos":
					exclusaoEventos(dic["ano"], dic["modalidade"], dic["campus"], dic["excluirMarcadores"])
				
				if dic["modelExclusao"] == "excluirFerias":
					exclusaoFerias(dic["ano"], dic["campus"], dic["excluirMarcadores"])

				if dic["modelExclusao"] == "excluirAtividades":
					exclusaoAtividades(dic["ano"], dic["campus"], dic["excluirMarcadores"])
		
		return render_template("adm.html", campus=campus, semSenha=False, anoOcupado=False, dias=[*range(1,32)], meses=calendario, erroEventoNovo=False, excluirGenerico=False, excluirFerias=False, excluirAtividades=False)	
	else:
		return redirect(url_for('home'))