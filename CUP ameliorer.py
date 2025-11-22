import cv2
import numpy as np
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter, binary_opening, binary_closing
import pandas as pd
import datetime
import os
import time

# -------------------- Réglages --------------------
screen_width = 1800
screen_height = 980
bg_color = 245
img_base = np.full((screen_height, screen_width, 3), bg_color, np.uint8)

max_radius = min(screen_width, screen_height) // 4
rayons = [max_radius - i * max(1, (max_radius // 18)) for i in range(18)]
nb_sections = 10

tmin_init = 31.0
tmax_init = 38.0
seuil_chaud_init = 37.5
lissage_sigma = 1.2

out_dir = "reports_thermo"
os.makedirs(out_dir, exist_ok=True)

# -------------------- Utilitaires --------------------
def extend_to_length(values, length):
    return [values[i % len(values)] for i in range(length)]

def compute_grid(centre, rayons, nb_sections, valeurs, grid_res=360):
    # construit points annulus -> grille carrée centrée sur centre, retournant mask circulaire
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
    # grille définie dans l'espace image (coordonnées réelles)
    grid_x, grid_y = np.mgrid[centre[0]-max_r:centre[0]+max_r:complex(grid_res),
                              centre[1]-max_r:centre[1]+max_r:complex(grid_res)]
    # interpolation sécurisée
    try:
        grid_z = griddata(points, vals, (grid_x, grid_y), method='linear')
    except Exception:
        grid_z = np.full(grid_x.shape, np.nan)
    mask = np.sqrt((grid_x-centre[0])**2 + (grid_y-centre[1])**2) <= max_r
    grid_z[~mask] = np.nan
    return grid_x, grid_y, grid_z, mask

def render_heatmap_on_image(img, centre, grid_x, grid_y, grid_z, mask, tmin, tmax, gamma=1.2):
    # remplit NaN par tmin pour l'affichage, lisse, normalise, applique colormap et copie dans ROI
    grid_z_filled = np.nan_to_num(grid_z, nan=tmin)
    grid_z_smooth = gaussian_filter(grid_z_filled, sigma=lissage_sigma)
    denom = max(1e-6, (tmax - tmin))
    grid_norm = np.clip((grid_z_smooth - tmin) / denom, 0, 1)
    grid_norm = (grid_norm ** gamma * 255).astype(np.uint8)
    heatmap = cv2.applyColorMap(grid_norm, cv2.COLORMAP_JET)

    max_r = max(rayons)
    # extraire ROI image et coller heatmap (prendre garde aux bords)
    x0 = max(0, centre[0]-max_r); y0 = max(0, centre[1]-max_r)
    x1 = min(screen_width, centre[0]+max_r); y1 = min(screen_height, centre[1]+max_r)
    w = x1 - x0; h = y1 - y0
    heatmap_resized = cv2.resize(heatmap, (w, h), interpolation=cv2.INTER_CUBIC)
    mask_resized = cv2.resize(mask.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST).astype(bool)
    roi = img[y0:y1, x0:x1]
    # copier seulement les pixels valides du mask
    np.copyto(roi, heatmap_resized, where=np.dstack([mask_resized]*3))
    img[y0:y1, x0:x1] = roi
    return grid_z_smooth, mask_resized, (x0, y0, w, h)

def detect_hot_zones_and_smooth(grid_z, mask, seuil):
    valid = ~np.isnan(grid_z)
    chaud = np.zeros_like(grid_z, dtype=bool)
    chaud[valid] = grid_z[valid] > seuil
    # nettoyage morphologique (évite petit bruit)
    chaud_clean = binary_opening(chaud, structure=np.ones((3,3)))
    chaud_clean = binary_closing(chaud_clean, structure=np.ones((5,5)))
    valid_count = np.count_nonzero(valid)
    pct = (np.count_nonzero(chaud_clean) / valid_count * 100.0) if valid_count else 0.0
    return chaud_clean, pct

def draw_contours_and_boxes(img, centre, bool_mask, grid_z, offset_info=None, couleur=(0,0,255)):
    """
    bool_mask : mask 2D de la grille (shape grid_h, grid_w)
    offset_info : (x0, y0, w, h) = position de la grille dans l'image (retour de render_heatmap_on_image)
    """
    if offset_info is None:
        return []
    x0, y0, w, h = offset_info
    mask_uint = (bool_mask.astype(np.uint8) * 255)
    contours, _ = cv2.findContours(mask_uint, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    annotations = []
    # paramètres d'échelle pour transformer coords grille -> image
    gh, gw = mask_uint.shape
    sx = w / max(1, gw)
    sy = h / max(1, gh)

    for c in contours:
        if cv2.contourArea(c) < 10:  # ignorer petits bruits
            continue
        x, y, cw, ch = cv2.boundingRect(c)
        area_pixels = cv2.contourArea(c)
        total_valid = np.count_nonzero(~np.isnan(grid_z))
        pct_area = (area_pixels / total_valid * 100) if total_valid else 0.0
        # poly transformée
        poly = c.squeeze().astype(np.float32)
        if poly.ndim == 1:
            continue
        poly[:,0] = poly[:,0]*sx + x0
        poly[:,1] = poly[:,1]*sy + y0
        pts = poly.reshape((-1,1,2)).astype(np.int32)
        cv2.polylines(img, [pts], True, couleur, 2, cv2.LINE_AA)
        # centroid
        M = cv2.moments(c)
        if M['m00'] != 0:
            cxg = int(M['m10']/M['m00']); cyg = int(M['m01']/M['m00'])
            cx = int(cxg * sx + x0); cy = int(cyg * sy + y0)
        else:
            cx = int(np.mean(poly[:,0])); cy = int(np.mean(poly[:,1]))
        label = f"{pct_area:.1f}%"
        # fond pour texte
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(img, (cx-tw//2-6, cy-th-10), (cx+tw//2+6, cy+4), (255,255,255), -1)
        cv2.putText(img, label, (cx-tw//2, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10,10,10), 1, cv2.LINE_AA)
        annotations.append((cx, cy, pct_area))
    return annotations

def grid_value_at_pixel(grid_z, centre, px, py):
    max_r = max(rayons)
    gx = grid_z.shape[1]
    gy = grid_z.shape[0]
    xi = int((px - (centre[0] - max_r)) / (2 * max_r) * gx)
    yi = int((py - (centre[1] - max_r)) / (2 * max_r) * gy)
    xi = np.clip(xi, 0, gx-1)
    yi = np.clip(yi, 0, gy-1)
    val = grid_z[yi, xi]
    return None if np.isnan(val) else float(val)

# -------------------- Données exemples --------------------
def make_example_values(low=33.0, high=37.5):
    return [[np.random.uniform(low, high, nb_sections) for _ in range(len(rayons))] for _ in range(4)]

valeurs_sein_gauche = make_example_values(33.0, 37.0)
valeurs_sein_droit  = make_example_values(33.2, 38.0)

centre_gauche = (screen_width // 2 - 340, screen_height // 2 + 20)
centre_droit  = (screen_width // 2 + 340, screen_height // 2 + 20)

# -------------------- Fenêtre et trackbars --------------------
win_name = "Thermo IA - Clinique (o = toggle overlay)"
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(win_name, 1200, 700)
cv2.createTrackbar("Tmin x10", win_name, int(tmin_init*10), 500, lambda v: None)
cv2.createTrackbar("Tmax x10", win_name, int(tmax_init*10), 500, lambda v: None)
cv2.createTrackbar("Seuil chaud x10", win_name, int(seuil_chaud_init*10), 500, lambda v: None)
cv2.createTrackbar("Gamma x10", win_name, int(12), 50, lambda v: None)

last_grids = {'gauche': None, 'droit': None}
param_images = {}
overlay_on = True  # overlay anatomique par défaut
last_save_time = 0

# -------------------- Dessin overlay anatomique --------------------
def draw_anatomical_overlay(img, centre, radius, alpha=0.22, color=(220,220,220)):
    overlay = img.copy()
    axes = (int(radius*0.95), int(radius*0.78))
    cv2.ellipse(overlay, centre, axes, 0, 0, 360, color, -1)
    # repères (sous-ton)
    cv2.line(overlay, (centre[0], centre[1]-axes[1]), (centre[0], centre[1]+axes[1]), (200,200,200), 1)
    cv2.line(overlay, (centre[0]-axes[0], centre[1]), (centre[0]+axes[0], centre[1]), (200,200,200), 1)
    cv2.addWeighted(overlay, alpha, img, 1-alpha, 0, img)

# -------------------- Mouse callback --------------------
zoom_window_name = "Zoom (clic gauche pour fermer)"
def on_mouse(event, x, y, flags, param):
    global overlay_on
    if event == cv2.EVENT_LBUTTONDOWN:
        for label, centre in [('gauche', centre_gauche), ('droit', centre_droit)]:
            if (x-centre[0])**2 + (y-centre[1])**2 <= max_radius**2:
                img_for_zoom = param_images.get('img_for_mouse', None)
                if img_for_zoom is not None:
                    # crop centré sur clic
                    w = int(max_radius*1.0); h = int(max_radius*1.0)
                    x0 = int(np.clip(x - w//2, 0, screen_width - w))
                    y0 = int(np.clip(y - h//2, 0, screen_height - h))
                    crop = img_for_zoom[y0:y0+h, x0:x0+w].copy()
                    crop_zoomed = cv2.resize(crop, (int(w*2.2), int(h*2.2)), interpolation=cv2.INTER_CUBIC)
                    cv2.imshow(zoom_window_name, crop_zoomed)
                break

    if event == cv2.EVENT_MOUSEMOVE:
        img_copy = param_images.get('img_for_mouse', None)
        if img_copy is None:
            return
        display_info = None
        for label, centre in [('gauche', centre_gauche), ('droit', centre_droit)]:
            grd = last_grids[label]
            if grd is None: continue
            gx, gy, gz, mask = grd
            if (x-centre[0])**2 + (y-centre[1])**2 <= max_radius**2:
                val = grid_value_at_pixel(gz, centre, x, y)
                if val is not None:
                    display_info = (label, val, x, y)
                break
        img_temp = img_copy.copy()
        if display_info:
            label, val, px, py = display_info
            txt = f"{label.upper()} : {val:.2f} °C"
            tx = px + 12 if px < screen_width-200 else px - 160
            ty = py - 10 if py > 40 else py + 20
            # fond semi-opaque
            (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(img_temp, (tx-6, ty-th-6), (tx+tw+6, ty+6), (255,255,255), -1)
            cv2.putText(img_temp, txt, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (10,10,10), 2, cv2.LINE_AA)
        cv2.imshow(win_name, img_temp)

cv2.setMouseCallback(win_name, on_mouse)

# -------------------- Panneau d'information (amélioré) --------------------
def draw_info_panel(img, x, y, width, height,
                    min_g, max_g, mean_g,
                    min_d, max_d, mean_d,
                    pct_g, pct_d, asym, seuil,
                    alert=False):
    overlay = img.copy()
    alpha = 0.95
    panel_color = (250, 250, 250)
    cv2.rectangle(overlay, (x, y), (x + width, y + height), panel_color, -1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

    # Bordure principale
    border_color = (0, 90, 200) if alert else (90, 90, 90)
    cv2.rectangle(img, (x, y), (x + width, y + height), border_color, 2, cv2.LINE_AA)

    # Titres et méta
    title = "ANALYSE THERMOGRAPHIQUE"
    cv2.putText(img, title, (x + 12, y + 30),
                cv2.FONT_HERSHEY_DUPLEX, 0.7, (10, 50, 120), 2)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(img, f"Patient : [Nom Prénom]", (x + 12, y + 58), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (30,30,30), 1)
    cv2.putText(img, f"Examinateur : [Dr. ...]", (x + 12, y + 58 + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (30,30,30), 1)
    cv2.putText(img, f"Date : {now}", (x + 12, y + 58 + 44), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (30,30,30), 1)

    # lignes séparatrices
    start_blocks = y + 58 + 66
    line_h = 24
    block_h = 3 * line_h + 14

    # SEIN GAUCHE
    yg = start_blocks
    cv2.rectangle(img, (x + 8, yg - 18), (x + width - 8, yg + block_h - 6), (225, 238, 255), -1)
    cv2.putText(img, "SEIN GAUCHE", (x + 14, yg), cv2.FONT_HERSHEY_SIMPLEX, 0.54, (0,40,140), 2)
    cv2.putText(img, f"Min: {min_g:.1f}  Max: {max_g:.1f}  Moy: {mean_g:.1f}", (x + 14, yg + line_h), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0,30,110), 1)
    cv2.putText(img, f"Zone chaude: {pct_g:.1f} %", (x + 14, yg + 2*line_h), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0,30,110), 1)
    # barre visuelle
    bar_x = x + 14; bar_y = yg + 2*line_h + 14
    bar_w = width - 40; bar_h_vis = 10
    cv2.rectangle(img, (bar_x, bar_y), (bar_x+bar_w, bar_y+bar_h_vis), (230,230,230), -1)
    filled_w = int(bar_w * min(pct_g/100.0, 1.0))
    cv2.rectangle(img, (bar_x, bar_y), (bar_x+filled_w, bar_y+bar_h_vis), (0,60,200), -1)

    # SEIN DROIT
    yd = yg + block_h + 12
    cv2.rectangle(img, (x + 8, yd - 18), (x + width - 8, yd + block_h - 6), (255, 235, 235), -1)
    cv2.putText(img, "SEIN DROIT", (x + 14, yd), cv2.FONT_HERSHEY_SIMPLEX, 0.54, (140,20,20), 2)
    cv2.putText(img, f"Min: {min_d:.1f}  Max: {max_d:.1f}  Moy: {mean_d:.1f}", (x + 14, yd + line_h), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (120,20,20), 1)
    cv2.putText(img, f"Zone chaude: {pct_d:.1f} %", (x + 14, yd + 2*line_h), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (120,20,20), 1)
    # barre visuelle
    bar_y2 = yd + 2*line_h + 14
    cv2.rectangle(img, (bar_x, bar_y2), (bar_x+bar_w, bar_y2+bar_h_vis), (230,230,230), -1)
    filled_w2 = int(bar_w * min(pct_d/100.0, 1.0))
    cv2.rectangle(img, (bar_x, bar_y2), (bar_x+filled_w2, bar_y2+bar_h_vis), (0,60,200), -1)

    # Asymétrie & seuil
    y_asym = bar_y2 + bar_h_vis + 18
    cv2.putText(img, f"Asymétrie moyenne: {asym:.2f} °C", (x + 12, y_asym), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (60,30,30), 1)
    cv2.putText(img, f"Seuil chaud: {seuil:.1f} °C", (x + 12, y_asym + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (30,30,30), 1)

    # Interprétation
    y_inter = y_asym + 46
    cv2.putText(img, "INTERPRÉTATION :", (x + 12, y_inter), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0,0,0), 1)
    y_inter += 22
    if alert:
        cv2.putText(img, "⚠ Suspicion d'activité locale - compléter par examens complémentaires", (x + 12, y_inter), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0,40,200), 1)
    else:
        cv2.putText(img, "✔ Symétrie et distribution thermique dans les limites observées", (x + 12, y_inter), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0,110,30), 1)

# -------------------- Boucle principale --------------------
while True:
    # Trackbars
    tmin = cv2.getTrackbarPos("Tmin x10", win_name) / 10.0
    tmax = cv2.getTrackbarPos("Tmax x10", win_name) / 10.0
    seuil = cv2.getTrackbarPos("Seuil chaud x10", win_name) / 10.0
    gamma_track = max(0.5, cv2.getTrackbarPos("Gamma x10", win_name) / 10.0)
    if tmax <= tmin + 0.1:
        tmax = tmin + 0.1

    img = img_base.copy()

    # Sein gauche
    gx_g, gy_g, gz_g, mask_g = compute_grid(centre_gauche, rayons, nb_sections, valeurs_sein_gauche, grid_res=360)
    gz_smooth_g, mask_roi_g, offset_g = render_heatmap_on_image(img, centre_gauche, gx_g, gy_g, gz_g, mask_g, tmin, tmax, gamma=gamma_track)
    chaud_g, pct_g = detect_hot_zones_and_smooth(gz_smooth_g, mask_g, seuil)
    annotations_g = draw_contours_and_boxes(img, centre_gauche, chaud_g, gz_smooth_g, offset_info=offset_g, couleur=(0,0,200))

    # Sein droit
    gx_d, gy_d, gz_d, mask_d = compute_grid(centre_droit, rayons, nb_sections, valeurs_sein_droit, grid_res=360)
    gz_smooth_d, mask_roi_d, offset_d = render_heatmap_on_image(img, centre_droit, gx_d, gy_d, gz_d, mask_d, tmin, tmax, gamma=gamma_track)
    chaud_d, pct_d = detect_hot_zones_and_smooth(gz_smooth_d, mask_d, seuil)
    annotations_d = draw_contours_and_boxes(img, centre_droit, chaud_d, gz_smooth_d, offset_info=offset_d, couleur=(0,0,200))

    # Stocker grilles pour callback souris
    # Stocke (gx, gy, gz_smooth, mask) - utile pour lecture pixel
    last_grids['gauche'] = (gx_g, gy_g, gz_smooth_g, mask_g)
    last_grids['droit']  = (gx_d, gy_d, gz_smooth_d, mask_d)

    # Statistiques (protéger NaN)
    try:
        mean_g = float(np.nanmean(gz_smooth_g))
        mean_d = float(np.nanmean(gz_smooth_d))
    except Exception:
        mean_g = mean_d = 0.0
    try:
        min_g  = float(np.nanmin(gz_smooth_g))
    except Exception:
        min_g = tmin
    try:
        max_g  = float(np.nanmax(gz_smooth_g))
    except Exception:
        max_g = tmin
    try:
        min_d  = float(np.nanmin(gz_smooth_d))
    except Exception:
        min_d = tmin
    try:
        max_d  = float(np.nanmax(gz_smooth_d))
    except Exception:
        max_d = tmin

    asym = abs(mean_g - mean_d)
    alert = (pct_g > 10.0 or pct_d > 10.0 or asym > 1.5)  # règle d'alerte (exemple)

    # Panneau d'information
    draw_info_panel(img, 10, 10, 380, 270,
                    min_g, max_g, mean_g,
                    min_d, max_d, mean_d,
                    pct_g, pct_d, asym, seuil,
                    alert)

    # Colorbar centrale (ajout de graduations)
    bar_h = 420; bar_w = 28
    bar = np.linspace(tmax, tmin, bar_h).reshape(bar_h, 1)
    denom = max(1e-6, (tmax - tmin))
    bar_norm = ((bar - tmin) / denom * 255).astype(np.uint8)
    bar_img = cv2.applyColorMap(bar_norm, cv2.COLORMAP_JET)
    x_bar = (centre_gauche[0] + centre_droit[0]) // 2 - bar_w//2
    y_bar = (screen_height//2) - bar_h//2
    img[y_bar:y_bar+bar_h, x_bar:x_bar+bar_w] = cv2.resize(bar_img, (bar_w, bar_h))
    # graduations textuelles
    cv2.putText(img, f"{tmax:.1f}", (x_bar+bar_w+8, y_bar+12), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (10,10,10),2)
    cv2.putText(img, f"{tmin:.1f}", (x_bar+bar_w+8, y_bar+bar_h-6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (10,10,10),2)
    cv2.putText(img, "Temp (°C)", (x_bar-10, y_bar-14), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (20,20,20),2)

    # annotations hotspots (liste)
    def draw_hotspot_list(img, annotations, x_start, y_start, title):
        cv2.putText(img, title, (x_start, y_start), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (20,20,20), 1)
        y = y_start + 20
        for i, (cx, cy, pct) in enumerate(annotations[:6]):
            txt = f"{i+1}. {pct:.1f}% @ ({cx},{cy})"
            cv2.putText(img, txt, (x_start, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (30,30,30), 1)
            y += 18
    draw_hotspot_list(img, annotations_g, 10, 300, "Hotspots sein gauche:")
    draw_hotspot_list(img, annotations_d, 10, 380, "Hotspots sein droit:")

    # Overlay anatomique
    if overlay_on:
        draw_anatomical_overlay(img, centre_gauche, max_radius, alpha=0.22)
        draw_anatomical_overlay(img, centre_droit, max_radius, alpha=0.22)

    # Info bas
    cv2.putText(img, "Touches: s=save PNG | c=CSV | o=overlay | q/Esc=quit", (20, screen_height-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30,30,30),2)

    # Indiquer dernière sauvegarde (petit feedback)
    if last_save_time and time.time() - last_save_time < 2.0:
        cv2.putText(img, "✔ Rapport sauvegardé", (screen_width-220, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20,120,20), 2)

    # Stocker image pour callback souris / zoom
    param_images['img_for_mouse'] = img.copy()
    cv2.imshow(win_name, img)

    # Gestion touches clavier
    key = cv2.waitKey(50) & 0xFF
    if key == ord('q') or key == 27:
        break
    if key == ord('o'):
        overlay_on = not overlay_on
    if key == ord('s'):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = os.path.join(out_dir, f"rapport_thermo_{ts}.png")
        cv2.imwrite(fname, img)
        last_save_time = time.time()
        print(f"[INFO] Rapport sauvegardé -> {fname}")
    if key == ord('c'):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        # Export des grilles (sauvegarde en csv avec NaN)
        csv_g = os.path.join(out_dir, f"grid_gauche_{ts}.csv")
        csv_d = os.path.join(out_dir, f"grid_droit_{ts}.csv")
        try:
            pd.DataFrame(gz_smooth_g).to_csv(csv_g, index=False, header=False)
            pd.DataFrame(gz_smooth_d).to_csv(csv_d, index=False, header=False)
            print(f"[INFO] CSV exportés -> {csv_g} , {csv_d}")
            last_save_time = time.time()
        except Exception as e:
            print("[ERR] Export CSV :", e)

cv2.destroyAllWindows()
