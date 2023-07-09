import os
from PIL import Image, ImageTk, ExifTags
import tkinter as tk
import rawpy
import exifread


print("lancement du programme")
# Chemin du dossier contenant les photos
dossier_photos = "F:\Catalog\\04-07-23\DCIM\\104MSDCF"

# Affichage de la dernière photo ajoutée en plein écran
root = tk.Tk()
root.attributes("-fullscreen", True)

canvas = tk.Canvas(root, highlightthickness=0,bg="black")
canvas.pack(fill=tk.BOTH, expand=True)

photo = None  # Variable pour stocker l'objet PhotoImage
current_image = None  # Variable pour stocker l'image actuellement affichée
original_image = None  # Variable pour stocker l'image d'origine sans rotation
is_rotated = False  # Variable booléenne pour vérifier si l'image est tournée

def afficher_derniere_photo():
    global photo, current_image, original_image, is_rotated

    # Parcours du dossier pour trouver la dernière photo ajoutée
    fichiers = [f for f in os.listdir(dossier_photos) if os.path.isfile(os.path.join(dossier_photos, f))]
    fichiers_tries = sorted(fichiers, key=lambda x: os.path.getmtime(os.path.join(dossier_photos, x)), reverse=True)

    if fichiers_tries:
        chemin_fichier_recent = os.path.join(dossier_photos, fichiers_tries[0])
        largeur_ecran, hauteur_ecran = root.winfo_screenwidth(), root.winfo_screenheight()
        # Chargement de l'image et redimensionnement pour correspondre à l'écran
        if "ARW" in chemin_fichier_recent or "RAW" in chemin_fichier_recent:
            raw_file = chemin_fichier_recent
            raw = rawpy.imread(raw_file)
            rgb = raw.postprocess()
            image = Image.fromarray(rgb)
            
            with open(raw_file, 'rb') as f:
                exifr = exifread.process_file(f)
            orientation = exifr['Image Orientation'].values

        else : 
            image = Image.open(chemin_fichier_recent)
            
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation]=='Orientation':
                    break
            exif = image._getexif()
            try:
                orientation = exif[orientation]
            except : pass


        if orientation == 8:
            image=image.transpose(Image.ROTATE_90)
        largeur, hauteur = root.winfo_screenwidth(), root.winfo_screenheight()

        image.thumbnail((largeur, hauteur))

        photo = ImageTk.PhotoImage(image)
        canvas.delete("image")  # Supprimer uniquement les objets de type "image"
        canvas.config(width=largeur, height=hauteur)
        canvas.create_image((largeur_ecran-image.width)//2, 0, anchor="nw", image=photo, tags="image")

        # Mise à jour de l'image actuelle et de l'image d'origine
        current_image = image
        if original_image is None:
            original_image = image.copy()

    # Actualisation toutes les 2 secondes (ajustez si nécessaire)
    root.after(100, afficher_derniere_photo)

def rotate_image():
    global is_rotated

    if not is_rotated:
        is_rotated = True
        afficher_derniere_photo()

def reset_image():
    global is_rotated

    if is_rotated:
        is_rotated = False
        afficher_derniere_photo()

# Lancement de l'affichage de la dernière photo
afficher_derniere_photo()
print("programme lancé")
root.mainloop()
