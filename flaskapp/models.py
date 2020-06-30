from flaskapp import db

class Campi(db.Model):
	cidade = db.Column(db.String(20), primary_key=True)
	senha = db.Column(db.String(20), nullable=False)
	email = db.Column(db.String(120))
	ferias = db.relationship('Ferias', backref='campus1', lazy=True)
	atividades = db.relationship('Atividades', backref='campus2', lazy=True)
	tecnico = db.relationship('Tecnico', backref='campus3', lazy=True)
	calem = db.relationship('Calem', backref='campus4', lazy=True)
	graduacao = db.relationship('Graduacao', backref='campus5', lazy=True)

	def __repr__(self):
		return f"{self.cidade}"

class Tecnico(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	tabela1 = db.Column(db.Text)
	tabela2 = db.Column(db.Text)
	atividades = db.relationship('Eventos', backref='tecnico', lazy=True)
	cidade_id = db.Column(db.String(20), db.ForeignKey('campi.cidade'))
	dias = db.relationship('Letivos', backref='grad3', lazy=True)

	def __repr__(self):
		return f"{self.id}"


class Calem(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	tabela1 = db.Column(db.Text)
	tabela2 = db.Column(db.Text)
	atividades = db.relationship('Eventos', backref='calem', lazy=True)
	cidade_id = db.Column(db.String(20), db.ForeignKey('campi.cidade'))
	dias = db.relationship('Letivos', backref='grad2', lazy=True)
	def __repr__(self):
		return f"{self.id}"

class Graduacao(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	tabela1 = db.Column(db.Text)
	tabela2 = db.Column(db.Text)
	atividades = db.relationship('Eventos', backref='graduacao', lazy=True)
	cidade_id = db.Column(db.String(20), db.ForeignKey('campi.cidade'))
	dias = db.relationship('Letivos', backref='grad1', lazy=True)

	def __repr__(self):
		return f"{self.id}"

class Eventos(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	dia = db.Column(db.Integer, nullable=False)
	mes = db.Column(db.Integer, nullable=False)
	comentario = db.Column(db.Text, nullable=False)
	tecnico_id = db.Column(db.Integer, db.ForeignKey('tecnico.id'))
	calem_id = db.Column(db.Integer, db.ForeignKey('calem.id'))
	graduacao_id = db.Column(db.Integer, db.ForeignKey('graduacao.id'))
	ano = db.Column(db.Integer, nullable=False)
	flag = db.Column(db.Boolean, nullable=False)

	def __repr__(self):
		return r"\textbf{%.2d}\qquad %s \newline" %(self.dia, self.comentario)

	def __lt__(self, outro):
		if self.mes == outro.mes:
			return self.dia < outro.dia
		else:
			return self.mes < outro.mes

class Letivos(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	dia = db.Column(db.Integer, nullable=False)
	mes = db.Column(db.Integer, nullable=False)
	tecnico_id = db.Column(db.Integer, db.ForeignKey('tecnico.id'))
	calem_id = db.Column(db.Integer, db.ForeignKey('calem.id'))
	graduacao_id = db.Column(db.Integer, db.ForeignKey('graduacao.id'))
	ano = db.Column(db.Integer, nullable=False)

	def __repr__(self):
		return f"{self.id}"

	def __lt__(self, outro):
		if self.mes == outro.mes:
			return self.dia < outro.dia
		else:
			return self.mes < outro.mes


class Atividades(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	dia_inicio = db.Column(db.Integer, nullable=False)
	dia_final = db.Column(db.Integer,nullable=False)
	mes = db.Column(db.Integer, nullable=False)
	comentario = db.Column(db.Text, nullable=False)
	cidade_id = db.Column(db.String(20), db.ForeignKey('campi.cidade'))
	ano = db.Column(db.Integer, nullable=False)
	flag = db.Column(db.Boolean, nullable=False)

	def __repr__(self):
		if self.dia_final <= self.dia_inicio:
			return r"\textbf{%.2d}\quad \quad \quad \quad %s \newline" %(self.dia_inicio, self.comentario)
		else:
			return r"\textbf{%.2d a %.2d}\quad \quad %s \newline" %(self.dia_inicio, self.dia_final, self.comentario)

	def __lt__(self, outro):
		if self.mes == outro.mes:
			return self.dia_inicio < outro.dia_inicio
		else:
			return self.mes < outro.mes

class Ferias(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	dia = db.Column(db.Text, nullable=False)
	mes = db.Column(db.Integer, nullable=False)
	comentario = db.Column(db.Text, nullable=False)
	cidade_id = db.Column(db.String(20), db.ForeignKey('campi.cidade'))
	ano = db.Column(db.Integer, nullable=False)
	flag = db.Column(db.Boolean, nullable=False)

	def __repr__(self):
		if len(self.dia) < 4:
			return r"\textbf{%s}\quad \quad \quad \quad %s \newline" %(self.dia, self.comentario)
		else:
			return r"\textbf{%s}\quad \quad %s \newline" %(self.dia, self.comentario)

	def __lt__(self, outro):
		if self.mes == outro.mes:
			only_nm = self.dia[0:2].strip()
			outer_nm = outro.dia[0:2].strip()
			return only_nm < outer_nm
		else:
			return self.mes < outro.mes
