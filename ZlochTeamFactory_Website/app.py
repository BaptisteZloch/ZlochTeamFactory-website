from logging import NullHandler
from flask import Flask, render_template, request, redirect, jsonify
import smtplib
import os
import mysql.connector

app = Flask(__name__, static_folder="static")

host = 'lmc8ixkebgaq22lo.chr7pe7iynqr.eu-west-1.rds.amazonaws.com'
username='rfnw78zju18x3b4i'
password ='pmgjyf7r74tvnosc'
database ='bxh5i89l7u1i58td'

mydb = mysql.connector.connect(
    host=host, user=username, password=password, database=database)
cur = mydb.cursor()

app.config['isAuth'] = False


@app.route('/', methods=['GET', 'POST'])
def index():
    cur.execute("Select * from articles order by Date_article desc")
    rows = cur.fetchall()
    tags = {}
    photos = {}
    for row in rows:
        cur.execute(
            F"Select * from tags inner join tags_on_articles on tags.ID_tag=tags_on_articles.ID_tag where tags_on_articles.ID_article={row[0]}")
        article_tag = []
        article_tag = cur.fetchall()
        tags[row[0]] = article_tag
        cur.execute(
        F"Select Adresse_Image from articles inner join photos on photos.ID_article=articles.ID_article WHERE articles.ID_article={row[0]}")
        for photo in cur.fetchall():
            for p in photo:
                photos[row[0]] = p
                break
            break
    return render_template('index.html', articles=rows, tags=tags, photos=photos)


@app.route('/admin', methods=['GET', 'POST'])
def connexion():
    if request.method == 'POST':
        mail = request.form.get('mail')
        mdp = request.form.get('mdp')
        req2 = F"SELECT * FROM `administrateur` WHERE administrateur.mdp_administrateur='{mdp}' AND administrateur.mail_administrateur='{mail}' limit 1"
        cur.execute(req2)
        rows = cur.fetchall()
        if rows is not None:
            app.config['isAuth'] = True
            print(app.config['isAuth'])
        return ""
    else:
        print('in Admin')
        print(app.config['isAuth'])
        cur.execute('Select * from tags')
        tags = cur.fetchall()
        cur.execute('Select * from articles')
        articles = cur.fetchall()
        cur.execute('Select * from realisations')
        realisations = cur.fetchall()
        return render_template('admin.html', isAuth=app.config['isAuth'], tags=tags, articles=articles, realisations=realisations)


@app.route('/NewArticle', methods=['GET'])
def newArticle():
    titre = request.args.get('article_titre')
    contenu = request.args.get('article_texte')
    date = request.args.get('article_date')
    auteur = request.args.get('article_auteur')
    tags = request.args.getlist('tags[]')
    images = request.args.getlist('files[]')
    #print(titre, ' ', contenu, ' ', date, ' ', auteur,' tags : ', tags, ' Images : ', images)
    cur.execute('INSERT INTO Articles VALUES(NULL, %s,%s,%s,%s)',
                [titre, contenu, auteur, date])
    mydb.commit()
    id = cur.lastrowid
    if tags:
        for tag in tags:
            cur.execute(F'INSERT INTO tags_on_articles VALUES({id}, {tag})')
            mydb.commit()
    if images:
        for image in images:
            cur.execute(
                F'INSERT INTO photos VALUES(NULL,"{image}",NULL, {id})')
            mydb.commit()
    return redirect('/admin')


@app.route('/NewRealisation', methods=['GET'])
def NewRealisation():
    titre = request.args.get('titre_rea')
    description = request.args.get('description_rea')
    couleur = request.args.getlist('couleur_rea[]')
    couleurs = ', '.join(couleur)
    dimensions = request.args.get(
        'dim_x')+'x'+request.args.get('dim_y')+'x'+request.args.get('dim_z')
    prix = request.args.get('prix_rea')
    tags = request.args.getlist('tags[]')
    images = request.args.getlist('image_rea[]')
    date = request.args.get('date_rea')
    materiaux = request.args.getlist('materiaux[]')
    matiere = ', '.join(materiaux)
    print(titre, ' ', description, ' ', date, ' ', couleurs, ' ', prix,
          ' ', dimensions, ' ', 'tags : ', tags, ' images : ', images)
    cur.execute('INSERT INTO Realisations VALUES(NULL, %s,%s,%s,%s,%s,%s,%s)',
                [titre, description, couleurs, matiere, dimensions, prix, date])
    mydb.commit()
    id = cur.lastrowid
    if tags:
        for tag in tags:
            cur.execute(F'INSERT INTO tags_on_realisations VALUES({tag},{id})')
            mydb.commit()
    if images:
        for image in images:
            cur.execute(F'INSERT INTO photos VALUES(NULL,"{image}",{id},NULL)')
            mydb.commit()
    if request.files:
        for image_name in images:
            current_image_file = request.files[image_name]
            path = os.path.join('./static', current_image_file.filename)
            print('in saving')
            current_image_file.save(path)
    return redirect('/admin')


@app.route('/upload_image_article', methods=['POST'])
def uploadimage_art():
    # check if the post request has the file part
    if 'files[]' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    files = request.files.getlist('files[]')
    errors = {}
    success = False
    for file in files:
        if file:
            file.save(os.path.join('./static/Articles', file.filename))
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'
    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 206
        return resp
    if success:
        resp = jsonify({'message': 'Files successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 400
        return resp


@app.route('/upload_image_realisation', methods=['POST'])
def uploadimage_rea():
    # check if the post request has the file part
    if 'files_rea[]' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    files = request.files.getlist('files_rea[]')
    errors = {}
    success = False
    for file in files:
        if file:
            file.save(os.path.join('./static/Réalisations', file.filename))
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'
    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 206
        return resp
    if success:
        resp = jsonify({'message': 'Files successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 400
        return resp


@app.route('/SupressionRealisation', methods=['POST'])
def SupprRea():
    cur.execute(
        F'Select photos.adresse_image from photos where photos.ID_article={request.form.get("realisation")}')
    for image in cur.fetchall():
        if os.path.exists(os.path.join('./static/Réalisations/', image[0])):
            os.remove(os.path.join('./static/Réalisations/', image[0]))
    cur.execute(
        F'DELETE FROM realisations WHERE realisations.ID_realisation={request.form.get("realisation")}')
    mydb.commit()
    return redirect('/admin')


@app.route('/SuppressionArticle', methods=['POST'])
def SupprArticle():
    cur.execute(
        F'Select photos.adresse_image from photos where photos.ID_article={request.form.get("article_to_suppr")}')
    for image in cur.fetchall():
        if os.path.exists(os.path.join('./static/Articles/', image[0])):
            os.remove(os.path.join('./static/Articles/', image[0]))
    cur.execute(
        F'DELETE FROM articles WHERE articles.ID_article={request.form.get("article_to_suppr")}')
    mydb.commit()
    return redirect('/admin')


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


@app.route('/tags', methods=['POST', 'GET'])
def Tag_viz():
    print('in the post tag')
    print(request.form.get('tag'))
    return render_template('tags.html')


@app.route('/Message', methods=['GET', 'POST'])
def sendingMessage():
    print(request.form.get('nom'))
    server = smtplib.SMTP_SSL()
    server.connect('smtp.toto.fr')
    server.ehlo()
    server.login('user', 'pass')
    fromaddr = 'bzloch@hotmail.fr'
    toaddrs = request.form.get('email')
    sujet = request.form.get('objet')
    message = F'message de {request.form.get("nom")} {request.form.get("prenom")}\r\n' + \
        request.form.get('mail')
    msg = """\
    From: %s\r\n\
    To: %s\r\n\
    Subject: %s\r\n\
    \r\n\
    %s
    """ % (fromaddr, toaddrs, sujet, message)
    try:
        server.sendmail(fromaddr, toaddrs, msg)
    except smtplib.SMTPException as e:
        print(e)
    server.quit()
    return redirect("/Contact")


@app.route('/Contact')
def contact():
    return render_template('contact.html')


@app.route('/Apropos')
def Apropos():
    return render_template('Apropos.html')


@app.route('/Realisations')
def realisations():
    cur.execute("Select * from realisations")
    realisations = cur.fetchall()
    print(realisations)
    photos = {}
    for row in realisations:
        cur.execute(
            F"Select photos.Adresse_Image from photos inner join Realisations on photos.ID_realisation=Realisations.ID_realisation where photos.ID_realisation={row[0]} limit 1")
        rea_image = []
        rea_image = cur.fetchall()
        print(rea_image[0][0])
        for photo in rea_image:
            for p in photo:
                photos[row[0]] = p
                break
            break
    print(photos)
    return render_template("realisations.html", rows=realisations, photos=photos)


@app.route('/Realisations/<int:realisation_id>', methods=['GET'])
def realisation(realisation_id):
    fields = ["ID_realisation", "Titre_realisation",
              "Description_realisation", "Couleur", "Matiere", "Dimensions", "Prix"]
    cur.execute(
        F"Select realisations.ID_realisation,Titre_realisation,Description_realisation,Couleur,Matiere,Dimensions,Prix from realisations WHERE realisations.ID_realisation={realisation_id}")
    realisation = dict(zip(fields, cur.fetchall()[0]))

    cur.execute(
        F"Select Adresse_Image from realisations inner join photos on photos.ID_realisation=realisations.ID_realisation WHERE realisations.ID_realisation={realisation_id}")
    photos = cur.fetchall()
    list_of_photos = []
    for photo in photos:
        list_of_photos.append(str(photo[0]))
    realisation['Photos'] = list_of_photos

    cur.execute(
        F"Select Tags.Tag from Tags INNER JOIN tags_on_realisations ON Tags.ID_tag=tags_on_realisations.ID_tag  WHERE tags_on_realisations.ID_realisation={realisation_id}")
    tags = cur.fetchall()
    list_of_tags = []
    for tag in tags:
        list_of_tags.append(str(tag[0]))
    realisation['Tags'] = list_of_tags
    print(realisation)
    return render_template("realisation.html", realisation=realisation)


@app.route('/Articles/<int:article_id>', methods=['GET'])
def article_unitaire(article_id):
    fields = [
        "ID_article",
        "Titre_article",
        "Texte_article",
        "Auteur_article",
        "Date_article",
    ]
    cur.execute(
        F"Select * from articles WHERE articles.ID_article={article_id}")
    article = dict(zip(fields, cur.fetchall()[0]))
    cur.execute(
        F"Select Adresse_Image from articles inner join photos on photos.ID_article=articles.ID_article WHERE articles.ID_article={article_id}")
    photos = cur.fetchall()
    print(photos)
    list_of_photos = []
    for photo in photos:
        list_of_photos.append(str(photo[0]))
    article['Photos'] = list_of_photos

    cur.execute(
        F"Select Tags.Tag from Tags INNER JOIN tags_on_articles ON Tags.ID_tag=tags_on_articles.ID_tag  WHERE tags_on_articles.ID_article={article_id}")
    tags = cur.fetchall()
    list_of_tags = []
    for tag in tags:
        list_of_tags.append(str(tag[0]))
    article['Tags'] = list_of_tags
    print(article)
    return render_template("article.html", article=article)


@app.route('/Techniques/Laser')
def Laser():
    return render_template('Techniques/Laser.html')


@app.route('/Techniques/CNC')
def CNC():
    return render_template('Techniques/CNC.html')


@app.route('/Techniques/Impression3D')
def Printing3D():
    return render_template('Techniques/Impression3D.html')


if __name__ == '__main__':
    app.run(debug=True)
