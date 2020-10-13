from flask import Flask, Request, render_template, request, url_for, redirect, flash
from flask_wtf import CsrfProtect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from models import db, Antibiotico, Medico, Receta
 

app = Flask(__name__)
app.secret_key = '32e453c7329326c419e8a5748e9e828fe90337e9dd56f125'
csrf = CsrfProtect(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/db.db'

db = SQLAlchemy(app)

# Parametros
min_stock = 10
max_stock = 100
months = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]

class Antibiotico(db.Model):
    __tablename__ = 'antibioticos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clave = db.Column(db.String(12), unique = True, nullable = False)
    nombre = db.Column(db.String(120), nullable = False)
    receta = db.relationship('Receta')
    presentacion = db.Column(db.String(120), nullable = False)
    stock = db.Column(db.Integer, nullable = False)
    

class Medico(db.Model):
    __tablename__ = 'medicos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ced_profesional = db.Column(db.String(12), unique = True, nullable = False)
    nombre = db.Column(db.String(80), nullable = False)
    apellido_paterno = db.Column(db.String(80), nullable = False)
    apellido_materno = db.Column(db.String(80), nullable = False)
    receta = db.relationship('Receta')
    rfc = db.Column(db.String(30), unique = True)


class Receta(db.Model):
    __tablename__ = 'recetas'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    folio = db.Column(db.String(10), unique = True, nullable = False)
    clave_antibiotico = db.Column(db.Integer, db.ForeignKey('antibioticos.clave'))
    piezas = db.Column(db.Integer, nullable = False)
    consecutivo = db.Column(db.Integer, nullable=False, default = 1)
    medico = db.Column(db.Integer, db.ForeignKey('medicos.id'))
    pasiente = db.Column(db.String(80), nullable = False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    stock_actual = db.Column(db.Integer )
    piezas_entrada = db.Column(db.Integer )
    fecha_entrada = db.Column(db.DateTime)#, nullable=False, default=datetime.utcnow)


def crear_fecha(date):
    temp_f = date[2:]
    fecha = datetime.strptime(temp_f, '%y-%m-%d')
    return fecha

@app.route('/')
def home():
    doctors = Medico.query.all()
    
    antibiotics = Antibiotico.query.all()
    total = ''
    for a in antibiotics:
        if a.stock < min_stock:
            total += ' {}, '.format(a.clave)
    mess = 'nesecitamos mas piezas de {}'.format(total)
    flash(mess)
    antibioticos = Antibiotico.query.order_by("clave")
    del(antibiotics)
    return render_template('home.html', antibioticos = antibioticos, doctors = doctors, antibiotics = antibioticos, min_stock = min_stock)

@app.route('/new_antibiotic', methods=['POST'])
def new_antibiotic():
    clave = request.form['clave']
    nombre  = request.form['nombre'].title()
    presentacion  = request.form['presentacion'].title()
    stock = request.form['stock']
    
    a = Antibiotico(clave = clave, nombre = nombre, presentacion = presentacion, stock = stock)
    db.session.add(a)
    db.session.commit()
    mess = 'Se ha agregado {} a la lista de antibioticos'.format(nombre)
    flash(mess)
    return redirect(url_for('home'))

@app.route('/delete_antbiotic/<id>')
def delete_antbiotic(id):
    a = Antibiotico.query.filter_by(id = id).first()
    clave = a.clave
    nombre = a.nombre
    Antibiotico.query.filter_by(id  = int(id)).delete()
    db.session.commit()     
    mess = 'Se ha eliminado el antibiotico {} {} de la lista'.format(clave, nombre)
    flash(mess)
    return redirect(url_for('home'))

@app.route('/new_medico', methods = ['POST'])
def new_medico():
    nombre = request.form['nombre'].title()
    ap_pat = request.form['ap_pat'].title()
    ap_mat = request.form['ap_mat'].title()
    ced_prof = request.form['ced_prof'].upper()
    rfc = request.form['rfc'].upper()
    

    m = Medico(nombre = nombre, 
               apellido_paterno = ap_pat, 
               apellido_materno = ap_mat,
               ced_profesional = ced_prof,
               rfc = rfc
               )
    db.session.add(m)
    db.session.commit()
    mess = 'Se ha guardado a {} como un nuevo medico'.format(nombre)
    flash(mess)
    return redirect(url_for('home'))

@app.route('/medicos')
def all_doctors():
    doctors = Medico.query.all()
    size = len(doctors)
    return render_template('all_doctors.html', doctors = doctors, size = size)

@app.route('/delete/<id>')
def delete_doctor(id):
    m = Medico.query.filter_by(id = int(id)).first()
    nombre = m.nombre
    Medico.query.filter_by(id = int(id)).delete()
    db.session.commit()
    mess = 'Se ha eliminado a {} de la lista de medicos'.format(nombre)
    flash(mess)
    return redirect(url_for('all_doctors')) 

@app.route('/new_receta', methods = ['POST'])
def new_receta():
    medico = request.form['medico']
    folio = request.form['folio'].upper()
    clave = request.form['clave'] 
    piezas = request.form['piezas'] 
    piezas = int(piezas)
    nombre_paciente = request.form['nombre_paciente'].title()
    fecha_v = None    
    if request.form['fecha']:
        date = request.form['fecha']
        fecha_v = crear_fecha(date)

    # db.session.query(re).order_by(re.id.desc()).first() 
    in_list = []
    re = Receta.query.all() 
    if Receta.query.all() == []:
        cnsctvo = 1
        del(in_list)
        del(re)
    else:
        for r in re:
            in_list.append(r.clave_antibiotico)
    if int(clave) in in_list:
        re = Receta.query.filter_by(clave_antibiotico = clave) 
        cons = []
        for r in re:
            cons.append(r.consecutivo)
        cnsctvo = cons[-1] + 1
        del(cons)
    else:
        cnsctvo = 1                          

    a = Antibiotico.query.filter_by(clave = clave).first() 
    stock = int(a.stock) - piezas
    if stock <= 0:
        mess = 'no cuentas con las piezas suficientes'
        flash(mess)
        return redirect(url_for('home'))
    r = Receta(folio = folio, clave_antibiotico = clave, piezas = piezas, medico = medico, 
    pasiente = nombre_paciente, fecha = fecha_v, consecutivo = cnsctvo, stock_actual = stock)   
    db.session.add(r)
    db.session.commit()
    
    new_stock = int(a.stock) - piezas
    a.stock = new_stock
    db.session.add(a)
    db.session.commit()

    mess = 'Se ha añadido con exito una nueva receta con folio {}'.format(folio)
    flash(mess)

    return redirect(url_for('home'))

@app.route('/detalles', methods = ['POST'])
def detalles():
    clave = request.form['auditar_clave']

    a = Antibiotico.query.filter_by(clave = clave).first()
    recetas = Receta.query.filter_by(clave_antibiotico = clave)
    #ref = db.session.query(Medico, Receta).join(Receta).filter_by(clave_antibiotico = 2127)
    # return clave
    # a = db.session.query(Antibiotico).order_by(Antibiotico.id.desc()).first()
    return render_template('detalles.html', recetas = recetas, a = a, months = months)
    

if __name__ == '__main__':
    app.run(debug=True)
