import eventlet
eventlet.monkey_patch()
from scipy.ndimage import gaussian_filter, binary_opening, binary_closing
from scipy.interpolate import griddata
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
screen_width = 1800
screen_height = 980
bg_color = 245
nb_sections = 10
img_base = np.full((screen_height, screen_width, 3), bg_color, np.uint8)

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
        photo_filename = secure_filename(f"{username}.png")
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

    patient = db.session.get(Patient, patient_id)
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


# # Paramètres globaux

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
max_radius = min(screen_width, screen_height) // 4
centre_gauche = (800, screen_height // 2 + 20)
centre_droit = (1500, screen_height // 2 + 20)
lissage_sigma = 1.2
rayons = [max_radius - i * max(1, (max_radius // 18)) for i in range(18)]

# Lire ligne série et convertir en flottants

# -------------------- Utilitaires --------------------
def extend_to_length(values, length):
    return [values[i % len(values)] for i in range(length)]
def compute_grid(centre, rayons, nb_sections, valeurs, grid_res=360):
    points, vals = [], []
    pas = 90.0 / max(1, nb_sections)
    for q in range(4):
        for idx, r in enumerate(rayons):
            temp_vals = extend_to_length(valeurs[q][idx], nb_sections)
            temp_vals = temp_vals[::-1]
            for i in range(nb_sections):
                angle = q * 90 + (i + 0.5) * pas
                x = centre[0] + r * np.cos(np.radians(angle))
                y = centre[1] + r * np.sin(np.radians(angle))
                points.append([x, y])
                vals.append(temp_vals[i % len(temp_vals)])
    points = np.array(points)
    vals = np.array(vals)

    max_r = max(rayons)
    grid_x, grid_y = np.mgrid[centre[0] - max_r:centre[0] + max_r:complex(grid_res),
                     centre[1] - max_r:centre[1] + max_r:complex(grid_res)]
    try:
        grid_z = griddata(points, vals, (grid_x, grid_y), method='linear')
    except Exception:
        grid_z = np.full(grid_x.shape, np.nan)
    mask = np.sqrt((grid_x - centre[0]) ** 2 + (grid_y - centre[1]) ** 2) <= max_r
    grid_z[~mask] = np.nan
    return grid_x, grid_y, grid_z, mask

def render_heatmap_on_image(img, centre, grid_x, grid_y, grid_z, mask, tmin, seuil_chaud_init, gamma=0.1):
    grid_z_filled = np.nan_to_num(grid_z, nan=tmin)
    grid_z_smooth = gaussian_filter(grid_z_filled, sigma=lissage_sigma)

    # Normalisation par rapport au seuil chaud
    denom = max(1e-6, (seuil_chaud_init - tmin))
    grid_norm = np.clip((grid_z_smooth - tmin) / denom, 0, 1)
    grid_norm = (grid_norm ** gamma * 255).astype(np.uint8)

    # Appliquer colormap
    heatmap = cv2.applyColorMap(grid_norm, cv2.COLORMAP_JET)

    # Masque et ROI
    max_r = max(rayons)
    x0 = max(0, centre[0] - max_r)
    y0 = max(0, centre[1] - max_r)
    x1 = min(screen_width, centre[0] + max_r)
    y1 = min(screen_height, centre[1] + max_r)
    w, h = x1 - x0, y1 - y0

    heatmap_resized = cv2.resize(heatmap, (w, h), interpolation=cv2.INTER_CUBIC)
    mask_resized = cv2.resize(mask.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST).astype(bool)
    roi = img[y0:y1, x0:x1]
    np.copyto(roi, heatmap_resized, where=np.dstack([mask_resized]*3))
    img[y0:y1, x0:x1] = roi

    return grid_z_smooth, mask_resized, (x0, y0, w, h)


def detect_hot_zones_and_smooth(grid_z, mask, seuil):
    valid = ~np.isnan(grid_z)
    chaud = np.zeros_like(grid_z, dtype=bool)
    chaud[valid] = grid_z[valid] > seuil
    chaud_clean = binary_opening(chaud, structure=np.ones((3, 3)))
    chaud_clean = binary_closing(chaud_clean, structure=np.ones((5, 5)))
    valid_count = np.count_nonzero(valid)
    pct = (np.count_nonzero(chaud_clean) / valid_count * 100.0) if valid_count else 0.0
    return chaud_clean, pct

def draw_contours_and_boxes(img, centre, bool_mask, grid_z, offset_info=None, couleur=(0, 0, 255)):
    if offset_info is None:
        return []
    x0, y0, w, h = offset_info
    mask_uint = (bool_mask.astype(np.uint8) * 255)
    contours, _ = cv2.findContours(mask_uint, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    annotations = []
    gh, gw = mask_uint.shape
    sx = w / max(1, gw)
    sy = h / max(1, gh)

    for c in contours:
        if cv2.contourArea(c) < 10:
            continue
        x, y, cw, ch = cv2.boundingRect(c)
        area_pixels = cv2.contourArea(c)
        total_valid = np.count_nonzero(~np.isnan(grid_z))
        pct_area = (area_pixels / total_valid * 100) if total_valid else 0.0
        poly = c.squeeze().astype(np.float32)
        if poly.ndim == 1:
            continue
        poly[:, 0] = poly[:, 0] * sx + x0
        poly[:, 1] = poly[:, 1] * sy + y0
        pts = poly.reshape((-1, 1, 2)).astype(np.int32)
        cv2.polylines(img, [pts], True, couleur, 2, cv2.LINE_AA)
        M = cv2.moments(c)
        if M['m00'] != 0:
            cxg = int(M['m10'] / M['m00']);
            cyg = int(M['m01'] / M['m00'])
            cx = int(cxg * sx + x0);
            cy = int(cyg * sy + y0)
        else:
            cx = int(np.mean(poly[:, 0]));
            cy = int(np.mean(poly[:, 1]))
        # label = f"{pct_area:.1f}%"
        # (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        # cv2.rectangle(img, (cx - tw // 2 - 6, cy - th - 10), (cx + tw // 2 + 6, cy + 4), (255, 255, 255), -1)
        # cv2.putText(img, label, (cx - tw // 2, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 1, cv2.LINE_AA)
        annotations.append((cx, cy, pct_area))
    return annotations

def detecter_zones_asymetrie(grid_g, grid_d, seuil_asym=0.5):
    """Détecte les zones où la différence entre les seins dépasse le seuil"""
    diff_grid = np.abs(grid_g - grid_d)
    zones_asym = np.zeros_like(diff_grid, dtype=bool)
    zones_asym[~np.isnan(diff_grid)] = diff_grid[~np.isnan(diff_grid)] > seuil_asym
    return zones_asym

def dessiner_contours_asymetrie(img, centre, bool_mask, grid_z, offset_info=None, couleur=(0, 255, 255)):
    """Dessine des contours autour des zones d'asymétrie"""
    if offset_info is None:
        return 0
    x0, y0, w, h = offset_info
    mask_uint = (bool_mask.astype(np.uint8) * 255)
    contours, _ = cv2.findContours(mask_uint, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    gh, gw = mask_uint.shape
    sx = w / max(1, gw)
    sy = h / max(1, gh)

    for c in contours:
        if cv2.contourArea(c) < 5:  # Seuil plus bas pour les petites zones
            continue
        poly = c.squeeze().astype(np.float32)
        if poly.ndim == 1:
            continue
        poly[:, 0] = poly[:, 0] * sx + x0
        poly[:, 1] = poly[:, 1] * sy + y0
        pts = poly.reshape((-1, 1, 2)).astype(np.int32)
        # Dessiner en pointillé pour différencier des zones chaudes
        cv2.polylines(img, [pts], True, couleur, 2, cv2.LINE_AA, shift=0)

        # Ajouter un label "Asym"
        M = cv2.moments(c)
        if M['m00'] != 0:
            cxg = int(M['m10'] / M['m00'])
            cyg = int(M['m01'] / M['m00'])
            cx = int(cxg * sx + x0)
            cy = int(cyg * sy + y0)
            label = "Asym"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(img, (cx - tw // 2 - 4, cy - th - 8), (cx + tw // 2 + 4, cy + 4), (255, 255, 255), -1)
            cv2.putText(img, label, (cx - tw // 2, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 100, 100), 1, cv2.LINE_AA)

    return len(contours)

def grid_value_at_pixel(grid_z, centre, px, py):
    max_r = max(rayons)
    gx = grid_z.shape[1]
    gy = grid_z.shape[0]
    xi = int((px - (centre[0] - max_r)) / (2 * max_r) * gx)
    yi = int((py - (centre[1] - max_r)) / (2 * max_r) * gy)
    xi = np.clip(xi, 0, gx - 1)
    yi = np.clip(yi, 0, gy - 1)
    val = grid_z[yi, xi]
    return None if np.isnan(val) else float(val)


# -------------------- Fenêtre et trackbars --------------------
class ThermalImager:
    def __init__(self, screen_width, screen_height):
        self.win_name = "Thermo IA - Clinique (o = toggle overlay)"
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.initialized = False

    def init_window(self):
        """Initialise la fenêtre et les trackbars si ce n'est pas déjà fait"""
        if not self.initialized:
            cv2.namedWindow(self.win_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.win_name, self.screen_width, self.screen_height)

            # Trackbars
            cv2.createTrackbar("Tmin x10", self.win_name, 180, 500, lambda v: None)
            cv2.createTrackbar("Tmax x10", self.win_name, 350, 500, lambda v: None)
            cv2.createTrackbar("Seuil chaud x10", self.win_name, 300, 500, lambda v: None)
            cv2.createTrackbar("Gamma x10", self.win_name, 1, 30, lambda v: None)

            self.initialized = True

    def get_trackbar_values(self):
        """Récupère les valeurs actuelles des trackbars"""
        tmin = cv2.getTrackbarPos("Tmin x10", self.win_name) / 10.0
        tmax = cv2.getTrackbarPos("Tmax x10", self.win_name) / 10.0
        seuil = cv2.getTrackbarPos("Seuil chaud x10", self.win_name) / 10.0
        gamma = max(0.5, cv2.getTrackbarPos("Gamma x10", self.win_name) / 10.0)
        if tmax <= tmin + 0.1:
            tmax = tmin + 0.1
        return tmin, tmax, seuil, gamma

    def show_image(self, img):
        """Affiche l'image dans la fenêtre"""
        cv2.imshow(self.win_name, img)

    def set_trackbar_positions(self, tmin=None, tmax=None, seuil=None, gamma=None):
        """Met à jour les trackbars si des valeurs sont fournies"""
        if tmin is not None:
            cv2.setTrackbarPos("Tmin x10", self.win_name, int(tmin * 10))
        if tmax is not None:
            cv2.setTrackbarPos("Tmax x10", self.win_name, int(tmax * 10))
        if seuil is not None:
            cv2.setTrackbarPos("Seuil chaud x10", self.win_name, int(seuil * 10))
        if gamma is not None:
            cv2.setTrackbarPos("Gamma x10", self.win_name, int(gamma * 10))
# thermal_imager = ThermalImager(screen_width=1200, screen_height=700)
# thermal_imager.init_window()


last_grids = {'gauche': None, 'droit': None}
param_images = {}
overlay_on = False
last_save_time = 0

# -------------------- Dessin overlay anatomique --------------------
def draw_anatomical_overlay(img, centre, radius, alpha=0.22, color=(220, 220, 220)):
    overlay = img.copy()
    axes = (int(radius * 0.95), int(radius * 0.78))
    cv2.ellipse(overlay, centre, axes, 0, 0, 360, color, -1)
    cv2.line(overlay, (centre[0], centre[1] - axes[1]), (centre[0], centre[1] + axes[1]), (200, 200, 200), 1)
    cv2.line(overlay, (centre[0] - axes[0], centre[1]), (centre[0] + axes[0], centre[1]), (200, 200, 200), 1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

# -------------------- Mouse callback --------------------
zoom_states = [None, None]  # Contiendra les deux crops zoomés
zoom_window_names = ["Zoom 1", "Zoom 2"]

def on_mouse(event, x, y, flags, param):
    global zoom_states

    img_for_zoom = param_images.get('img_clean_for_zoom', None)
    if img_for_zoom is None:
        return

    # Taille du crop autour du clic
    w = int(max_radius * 1.0)
    h = int(max_radius * 1.0)

    # Fonction pour créer le zoom
    def create_zoom(x, y):
        x0 = int(np.clip(x - w // 2, 0, screen_width - w))
        y0 = int(np.clip(y - h // 2, 0, screen_height - h))
        crop = img_for_zoom[y0:y0 + h, x0:x0 + w].copy()
        crop_zoomed = cv2.resize(crop, (int(w * 2.2), int(h * 2.2)), interpolation=cv2.INTER_CUBIC)
        return crop_zoomed

    if event == cv2.EVENT_LBUTTONDOWN:
        # Vérifie clic sur sein droit
        if (x - centre_droit[0])**2 + (y - centre_droit[1])**2 <= max_radius**2:
            zoom_states[0] = create_zoom(x, y)
            window_name = "Zoom du sein droit"
            #cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 400, 400)  # Taille plus petite
            cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
         #   cv2.imshow(window_name, zoom_states[0])

        # Vérifie clic sur sein gauche
        elif (x - centre_gauche[0])**2 + (y - centre_gauche[1])**2 <= max_radius**2:
            zoom_states[1] = create_zoom(x, y)
            window_name = "Zoom du sein gauche"
           # cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 400, 400)  # Taille plus petite
            cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
          #  cv2.imshow(window_name, zoom_states[1])

    elif event == cv2.EVENT_MOUSEMOVE:
        img_copy = param_images.get('img_for_mouse', None)
        if img_copy is None:
            return

        display_info = None
        for label, centre in [('gauche', centre_gauche), ('droit', centre_droit)]:
            grd = last_grids[label]
            if grd is None:
                continue
            gx, gy, gz, mask = grd
            if (x - centre[0])**2 + (y - centre[1])**2 <= max_radius**2:
                val = grid_value_at_pixel(gz, centre, x, y)
                if val is not None:
                    display_info = (label, val, x, y)
                break

        img_temp = img_copy.copy()
        if display_info:
            label, val, px, py = display_info
            txt = f"{label.upper()} : {val:.2f} C"
            tx = px + 15 if px < screen_width - 200 else px - 170
            ty = py - 15 if py > 50 else py + 25
            (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(img_temp, (tx - 8, ty - th - 8), (tx + tw + 8, ty + 8), (255, 255, 255), -1)
            cv2.putText(img_temp, txt, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 10, 10), 2, cv2.LINE_AA)

       # cv2.imshow(win_name, img_temp)


#cv2.setMouseCallback(win_name, on_mouse)


# -------------------- Panneau d'information À GAUCHE --------------------
def draw_info_panel(img, x, y, width, height,
                    min_g, max_g, mean_g,
                    min_d, max_d, mean_d,
                    pct_g, pct_d, asym, seuil,
                    nb_zones_asym_g, nb_zones_asym_d,
                    alert=False):
    panel = np.full((height, width, 3), bg_color, dtype=np.uint8)

    border_color = (0, 0, 200) if alert else (50, 50, 150)
    cv2.rectangle(panel, (0, 0), (width - 1, height - 1), border_color, 3)

    title_y = 40
    cv2.putText(panel, "ANALYSE THERMOGRAPHIQUE",
                (width // 2 - 220, title_y), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 60, 120), 2)

    cv2.line(panel, (10, title_y + 15), (width - 10, title_y + 15), (100, 100, 100), 2)

    col_w = (width - 60) // 2
    col_x = [30, 30 + col_w + 20]
    start_y = title_y + 45
    line_height = 30

    # --- Colonne 1: Sein Gauche ---
    current_y = start_y
    cv2.putText(panel, "SEIN GAUCHE", (col_x[0], current_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 200), 2)
    current_y += line_height

    cv2.putText(panel, f"Min: {min_g:.1f}C", (col_x[0], current_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    current_y += line_height

    cv2.putText(panel, f"Max: {max_g:.1f}C", (col_x[0], current_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    current_y += line_height

    cv2.putText(panel, f"Moy: {mean_g:.1f}C", (col_x[0], current_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    current_y += line_height

    cv2.putText(panel, f"Zone chaude: {pct_g:.1f}%", (col_x[0], current_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 200), 2)

    bar_y = current_y + 12
    bar_width = col_w - 20
    bar_filled = int(bar_width * min(pct_g / 100, 1.0))
    cv2.rectangle(panel, (col_x[0], bar_y), (col_x[0] + bar_filled, bar_y + 12), (0, 0, 255), -1)
    cv2.rectangle(panel, (col_x[0], bar_y), (col_x[0] + bar_width, bar_y + 12), (80, 80, 80), 2)

    # --- Colonne 2: Sein Droit ---
    current_y = start_y
    cv2.putText(panel, "SEIN DROIT", (col_x[1], current_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 0, 0), 2)
    current_y += line_height

    cv2.putText(panel, f"Min: {min_d:.1f}C", (col_x[1], current_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    current_y += line_height

    cv2.putText(panel, f"Max: {max_d:.1f}C", (col_x[1], current_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    current_y += line_height

    cv2.putText(panel, f"Moy: {mean_d:.1f}C", (col_x[1], current_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    current_y += line_height

    cv2.putText(panel, f"Zone chaude: {pct_d:.1f}%", (col_x[1], current_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 0, 0), 2)

    bar_y = current_y + 12
    bar_filled = int(bar_width * min(pct_d / 100, 1.0))
    cv2.rectangle(panel, (col_x[1], bar_y), (col_x[1] + bar_filled, bar_y + 12), (0, 0, 255), -1)
    cv2.rectangle(panel, (col_x[1], bar_y), (col_x[1] + bar_width, bar_y + 12), (80, 80, 80), 2)

    # --- Section Analyse en bas du panneau ---
    analysis_y = start_y + line_height * 5 + 30

    cv2.putText(panel, "ANALYSE GLOBALE", (width // 2 - 120, analysis_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 100, 0), 2)
    analysis_y += line_height

    # Afficher l'asymétrie seulement si > 0.1°C
    if asym > 0.5:
        cv2.putText(panel, f"Asymetrie: {asym:.2f}C", (width // 2 - 100, analysis_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    else:
        cv2.putText(panel, "Asymetrie: < 0.1C", (width // 2 - 100, analysis_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 150, 0), 2)
    analysis_y += line_height

    cv2.putText(panel, f"Seuil chaud: {seuil:.1f}C", (width // 2 - 100, analysis_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    analysis_y += line_height

    # Information sur les zones d'asymétrie
    if nb_zones_asym_g > 0 or nb_zones_asym_d > 0:
        cv2.putText(panel, f"Zones asymetriques: {nb_zones_asym_g}",
                    (width // 2 - 120, analysis_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 100, 100), 2)
    else:
        cv2.putText(panel, "Aucune zone asymetrique",
                    (width // 2 - 100, analysis_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 150, 0), 2)
    analysis_y += line_height + 10

    alert_y = analysis_y + 15
    if alert:
        cv2.putText(panel, "ALERTE - SUSPICION DETECTEE", (width // 2 - 180, alert_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 200), 2)
        alert_y += line_height
        cv2.putText(panel, "Examens complementaires requis", (width // 2 - 160, alert_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 200), 2)
    else:
        cv2.putText(panel, "PROFIL THERMIQUE NORMAL", (width // 2 - 180, alert_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 150, 0), 2)
        alert_y += line_height
        cv2.putText(panel, "Symetrie thermique dans les normes", (width // 2 - 200, alert_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 150, 0), 2)

    img[y:y + height, x:x + width] = panel


def generate_thermal_image(patient_id, ser):
    # Fetch the patient using the new method
    patient = db.session.get(Patient, patient_id)
    if patient is None:
        raise ValueError(f"No patient found with id {patient_id}")

    try:
        #while True:
                # Lire une ligne du port série
                line = ser.readline().decode('latin1').strip()
                # ou pour ignorer les caractères invalides
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                values = line.split(',')

                if len(values) == 64:
                    sensor_values = [float(v) for v in values]

                    # RGB mapping
                  #  for i in range(64):
                   #     r[i], g[i], b[i] = rgb(minimum, maximum, sensor_values[i])

                    # Sauvegarde DB
                    new_diagnostic_record = Diagnostic(
                        patient_id=patient.id,
                        sensor_data=sensor_values
                    )
                    db.session.add(new_diagnostic_record)
                    db.session.commit()

                    socketio.emit('sensor_data', {'data': sensor_values})

                else:
                    print("Trame invalide :", len(values))

    except KeyboardInterrupt:
        print("Arrêt du programme par l'utilisateur.")
    finally:
        close_serial_connection(ser)

        img = np.zeros((screen_height, screen_width, 3), np.uint8)
        img[:] = (255, 255, 255)
        tmin = tmin_init = min(sensor_values)
        tmax = tmax_init = max(sensor_values)
        seuil_chaud_init = 35
        # Optionnel : mettre à jour les trackbars pour affichage dynamique
        # cv2.setTrackbarPos("Tmin x10", win_name, int(tmin * 10))
        # cv2.setTrackbarPos("Tmax x10", win_name, int(tmax * 10))
        # cv2.setTrackbarPos("Seuil chaud x10", win_name, int(seuil_chaud_init * 10))

        # --- remplir grid_data_list avec nouvelles grilles ---
        grid_data_list = []

        IC = sensor_values
        # ============== sein_gauche ================#
        valeurs_BrLeft_hg = [
            [IC[9], IC[9], IC[0], IC[0], IC[0], IC[0], IC[0], IC[0], IC[12], IC[12]],
            [IC[9], IC[9], IC[0], IC[0], IC[0], IC[0], IC[0], IC[0], IC[12], IC[12]],
            [IC[9], IC[9], IC[3], IC[3], IC[0], IC[0], IC[1], IC[1], IC[12], IC[12]],
            [IC[9], IC[9], IC[3], IC[3], IC[2], IC[2], IC[1], IC[1], IC[12], IC[12]],
            [IC[10], IC[10], IC[3], IC[3], IC[2], IC[2], IC[1], IC[1], IC[12], IC[12]],
            [IC[10], IC[10], IC[3], IC[3], IC[2], IC[2], IC[1], IC[1], IC[12], IC[12]],
            [IC[10], IC[10], IC[3], IC[3], IC[2], IC[2], IC[1], IC[1], IC[13], IC[13]],
            [IC[10], IC[10], IC[5], IC[5], IC[2], IC[2], IC[6], IC[6], IC[13], IC[13]],
            [IC[11], IC[11], IC[5], IC[5], IC[4], IC[4], IC[6], IC[6], IC[13], IC[13]],
            [IC[11], IC[11], IC[5], IC[5], IC[4], IC[4], IC[6], IC[6], IC[13], IC[13]],
            [IC[11], IC[11], IC[5], IC[5], IC[4], IC[4], IC[6], IC[6], IC[13], IC[13]],
            [IC[31], IC[31], IC[31], IC[7], IC[7], IC[7], IC[7], IC[14], IC[14], IC[14]],
            [IC[31], IC[31], IC[31], IC[7], IC[7], IC[7], IC[7], IC[14], IC[14], IC[14]],
            [IC[31], IC[31], IC[31], IC[7], IC[7], IC[7], IC[7], IC[14], IC[14], IC[14]],
            [IC[31], IC[31], IC[31], IC[8], IC[8], IC[8], IC[8], IC[14], IC[14], IC[14]],
            [IC[31], IC[31], IC[31], IC[8], IC[8], IC[8], IC[8], IC[14], IC[14], IC[14]],
            [IC[31], IC[31], IC[31], IC[8], IC[8], IC[8], IC[8], IC[14], IC[14], IC[14]],
            [IC[31], IC[31], IC[31], IC[8], IC[8], IC[8], IC[8], IC[14], IC[14], IC[14]]
        ]
        valeurs_BrLeft_hd = [
            [IC[12], IC[12], IC[18], IC[18], IC[18], IC[18], IC[18], IC[21], IC[21], IC[21]],
            [IC[12], IC[12], IC[18], IC[18], IC[18], IC[18], IC[18], IC[21], IC[21], IC[21]],
            [IC[12], IC[12], IC[18], IC[18], IC[18], IC[18], IC[18], IC[21], IC[21], IC[21]],
            [IC[12], IC[12], IC[18], IC[18], IC[18], IC[18], IC[18], IC[21], IC[21], IC[21]],
            [IC[12], IC[12], IC[18], IC[18], IC[18], IC[18], IC[18], IC[21], IC[21], IC[21]],
            [IC[13], IC[13], IC[17], IC[17], IC[17], IC[17], IC[17], IC[20], IC[20], IC[20]],
            [IC[13], IC[13], IC[17], IC[17], IC[17], IC[17], IC[17], IC[20], IC[20], IC[20]],
            [IC[13], IC[13], IC[17], IC[17], IC[17], IC[17], IC[17], IC[20], IC[20], IC[20]],
            [IC[13], IC[13], IC[17], IC[17], IC[17], IC[17], IC[17], IC[20], IC[20], IC[20]],
            [IC[13], IC[13], IC[17], IC[17], IC[17], IC[17], IC[17], IC[20], IC[20], IC[20]],
            [IC[14], IC[14], IC[16], IC[16], IC[16], IC[16], IC[16], IC[15], IC[15], IC[15]],
            [IC[14], IC[14], IC[16], IC[16], IC[16], IC[16], IC[16], IC[15], IC[15], IC[15]],
            [IC[14], IC[14], IC[16], IC[16], IC[16], IC[16], IC[16], IC[15], IC[15], IC[15]],
            [IC[14], IC[14], IC[16], IC[16], IC[16], IC[16], IC[16], IC[15], IC[15], IC[15]],
            [IC[14], IC[14], IC[14], IC[16], IC[16], IC[16], IC[19], IC[19], IC[19], IC[19]],
            [IC[14], IC[14], IC[14], IC[16], IC[16], IC[16], IC[19], IC[19], IC[19], IC[19]],
            [IC[14], IC[14], IC[14], IC[16], IC[16], IC[16], IC[19], IC[19], IC[19], IC[19]],
            [IC[14], IC[14], IC[14], IC[19], IC[19], IC[19], IC[19], IC[19], IC[19], IC[19]]
        ]
        valeurs_BrLeft_bg = [
            [IC[27], IC[27], IC[27], IC[30], IC[30], IC[30], IC[30], IC[9], IC[9], IC[9]],
            [IC[27], IC[27], IC[27], IC[30], IC[30], IC[30], IC[30], IC[9], IC[9], IC[9]],
            [IC[27], IC[27], IC[27], IC[30], IC[30], IC[30], IC[30], IC[9], IC[9], IC[9]],
            [IC[27], IC[27], IC[27], IC[30], IC[30], IC[30], IC[30], IC[9], IC[9], IC[9]],
            [IC[27], IC[27], IC[27], IC[30], IC[30], IC[30], IC[30], IC[9], IC[9], IC[9]],
            [IC[27], IC[27], IC[27], IC[30], IC[30], IC[30], IC[30], IC[10], IC[10], IC[10]],
            [IC[27], IC[27], IC[27], IC[30], IC[30], IC[30], IC[30], IC[10], IC[10], IC[10]],
            [IC[27], IC[27], IC[27], IC[30], IC[30], IC[30], IC[30], IC[10], IC[10], IC[10]],
            [IC[27], IC[27], IC[27], IC[29], IC[29], IC[29], IC[29], IC[10], IC[10], IC[10]],
            [IC[26], IC[26], IC[26], IC[29], IC[29], IC[29], IC[29], IC[11], IC[11], IC[11]],
            [IC[26], IC[26], IC[26], IC[29], IC[29], IC[29], IC[29], IC[11], IC[11], IC[11]],
            [IC[26], IC[26], IC[26], IC[29], IC[29], IC[29], IC[29], IC[11], IC[11], IC[11]],
            [IC[25], IC[25], IC[25], IC[28], IC[28], IC[28], IC[28], IC[31], IC[31], IC[31]],
            [IC[25], IC[25], IC[25], IC[28], IC[28], IC[28], IC[28], IC[31], IC[31], IC[31]],
            [IC[25], IC[25], IC[25], IC[28], IC[28], IC[28], IC[28], IC[31], IC[31], IC[31]],
            [IC[25], IC[25], IC[25], IC[28], IC[28], IC[28], IC[28], IC[31], IC[31], IC[31]],
            [IC[25], IC[25], IC[25], IC[28], IC[28], IC[28], IC[28], IC[31], IC[31], IC[31]],
            [IC[25], IC[25], IC[25], IC[28], IC[28], IC[28], IC[28], IC[31], IC[31], IC[31]]
        ]
        valeurs_BrLeft_bd = [
            [IC[21], IC[21], IC[21], IC[24], IC[24], IC[24], IC[24], IC[27], IC[27], IC[27]],
            [IC[21], IC[21], IC[21], IC[24], IC[24], IC[24], IC[24], IC[27], IC[27], IC[27]],
            [IC[21], IC[21], IC[21], IC[24], IC[24], IC[24], IC[24], IC[27], IC[27], IC[27]],
            [IC[21], IC[21], IC[21], IC[24], IC[24], IC[24], IC[24], IC[27], IC[27], IC[27]],
            [IC[21], IC[21], IC[21], IC[24], IC[24], IC[24], IC[24], IC[27], IC[27], IC[27]],
            [IC[20], IC[20], IC[20], IC[24], IC[24], IC[24], IC[24], IC[27], IC[27], IC[27]],
            [IC[20], IC[20], IC[20], IC[23], IC[23], IC[23], IC[23], IC[27], IC[27], IC[27]],
            [IC[20], IC[20], IC[20], IC[23], IC[23], IC[23], IC[23], IC[27], IC[27], IC[27]],
            [IC[20], IC[20], IC[20], IC[23], IC[23], IC[23], IC[23], IC[27], IC[27], IC[27]],
            [IC[20], IC[20], IC[20], IC[23], IC[23], IC[23], IC[23], IC[27], IC[27], IC[27]],
            [IC[15], IC[15], IC[15], IC[23], IC[23], IC[23], IC[23], IC[26], IC[26], IC[26]],
            [IC[15], IC[15], IC[15], IC[22], IC[22], IC[22], IC[22], IC[26], IC[26], IC[26]],
            [IC[15], IC[15], IC[15], IC[22], IC[22], IC[22], IC[22], IC[26], IC[26], IC[26]],
            [IC[15], IC[15], IC[15], IC[22], IC[22], IC[22], IC[22], IC[26], IC[26], IC[26]],
            [IC[19], IC[19], IC[19], IC[22], IC[22], IC[22], IC[22], IC[25], IC[25], IC[25]],
            [IC[19], IC[19], IC[19], IC[22], IC[22], IC[22], IC[22], IC[25], IC[25], IC[25]],
            [IC[19], IC[19], IC[19], IC[19], IC[22], IC[22], IC[25], IC[25], IC[25], IC[25]],
            [IC[19], IC[19], IC[19], IC[19], IC[22], IC[22], IC[25], IC[25], IC[25], IC[25]]
        ]

        # ============== sein_droit ================#
        valeurs_BrRight_hg = [
            [IC[21 + 32], IC[21 + 32], IC[21 + 32], IC[18 + 32], IC[18 + 32], IC[18 + 32], IC[18 + 32], IC[18 + 32],
             IC[12 + 32], IC[12 + 32]],
            [IC[21 + 32], IC[21 + 32], IC[21 + 32], IC[18 + 32], IC[18 + 32], IC[18 + 32], IC[18 + 32], IC[18 + 32],
             IC[12 + 32], IC[12 + 32]],
            [IC[21 + 32], IC[21 + 32], IC[21 + 32], IC[18 + 32], IC[18 + 32], IC[18 + 32], IC[18 + 32], IC[18 + 32],
             IC[12 + 32], IC[12 + 32]],
            [IC[21 + 32], IC[21 + 32], IC[21 + 32], IC[18 + 32], IC[18 + 32], IC[18 + 32], IC[18 + 32], IC[18 + 32],
             IC[12 + 32], IC[12 + 32]],
            [IC[21 + 32], IC[21 + 32], IC[21 + 32], IC[18 + 32], IC[18 + 32], IC[18 + 32], IC[18 + 32], IC[18 + 32],
             IC[12 + 32], IC[12 + 32]],
            [IC[20 + 32], IC[20 + 32], IC[20 + 32], IC[17 + 32], IC[17 + 32], IC[17 + 32], IC[17 + 32], IC[17 + 32],
             IC[13 + 32], IC[13 + 32]],
            [IC[20 + 32], IC[20 + 32], IC[20 + 32], IC[17 + 32], IC[17 + 32], IC[17 + 32], IC[17 + 32], IC[17 + 32],
             IC[13 + 32], IC[13 + 32]],
            [IC[20 + 32], IC[20 + 32], IC[20 + 32], IC[17 + 32], IC[17 + 32], IC[17 + 32], IC[17 + 32], IC[17 + 32],
             IC[13 + 32], IC[13 + 32]],
            [IC[20 + 32], IC[20 + 32], IC[20 + 32], IC[17 + 32], IC[17 + 32], IC[17 + 32], IC[17 + 32], IC[17 + 32],
             IC[13 + 32], IC[13 + 32]],
            [IC[20 + 32], IC[20 + 32], IC[20 + 32], IC[17 + 32], IC[17 + 32], IC[17 + 32], IC[17 + 32], IC[17 + 32],
             IC[13 + 32], IC[13 + 32]],
            [IC[15 + 32], IC[15 + 32], IC[15 + 32], IC[16 + 32], IC[16 + 32], IC[16 + 32], IC[16 + 32], IC[16 + 32],
             IC[14 + 32], IC[14 + 32]],
            [IC[15 + 32], IC[15 + 32], IC[15 + 32], IC[16 + 32], IC[16 + 32], IC[16 + 32], IC[16 + 32], IC[16 + 32],
             IC[14 + 32], IC[14 + 32]],
            [IC[15 + 32], IC[15 + 32], IC[15 + 32], IC[16 + 32], IC[16 + 32], IC[16 + 32], IC[16 + 32], IC[16 + 32],
             IC[14 + 32], IC[14 + 32]],
            [IC[15 + 32], IC[15 + 32], IC[15 + 32], IC[16 + 32], IC[16 + 32], IC[16 + 32], IC[16 + 32], IC[16 + 32],
             IC[14 + 32], IC[14 + 32]],
            [IC[19 + 32], IC[19 + 32], IC[19 + 32], IC[19 + 32], IC[16 + 32], IC[16 + 32], IC[16 + 32], IC[14 + 32],
             IC[14 + 32], IC[14 + 32]],
            [IC[19 + 32], IC[19 + 32], IC[19 + 32], IC[19 + 32], IC[16 + 32], IC[16 + 32], IC[16 + 32], IC[14 + 32],
             IC[14 + 32], IC[14 + 32]],
            [IC[19 + 32], IC[19 + 32], IC[19 + 32], IC[19 + 32], IC[16 + 32], IC[16 + 32], IC[16 + 32], IC[14 + 32],
             IC[14 + 32], IC[14 + 32]],
            [IC[19 + 32], IC[19 + 32], IC[19 + 32], IC[19 + 32], IC[19 + 32], IC[19 + 32], IC[19 + 32], IC[14 + 32],
             IC[14 + 32], IC[14 + 32]]
        ]
        valeurs_BrRight_hd = [
            [IC[12 + 32], IC[12 + 32], IC[0 + 32], IC[0 + 32], IC[0 + 32], IC[0 + 32], IC[0 + 32], IC[0 + 32],
             IC[9 + 32],
             IC[9 + 32]],
            [IC[12 + 32], IC[12 + 32], IC[0 + 32], IC[0 + 32], IC[0 + 32], IC[0 + 32], IC[0 + 32], IC[0 + 32],
             IC[9 + 32],
             IC[9 + 32]],
            [IC[12 + 32], IC[12 + 32], IC[3 + 32], IC[3 + 32], IC[0 + 32], IC[0 + 32], IC[1 + 32], IC[1 + 32],
             IC[9 + 32],
             IC[9 + 32]],
            [IC[12 + 32], IC[12 + 32], IC[3 + 32], IC[3 + 32], IC[2 + 32], IC[2 + 32], IC[1 + 32], IC[1 + 32],
             IC[9 + 32],
             IC[9 + 32]],
            [IC[12 + 32], IC[12 + 32], IC[3 + 32], IC[3 + 32], IC[2 + 32], IC[2 + 32], IC[1 + 32], IC[1 + 32],
             IC[10 + 32],
             IC[10 + 32]],
            [IC[12 + 32], IC[12 + 32], IC[3 + 32], IC[3 + 32], IC[2 + 32], IC[2 + 32], IC[1 + 32], IC[1 + 32],
             IC[10 + 32],
             IC[10 + 32]],
            [IC[13 + 32], IC[13 + 32], IC[3 + 32], IC[3 + 32], IC[2 + 32], IC[2 + 32], IC[1 + 32], IC[1 + 32],
             IC[10 + 32],
             IC[10 + 32]],
            [IC[13 + 32], IC[13 + 32], IC[5 + 32], IC[5 + 32], IC[2 + 32], IC[2 + 32], IC[6 + 32], IC[6 + 32],
             IC[10 + 32],
             IC[10 + 32]],
            [IC[13 + 32], IC[13 + 32], IC[5 + 32], IC[5 + 32], IC[4 + 32], IC[4 + 32], IC[6 + 32], IC[6 + 32],
             IC[11 + 32],
             IC[11 + 32]],
            [IC[13 + 32], IC[13 + 32], IC[5 + 32], IC[5 + 32], IC[4 + 32], IC[4 + 32], IC[6 + 32], IC[6 + 32],
             IC[11 + 32],
             IC[11 + 32]],
            [IC[13 + 32], IC[13 + 32], IC[5 + 32], IC[5 + 32], IC[4 + 32], IC[4 + 32], IC[6 + 32], IC[6 + 32],
             IC[11 + 32],
             IC[11 + 32]],
            [IC[14 + 32], IC[14 + 32], IC[14 + 32], IC[7 + 32], IC[7 + 32], IC[7 + 32], IC[7 + 32], IC[31 + 32],
             IC[31 + 32], IC[31 + 32]],
            [IC[14 + 32], IC[14 + 32], IC[14 + 32], IC[7 + 32], IC[7 + 32], IC[7 + 32], IC[7 + 32], IC[31 + 32],
             IC[31 + 32], IC[31 + 32]],
            [IC[14 + 32], IC[14 + 32], IC[14 + 32], IC[7 + 32], IC[7 + 32], IC[7 + 32], IC[7 + 32], IC[31 + 32],
             IC[31 + 32], IC[31 + 32]],
            [IC[14 + 32], IC[14 + 32], IC[14 + 32], IC[8 + 32], IC[8 + 32], IC[8 + 32], IC[8 + 32], IC[31 + 32],
             IC[31 + 32], IC[31 + 32]],
            [IC[14 + 32], IC[14 + 32], IC[14 + 32], IC[8 + 32], IC[8 + 32], IC[8 + 32], IC[8 + 32], IC[31 + 32],
             IC[31 + 32], IC[31 + 32]],
            [IC[14 + 32], IC[14 + 32], IC[14 + 32], IC[8 + 32], IC[8 + 32], IC[8 + 32], IC[8 + 32], IC[31 + 32],
             IC[31 + 32], IC[31 + 32]],
            [IC[14 + 32], IC[14 + 32], IC[14 + 32], IC[8 + 32], IC[8 + 32], IC[8 + 32], IC[8 + 32], IC[31 + 32],
             IC[31 + 32], IC[31 + 32]]
        ]
        valeurs_BrRight_bg = [
            [IC[27 + 32], IC[27 + 32], IC[27 + 32], IC[24 + 32], IC[24 + 32], IC[24 + 32], IC[24 + 32], IC[21 + 32],
             IC[21 + 32], IC[21 + 32]],
            [IC[27 + 32], IC[27 + 32], IC[27 + 32], IC[24 + 32], IC[24 + 32], IC[24 + 32], IC[24 + 32], IC[21 + 32],
             IC[21 + 32], IC[21 + 32]],
            [IC[27 + 32], IC[27 + 32], IC[27 + 32], IC[24 + 32], IC[24 + 32], IC[24 + 32], IC[24 + 32], IC[21 + 32],
             IC[21 + 32], IC[21 + 32]],
            [IC[27 + 32], IC[27 + 32], IC[27 + 32], IC[24 + 32], IC[24 + 32], IC[24 + 32], IC[24 + 32], IC[21 + 32],
             IC[21 + 32], IC[21 + 32]],
            [IC[27 + 32], IC[27 + 32], IC[27 + 32], IC[24 + 32], IC[24 + 32], IC[24 + 32], IC[24 + 32], IC[21 + 32],
             IC[21 + 32], IC[21 + 32]],
            [IC[27 + 32], IC[27 + 32], IC[27 + 32], IC[24 + 32], IC[24 + 32], IC[24 + 32], IC[24 + 32], IC[20 + 32],
             IC[20 + 32], IC[20 + 32]],
            [IC[27 + 32], IC[27 + 32], IC[27 + 32], IC[23 + 32], IC[23 + 32], IC[23 + 32], IC[23 + 32], IC[20 + 32],
             IC[20 + 32], IC[20 + 32]],
            [IC[27 + 32], IC[27 + 32], IC[27 + 32], IC[23 + 32], IC[23 + 32], IC[23 + 32], IC[23 + 32], IC[20 + 32],
             IC[20 + 32], IC[20 + 32]],
            [IC[27 + 32], IC[27 + 32], IC[27 + 32], IC[23 + 32], IC[23 + 32], IC[23 + 32], IC[23 + 32], IC[20 + 32],
             IC[20 + 32], IC[20 + 32]],
            [IC[27 + 32], IC[27 + 32], IC[27 + 32], IC[23 + 32], IC[23 + 32], IC[23 + 32], IC[23 + 32], IC[20 + 32],
             IC[20 + 32], IC[20 + 32]],
            [IC[26 + 32], IC[26 + 32], IC[26 + 32], IC[23 + 32], IC[23 + 32], IC[23 + 32], IC[23 + 32], IC[15 + 32],
             IC[15 + 32], IC[15 + 32]],
            [IC[26 + 32], IC[26 + 32], IC[26 + 32], IC[22 + 32], IC[22 + 32], IC[22 + 32], IC[22 + 32], IC[15 + 32],
             IC[15 + 32], IC[15 + 32]],
            [IC[26 + 32], IC[26 + 32], IC[26 + 32], IC[22 + 32], IC[22 + 32], IC[22 + 32], IC[22 + 32], IC[15 + 32],
             IC[15 + 32], IC[15 + 32]],
            [IC[26 + 32], IC[26 + 32], IC[26 + 32], IC[22 + 32], IC[22 + 32], IC[22 + 32], IC[22 + 32], IC[15 + 32],
             IC[15 + 32], IC[15 + 32]],
            [IC[25 + 32], IC[25 + 32], IC[25 + 32], IC[22 + 32], IC[22 + 32], IC[22 + 32], IC[22 + 32], IC[19 + 32],
             IC[19 + 32], IC[19 + 32]],
            [IC[25 + 32], IC[25 + 32], IC[25 + 32], IC[22 + 32], IC[22 + 32], IC[22 + 32], IC[22 + 32], IC[19 + 32],
             IC[19 + 32], IC[19 + 32]],
            [IC[25 + 32], IC[25 + 32], IC[25 + 32], IC[25 + 32], IC[22 + 32], IC[22 + 32], IC[19 + 32], IC[19 + 32],
             IC[19 + 32], IC[19 + 32]],
            [IC[25 + 32], IC[25 + 32], IC[25 + 32], IC[25 + 32], IC[22 + 32], IC[22 + 32], IC[19 + 32], IC[19 + 32],
             IC[19 + 32], IC[19 + 32]]
        ]
        valeurs_BrRight_bd = [
            [IC[9 + 32], IC[9 + 32], IC[9 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[27 + 32],
             IC[27 + 32], IC[27 + 32]],
            [IC[9 + 32], IC[9 + 32], IC[9 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[27 + 32],
             IC[27 + 32], IC[27 + 32]],
            [IC[9 + 32], IC[9 + 32], IC[9 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[27 + 32],
             IC[27 + 32], IC[27 + 32]],
            [IC[9 + 32], IC[9 + 32], IC[9 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[27 + 32],
             IC[27 + 32], IC[27 + 32]],
            [IC[9 + 32], IC[9 + 32], IC[9 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[27 + 32],
             IC[27 + 32], IC[27 + 32]],
            [IC[10 + 32], IC[10 + 32], IC[10 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[27 + 32],
             IC[27 + 32], IC[27 + 32]],
            [IC[10 + 32], IC[10 + 32], IC[10 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[27 + 32],
             IC[27 + 32], IC[27 + 32]],
            [IC[10 + 32], IC[10 + 32], IC[10 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[30 + 32], IC[27 + 32],
             IC[27 + 32], IC[27 + 32]],
            [IC[10 + 32], IC[10 + 32], IC[10 + 32], IC[29 + 32], IC[29 + 32], IC[29 + 32], IC[29 + 32], IC[27 + 32],
             IC[27 + 32], IC[27 + 32]],
            [IC[11 + 32], IC[11 + 32], IC[11 + 32], IC[29 + 32], IC[29 + 32], IC[29 + 32], IC[29 + 32], IC[26 + 32],
             IC[26 + 32], IC[26 + 32]],
            [IC[11 + 32], IC[11 + 32], IC[11 + 32], IC[29 + 32], IC[29 + 32], IC[29 + 32], IC[29 + 32], IC[26 + 32],
             IC[26 + 32], IC[26 + 32]],
            [IC[11 + 32], IC[11 + 32], IC[11 + 32], IC[29 + 32], IC[29 + 32], IC[29 + 32], IC[29 + 32], IC[26 + 32],
             IC[26 + 32], IC[26 + 32]],
            [IC[31 + 32], IC[31 + 32], IC[31 + 32], IC[28 + 32], IC[28 + 32], IC[28 + 32], IC[28 + 32], IC[25 + 32],
             IC[25 + 32], IC[25 + 32]],
            [IC[31 + 32], IC[31 + 32], IC[31 + 32], IC[28 + 32], IC[28 + 32], IC[28 + 32], IC[28 + 32], IC[25 + 32],
             IC[25 + 32], IC[25 + 32]],
            [IC[31 + 32], IC[31 + 32], IC[31 + 32], IC[28 + 32], IC[28 + 32], IC[28 + 32], IC[28 + 32], IC[25 + 32],
             IC[25 + 32], IC[25 + 32]],
            [IC[31 + 32], IC[31 + 32], IC[31 + 32], IC[28 + 32], IC[28 + 32], IC[28 + 32], IC[28 + 32], IC[25 + 32],
             IC[25 + 32], IC[25 + 32]],
            [IC[31 + 32], IC[31 + 32], IC[31 + 32], IC[28 + 32], IC[28 + 32], IC[28 + 32], IC[28 + 32], IC[25 + 32],
             IC[25 + 32], IC[25 + 32]],
            [IC[31 + 32], IC[31 + 32], IC[31 + 32], IC[28 + 32], IC[28 + 32], IC[28 + 32], IC[28 + 32], IC[25 + 32],
             IC[25 + 32], IC[25 + 32]]
        ]

        valeurs_sein_gauche = [
            valeurs_BrLeft_bd,
            valeurs_BrLeft_hd,
            valeurs_BrLeft_hg,
            valeurs_BrLeft_bg
        ]
        valeurs_sein_droit = [
            valeurs_BrRight_bd,
            valeurs_BrRight_hd,
            valeurs_BrRight_hg,
            valeurs_BrRight_bg
        ]

        # tmin = cv2.getTrackbarPos("Tmin x10", win_name) / 10.0
        # tmax = cv2.getTrackbarPos("Tmax x10", win_name) / 10.0
        seuil = 35
        gamma_track = 0.5
        if tmax <= tmin + 0.1: tmax = tmin + 0.1

        img = img_base.copy()

        # ---------------- Sein gauche ----------------
        gx_g, gy_g, gz_g, mask_g = compute_grid(centre_gauche, rayons, nb_sections, valeurs_sein_gauche, grid_res=360)
        gz_smooth_g, mask_roi_g, offset_g = render_heatmap_on_image(img, centre_gauche, gx_g, gy_g, gz_g, mask_g, tmin,
                                                                    seuil_chaud_init, gamma=gamma_track)
        chaud_g, pct_g = detect_hot_zones_and_smooth(gz_smooth_g, mask_g, seuil)
        annotations_g = draw_contours_and_boxes(img, centre_gauche, chaud_g, gz_smooth_g, offset_info=offset_g,
                                                couleur=(0, 0, 200))

        # ---------------- Sein droit ----------------
        gx_d, gy_d, gz_d, mask_d = compute_grid(centre_droit, rayons, nb_sections, valeurs_sein_droit, grid_res=360)
        gz_smooth_d, mask_roi_d, offset_d = render_heatmap_on_image(img, centre_droit, gx_d, gy_d, gz_d, mask_d, tmin,
                                                                    seuil_chaud_init,
                                                                    gamma=gamma_track)
        chaud_d, pct_d = detect_hot_zones_and_smooth(gz_smooth_d, mask_d, seuil)
        annotations_d = draw_contours_and_boxes(img, centre_droit, chaud_d, gz_smooth_d, offset_info=offset_d,
                                                couleur=(0, 0, 200))

        # ---------------- Détection des zones d'asymétrie ----------------
        seuil_asymetrie = 0.5  # Seuil d'asymétrie en °C
        zones_asym_g = detecter_zones_asymetrie(gz_smooth_g, gz_smooth_d, seuil_asymetrie)
        zones_asym_d = detecter_zones_asymetrie(gz_smooth_d, gz_smooth_g, seuil_asymetrie)

        # Dessiner les contours d'asymétrie (en jaune/cyan)
        nb_zones_asym_g = dessiner_contours_asymetrie(img, centre_gauche, zones_asym_g, gz_smooth_g,
                                                      offset_info=offset_g, couleur=(0, 255, 255))  # Jaune
        nb_zones_asym_d = dessiner_contours_asymetrie(img, centre_droit, zones_asym_d, gz_smooth_d,
                                                      offset_info=offset_d, couleur=(255, 255, 0))  # Cyan

        # ---------------- Stockage grilles ----------------
        last_grids['gauche'] = (gx_g, gy_g, gz_smooth_g, mask_g)
        last_grids['droit'] = (gx_d, gy_d, gz_smooth_d, mask_d)

        # ---------------- Statistiques ----------------
        mean_g, mean_d = float(np.nanmean(gz_smooth_g)), float(np.nanmean(gz_smooth_d))
        min_g, max_g = float(np.nanmin(gz_smooth_g)), float(np.nanmax(gz_smooth_g))
        min_d, max_d = float(np.nanmin(gz_smooth_d)), float(np.nanmax(gz_smooth_d))

        # Calcul de l'asymétrie globale
        diff_grid = np.abs(gz_smooth_g - gz_smooth_d)
        asym = float(np.nanmax(diff_grid)) if np.any(~np.isnan(diff_grid)) else 0.0
        asym = round(asym, 2)

        alert = (pct_g > 10.0 or pct_d > 10.0 or asym > 1.5 or nb_zones_asym_g > 0 or nb_zones_asym_d > 0)

        # ---------------- Colorbar centrale ----------------
        bar_h, bar_w = 450, 10
        bar = np.linspace(seuil_chaud_init, tmin, bar_h).reshape(bar_h, 1)
        denom = max(1e-6, seuil_chaud_init - tmin)
        bar_norm = ((bar - tmin) / denom * 255).astype(np.uint8)
        bar_img = cv2.applyColorMap(bar_norm, cv2.COLORMAP_JET)
        x_bar = (centre_gauche[0] + centre_droit[0]) // 2 - bar_w // 2
        y_bar = (screen_height // 2) - bar_h // 2
        img[y_bar:y_bar + bar_h, x_bar:x_bar + bar_w] = cv2.resize(bar_img, (bar_w, bar_h))

        cv2.putText(img, f"{seuil_chaud_init:.1f}", (x_bar + bar_w + 10, y_bar + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 10, 10), 2)
        cv2.putText(img, f"{tmin:.1f}", (x_bar + bar_w + 10, y_bar + bar_h - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 10, 10), 2)
        cv2.putText(img, "Temp (C)", (x_bar - 15, y_bar - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 20, 20), 2)

        # ---------------- Overlay anatomique ----------------
        if overlay_on:
            draw_anatomical_overlay(img, centre_gauche, max_radius, alpha=0.22)
            draw_anatomical_overlay(img, centre_droit, max_radius, alpha=0.22)

        # ==================== Ajouter labels ====================
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.9
        color = (0, 0, 0)
        thickness = 2
        offset_y = 80

        # Calculer la largeur du texte pour le centrer
        text_left = "Cup C Br-Left"
        text_right = "Cup C Br-Right"

        (text_width_left, text_height_left), _ = cv2.getTextSize(text_left, font, font_scale, thickness)
        (text_width_right, text_height_right), _ = cv2.getTextSize(text_right, font, font_scale, thickness)

        # Centrer horizontalement et placer en bas
        cv2.putText(img, text_left,
                    (centre_gauche[0] - text_width_left // 2, centre_gauche[1] + max(rayons) + offset_y),
                    font, font_scale, color, thickness)
        cv2.putText(img, text_right,
                    (centre_droit[0] - text_width_right // 2, centre_droit[1] + max(rayons) + offset_y),
                    font, font_scale, color, thickness)

        # ---------------- Créer une image "propre" pour le zoom (sans annotations d'asymétrie) ----------------
        img_clean = img_base.copy()

        # Recréer les heatmaps sans les annotations d'asymétrie
        gz_smooth_g_clean, mask_roi_g_clean, offset_g_clean = render_heatmap_on_image(
            img_clean, centre_gauche, gx_g, gy_g, gz_g, mask_g, tmin, seuil_chaud_init, gamma=gamma_track)
        gz_smooth_d_clean, mask_roi_d_clean, offset_d_clean = render_heatmap_on_image(
            img_clean, centre_droit, gx_d, gy_d, gz_d, mask_d, tmin, seuil_chaud_init, gamma=gamma_track)

        # Dessiner seulement les contours des zones chaudes (pas d'asymétrie)
        annotations_g_clean = draw_contours_and_boxes(img_clean, centre_gauche, chaud_g, gz_smooth_g_clean,
                                                      offset_info=offset_g_clean, couleur=(0, 0, 200))
        annotations_d_clean = draw_contours_and_boxes(img_clean, centre_droit, chaud_d, gz_smooth_d_clean,
                                                      offset_info=offset_d_clean, couleur=(0, 0, 200))

        # Colorbar centrale pour l'image propre
        img_clean[y_bar:y_bar + bar_h, x_bar:x_bar + bar_w] = cv2.resize(bar_img, (bar_w, bar_h))
        cv2.putText(img_clean, f"{tmax:.1f}", (x_bar + bar_w + 10, y_bar + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 10, 10), 2)
        cv2.putText(img_clean, f"{tmin:.1f}", (x_bar + bar_w + 10, y_bar + bar_h - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 10, 10), 2)
        cv2.putText(img_clean, "Temp (C)", (x_bar - 15, y_bar - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 20, 20), 2)

        # Overlay anatomique pour l'image propre
        if overlay_on:
            draw_anatomical_overlay(img_clean, centre_gauche, max_radius, alpha=0.22)
            draw_anatomical_overlay(img_clean, centre_droit, max_radius, alpha=0.22)

        # Labels pour l'image propre
        cv2.putText(img_clean, text_left,
                    (centre_gauche[0] - text_width_left // 2, centre_gauche[1] + max(rayons) + offset_y),
                    font, font_scale, color, thickness)
        cv2.putText(img_clean, text_right,
                    (centre_droit[0] - text_width_right // 2, centre_droit[1] + max(rayons) + offset_y),
                    font, font_scale, color, thickness)

        # Stocker l'image propre pour le zoom
        param_images['img_clean_for_zoom'] = img_clean.copy()

        # ---------------- Panneau info À GAUCHE ----------------
        panel_width = 500
        panel_height = 450
        panel_x = 20
        panel_y = (screen_height - panel_height) // 2

        draw_info_panel(img, panel_x, panel_y, panel_width, panel_height,
                        min_g, max_g, mean_g,
                        min_d, max_d, mean_d,
                        pct_g, pct_d, asym, seuil,
                        nb_zones_asym_g, nb_zones_asym_d,
                        alert)

        # ---------------- Info bas ----------------
        # cv2.putText(img, "Touches: s=save PNG | c=CSV | o=overlay | q/Esc=quit",
        #             (20, screen_height - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 30), 2)

        if last_save_time and time.time() - last_save_time < 2.0:
            cv2.putText(img, "Rapport sauvegarde", (screen_width - 250, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 120, 20), 2)

        param_images['img_for_mouse'] = img.copy()

        #cv2.imshow(win_name, img)

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

    # Vérification des paramètres
    if not video_file or not patient_id:
        return jsonify({'success': False, 'error': 'Aucun fichier vidéo fourni ou patient_id manquant.'}), 400

    # Vérification si l'ID du patient est un entier valide
    try:
        patient_id = int(patient_id)
    except ValueError:
        return jsonify({'success': False, 'error': 'patient_id invalide.'}), 400

    # Crée un timestamp pour le nom de fichier
    timestamp = int(time.time() * 1000)
    video_filename = f"{patient_id}_{timestamp}.webm"

    # Définit le dossier de destination
    upload_path = app.config.get('UPLOAD_FOLDER_videos', None)
    if not upload_path:
        return jsonify({'success': False, 'error': 'Le dossier de destination n\'est pas configuré.'}), 500

    # Crée le dossier si il n'existe pas
    if not os.path.exists(upload_path):
        try:
            os.makedirs(upload_path)
        except Exception as e:
            return jsonify({'success': False, 'error': f"Impossible de créer le dossier: {str(e)}"}), 500

    # Chemin complet du fichier
    file_path = os.path.join(upload_path, video_filename)
    print("Chemin final du fichier:", file_path)  # Pour debug

    # Sauvegarde du fichier et ajout en base
    try:
        video_file.save(file_path)

        # Crée un nouveau diagnostic
        new_diagnostic = Diagnostic(
            patient_id=patient_id,
            type='Vidéo',
            date=datetime.utcnow(),
            file=video_filename
        )
        db.session.add(new_diagnostic)
        db.session.commit()

        return jsonify({
            'success': True,
            'filename': video_filename,
            'date': datetime.utcnow().strftime('%d/%m/%Y %H:%M')
        })
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
     socketio.run(app,host='192.168.43.37', port=5000)

     #socketio.run(app,host='0.0.0.0', port=5000)
