import eventlet
eventlet.monkey_patch()

import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Patient, Medecin,Diagnostic,Commentaire,ReponseCommentaire,Consultation
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager,current_user, login_required, UserMixin, login_user, login_required, logout_user
from flask_login import login_user, logout_user
from flask import Flask, render_template, Response,current_app
import serial, time
import cv2
import numpy as np
import json
import serial.tools.list_ports
from flask_socketio import SocketIO, emit
# Initialisation de la base de données et de Flask-Login

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads/photos'
app.config['UPLOAD_FOLDER_videos'] = 'static/uploads/videos'
app.config['UPLOAD_FOLDER_files'] = 'static/uploads/document'

app.secret_key = 'votre_cle_secrete'
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
#socketio = SocketIO(app)
socketio = SocketIO(app, async_mode='eventlet')

@login_manager.user_loader
def load_user(user_id):
    patient = Patient.query.get(user_id)
    if patient:
        return patient
    medecin = Medecin.query.get(user_id)
    return medecin  # Cela retourne le médecin si l'utilisateur n'est pas un patient

# Route d'accueil
@app.route('/')
def indexe():
    print("Accès à la route d'accueil")

    return render_template('indexe.html')
@app.route('/home')
def home():
    print("Accès à la route d'authetification")

    return render_template('home.html')

# Liste des villes marocaines
villes_maroc = [
    'Casablanca', 'Rabat', 'Marrakech', 'Fès', 'Tanger', 'Agadir',
    'Oujda', 'Meknès', 'Kenitra', 'Tétouan', 'Safi', 'El Jadida',
    'Beni Mellal', 'Kénitra', 'Laâyoune', 'Dakhla', 'Settat',
    'Salé', 'Nador', 'Berrechid', 'Taroudant', 'Ksar es Souk',
    'Mohammedia', 'Sidi Kacem', 'El Hoceïma', 'Tiznit', 'Tinghir'
]

# Route d'enregistrement patient
@app.route('/register/patient', methods=['GET', 'POST'])
def register_patient():
    villes = villes_maroc  # Liste des villes

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        cin = request.form['cin']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        ville = request.form['ville']  # Champ pour la ville
        medecin_id = request.form['medecin']  # ID du médecin choisi
        photo = request.files['photo']

        # Vérification des champs requis
        if not all([first_name, last_name, cin, email, username, password, ville, medecin_id, photo]):
            flash("Tous les champs sont requis !")
            return redirect(url_for('register_patient'))

        # Sauvegarder la photo
        photo_filename = secure_filename(f"{username}.jpg")
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        # Créer le patient
        new_patient = Patient(
            first_name=first_name,
            last_name=last_name,
            cin=cin,
            email=email,
            username=username,
            password=generate_password_hash(password),  # Hash du mot de passe
            photo=photo_filename,
            ville=ville,  # Associer la ville
            medecin_id=medecin_id  # Lier le médecin choisi
        )
        db.session.add(new_patient)
        db.session.commit()

        flash("Patient enregistré avec succès !")
        return redirect(url_for('home'))

    return render_template('register_patient.html', villes=villes)

@app.route('/register/medecin', methods=['GET', 'POST'])
def register_medecin():
    # Liste des spécialités
    specialites = ['Cardiologie', 'Dermatologie', 'Neurologie', 'Oncologie']

    # Liste des villes au Maroc
    villes = villes_maroc  # Utilisation de la liste des villes

    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        cin = request.form['cin']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        specialite = request.form['specialite']  # Sélection de la spécialité
        adresse = request.form['adresse']  # Nouveau champ pour l'adresse
        ville = request.form['ville']  # Nouveau champ pour la ville
        photo = request.files['photo']  # Sauvegarde de la photo

        # Vérification des champs requis
        if not all([first_name, last_name, cin, email, username, password, specialite, adresse, ville, photo]):
            flash("Tous les champs sont requis !")
            return redirect(url_for('register_medecin'))

        # Sauvegarder la photo
        photo_filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

        # Enregistrement dans la base de données
        new_medecin = Medecin(
            first_name=first_name,
            last_name=last_name,
            cin=cin,
            email=email,
            username=username,
            password=generate_password_hash(password),  # Hash du mot de passe
            specialite=specialite,
            photo=photo_filename,
            adresse=adresse,  # Adresse du médecin
            ville=ville  # Ville du médecin
        )
        db.session.add(new_medecin)
        db.session.commit()

        flash('Médecin enregistré avec succès !')
        return redirect(url_for('home'))

    return render_template('register_medecin.html', villes=villes, specialites=specialites)

@app.route('/get_medecins', methods=['GET'])
def get_medecins():
    ville = request.args.get('ville')
    medecins = Medecin.query.filter_by(ville=ville).all()
    return [{'id': m.id, 'first_name': m.first_name, 'last_name': m.last_name, 'specialite': m.specialite} for m in medecins]

@app.route('/login/patient', methods=['GET', 'POST'])
def login_patient():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Rechercher le patient dans la base de données
        patient = Patient.query.filter_by(username=username).first()

        # Vérifier si le patient existe et le mot de passe est correct
        if patient and check_password_hash(patient.password, password):
            # Stocker l'ID du patient dans la session
            session['patient_id'] = patient.id
            return redirect(url_for('dashboard_patient'))  # Redirection vers le tableau de bord
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.")

    return render_template('login_patient.html')

@app.route('/login/medecin', methods=['GET', 'POST'])
def login_medecin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        medecin = Medecin.query.filter_by(username=username).first()

        if medecin and check_password_hash(medecin.password, password):
            session['medecin_id'] = medecin.id  # Stocker l'ID du médecin dans la session
            print(f"ID du médecin connecté :{medecin.id}")
            return redirect(url_for('dashboard_medecin'))  # Rediriger vers le tableau de bord du médecin
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect.")

    return render_template('login_medecin.html')

@app.route('/send_comment/<int:diagnostic_id>', methods=['POST'])
@login_required
def send_comment(diagnostic_id):
    comment_text = request.form.get('comment')
    file = request.files.get('file')

    # Assurez-vous d'avoir un diagnostic
    diagnostic = Diagnostic.query.get(diagnostic_id)
    if diagnostic is None:
        flash('Diagnostic non trouvé.')
        return redirect(url_for('dashboard_medecin'))  # Redirigez vers le tableau de bord du médecin

    # Si un fichier est uploadé, sauvegardez-le
    file_path = None
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER_files'], filename)
        file.save(file_path)

    # Créez un nouveau commentaire
    new_comment = Commentaire(
        text=comment_text,
        file=file_path,
        diagnostic_id=diagnostic.id,
        medecin_id=current_user.id,  # Utiliser l'ID du médecin connecté
        patient_id=diagnostic.patient_id  # Associer le patient du diagnostic
    )
    db.session.add(new_comment)
    db.session.commit()

    flash('Commentaire envoyé avec succès.')
    return redirect(url_for('dashboard_medecin'))  # Redirigez vers le tableau de bord du médecin

@app.route('/dashboard/patient')
def dashboard_patient():
    patient_id = session.get('patient_id')
    if not patient_id:
        return redirect(url_for('login_patient'))  # Rediriger vers la page de connexion si non connecté

    patient = Patient.query.get(patient_id)
    # Récupérer les diagnostics pour le patient
    patient.diagnostics = Diagnostic.query.filter_by(patient_id=patient_id).all()
    # Récupérer les commentaires associés au patient
    comments = Commentaire.query.filter_by(patient_id=patient_id).all()

    # Pour chaque diagnostic, récupérer les commentaires associés
    for diagnostic in patient.diagnostics:
        diagnostic.commentaires = Commentaire.query.filter_by(diagnostic_id=diagnostic.id).all()

    return render_template('dashboard_patient.html', patient=patient, comments=comments)  # Afficher le tableau de bord du patient

@app.route('/dashboard/medecin')
def dashboard_medecin():
    medecin_id = session.get('medecin_id')  # Vérifiez que vous récupérez l'ID du médecin connecté
    if not medecin_id:
        return redirect(url_for('login'))  # Rediriger si le médecin n'est pas connecté

    medecin = Medecin.query.get(medecin_id)
    patients = Patient.query.filter_by(medecin_id=medecin_id).all()

    for patient in patients:
        patient.diagnostics = Diagnostic.query.filter_by(patient_id=patient.id).all()
        patient.diagnostics = Diagnostic.query.filter_by(patient_id=patient.id).all()
        for diagnostic in patient.diagnostics:
            diagnostic.commentaires = Commentaire.query.filter_by(diagnostic_id=diagnostic.id).all()

    return render_template('dashboard_medecin.html', medecin=medecin, patients=patients)

def send_to_medecin(diagnostic_id):
    comment = request.form.get('comment')
    # Logique pour envoyer le diagnostic et le commentaire au médecin
    flash('Diagnostic et commentaire envoyés au médecin avec succès !', 'info')
    return redirect(url_for('dashboard_patient'))

def add_diagnostic(patient_id, file_path, diagnostic_type):
    new_diagnostic = Diagnostic(type=diagnostic_type, date=datetime.utcnow(), file=file_path, patient_id=patient_id)
    db.session.add(new_diagnostic)
    db.session.commit()


@app.route('/upload_file/<int:patient_id>', methods=['POST'])
def upload_file(patient_id):
    # Vérification de l'existence du fichier
    if 'file' not in request.files:
        flash('Aucun fichier sélectionné.')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('Aucun fichier sélectionné.')
        return redirect(request.url)

    # Récupération du type de document
    document_type = request.form['document_type']
    other_type = request.form.get('other_type', '')  # Récupérer le type s'il est spécifié
    if document_type == 'Autre' and other_type:
        document_type = other_type  # Si l'utilisateur a spécifié un autre type, on l'utilise

    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER_files'], filename))

    # Créer un nouveau diagnostic
    add_diagnostic(patient_id, filename, document_type)  # Passer le type de document ici

    flash('Fichier téléchargé avec succès.')
    return redirect(url_for('dashboard_patient', patient_id=patient_id))

@app.route('/logout')
def logout():
    session.pop('patient_id', None)  # Déconnexion du patient
    session.pop('medecin_id', None)  # Déconnexion du médecin
    return redirect(url_for('home'))

@app.route('/comment_diagnostic/<int:patient_id>/<int:diagnostic_id>', methods=['POST'])
def comment_diagnostic(patient_id, diagnostic_id):
    commentaire_text = request.form['comment']
    fichier = request.files.get('file')

    nouveau_commentaire = Commentaire(text=commentaire_text, diagnostic_id=diagnostic_id, medecin_id=session.get('medecin_id'))

    if fichier:
        # Gérer le téléchargement de fichier
        filename = secure_filename(fichier.filename)
        fichier.save(os.path.join(app.config['UPLOAD_FOLDER_files'], filename))
        nouveau_commentaire.file = filename

    db.session.add(nouveau_commentaire)
    db.session.commit()

    flash('Commentaire ajouté avec succès.')
    return redirect(url_for('dashboard_medecin'))

@app.route('/commentaire/<int:commentaire_id>/repondre', methods=['POST'])
def repondre_commentaire(commentaire_id):

    print(session)  # Imprimer la session pour débogage
    # Vérifiez que l'utilisateur est connecté
    if 'patient_id' not in session:
        flash("Vous devez être connecté pour répondre.")
        return redirect(url_for('login_patient'))

    texte_reponse = request.form.get('contenu')

    # Vérifiez que la réponse n'est pas vide
    if not texte_reponse:
        flash("La réponse ne peut pas être vide !")
        return redirect(url_for('dashboard_patient'))

    # Créer une nouvelle réponse de commentaire
    reponse = ReponseCommentaire(
        contenu=texte_reponse,
        patient_id=session['patient_id'],  # Utiliser l'ID du patient
        commentaire_id=commentaire_id  # Lier au commentaire d'origine
    )

    db.session.add(reponse)
    db.session.commit()

    flash("Réponse envoyée avec succès !")
    return redirect(url_for('dashboard_patient'))

##############################################################################
#################################Consultation En ligne#############################


# Paramètres globaux
n = 128
sensor_values = [[0] * n for p in range(n)]
r = [[0] * n for p in range(n)]
g = [[0] * n for p in range(n)]
b = [[0] * n for p in range(n)]

minimum = 18
maximum = 28
img = np.zeros((800, 1700, 3), np.uint8)
img[:] = (240, 180, 203)

import serial.tools.list_ports

@app.route('/available_ports', methods=['GET'])
def available_ports():
    """Retourne la liste des ports série disponibles."""
    ports = serial.tools.list_ports.comports()
    port_list = [port.device for port in ports]
    return {'ports': port_list}

@app.route('/api/ports', methods=['GET'])
def get_ports():
    ports = [port.device for port in serial.tools.list_ports.comports()]
    return jsonify(ports)

@app.route('/api/connect', methods=['POST'])
def connect_port():
    global ser  # Utilisez la variable globale pour le port série
    sensor_values = request.json
    port = sensor_values.get('port')
    patient_id = sensor_values.get('patient_id')

    if not port or not patient_id:
        return jsonify({"error": "Le port et l'ID du patient sont requis."}), 400

    try:
        # Vérifiez si l'ID du patient est un entier
        patient_id = int(patient_id)

        # Vérifiez si le patient existe dans la base de données
        patient = db.session.get(Patient, patient_id)
        if not patient:
            return jsonify({"error": "Aucun patient trouvé avec cet ID."}), 404

        # Ouvrir le port série
        ser = serial.Serial(port, 9600, timeout=1)

        # Lancer la fonction pour générer l'image thermique
        generate_thermal_image(patient_id, ser)

        return jsonify({"message": f"Connecté à {port}."}), 200
    except ValueError:
        return jsonify({"error": "L'ID du patient doit être un nombre valide."}), 400
    except serial.SerialException as e:
        return jsonify({"error": f"Erreur de port série : {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def rgb(minimum, maximum, value):
    minimum, maximum, value = float(minimum), float(maximum), float(value)
    ratio = 2 * (value - minimum) / (maximum - minimum)
    b1 = int(max(0, 255 * (1 - ratio)))
    r1 = int(max(0, 255 * (ratio - 1)))
    g1 = 255 - b1 - r1
    return r1, g1, b1

def close_serial_connection(ser):
    if ser and ser.is_open:
        ser.close()

def generate_thermal_image(patient_id, ser):
    # Fetch the patient using the new method
    patient = db.session.get(Patient, patient_id)
    if not patient:
        # Handle the case where the patient doesn't exist
        raise ValueError(f"No patient found with id {patient_id}")
    try:
        while True:
                # Lire une ligne du port série
                line = ser.readline().decode('utf-8')
                # Split la ligne en valeurs séparées par des virgules
                line = line.split(',')

                # Vérifier que nous avons au moins 32 valeurs
                if len(line) >= 32:
                    # Nettoyer les valeurs et les convertir en int
                    line = [x.strip() for x in line]  # Utiliser float ici

                    for i in range(32):
                        sensor_values[i] = line[i]
                        sensor_values[i + 32] = line[i + 32]
                        sensor_values[i + 64] = line[i + 64]
                        sensor_values[i + 96] = line[i + 96]
                    for i in range(32):
                        (r[i], g[i], b[i]) = rgb(minimum, maximum, sensor_values[i])
                        (r[i + 32], g[i + 32], b[i + 32]) = rgb(minimum, maximum, sensor_values[i + 32])
                        (r[i + 64], g[i + 64], b[i + 64]) = rgb(minimum, maximum, sensor_values[i + 64])
                        (r[i + 96], g[i + 96], b[i + 96]) = rgb(minimum, maximum, sensor_values[i + 96])

                    print(sensor_values)
                    # Save data in the database
                    new_diagnostic_record = Diagnostic(
                        patient_id=patient.id,
                        sensor_data=sensor_values
                    )
                    db.session.add(new_diagnostic_record)
                    db.session.commit()  # N'oubliez pas de valider la transaction

                    print(f"Valeurs des capteurs : {sensor_values}")
                    socketio.emit('sensor_data', {'data': sensor_values})

                else:
                    print("Les données reçues ne contiennent pas assez de valeurs.")
                time.sleep(1)
    except KeyboardInterrupt:
        print("Arrêt du programme par l'utilisateur.")
    finally:
        close_serial_connection(ser)


        #############################################
        #       Le Sein droit     #
        #############################################

        #############################################################
        #                 Le 1er Quadrant Sup_droit                 #
        #############################################################

                                 ## 1 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (350, 350), 0, 0, -11.25, (b[2], g[2], r[2]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, -11.25, -22.5, (b[0], g[0], r[0]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, -22.5, -33.75, (b[3], g[3], r[3]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, -33.75, -45, (b[16], g[16], r[16]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, -45, -56.25, (b[29], g[29], r[29]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, -56.25, -67.5, (b[31], g[31], r[31]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, -67.5, -78.75, (b[28], g[28], r[28]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, -78.75, -90, (b[30], g[30], r[30]), -1)
                                 ## 2 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (290, 290), 0, 0, -11.25, (b[1], g[1], r[1]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, -11.25, -22.5, (b[7], g[7], r[7]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, -22.5, -33.75, (b[5], g[5], r[5]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, -33.75, -45, (b[6], g[6], r[6]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, -45, -56.25, (b[4], g[4], r[4]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, -56.25, -67.5, (b[17], g[17], r[17]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, -67.5, -78.75, (b[25], g[25], r[25]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, -78.75, -90, (b[24], g[24], r[24]), -1)
                                ## 3 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (230, 230), 0, 0, -12.85714286, (b[8], g[8], r[8]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, -12.85714286, -25.71428571, (b[10], g[10], r[10]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, -25.71428571, -38.57142857, (b[9], g[9], r[9]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, -38.57142857, -51.42857143, (b[20], g[20], r[20]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, -51.42857143, -64.28571429, (b[21], g[21], r[21]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, -64.28571429, -77.14285715, (b[22], g[22], r[22]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, -77.14285715, -90, (b[23], g[23], r[23]), -1)
                                 ## 4 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (170, 170), 0, 0, -18, (b[11], g[11], r[11]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 0, -18, -36, (b[18], g[18], r[18]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 0, -36, -54, (b[19], g[19], r[19]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 0, -54, -72, (b[15], g[15], r[15]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 0, -72, -90, (b[14], g[14], r[14]), -1)
                                ## 5 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (110, 110), 0, 0, -30, (b[27], g[27], r[27]), -1)
        cv2.ellipse(img, (350, 350), (110, 110), 0, -30, -60, (b[12], g[12], r[12]), -1)
        cv2.ellipse(img, (350, 350), (110, 110), 0, -60, -90, (b[13], g[13], r[13]), -1)
                                ## 6 Cercle rjouté  ##
        cv2.ellipse(img, (350, 350), (50, 50), 0, 0, -90, (b[26], g[26], r[26]), -1)

            #############################################################
            #                 Le 2eme Quadrant Inf_droit                #
            #############################################################

                            ## 1 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (350, 350), 0, 0, 11.25, (b[62], g[62], r[62]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, 11.25, 22.5, (b[60], g[60], r[60]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, 22.5, 33.75, (b[63], g[63], r[63]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, 33.75, 45, (b[61], g[61], r[61]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, 45, 56.25, (b[48], g[48], r[48]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, 56.25, 67.5, (b[35], g[35], r[35]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, 67.5, 78.75, (b[32], g[32], r[32]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 0, 78.75, 90, (b[34], g[34], r[34]), -1)

                            ## 2 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (290, 290), 0, 0, 11.25, (b[56], g[56], r[56]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, 11.25, 22.5, (b[57], g[57], r[57]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, 22.5, 33.75, (b[49], g[49], r[49]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, 33.75, 45, (b[36], g[36], r[36]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, 45, 56.25, (b[38], g[38], r[38]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, 56.25, 67.5, (b[37], g[37], r[37]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, 67.5, 78.75, (b[39], g[39], r[39]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 0, 78.75, 90, (b[33], g[33], r[33]), -1)
                              ## 3 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (230, 230), 0, 0, 12.85714286, (b[55], g[55], r[55]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, 12.85714286, 25.71428571, (b[54], g[54], r[54]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, 25.71428571, 38.57142857, (b[53], g[53], r[53]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, 38.57142857, 51.42857143, (b[52], g[52], r[52]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, 51.42857143, 64.28571429, (b[41], g[41], r[41]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, 64.28571429, 77.14285715, (b[42], g[42], r[42]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 0, 77.14285715, 90, (b[40], g[40], r[40]), -1)
                             ## 4 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (170, 170), 0, 0, 18, (b[46], g[46], r[46]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 0, 18, 36, (b[47], g[47], r[47]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 0, 36, 54, (b[51], g[51], r[51]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 0, 54, 72, (b[50], g[50], r[50]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 0, 72, 90, (b[43], g[43], r[43]), -1)
                              ## 5 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (110, 110), 0, 0, 30, (b[45], g[45], r[45]), -1)
        cv2.ellipse(img, (350, 350), (110, 110), 0, 30, 60, (b[44], g[44], r[44]), -1)
        cv2.ellipse(img, (350, 350), (110, 110), 0, 60, 90, (b[59], g[59], r[59]), -1)
                            ## 6 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (50, 50), 0, 0, 90, (b[58], g[58], r[58]), -1)
                        #############################################################
                        #                 Le 3eme Quadrant Sup_gauche               #
                        #############################################################

                                     ## 1 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (350, 350), -90, 0, -11.25, (b[98], g[98], r[98]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), -90, -11.25, -22.5, (b[96], g[96], r[96]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), -90, -22.5, -33.75, (b[99], g[99], r[99]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), -90, -33.75, -45, (b[112], g[112], r[112]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), -90, -45, -56.25, (b[125], g[125], r[125]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), -90, -56.25, -67.5, (b[127], g[127], r[127]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), -90, -67.5, -78.75, (b[124], g[124], r[124]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), -90, -78.75, -90, (b[126], g[126], r[126]), -1)
                                                ## 2 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (290, 290), -90, 0, -11.25, (b[97], g[97], r[97]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), -90, -11.25, -22.5, (b[103], g[103], r[103]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), -90, -22.5, -33.75, (b[101], g[101], r[101]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), -90, -33.75, -45, (b[102], g[102], r[102]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), -90, -45, -56.25, (b[100], g[100], r[100]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), -90, -56.25, -67.5, (b[113], g[113], r[113]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), -90, -67.5, -78.75, (b[121], g[121], r[121]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), -90, -78.75, -90, (b[120], g[120], r[120]), -1)

                                             ## 3 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (230, 230), -90, 0, -12.85714286, (b[104], g[104], r[104]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), -90, -12.85714286, -25.71428571, (b[106], g[106], r[106]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), -90, -25.71428571, -38.57142857, (b[105], g[105], r[105]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), -90, -38.57142857, -51.42857143, (b[116], g[116], r[116]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), -90, -51.42857143, -64.28571429, (b[117], g[117], r[117]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), -90, -64.28571429, -77.14285715, (b[118], g[118], r[118]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), -90, -77.14285715, -90, (b[119], g[119], r[119]), -1)

                                                ## 4 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (170, 170), -90, 0, -18, (b[107], g[107], r[107]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), -90, -18, -36, (b[114], g[114], r[114]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), -90, -36, -54, (b[115], g[115], r[115]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), -90, -54, -72, (b[111], g[111], r[111]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), -90, -72, -90, (b[110], g[110], r[110]), -1)

                                             ## 5 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (110, 110), -90, 0, -30, (b[123], g[123], r[123]), -1)
        cv2.ellipse(img, (350, 350), (110, 110), -90, -30, -60, (b[108], g[108], r[108]), -1)
        cv2.ellipse(img, (350, 350), (110, 110), -90, -60, -90, (b[109], g[109], r[109]), -1)

                                            ## 6 Cercle rjouté  ##
        cv2.ellipse(img, (350, 350), (50, 50), -90, 0, -90, (b[122], g[122], r[122]), -1)

                            #############################################################
                            #                  Le 4eme Quadrant Inf_gauche              #
                            #############################################################

                                             ## 1 Cercle ajouté  ##

        cv2.ellipse(img, (350, 350), (350, 350), 90, 0, 11.25, (b[94], g[94], r[94]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 90, 11.25, 22.5, (b[92], g[92], r[92]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 90, 22.5, 33.75, (b[95], g[95], r[95]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 90, 33.75, 45, (b[93], g[93], r[93]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 90, 45, 56.25, (b[80], g[80], r[80]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 90, 56.25, 67.5, (b[67], g[67], r[67]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 90, 67.5, 78.75, (b[64], g[64], r[64]), -1)
        cv2.ellipse(img, (350, 350), (350, 350), 90, 78.75, 90, (b[66], g[66], r[66]), -1)

                                                  ## 2 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (290, 290), 90, 0, 11.25, (b[88], g[88], r[88]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 90, 11.25, 22.5, (b[89], g[89], r[89]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 90, 22.5, 33.75, (b[81], g[81], r[81]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 90, 33.75, 45, (b[68], g[68], r[68]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 90, 45, 56.25, (b[70], g[70], r[70]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 90, 56.25, 67.5, (b[69], g[69], r[69]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 90, 67.5, 78.75, (b[71], g[71], r[71]), -1)
        cv2.ellipse(img, (350, 350), (290, 290), 90, 78.75, 90, (b[65], g[65], r[65]), -1)

                                                 ## 3 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (230, 230), 90, 0, 12.85714286, (b[87], g[87], r[87]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 90, 12.85714286, 25.71428571, (b[86], g[86], r[86]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 90, 25.71428571, 38.57142857, (b[85], g[85], r[85]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 90, 38.57142857, 51.42857143, (b[84], g[84], r[84]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 90, 51.42857143, 64.28571429, (b[73], g[73], r[73]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 90, 64.28571429, 77.14285715, (b[74], g[74], r[74]), -1)
        cv2.ellipse(img, (350, 350), (230, 230), 90, 77.14285715, 90, (b[72], g[72], r[72]), -1)

                                                ## 4 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (170, 170), 90, 0, 18, (b[78], g[78], r[78]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 90, 18, 36, (b[79], g[79], r[79]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 90, 36, 54, (b[83], g[83], r[83]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 90, 54, 72, (b[82], g[82], r[82]), -1)
        cv2.ellipse(img, (350, 350), (170, 170), 90, 72, 90, (b[75], g[75], r[75]), -1)

                                                 ## 5 Cercle ajouté  ##
        cv2.ellipse(img, (350, 350), (110, 110), 90, 0, 30, (b[77], g[77], r[77]), -1)
        cv2.ellipse(img, (350, 350), (110, 110), 90, 30, 60, (b[76], g[76], r[76]), -1)
        cv2.ellipse(img, (350, 350), (110, 110), 90, 60, 90, (b[91], g[91], r[91]), -1)

                                                  ## 6 Cercle rjouté  ##
        cv2.ellipse(img, (350, 350), (50, 50), 90, 0, 90, (b[90], g[90], r[90]), -1)

        #############################################
        #       Le Sein gauche     #
        #############################################

        #############################################################
        #                 Le 1er Quadrant Sup_droit                 #
        #############################################################

        ## 1 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (350, 350), 0, 0, -11.25, (b[2], g[2], r[2]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 0, -11.25, -22.5, (b[0], g[0], r[0]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 0, -22.5, -33.75, (b[3], g[3], r[3]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 0, -33.75, -45, (b[16], g[16], r[16]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 0, -45, -56.25, (b[29], g[29], r[29]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 0, -56.25, -67.5, (b[31], g[31], r[31]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 0, -67.5, -78.75, (b[28], g[28], r[28]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 0, -78.75, -90, (b[30], g[30], r[30]), -1)

        ## 2 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (290, 290), 0, 0, -11.25, (b[1], g[1], r[1]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 0, -11.25, -22.5, (b[7], g[7], r[7]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 0, -22.5, -33.75, (b[5], g[5], r[5]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 0, -33.75, -45, (b[6], g[6], r[6]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 0, -45, -56.25, (b[4], g[4], r[4]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 0, -56.25, -67.5, (b[17], g[17], r[17]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 0, -67.5, -78.75, (b[25], g[25], r[25]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 0, -78.75, -90, (b[24], g[24], r[24]), -1)

        # ## 3 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (230, 230), 0, 0, -12.85714286, (b[8], g[8], r[8]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 0, -12.85714286, -25.71428571, (b[10], g[10], r[10]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 0, -25.71428571, -38.57142857, (b[9], g[9], r[9]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 0, -38.57142857, -51.42857143, (b[20], g[20], r[20]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 0, -51.42857143, -64.28571429, (b[21], g[21], r[21]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 0, -64.28571429, -77.14285715, (b[22], g[22], r[22]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 0, -77.14285715, -90, (b[23], g[23], r[23]), -1)

        # ## 4 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (170, 170), 0, 0, -18, (b[11], g[11], r[11]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), 0, -18, -36, (b[18], g[18], r[18]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), 0, -36, -54, (b[19], g[19], r[19]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), 0, -54, -72, (b[15], g[15], r[15]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), 0, -72, -90, (b[14], g[14], r[14]), -1)

        # ## 5 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (110, 110), 0, 0, -30, (b[27], g[27], r[27]), -1)
        cv2.ellipse(img, (1350, 350), (110, 110), 0, -30, -60, (b[12], g[12], r[12]), -1)
        cv2.ellipse(img, (1350, 350), (110, 110), 0, -60, -90, (b[13], g[13], r[13]), -1)

        # ## 6 Cercle rjouté  ##
        cv2.ellipse(img, (1350, 350), (50, 50), 0, 0, -90, (b[26], g[26], r[26]), -1)
        #
        # #############################################################
        # #                 Le 2eme Quadrant Inf_droit                #
        # #############################################################
        #
        # ## 1 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (350, 350), 0, 0, 11.25, (b[62], g[62], r[62]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 0, 11.25, 22.5, (b[60], g[60], r[60]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 0, 22.5, 33.75, (b[63], g[63], r[63]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 0, 33.75, 45, (b[61], g[61], r[61]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 0, 45, 56.25, (b[48], g[48], r[48]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 0, 56.25, 67.5, (b[35], g[35], r[35]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 0, 67.5, 78.75, (b[32], g[32], r[32]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 0, 78.75, 90, (b[34], g[34], r[34]), -1)
        #
        # ## 2 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (290, 290), 0, 0, 11.25, (b[56], g[56], r[56]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 0, 11.25, 22.5, (b[57], g[57], r[57]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 0, 22.5, 33.75, (b[49], g[49], r[49]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 0, 33.75, 45, (b[36], g[36], r[36]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 0, 45, 56.25, (b[38], g[38], r[38]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 0, 56.25, 67.5, (b[37], g[37], r[37]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 0, 67.5, 78.75, (b[39], g[39], r[39]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 0, 78.75, 90, (b[33], g[33], r[33]), -1)

        # ## 3 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (230, 230), 0, 0, 12.85714286, (b[55], g[55], r[55]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 0, 12.85714286, 25.71428571, (b[54], g[54], r[54]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 0, 25.71428571, 38.57142857, (b[53], g[53], r[53]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 0, 38.57142857, 51.42857143, (b[52], g[52], r[52]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 0, 51.42857143, 64.28571429, (b[41], g[41], r[41]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 0, 64.28571429, 77.14285715, (b[42], g[42], r[42]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 0, 77.14285715, 90, (b[40], g[40], r[40]), -1)

        # ## 4 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (170, 170), 0, 0, 18, (b[46], g[46], r[46]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), 0, 18, 36, (b[47], g[47], r[47]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), 0, 36, 54, (b[51], g[51], r[51]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), 0, 54, 72, (b[50], g[50], r[50]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), 0, 72, 90, (b[43], g[43], r[43]), -1)

        # ## 5 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (110, 110), 0, 0, 30, (b[45], g[45], r[45]), -1)
        cv2.ellipse(img, (1350, 350), (110, 110), 0, 30, 60, (b[44], g[44], r[44]), -1)
        cv2.ellipse(img, (1350, 350), (110, 110), 0, 60, 90, (b[59], g[59], r[59]), -1)

        # ## 6 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (50, 50), 0, 0, 90, (b[58], g[58], r[58]), -1)

        # #############################################################
        # #                 Le 3eme Quadrant Sup_gauche               #
        # #############################################################
        #
        # ## 1 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (350, 350), -90, 0, -11.25, (b[98], g[98], r[98]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), -90, -11.25, -22.5, (b[96], g[96], r[96]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), -90, -22.5, -33.75, (b[99], g[99], r[99]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), -90, -33.75, -45, (b[112], g[112], r[112]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), -90, -45, -56.25, (b[125], g[125], r[125]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), -90, -56.25, -67.5, (b[127], g[127], r[127]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), -90, -67.5, -78.75, (b[124], g[124], r[124]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), -90, -78.75, -90, (b[126], g[126], r[126]), -1)

        # ## 2 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (290, 290), -90, 0, -11.25, (b[97], g[97], r[97]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), -90, -11.25, -22.5, (b[103], g[103], r[103]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), -90, -22.5, -33.75, (b[101], g[101], r[101]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), -90, -33.75, -45, (b[102], g[102], r[102]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), -90, -45, -56.25, (b[100], g[100], r[100]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), -90, -56.25, -67.5, (b[113], g[113], r[113]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), -90, -67.5, -78.75, (b[121], g[121], r[121]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), -90, -78.75, -90, (b[120], g[120], r[120]), -1)
        #
        # ## 3 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (230, 230), -90, 0, -12.85714286, (b[104], g[104], r[104]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), -90, -12.85714286, -25.71428571, (b[106], g[106], r[106]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), -90, -25.71428571, -38.57142857, (b[105], g[105], r[105]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), -90, -38.57142857, -51.42857143, (b[116], g[116], r[116]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), -90, -51.42857143, -64.28571429, (b[117], g[117], r[117]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), -90, -64.28571429, -77.14285715, (b[118], g[118], r[118]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), -90, -77.14285715, -90, (b[119], g[119], r[119]), -1)
        #
        # ## 4 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (170, 170), -90, 0, -18, (b[107], g[107], r[107]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), -90, -18, -36, (b[114], g[114], r[114]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), -90, -36, -54, (b[115], g[115], r[115]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), -90, -54, -72, (b[111], g[111], r[111]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), -90, -72, -90, (b[110], g[110], r[110]), -1)
        #
        # ## 5 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (110, 110), -90, 0, -30, (b[123], g[123], r[123]), -1)
        cv2.ellipse(img, (1350, 350), (110, 110), -90, -30, -60, (b[108], g[108], r[108]), -1)
        cv2.ellipse(img, (1350, 350), (110, 110), -90, -60, -90, (b[109], g[109], r[109]), -1)
        #
        # ## 6 Cercle rjouté  ##
        cv2.ellipse(img, (1350, 350), (50, 50), -90, 0, -90, (b[122], g[122], r[122]), -1)
        #
        # #############################################################
        # #                  Le 4eme Quadrant Inf_gauche              #
        # #############################################################
        #
        # ## 1 Cercle ajouté  ##
        #
        cv2.ellipse(img, (1350, 350), (350, 350), 90, 0, 11.25, (b[94], g[94], r[94]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 90, 11.25, 22.5, (b[92], g[92], r[92]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 90, 22.5, 33.75, (b[95], g[95], r[95]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 90, 33.75, 45, (b[93], g[93], r[93]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 90, 45, 56.25, (b[80], g[80], r[80]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 90, 56.25, 67.5, (b[67], g[67], r[67]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 90, 67.5, 78.75, (b[64], g[64], r[64]), -1)
        cv2.ellipse(img, (1350, 350), (350, 350), 90, 78.75, 90, (b[66], g[66], r[66]), -1)
        #
        # ## 2 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (290, 290), 90, 0, 11.25, (b[88], g[88], r[88]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 90, 11.25, 22.5, (b[89], g[89], r[89]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 90, 22.5, 33.75, (b[81], g[81], r[81]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 90, 33.75, 45, (b[68], g[68], r[68]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 90, 45, 56.25, (b[70], g[70], r[70]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 90, 56.25, 67.5, (b[69], g[69], r[69]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 90, 67.5, 78.75, (b[71], g[71], r[71]), -1)
        cv2.ellipse(img, (1350, 350), (290, 290), 90, 78.75, 90, (b[65], g[65], r[65]), -1)
        #
        # ## 3 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (230, 230), 90, 0, 12.85714286, (b[87], g[87], r[87]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 90, 12.85714286, 25.71428571, (b[86], g[86], r[86]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 90, 25.71428571, 38.57142857, (b[85], g[85], r[85]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 90, 38.57142857, 51.42857143, (b[84], g[84], r[84]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 90, 51.42857143, 64.28571429, (b[73], g[73], r[73]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 90, 64.28571429, 77.14285715, (b[74], g[74], r[74]), -1)
        cv2.ellipse(img, (1350, 350), (230, 230), 90, 77.14285715, 90, (b[72], g[72], r[72]), -1)
        #
        # ## 4 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (170, 170), 90, 0, 18, (b[78], g[78], r[78]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), 90, 18, 36, (b[79], g[79], r[79]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), 90, 36, 54, (b[83], g[83], r[83]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), 90, 54, 72, (b[82], g[82], r[82]), -1)
        cv2.ellipse(img, (1350, 350), (170, 170), 90, 72, 90, (b[75], g[75], r[75]), -1)
        #
        # ## 5 Cercle ajouté  ##
        cv2.ellipse(img, (1350, 350), (110, 110), 90, 0, 30, (b[77], g[77], r[77]), -1)
        cv2.ellipse(img, (1350, 350), (110, 110), 90, 30, 60, (b[76], g[76], r[76]), -1)
        cv2.ellipse(img, (1350, 350), (110, 110), 90, 60, 90, (b[91], g[91], r[91]), -1)
        #
        # ## 6 Cercle rjouté  ##
        cv2.ellipse(img, (1350, 350), (50, 50), 90, 0, 90, (b[90], g[90], r[90]), -1)
        #

        #############################################################
            #                        Show image                         #
            #############################################################
            # bicubic_img = cv2.resize(img, None, fx=0.8, fy=0.8, interpolation=cv2.INTER_LINEAR)
            #
            # cv2.imshow(' Breast Phantom with LOQ Tumor -OpenCV-', bicubic_img)
            #
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            # break

            # Ajoutez les légendes souhaitées
        legend1 = "UIQ"
        legend2 = "UOQ"
        legend3 = "LIQ"
        legend4 = "LOQ"
        legend5 = "RIGHT BREAST"
        legend1_1 = "UOQ"
        legend2_2 = "UIQ"
        legend3_3 = "LOQ"
        legend4_4 = "LIQ"
        legend5_5 = "LEFT BREAST"
            # Paramètres du texte
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8
        color = (0, 0, 0)  # Couleur du texte (noir dans cet exemple)
        thickness = 2  # Épaisseur du texte

            # Position des légendes
        legend1_position = (5, 100)  # Coordonnées de la légende 1
        legend2_position = (630, 100)  # Coordonnées de la légende 2
        legend3_position = (5, 630)  # Coordonnées de la légende 3
        legend4_position = (630, 630)  # Coordonnées de la légende 4
        legend5_position = (250, 750)  # Coordonnées de la légende 5
        legend1_1_position = (995, 100)  # Coordonnées de la légende 1
        legend2_2_position = (1630, 100)  # Coordonnées de la légende 2
        legend3_3_position = (995, 630)  # Coordonnées de la légende 3
        legend4_4_position = (1630, 630)  # Coordonnées de la légende 4
        legend5_5_position = (1270, 750)  # Coordonnées de la légende 5
            # ...

           # Ajoutez les légendes à l'image
        cv2.putText(img, legend1, legend1_position, font, font_scale, color, thickness, cv2.LINE_AA)
        cv2.putText(img, legend2, legend2_position, font, font_scale, color, thickness, cv2.LINE_AA)
        cv2.putText(img, legend3, legend3_position, font, font_scale, color, thickness, cv2.LINE_AA)
        cv2.putText(img, legend4, legend4_position, font, font_scale, color, thickness, cv2.LINE_AA)
        cv2.putText(img, legend5, legend5_position, font, font_scale, color, 2, cv2.LINE_AA)
        cv2.putText(img, legend1_1, legend1_1_position, font, font_scale, color, thickness, cv2.LINE_AA)
        cv2.putText(img, legend2_2, legend2_2_position, font, font_scale, color, thickness, cv2.LINE_AA)
        cv2.putText(img, legend3_3, legend3_3_position, font, font_scale, color, thickness, cv2.LINE_AA)
        cv2.putText(img, legend4_4, legend4_4_position, font, font_scale, color, thickness, cv2.LINE_AA)
        cv2.putText(img, legend5_5, legend5_5_position, font, font_scale, color, 2, cv2.LINE_AA)


        _, img_encoded = cv2.imencode('.png', img)
        img_data = img_encoded.tobytes()
            # blurred_img = cv2.GaussianBlur(resized_img, (0, 0), sigmaX=2, sigmaY=2)
        print("Génération de l'image thermique pour le patient:", patient_id)

        return img

            # Rechercher un patient par exemple avec un ID de 1

@app.route('/thermal_image', methods=['GET'])
def thermal_image():
    patient_id = request.args.get('patient_id')
    port = request.args.get('port')  # Ajoutez le port en tant que paramètre d'URL

    if patient_id is None or patient_id.strip() == '':
        return "patient_id is required", 400
    if not port or port.strip() == '':
        return "port is required", 800
    try:
        app.logger.info(f"patient_id: {patient_id}, port: {port}")  # Log des valeurs

        ser = serial.Serial(port, 9600, timeout=1)

        img = generate_thermal_image(patient_id,ser)
        # Encoder l'image en PNG
        if img is None or not isinstance(img, np.ndarray):
            app.logger.error("L'image thermique générée est invalide.")

            return "Image thermique invalide.", 500

        ret, buffer = cv2.imencode('.png', img)
        if not ret:
            app.logger.error("Erreur lors de l'encodage de l'image.")

            return "Erreur lors de l'encodage de l'image.", 500

        response = Response(buffer.tobytes(), mimetype='image/png')
        return response
    except ValueError as e:
        return str(e), 404  # Retourne une erreur 404 si le patient n'est pas trouvé
    except serial.SerialException as e:
        app.logger.error(f"Erreur de connexion au port série: {str(e)}")

        return f"Erreur de connexion au port série: {str(e)}", 500
    except Exception as e:
        app.logger.error(f"Erreur inattendue: {str(e)}")

        return str(e), 500

@app.route('/upload_video', methods=['POST'])
def upload_video():
    patient_id = request.args.get('patient_id')
    video_file = request.files.get('video')

    if not video_file or not patient_id:
        return jsonify({'success': False, 'error': 'No video file provided or patient_id is missing.'}), 400

    # Vérification si l'ID du patient est un entier valide
    try:
        patient_id = int(patient_id)
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid patient_id.'}), 400

    timestamp = int(time.time() * 500)
    # Créez le nom de fichier en fonction de l'ID du patient et du timestamp
    video_filename = f"{patient_id}_{timestamp}.webm"
    # Sauvegardez dans le dossier UPLOAD_FOLDER_videos
    try:
        # Sauvegarde du fichier vidéo à cet emplacement
        video_file.save(os.path.join(app.config['UPLOAD_FOLDER_videos'], video_filename))

        # Crée un nouveau diagnostic pour le patient
        new_diagnostic = Diagnostic(patient_id=patient_id, type='Vidéo', date=datetime.utcnow(), file=video_filename)
        db.session.add(new_diagnostic)
        db.session.commit()

        return jsonify(success=True, filename=video_filename, date=datetime.utcnow().strftime('%d/%m/%Y %H:%M'))
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/consultation', methods=['GET', 'POST'])
def consultation():
    if request.method == 'POST':
        # Récupérer les données du formulaire de consultation
        patient_id = request.form.get('patient_id')
        date = request.form.get('date')
        note = request.form.get('note')

        # Vérifiez que les champs ne sont pas vides
        if not patient_id or not date:
            flash("Tous les champs sont requis.")
            return redirect(url_for('consultation'))

        # Créer une nouvelle consultation
        new_consultation = Consultation(
            patient_id=patient_id,
            date=date,
            note=note,
            medecin_id=current_user.id  # Associer le médecin connecté à la consultation
        )
        db.session.add(new_consultation)
        db.session.commit()

        flash("Consultation ajoutée avec succès.")
        return redirect(url_for('dashboard_medecin'))  # Rediriger vers le tableau de bord du médecin

    # Si la méthode est GET, afficher le formulaire de consultation
    patients = Patient.query.all()  # Récupérer tous les patients
    sensor_values = {}  # Dictionnaire pour stocker les valeurs des capteurs pour chaque patient

    # Récupérer les valeurs des capteurs pour chaque patient
    for patient in patients:
        sensor_values[patient.id] = patient.sensor_values  # Stocker les valeurs des capteurs par ID de patient

    return render_template('consultation.html', patients=patients, sensor_values=sensor_values)

@app.route('/envoyer-consultation', methods=['POST'])
def envoyer_consultation():
    # Charger la vidéo enregistrée et l’envoyer au médecin via la base de données
    return "Consultation envoyée avec succès!"

UPLOAD_FOLDER___ = 'static/images'  # Répertoire pour enregistrer les images temporaires
VIDEO_FOLDER__ = 'static/uploads/videos'    # Répertoire pour enregistrer les vidéos

############################################################################
# ... Pour afficher les tableaux de database ...

@app.route('/debug-db')
def lire_database():
    import sqlite3
    conn = sqlite3.connect('instance/database.db')  # adapte ce chemin si ta base est ailleurs
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    output = ""
    for table_name in tables:
        output += f"<h2>Table: {table_name[0]}</h2>"

        try:
            cursor.execute(f"SELECT * FROM {table_name[0]}")
            rows = cursor.fetchall()
            col_names = [description[0] for description in cursor.description]

            output += "<table border='1'><tr>"
            for col in col_names:
                output += f"<th>{col}</th>"
            output += "</tr>"

            for row in rows:
                output += "<tr>"
                for cell in row:
                    output += f"<td>{cell}</td>"
                output += "</tr>"
            output += "</table>"

        except Exception as e:
            output += f"<p>Erreur : {e}</p>"

    conn.close()
    return output

if __name__ == '__main__':
     os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
     os.makedirs(app.config['UPLOAD_FOLDER_videos'], exist_ok=True)
     os.makedirs(app.config['UPLOAD_FOLDER_files'], exist_ok=True)
     os.makedirs(UPLOAD_FOLDER___, exist_ok=True)
     os.makedirs(VIDEO_FOLDER__, exist_ok=True)

     with app.app_context():
         db.create_all()  # Créer les tables

     socketio.run(app,host='10.2.28.39', port=5000)
