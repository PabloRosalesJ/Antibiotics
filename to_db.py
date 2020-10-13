import csv
from app import db, Antibiotico, Medico 

with open('ANTIBIOTICOS.csv', newline='') as File:  
    reader = csv.reader(File)
    for row in reader:
        
        a = Antibiotico(clave = row[0], nombre = row[1].title(), presentacion = row[2].title
        (), stock = 10)
        db.session.add(a)
        db.session.commit() 
        print(row[2], row[1], row[2])

with open('MEDICOS.csv', newline='') as File:  
    reader = csv.reader(File)
    for row in reader:
        name =  row[0].split()

        m = Medico(nombre = name[0], apellido_paterno = name[1], apellido_materno = name[2], ced_profesional = row[1], rfc = 'RFC to: {}'.format(row[1]) )
        db.session.add(m)
        db.session.commit()

        print(name[0], name[1], name[2])
        print(row[1])


 