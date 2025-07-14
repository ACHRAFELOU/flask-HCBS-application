from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class Medecin(db.Model):
    __tablename__ = 'medecins'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    cin = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    specialite = db.Column(db.String(120), nullable=False)
    adresse = db.Column(db.String(200), nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(200), nullable=True)

    # Relation avec les patients
    patients = db.relationship('Patient', back_populates='medecin')

    # Relation avec les commentaires
    commentaires = db.relationship('Commentaire', back_populates='medecin')

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    cin = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    ville = db.Column(db.String(50), nullable=False)
    photo = db.Column(db.String(200), nullable=True)

    # Clé étrangère pour associer un médecin
    medecin_id = db.Column(db.Integer, db.ForeignKey('medecins.id'))
    medecin = db.relationship('Medecin', back_populates='patients')

    # Relation avec les diagnostics
    diagnostics = db.relationship('Diagnostic', back_populates='patient')
    # Relation avec les commentaires
    commentaires = db.relationship('Commentaire', back_populates='patient')
    consultations = db.relationship('Consultation', back_populates='patient', cascade="all, delete-orphan")
    sensor_values = db.Column(db.String(1000), nullable=True)
    sensor_data = db.Column(db.Text, nullable=True)


# Modèle Commentaire
class Commentaire(db.Model):
    __tablename__ = 'commentaire'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    contenu = db.Column(db.String)
    date_creation = db.Column(db.DateTime, default=db.func.current_timestamp())
    file = db.Column(db.String)
    diagnostic_id = db.Column(db.Integer, db.ForeignKey('diagnostic.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    medecin_id = db.Column(db.Integer, db.ForeignKey('medecins.id'))

    # Relations
    diagnostic = db.relationship('Diagnostic', back_populates='commentaires')
    patient = db.relationship('Patient', back_populates='commentaires')
    medecin = db.relationship('Medecin', back_populates='commentaires')

    reponses = relationship("ReponseCommentaire", back_populates="commentaire")
    def __repr__(self):
        return f"<Commentaire id={self.id}, text='{self.text}', file='{self.file}'>"

class ReponseCommentaire(db.Model):
    __tablename__ = 'reponse_commentaire'

    id = db.Column(db.Integer, primary_key=True)
    commentaire_id = db.Column(db.Integer, ForeignKey('commentaire.id'), nullable=False)
    patient_id = db.Column(db.Integer, ForeignKey('patients.id'), nullable=False)
    contenu = db.Column(db.Text, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

    commentaire = relationship("Commentaire", back_populates="reponses")
    patient = relationship("Patient")

# Modèle Diagnostic
class Diagnostic(db.Model):
    __tablename__ = 'diagnostic'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    file = db.Column(db.String(100), nullable=True)

    # Clé étrangère pour associer un patient
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)

    # Relation avec les commentaires
    commentaires = db.relationship('Commentaire', back_populates='diagnostic', cascade='all, delete-orphan')

    # Relation avec le patient
    patient = db.relationship('Patient', back_populates='diagnostics')

    # Relation pour les commentaires des patients
    commentaires_patient = db.relationship('CommentairePatient', back_populates='diagnostic', cascade='all, delete-orphan')
    sensor_data = db.Column(db.String, nullable=True)


class CommentairePatient(db.Model):
    __tablename__ = 'commentaire_patient'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    date_creation = db.Column(db.DateTime, default=db.func.current_timestamp())
    diagnostic_id = db.Column(db.Integer, db.ForeignKey('diagnostic.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))

    # Relations
    diagnostic = db.relationship('Diagnostic', back_populates='commentaires_patient')
    patient = db.relationship('Patient', backref='commentaires_patient')

class Consultation(db.Model):
    __tablename__ = 'consultation'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    file = db.Column(db.String(150), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    patient = db.relationship('Patient', back_populates='consultations')
    video_path = db.Column(db.String(255), nullable=True)
    # Ajoutez d'autres champs si nécessaire

