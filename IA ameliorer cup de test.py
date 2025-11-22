import cv2
import numpy as np
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
import pandas as pd
import datetime
import os

# -------------------- Paramètres écran / visuels --------------------
screen_width = 1800
screen_height = 980
bg_color = 245  # gris très clair
img_base = np.full((screen_height, screen_width, 3), bg_color, np.uint8)

max_radius = min(screen_width, screen_height) // 4
rayons = [max_radius - i * (max_radius // 18) for i in range(18)]
nb_sections = 10

# valeurs initiales (en °C)
tmin_init = 31.0
tmax_init = 38.0
seuil_chaud_init = 37.5
lissage_sigma = 1.2  # gaussien pour lisser la grille

# chemins de sauvegarde
out_dir = "reports_thermo"
os.makedirs(out_dir, exist_ok=True)

# -------------------- Fonctions utilitaires --------------------
def extend_to_length(values, length):
    return [values[i % len(values)] for i in range(length)]

def compute_grid(centre, rayons, nb_sections, valeurs, grid_res=500):
    """Construit la grille (grid_x, grid_y, grid_z non-normalisée) pour un centre."""
    points, vals = [], []
    pas = 90 / nb_sections
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
    grid_x, grid_y = np.mgrid[centre[0]-max_r:centre[0]+max_r:complex(grid_res),
                              centre[1]-max_r:centre[1]+max_r:complex(grid_res)]
    grid_z = griddata(points, vals, (grid_x, grid_y), method='linear')
    # mask circulaire (sein)
    mask = np.sqrt((grid_x-centre[0])**2 + (grid_y-centre[1])**2) <= max_r
    grid_z[~mask] = np.nan
    return grid_x, grid_y, grid_z, mask

def render_heatmap_on_image(img, centre, grid_x, grid_y, grid_z, mask, tmin, tmax, gamma=1.2):
    """Applique heatmap lissée sur l'image (inplace) et renvoie stats + mask chaud."""
    # Remplir NAN par tmin (visuel)
    grid_z_filled = np.nan_to_num(grid_z, nan=tmin)
    # Lissage pour rendre l'affichage plus clinique
    grid_z_smooth = gaussian_filter(grid_z_filled, sigma=lissage_sigma)
    # normaliser pour color map
    grid_norm = np.clip((grid_z_smooth - tmin) / (tmax - tmin), 0, 1)
    grid_norm = (grid_norm ** gamma * 255).astype(np.uint8)

    # Appliquer colormap
    heatmap = cv2.applyColorMap(grid_norm, cv2.COLORMAP_JET)

    max_r = max(rayons)
    roi = img[centre[1]-max_r:centre[1]+max_r, centre[0]-max_r:centre[0]+max_r]
    h, w = roi.shape[:2]
    heatmap_resized = cv2.resize(heatmap, (w, h))
    mask_resized = cv2.resize(mask.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST).astype(bool)
    np.copyto(roi, heatmap_resized, where=np.dstack([mask_resized]*3))

    return grid_z_smooth, mask_resized

def detect_hot_zones(grid_z, mask, seuil):
    """Retourne masque zones chaudes (bool), pourcentage de zone chaude (par rapport au sein)."""
    chaud = np.zeros_like(grid_z, dtype=bool)
    # considérer valeurs nan comme False
    valid = ~np.isnan(grid_z)
    chaud[valid] = grid_z[valid] > seuil
    # Pourcentage (par rapport aux points valides du sein)
    pct = 0.0
    valid_count = np.count_nonzero(valid)
    if valid_count > 0:
        pct = np.count_nonzero(chaud) / valid_count * 100.0
    return chaud, pct

def draw_contours_on_img(img, centre, mask_small, bool_mask, color=(0,0,255), thickness=2):
    """Projette contours de bool_mask (taille grid_res) sur img (en coordonnées réelles)."""
    # bool_mask correspond à la même taille que mask_small (grid resolution)
    # trouve contours
    mask_uint = (bool_mask.astype(np.uint8) * 255)
    contours, _ = cv2.findContours(mask_uint, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_r = max(rayons)
    # facteur de mise à l'échelle entre résolution grid (mask_small.shape) et pixels ROI (2*max_r)
    grid_h, grid_w = mask_small.shape
    scale_x = (2 * max_r) / grid_w
    scale_y = (2 * max_r) / grid_h
    for c in contours:
        if c.shape[0] < 5:  # ignorer petits bruits
            continue
        # convertir coordonnées grid -> image
        c = c.squeeze().astype(np.float32)
        c[:, 0] = c[:, 0] * scale_x + (centre[0] - max_r)
        c[:, 1] = c[:, 1] * scale_y + (centre[1] - max_r)
        pts = c.reshape((-1,1,2)).astype(np.int32)
        cv2.polylines(img, [pts], True, color, thickness, lineType=cv2.LINE_AA)

def grid_value_at_pixel(grid_x, grid_y, grid_z, centre, px, py):
    """Interpole la valeur à la position de la souris (px,py) si dans le sein."""
    max_r = max(rayons)
    x_idx = int((px - (centre[0] - max_r)) / (2 * max_r) * grid_z.shape[1])
    y_idx = int((py - (centre[1] - max_r)) / (2 * max_r) * grid_z.shape[0])
    x_idx = np.clip(x_idx, 0, grid_z.shape[1]-1)
    y_idx = np.clip(y_idx, 0, grid_z.shape[0]-1)
    val = grid_z[y_idx, x_idx]
    if np.isnan(val):
        return None
    return float(val)

# -------------------- Données exemples (remplacer par mesures réelles) --------------------
# -- pour garder la compatibilité avec ton format de valeurs (4 quadrants, 18 rayons, nb_sections)
def make_example_values(low=33.0, high=37.5):
    return [[np.random.uniform(low, high, nb_sections) for _ in range(len(rayons))] for _ in range(4)]

valeurs_sein_gauche = make_example_values(33.0, 37.0)
valeurs_sein_droit  = make_example_values(33.2, 38.0)

# -------------------- Centres et états init --------------------
centre_gauche = (screen_width // 2 - 340, screen_height // 2 + 20)
centre_droit  = (screen_width // 2 + 340, screen_height // 2 + 20)

# -------------------- Fenêtre et trackbars --------------------
win_name = "Thermo IA - Vue Clinique"
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(win_name, 1200, 700)
cv2.createTrackbar("Tmin x10", win_name, int(tmin_init*10), 500, lambda v: None)
cv2.createTrackbar("Tmax x10", win_name, int(tmax_init*10), 500, lambda v: None)
cv2.createTrackbar("Seuil chaud x10", win_name, int(seuil_chaud_init*10), 500, lambda v: None)
cv2.createTrackbar("Gamma x10", win_name, int(12), 50, lambda v: None)  # puissance visuelle

# stocker dernière grille pour interaction souris
last_grids = {
    'gauche': None,  # (grid_x, grid_y, grid_z, mask)
    'droit': None
}

# -------------------- Callback souris (affiche température) --------------------
def mouse_cb(event, x, y, flags, param):
    # param non utilisé - utilise last_grids
    if event == cv2.EVENT_MOUSEMOVE:
        display_info = None
        for label, centre in [('gauche', centre_gauche), ('droit', centre_droit)]:
            gx = last_grids[label]
            if gx is None:
                continue
            grid_x, grid_y, grid_z, mask = gx
            # vérifier si le point est dans le masque (sein)
            max_r = max(rayons)
            if (x - centre[0])**2 + (y - centre[1])**2 <= max_r**2:
                val = grid_value_at_pixel(grid_x, grid_y, grid_z, centre, x, y)
                if val is not None:
                    display_info = (label, val, centre)
                break
        # on écrit la valeur sur l'image en temps réel via modification globale de param (géré dans boucle principale)
        param_img = param_images.get('img_for_mouse', None)
        if param_img is not None:
            img_copy = param_img.copy()
            if display_info:
                label, val, centre = display_info
                txt = f"{label.upper()} : {val:.2f} °C"
                # positionner texte proche curseur, éviter hors écran
                tx = x + 10 if x < screen_width - 200 else x - 150
                ty = y - 10 if y > 30 else y + 20
                cv2.putText(img_copy, txt, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (10,10,10), 2, cv2.LINE_AA)
            cv2.imshow(win_name, img_copy)

# petit conteneur pour passer l'image actuelle au callback
param_images = {}

cv2.setMouseCallback(win_name, mouse_cb, param=None)

# -------------------- Boucle principale --------------------
while True:
    # lire trackbars
    tmin = cv2.getTrackbarPos("Tmin x10", win_name) / 10.0
    tmax = cv2.getTrackbarPos("Tmax x10", win_name) / 10.0
    seuil = cv2.getTrackbarPos("Seuil chaud x10", win_name) / 10.0
    gamma_track = max(1.0, cv2.getTrackbarPos("Gamma x10", win_name) / 10.0)

    if tmax <= tmin + 0.1:
        tmax = tmin + 0.1

    # image base pour rendre
    img = img_base.copy()

    # tracer heatmaps (gauche)
    grid_x_g, grid_y_g, grid_z_g, mask_g = compute_grid(centre_gauche, rayons, nb_sections, valeurs_sein_gauche, grid_res=500)
    grid_z_smooth_g, mask_roi_g = render_heatmap_on_image(img, centre_gauche, grid_x_g, grid_y_g, grid_z_g, mask_g, tmin, tmax, gamma=gamma_track)
    chaud_g, pct_g = detect_hot_zones(grid_z_smooth_g, mask_g, seuil)
    draw_contours_on_img(img, centre_gauche, mask_g, chaud_g, color=(0,0,255), thickness=2)

    # tracer heatmaps (droit)
    grid_x_d, grid_y_d, grid_z_d, mask_d = compute_grid(centre_droit, rayons, nb_sections, valeurs_sein_droit, grid_res=500)
    grid_z_smooth_d, mask_roi_d = render_heatmap_on_image(img, centre_droit, grid_x_d, grid_y_d, grid_z_d, mask_d, tmin, tmax, gamma=gamma_track)
    chaud_d, pct_d = detect_hot_zones(grid_z_smooth_d, mask_d, seuil)
    draw_contours_on_img(img, centre_droit, mask_d, chaud_d, color=(0,0,255), thickness=2)

    # stocker grilles pour callback souris
    last_grids['gauche'] = (grid_x_g, grid_y_g, grid_z_smooth_g, mask_g)
    last_grids['droit']  = (grid_x_d, grid_y_d, grid_z_smooth_d, mask_d)

    # dessiner colorbar centrale
    bar_h = 420
    bar_w = 28
    bar = np.linspace(tmax, tmin, bar_h).reshape(bar_h, 1)
    bar_norm = ((bar - tmin) / (tmax - tmin) * 255).astype(np.uint8)
    bar_img = cv2.applyColorMap(bar_norm, cv2.COLORMAP_JET)
    x_bar = (centre_gauche[0] + centre_droit[0]) // 2 - bar_w//2
    y_bar = (screen_height//2) - bar_h//2
    img[y_bar:y_bar+bar_h, x_bar:x_bar+bar_w] = cv2.resize(bar_img, (bar_w, bar_h))
    cv2.putText(img, f"{tmax:.1f}", (x_bar+bar_w+8, y_bar+12), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (10,10,10),2)
    cv2.putText(img, f"{tmin:.1f}", (x_bar+bar_w+8, y_bar+bar_h-6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (10,10,10),2)
    cv2.putText(img, "Temp (°C)", (x_bar-10, y_bar-14), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (20,20,20),2)

    # panneau info à droite
    panel_x = screen_width - 420
    cv2.rectangle(img, (panel_x, 20), (screen_width-10, screen_height-20), (255,255,255), -1)
    cv2.rectangle(img, (panel_x, 20), (screen_width-10, screen_height-20), (200,200,200), 1)
    # entête
    cv2.putText(img, "ANALYSE THERMOGRAPHIQUE ASSISTEE - IA", (panel_x+10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,60,120), 2)
    # informations patient / meta
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(img, f"Patient: [Nom Prénom]", (panel_x+12, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20,20,20),1)
    cv2.putText(img, f"Examinateur: [Dr. ...]", (panel_x+12, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (20,20,20),1)
    cv2.putText(img, f"Date: {now}", (panel_x+12, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (20,20,20),1)

    # statistiques numériques
    min_g = float(np.nanmin(grid_z_smooth_g))
    max_g = float(np.nanmax(grid_z_smooth_g))
    mean_g = float(np.nanmean(grid_z_smooth_g))
    min_d = float(np.nanmin(grid_z_smooth_d))
    max_d = float(np.nanmax(grid_z_smooth_d))
    mean_d = float(np.nanmean(grid_z_smooth_d))
    asym = abs(mean_g - mean_d)

    cv2.putText(img, "STATISTIQUES :", (panel_x+12, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0),2)
    cv2.putText(img, f"Gauche - min:{min_g:.2f} max:{max_g:.2f} moy:{mean_g:.2f}", (panel_x+12, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10,10,10),1)
    cv2.putText(img, f"Droit  - min:{min_d:.2f} max:{max_d:.2f} moy:{mean_d:.2f}", (panel_x+12, 235), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10,10,10),1)
    cv2.putText(img, f"Asymétrie (|moyG-moyD|): {asym:.2f} °C", (panel_x+12, 265), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (80,0,0),1)
    cv2.putText(img, f"Seuil chaud: {seuil:.1f} °C", (panel_x+12, 295), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10,10,10),1)
    cv2.putText(img, f"Zone chaude G: {pct_g:.1f} %", (panel_x+12, 325), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10,10,10),1)
    cv2.putText(img, f"Zone chaude D: {pct_d:.1f} %", (panel_x+12, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10,10,10),1)

    # interprétation rapide (règle simple IA heuristique)
    inter_y = 385
    cv2.putText(img, "INTERPRETATION (heuristique):", (panel_x+12, inter_y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,0,0),2)
    inter_y += 30
    if asym > 0.5 or pct_g > 15 or pct_d > 15:
        cv2.putText(img, "Suspicion d'activité locale - compléter par examens", (panel_x+12, inter_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,200),1)
    else:
        cv2.putText(img, "Symétrie thermique dans les limites attendues", (panel_x+12, inter_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,120,0),1)

    # titre principal
    cv2.putText(img, "Analyse thermographique assistée par IA", (screen_width//2 - 420, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,80),3)

    # boutons aide (textes)
    cv2.putText(img, "Touches: s=save rapport | c=export CSV | q/Esc=quitter", (20, screen_height-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30,30,30),2)

    # stocker image actuelle pour callback souris
    param_images['img_for_mouse'] = img.copy()
    # afficher
    cv2.imshow(win_name, img)

    # ---------- clavier ----------
    key = cv2.waitKey(50) & 0xFF
    if key == ord('q') or key == 27:
        break

    if key == ord('s'):  # sauvegarder image rapport
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = os.path.join(out_dir, f"rapport_thermo_{ts}.png")
        cv2.imwrite(fname, img)
        print(f"[INFO] Rapport sauvegardé -> {fname}")

    if key == ord('c'):  # exporter CSV des grilles (moyennes par pixel)
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_g = os.path.join(out_dir, f"grid_gauche_{ts}.csv")
        csv_d = os.path.join(out_dir, f"grid_droit_{ts}.csv")
        # convertir grid_z (lissé) en dataframe (attention grande taille)
        df_g = pd.DataFrame(grid_z_smooth_g)
        df_d = pd.DataFrame(grid_z_smooth_d)
        df_g.to_csv(csv_g, index=False, header=False)
        df_d.to_csv(csv_d, index=False, header=False)
        print(f"[INFO] CSV exportés -> {csv_g} , {csv_d}")

# fermeture
cv2.destroyAllWindows()
