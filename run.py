# -*- coding: utf-8 -*- 
from flaskapp import app

# módulo para teste que sairá apenas em local mode, no port 5000, sendo acessável através de uma página web com localhost:5000 de url
if __name__ == '__main__':
	app.run(debug=True)

"""
#Para colocar em produção ative esse módulo, NÃO é recomendado o port 80, se você souber mexer com firewall
# para redirecionar para outro port a mudança deve ser feita no parâmetro 'port'
if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80, debug=True)
"""



