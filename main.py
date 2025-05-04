# Import des bibliothèques nécessaires
import mysql.connector  # Pour la connexion à la base de données MySQL
from tkinter import *  # Pour l'interface graphique
from tkinter import messagebox, simpledialog  # Pour les boîtes de dialogue Tkinter
from datetime import date  # Pour manipuler les dates
import matplotlib.pyplot as plt  # Pour l'affichage des graphiques
from collections import defaultdict  # Pour créer des dictionnaires avec des listes par défaut

# Classe pour gérer la connexion à la base de données
class GestionExcuses:
    def __init__(self, host, user, password, database):
        # Connexion à MySQL
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()  # Création du curseur

    def close(self):
        # Fermeture du curseur et de la connexion
        self.cursor.close()
        self.connection.close()

# Classe représentant une excuse
class Excuse:
    def __init__(self, db, excuse=None, note=None, date_excuse=None, etudiant_id=None, id=None):
        self.db = db  # Référence à la connexion base de données
        self.cursor = self.db.cursor  # Raccourci vers le curseur
        self.excuse = excuse  # Texte de l'excuse
        self.note = note  # Note de crédibilité
        self.date_excuse = date_excuse  # Date de l'excuse
        self.etudiant_id = etudiant_id  # ID de l'étudiant associé
        self.id = id  # ID de l'excuse

    def ajouter(self):
        # Ajout d'une excuse dans la base de données
        query = "INSERT INTO excuses (excuse, etudiant_id, date_excuse, note_excuse) VALUES (%s, %s, %s, %s)"
        valeurs = (self.excuse, self.etudiant_id, self.date_excuse, self.note)
        self.cursor.execute(query, valeurs)
        self.db.connection.commit()  # Validation de la requête

    def modifier(self):
        # Modification d'une excuse existante
        query = "UPDATE excuses SET excuse = %s, etudiant_id = %s, date_excuse = %s, note_excuse = %s WHERE id = %s"
        valeurs = (self.excuse, self.etudiant_id, self.date_excuse, self.note, self.id)
        self.cursor.execute(query, valeurs)
        self.db.connection.commit()

    def supprimer(self):
        # Suppression d'une excuse
        query = "DELETE FROM excuses WHERE id = %s"
        self.cursor.execute(query, (self.id,))
        self.db.connection.commit()

    @staticmethod
    def recuperer_toutes(db):
        # Récupère toutes les excuses avec les noms des étudiants
        query = """SELECT excuses.id, etudiants.nom, excuses.excuse, excuses.date_excuse, excuses.note_excuse 
                   FROM excuses 
                   JOIN etudiants ON excuses.etudiant_id = etudiants.id"""
        db.cursor.execute(query)
        return db.cursor.fetchall()

# Classe représentant un étudiant
class Etudiant:
    def __init__(self, db, nom=None, prenom=None, email=None, date_inscription=None, id=None):
        self.db = db
        self.cursor = self.db.cursor
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.date_inscription = date_inscription
        self.id = id

    def ajouter(self):
        # Ajout d'un étudiant dans la base de données
        query = "INSERT INTO etudiants (nom, prenom, email, date_inscription) VALUES (%s, %s, %s, %s)"
        valeurs = (self.nom, self.prenom, self.email, self.date_inscription)
        self.cursor.execute(query, valeurs)
        self.db.connection.commit()

    @staticmethod
    def recuperer_tous(db):
        # Récupère tous les étudiants
        query = "SELECT id, nom, prenom FROM etudiants"
        db.cursor.execute(query)
        return db.cursor.fetchall()

# Interface graphique principale
class Interface:
    def __init__(self, root, db):
        self.db = db
        self.root = root
        self.root.title("Gestionnaire d'Excuses")  # Titre de la fenêtre

        # Liste des excuses
        self.listbox = Listbox(self.root, width=80)
        self.listbox.pack(pady=10)

        # Boutons pour les différentes actions
        self.btn_ajouter = Button(self.root, text="Ajouter une excuse", command=self.ajouter_excuse)
        self.btn_ajouter.pack(fill=X, padx=20, pady=2)

        self.btn_modifier = Button(self.root, text="Modifier une excuse", command=self.modifier_excuse)
        self.btn_modifier.pack(fill=X, padx=20, pady=2)

        self.btn_supprimer = Button(self.root, text="Supprimer une excuse", command=self.supprimer_excuse)
        self.btn_supprimer.pack(fill=X, padx=20, pady=2)

        self.btn_ajouter_etudiant = Button(self.root, text="Ajouter un étudiant", command=self.ajouter_etudiant)
        self.btn_ajouter_etudiant.pack(fill=X, padx=20, pady=10)

        self.btn_stats = Button(self.root, text="Voir les statistiques", command=self.afficher_statistiques)
        self.btn_stats.pack(fill=X, padx=20, pady=10)

        # Rafraîchit la liste des excuses au lancement
        self.refresh_excuses()

    def refresh_excuses(self):
        # Met à jour l'affichage de la liste des excuses
        self.listbox.delete(0, END)
        excuses = Excuse.recuperer_toutes(self.db)
        for e in excuses:
            self.listbox.insert(END, f"ID: {e[0]} | Étudiant: {e[1]} | Excuse: {e[2]} | Date: {e[3]} | Note: {e[4]}/5")

    def ajouter_excuse(self):
        # Permet d'ajouter une excuse via une boîte de dialogue
        etudiants = Etudiant.recuperer_tous(self.db)
        if not etudiants:
            messagebox.showwarning("Aucun étudiant", "Ajoutez d'abord un étudiant.")
            return

        # Choix de l'étudiant
        choix = [f"{id} - {nom} {prenom}" for id, nom, prenom in etudiants]
        etudiant_choisi = simpledialog.askstring("Étudiant", f"Choisissez un étudiant :\n" + "\n".join(choix))
        if not etudiant_choisi:
            return

        try:
            etudiant_id = int(etudiant_choisi.split(" - ")[0])  # Extraction de l'ID
        except (IndexError, ValueError):
            messagebox.showerror("Erreur", "Format invalide")
            return

        # Saisie des informations de l'excuse
        excuse = simpledialog.askstring("Excuse", "Entrez l'excuse")
        date_excuse = simpledialog.askstring("Date", "Entrez la date (YYYY-MM-DD)", initialvalue=str(date.today()))
        note = simpledialog.askfloat("Note", "Entrez la note sur 5")

        # Vérification des champs et ajout
        if etudiant_id and excuse and date_excuse and (note is not None):
            if 0 <= note <= 5:
                e = Excuse(self.db, excuse=excuse, date_excuse=date_excuse, note=note, etudiant_id=etudiant_id)
                e.ajouter()
                self.refresh_excuses()
            else:
                messagebox.showerror("Erreur", "La note doit être entre 0 et 5.")
        else:
            messagebox.showerror("Erreur", "Tous les champs sont obligatoires")

    def modifier_excuse(self):
        # Modifie une excuse sélectionnée dans la liste
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Sélection", "Sélectionnez une excuse")
            return

        index = selection[0]
        excuses = Excuse.recuperer_toutes(self.db)
        excuse_data = excuses[index]

        # Saisie des nouvelles valeurs
        excuse = simpledialog.askstring("Modifier excuse", "Nouvelle excuse :", initialvalue=excuse_data[2])
        date_excuse = simpledialog.askstring("Modifier date", "Nouvelle date :", initialvalue=str(excuse_data[3]))
        note = simpledialog.askfloat("Modifier note", "Nouvelle note sur 5 :", initialvalue=excuse_data[4])

        # Mise à jour
        if 0 <= note <= 5:
            e = Excuse(self.db, excuse=excuse, date_excuse=date_excuse, note=note, etudiant_id=None, id=excuse_data[0])
            e.modifier()
            self.refresh_excuses()
        else:
            messagebox.showerror("Erreur", "La note doit être entre 0 et 5.")

    def supprimer_excuse(self):
        # Supprime l'excuse sélectionnée
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Sélection", "Sélectionnez une excuse")
            return

        index = selection[0]
        excuses = Excuse.recuperer_toutes(self.db)
        e = Excuse(self.db, id=excuses[index][0])
        if messagebox.askyesno("Confirmer", "Voulez-vous vraiment supprimer cette excuse ?"):
            e.supprimer()
            self.refresh_excuses()

    def ajouter_etudiant(self):
        # Ajout d'un nouvel étudiant
        nom = simpledialog.askstring("Nom", "Nom de l'étudiant :")
        prenom = simpledialog.askstring("Prénom", "Prénom de l'étudiant :")
        email = simpledialog.askstring("Email", "Email de l'étudiant :")
        date_inscription = simpledialog.askstring("Date d'inscription", "Date (YYYY-MM-DD) :", initialvalue=str(date.today()))

        if nom and prenom and email and date_inscription:
            etu = Etudiant(self.db, nom=nom, prenom=prenom, email=email, date_inscription=date_inscription)
            try:
                etu.ajouter()
                messagebox.showinfo("Succès", "Étudiant ajouté avec succès !")
            except mysql.connector.errors.IntegrityError:
                messagebox.showerror("Erreur", "Email déjà utilisé")
        else:
            messagebox.showerror("Erreur", "Tous les champs sont obligatoires")

    def afficher_statistiques(self):
        # Affiche un graphique des excuses en fonction de leur note moyenne
        excuses = Excuse.recuperer_toutes(self.db)

        if not excuses:
            messagebox.showinfo("Statistiques", "Aucune excuse enregistrée.")
            return

        stats = defaultdict(list)

        for e in excuses:
            texte = e[2]
            note = e[4]
            if note is not None:
                stats[texte].append(note)

        noms = []
        moyennes = []

        for excuse, notes in stats.items():
            moyenne = sum(notes) / len(notes)
            noms.append(excuse)
            moyennes.append(moyenne)

        plt.figure(figsize=(10, 6))
        plt.barh(noms, moyennes, color="skyblue")
        plt.xlabel("Note moyenne sur 5")
        plt.title("Efficacité des excuses (note moyenne)")
        plt.tight_layout()
        plt.show()

# Point d’entrée de l’application
if __name__ == "__main__":
    db = GestionExcuses(host="localhost", user="etudiant", password="123", database="gestion_excuses")
    root = Tk()
    app = Interface(root, db)
    root.mainloop()  # Lancement de la boucle Tkinter
    db.close()  # Fermeture de la base de données
