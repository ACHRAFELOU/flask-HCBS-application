import sqlite3
import os
import traceback
from datetime import datetime


def add_date_evenement_to_notifications():
    """Ajoute la colonne date_evenement à la table notifications"""

    print("🔄 MIGRATION: AJOUT DE DATE_EVENEMENT")
    print("=" * 60)

    # Chercher la base de données
    db_locations = [
        'instance/database.db',
        'database.db',
        'app.db',
        'hcbs.db'
    ]

    db_path = None
    for location in db_locations:
        if os.path.exists(location):
            db_path = location
            print(f"📁 Base de données trouvée: {location}")
            break

    if not db_path:
        print("❌ Aucune base de données trouvée.")
        db_path = input("Entrez le chemin de votre base de données: ").strip()

    if not os.path.exists(db_path):
        print(f"❌ Le fichier {db_path} n'existe pas.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print(f"🎯 Migration de: {db_path}")

        # 1. Vérifier la structure actuelle
        print("\n📋 Structure actuelle de la table 'notifications':")
        cursor.execute("PRAGMA table_info(notifications)")
        columns = cursor.fetchall()

        print("-" * 80)
        print(f"{'Colonne':20} {'Type':15} {'Nullable':10} {'PK':5}")
        print("-" * 80)

        has_date_evenement = False
        for col in columns:
            col_id, name, col_type, notnull, default, pk = col
            nullable = "NULL" if not notnull else "NOT NULL"
            pk_str = "✓" if pk else ""

            if name == 'date_evenement':
                has_date_evenement = True
                print(f"{name:20} {col_type:15} {nullable:10} {pk_str:5} ← EXISTE DÉJÀ")
            else:
                print(f"{name:20} {col_type:15} {nullable:10} {pk_str:5}")

        if has_date_evenement:
            print("\n✅ La colonne 'date_evenement' existe déjà!")
            response = input("Voulez-vous quand même mettre à jour la structure? (o/n): ").lower()
            if response != 'o':
                conn.close()
                return

        # 2. Si date_evenement n'existe pas, l'ajouter
        if not has_date_evenement:
            print("\n➕ Ajout de la colonne 'date_evenement'...")

            try:
                # SQLite ne supporte pas ADD COLUMN IF NOT EXISTS, donc on vérifie d'abord
                cursor.execute("ALTER TABLE notifications ADD COLUMN date_evenement TIMESTAMP")
                print("✅ Colonne 'date_evenement' ajoutée")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print("⚠️  La colonne existe déjà (message d'erreur différent)")
                else:
                    raise e

        # 3. Mettre à jour les données existantes
        print("\n🔄 Mise à jour des données existantes...")

        # Compter les notifications
        cursor.execute("SELECT COUNT(*) FROM notifications")
        total = cursor.fetchone()[0]
        print(f"📊 Total notifications: {total}")

        if total > 0:
            # Mettre date_evenement = date_creation pour les anciennes notifications
            cursor.execute("""
                UPDATE notifications 
                SET date_evenement = date_creation 
                WHERE date_evenement IS NULL
            """)
            updated = cursor.rowcount
            print(f"✅ {updated} notifications mises à jour")

            # Vérifier le résultat
            cursor.execute("SELECT COUNT(*) FROM notifications WHERE date_evenement IS NOT NULL")
            with_date = cursor.fetchone()[0]
            print(f"📊 Notifications avec date_evenement: {with_date}/{total}")

        # 4. Vérifier et créer les index si nécessaire
        print("\n📈 Vérification des index...")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='notifications'")
        existing_indexes = [idx[0] for idx in cursor.fetchall()]

        # Index recommandés
        recommended_indexes = [
            ('idx_notif_date_evenement', 'CREATE INDEX idx_notif_date_evenement ON notifications(date_evenement)'),
            ('idx_notif_medecin_lu', 'CREATE INDEX idx_notif_medecin_lu ON notifications(medecin_id, lu)'),
            ('idx_notif_date_creation', 'CREATE INDEX idx_notif_date_creation ON notifications(date_creation)')
        ]

        for idx_name, idx_sql in recommended_indexes:
            if idx_name not in existing_indexes:
                try:
                    cursor.execute(idx_sql)
                    print(f"✅ Index créé: {idx_name}")
                except Exception as e:
                    print(f"⚠️  Impossible de créer l'index {idx_name}: {e}")

        # 5. Vérifier les clés étrangères
        print("\n🔗 Vérification des clés étrangères...")
        cursor.execute("PRAGMA foreign_key_list(notifications)")
        fks = cursor.fetchall()

        if fks:
            print("✅ Clés étrangères configurées:")
            for fk in fks:
                id, seq, table, from_col, to_col, on_update, on_delete, match = fk
                print(f"  - {from_col} → {table}({to_col})")
        else:
            print("⚠️  Aucune clé étrangère trouvée")
            print("   Assurez-vous que les tables 'medecins' et 'patients' existent")

        # 6. Activer les clés étrangères
        cursor.execute("PRAGMA foreign_keys = ON")

        conn.commit()

        # 7. Afficher la structure finale
        print("\n📋 Structure finale de la table 'notifications':")
        cursor.execute("PRAGMA table_info(notifications)")
        columns = cursor.fetchall()

        print("-" * 85)
        print(f"{'Colonne':20} {'Type':15} {'Nullable':10} {'Default':20}")
        print("-" * 85)

        expected_columns = [
            ('id', 'INTEGER', 'NOT NULL'),
            ('medecin_id', 'INTEGER', 'NOT NULL'),
            ('patient_id', 'INTEGER', 'NULL'),
            ('type', 'VARCHAR(50)', 'NULL'),
            ('message', 'TEXT', 'NOT NULL'),
            ('lu', 'BOOLEAN', 'NULL'),
            ('date_creation', 'DATETIME', 'NULL'),
            ('data', 'JSON', 'NULL'),
            ('date_evenement', 'TIMESTAMP', 'NULL')
        ]

        for expected_name, expected_type, expected_nullable in expected_columns:
            found = False
            for col in columns:
                col_id, name, col_type, notnull, default, pk = col
                if name == expected_name:
                    found = True
                    nullable = "NOT NULL" if notnull else "NULL"
                    default_str = f"DEFAULT {default}" if default else ""

                    status = "✓" if col_type.upper() == expected_type.upper() and nullable == expected_nullable else "⚠️"
                    print(f"{status} {name:20} {col_type:15} {nullable:10} {default_str:20}")
                    break

            if not found:
                print(f"❌ {expected_name:20} {'MISSING':15} {'':10} {'':20}")

        # 8. Vérifier la compatibilité avec le modèle
        print("\n" + "=" * 70)
        print("✅ VÉRIFICATION DE COMPATIBILITÉ AVEC VOTRE MODÈLE")
        print("=" * 70)

        print("Votre modèle attend ces colonnes:")
        print("""
1. id (INTEGER, PRIMARY KEY)
2. medecin_id (INTEGER, FOREIGN KEY)
3. patient_id (INTEGER, FOREIGN KEY)
4. type (VARCHAR(50))
5. message (TEXT)
6. lu (BOOLEAN)
7. date_creation (DATETIME)
8. date_evenement (DATETIME)  ← NOUVELLE COLONNE
""")

        print("📊 Résultat:")
        print("-" * 40)

        # Vérifier chaque colonne
        model_columns = ['id', 'medecin_id', 'patient_id', 'type', 'message', 'lu', 'date_creation', 'date_evenement']
        table_columns = [col[1] for col in columns]

        all_good = True
        for col in model_columns:
            if col in table_columns:
                print(f"✓ {col}")
            else:
                print(f"❌ {col} - MANQUANTE")
                all_good = False

        if all_good:
            print("\n🎉 PARFAIT ! Votre modèle est compatible avec la table.")
        else:
            print("\n⚠️  ATTENTION: Certaines colonnes sont manquantes.")
            print("   Recréez la table avec le script complet.")

        # 9. Tester avec une requête SQLAlchemy simulée
        print("\n🧪 TEST SIMULÉ DE REQUÊTE:")

        # Créer une notification de test
        if total == 0:
            print("Création d'une notification de test...")

            # Trouver un médecin et un patient
            cursor.execute("SELECT id FROM medecins LIMIT 1")
            medecin = cursor.fetchone()

            cursor.execute("SELECT id FROM patients LIMIT 1")
            patient = cursor.fetchone()

            if medecin and patient:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute("""
                    INSERT INTO notifications 
                    (medecin_id, patient_id, type, message, lu, date_creation, date_evenement, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    medecin[0], patient[0], 'test', 'Notification de test', 0, now, now, '{"test": true}'
                ))
                conn.commit()
                print("✅ Notification de test créée")

        # Afficher quelques notifications
        cursor.execute("""
            SELECT id, type, message, 
                   datetime(date_creation, 'localtime') as date_creation,
                   datetime(date_evenement, 'localtime') as date_evenement,
                   lu
            FROM notifications 
            ORDER BY id DESC 
            LIMIT 3
        """)
        notifications = cursor.fetchall()

        if notifications:
            print("\n📄 Dernières notifications:")
            print("-" * 100)
            for notif in notifications:
                id, type, message, date_creation, date_evenement, lu = notif
                lu_str = "✓" if lu else "✗"
                print(f"ID {id} [{type}] {lu_str}")
                print(f"  Message: {message[:60]}...")
                print(f"  Date création: {date_creation}")
                print(f"  Date événement: {date_evenement}")
                print()

        conn.close()

        print("\n" + "=" * 70)
        print("✅ MIGRATION TERMINÉE")
        print("=" * 70)
        print("\nProchaines étapes:")
        print("1. Redémarrez votre application Flask")
        print("2. Testez les notifications dans le dashboard médecin")
        print("3. Changez un patient de médecin pour tester les notifications")
        print("\nSi vous avez des erreurs, vérifiez que:")
        print("✓ Votre modèle Notification a bien la colonne date_evenement")
        print("✓ Vous utilisez Notification.date_evenement dans vos requêtes")
        print("✓ Les noms des tables dans les FOREIGN KEY sont corrects")
        print("=" * 70)

    except sqlite3.Error as e:
        print(f"❌ Erreur SQLite: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        traceback.print_exc()


def check_table_names(db_path):
    """Vérifie les noms exacts des tables"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("\n🔍 VÉRIFICATION DES NOMS DE TABLES:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        print("Tables disponibles:")
        for table in tables:
            print(f"  - {table[0]}")

        conn.close()
    except Exception as e:
        print(f"Erreur: {e}")


if __name__ == "__main__":
    print("""
    🚀 MIGRATION DE LA BASE DE DONNÉES
    ==================================
    Ce script va ajouter la colonne 'date_evenement'
    à votre table 'notifications' pour qu'elle corresponde
    à votre modèle SQLAlchemy.
    """)

    # Demander le chemin de la base
    default_db = 'instance/database.db'
    if os.path.exists(default_db):
        db_path = default_db
    else:
        db_path = input("Chemin de votre base de données [instance/database.db]: ").strip() or default_db

    if not os.path.exists(db_path):
        print(f"❌ Fichier non trouvé: {db_path}")
        exit(1)

    # Vérifier les noms de tables
    check_table_names(db_path)

    # Lancer la migration
    add_date_evenement_to_notifications()