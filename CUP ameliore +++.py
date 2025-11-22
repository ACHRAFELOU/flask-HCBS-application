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

tmin_init = 36.0
tmax_init = 37.0
seuil_chaud_init = 36.5
lissage_sigma = 1.2

out_dir = "reports_thermo"
os.makedirs(out_dir, exist_ok=True)

# ==================== Données réelles ====================
# === Valeurs Haut-Gauche ===
IC1 = 36;
IC2 = 36.2;
IC3 = 36.5;
IC4 = 36;
IC5 = 36.4;
IC6 = 36;
IC7 = 36;
IC8 = 36.9
IC9 = 36.8;
IC10 = 36.7;
IC11 = 36.2;
IC12 = 36;
IC13 = 36.8;
IC14 = 36.9;
IC15 = 36;
IC16 = 36.8
IC17 = 36.7;
IC18 = 36.2;
IC19 = 36;
IC20 = 36;
IC21 = 36.8;
IC22 = 36;
IC23 = 36.9;
IC24 = 36.8
IC25 = 36.4;
IC26 = 36;
IC27 = 36.5;
IC28 = 36;
IC29 = 36.9;
IC30 = 36;
IC31 = 36.8;
IC32 = 36.01

valeurs_BrLeft_hg = [
    [IC10, IC10, IC1, IC1, IC1, IC1, IC1, IC1, IC13, IC13],
    [IC10, IC10, IC1, IC1, IC1, IC1, IC1, IC1, IC13, IC13],
    [IC10, IC10, IC4, IC4, IC1, IC1, IC2, IC2, IC13, IC13],
    [IC10, IC10, IC4, IC4, IC3, IC3, IC2, IC2, IC13, IC13],
    [IC11, IC11, IC4, IC4, IC3, IC3, IC2, IC2, IC13, IC13],
    [IC11, IC11, IC4, IC4, IC3, IC3, IC2, IC2, IC13, IC13],
    [IC11, IC11, IC4, IC4, IC3, IC3, IC2, IC2, IC14, IC14],
    [IC11, IC11, IC6, IC6, IC3, IC3, IC7, IC7, IC14, IC14],
    [IC12, IC12, IC6, IC6, IC5, IC5, IC7, IC7, IC14, IC14],
    [IC12, IC12, IC6, IC6, IC5, IC5, IC7, IC7, IC14, IC14],
    [IC12, IC12, IC6, IC6, IC5, IC5, IC7, IC7, IC14, IC14],
    [IC32, IC32, IC32, IC8, IC8, IC8, IC8, IC15, IC15, IC15],
    [IC32, IC32, IC32, IC8, IC8, IC8, IC8, IC15, IC15, IC15],
    [IC32, IC32, IC32, IC8, IC8, IC8, IC8, IC15, IC15, IC15],
    [IC32, IC32, IC32, IC9, IC9, IC9, IC9, IC15, IC15, IC15],
    [IC32, IC32, IC32, IC9, IC9, IC9, IC9, IC15, IC15, IC15],
    [IC32, IC32, IC32, IC9, IC9, IC9, IC9, IC15, IC15, IC15],
    [IC32, IC32, IC32, IC9, IC9, IC9, IC9, IC15, IC15, IC15]
]
valeurs_BrLeft_hd = [
    [IC13, IC13, IC19, IC19, IC19, IC19, IC19, IC22, IC22, IC22],
    [IC13, IC13, IC19, IC19, IC19, IC19, IC19, IC22, IC22, IC22],
    [IC13, IC13, IC19, IC19, IC19, IC19, IC19, IC22, IC22, IC22],
    [IC13, IC13, IC19, IC19, IC19, IC19, IC19, IC22, IC22, IC22],
    [IC13, IC13, IC19, IC19, IC19, IC19, IC19, IC22, IC22, IC22],
    [IC14, IC14, IC18, IC18, IC18, IC18, IC18, IC21, IC21, IC21],
    [IC14, IC14, IC18, IC18, IC18, IC18, IC18, IC21, IC21, IC21],
    [IC14, IC14, IC18, IC18, IC18, IC18, IC18, IC21, IC21, IC21],
    [IC14, IC14, IC18, IC18, IC18, IC18, IC18, IC21, IC21, IC21],
    [IC14, IC14, IC18, IC18, IC18, IC18, IC18, IC21, IC21, IC21],
    [IC15, IC15, IC17, IC17, IC17, IC17, IC17, IC16, IC16, IC16],
    [IC15, IC15, IC17, IC17, IC17, IC17, IC17, IC16, IC16, IC16],
    [IC15, IC15, IC17, IC17, IC17, IC17, IC17, IC16, IC16, IC16],
    [IC15, IC15, IC17, IC17, IC17, IC17, IC17, IC16, IC16, IC16],
    [IC15, IC15, IC15, IC17, IC17, IC17, IC20, IC20, IC20, IC20],
    [IC15, IC15, IC15, IC17, IC17, IC17, IC20, IC20, IC20, IC20],
    [IC15, IC15, IC15, IC17, IC17, IC17, IC20, IC20, IC20, IC20],
    [IC15, IC15, IC15, IC20, IC20, IC20, IC20, IC20, IC20, IC20]
]
valeurs_BrLeft_bg = [
    [IC28, IC28, IC28, IC31, IC31, IC31, IC31, IC10, IC10, IC10],
    [IC28, IC28, IC28, IC31, IC31, IC31, IC31, IC10, IC10, IC10],
    [IC28, IC28, IC28, IC31, IC31, IC31, IC31, IC10, IC10, IC10],
    [IC28, IC28, IC28, IC31, IC31, IC31, IC31, IC10, IC10, IC10],
    [IC28, IC28, IC28, IC31, IC31, IC31, IC31, IC10, IC10, IC10],
    [IC28, IC28, IC28, IC31, IC31, IC31, IC31, IC11, IC11, IC11],
    [IC28, IC28, IC28, IC31, IC31, IC31, IC31, IC11, IC11, IC11],
    [IC28, IC28, IC28, IC31, IC31, IC31, IC31, IC11, IC11, IC11],
    [IC28, IC28, IC28, IC30, IC30, IC30, IC30, IC11, IC11, IC11],
    [IC27, IC27, IC27, IC30, IC30, IC30, IC30, IC12, IC12, IC12],
    [IC27, IC27, IC27, IC30, IC30, IC30, IC30, IC12, IC12, IC12],
    [IC27, IC27, IC27, IC30, IC30, IC30, IC30, IC12, IC12, IC12],
    [IC26, IC26, IC26, IC29, IC29, IC29, IC29, IC32, IC32, IC32],
    [IC26, IC26, IC26, IC29, IC29, IC29, IC29, IC32, IC32, IC32],
    [IC26, IC26, IC26, IC29, IC29, IC29, IC29, IC32, IC32, IC32],
    [IC26, IC26, IC26, IC29, IC29, IC29, IC29, IC32, IC32, IC32],
    [IC26, IC26, IC26, IC29, IC29, IC29, IC29, IC32, IC32, IC32],
    [IC26, IC26, IC26, IC29, IC29, IC29, IC29, IC32, IC32, IC32]
]
valeurs_BrLeft_bd = [
    [IC22, IC22, IC22, IC25, IC25, IC25, IC25, IC28, IC28, IC28],
    [IC22, IC22, IC22, IC25, IC25, IC25, IC25, IC28, IC28, IC28],
    [IC22, IC22, IC22, IC25, IC25, IC25, IC25, IC28, IC28, IC28],
    [IC22, IC22, IC22, IC25, IC25, IC25, IC25, IC28, IC28, IC28],
    [IC22, IC22, IC22, IC25, IC25, IC25, IC25, IC28, IC28, IC28],
    [IC21, IC21, IC21, IC25, IC25, IC25, IC25, IC28, IC28, IC28],
    [IC21, IC21, IC21, IC24, IC24, IC24, IC24, IC28, IC28, IC28],
    [IC21, IC21, IC21, IC24, IC24, IC24, IC24, IC28, IC28, IC28],
    [IC21, IC21, IC21, IC24, IC24, IC24, IC24, IC28, IC28, IC28],
    [IC21, IC21, IC21, IC24, IC24, IC24, IC24, IC28, IC28, IC28],
    [IC16, IC16, IC16, IC24, IC24, IC24, IC24, IC27, IC27, IC27],
    [IC16, IC16, IC16, IC23, IC23, IC23, IC23, IC27, IC27, IC27],
    [IC16, IC16, IC16, IC23, IC23, IC23, IC23, IC27, IC27, IC27],
    [IC16, IC16, IC16, IC23, IC23, IC23, IC23, IC27, IC27, IC27],
    [IC20, IC20, IC20, IC23, IC23, IC23, IC23, IC26, IC26, IC26],
    [IC20, IC20, IC20, IC23, IC23, IC23, IC23, IC26, IC26, IC26],
    [IC20, IC20, IC20, IC20, IC23, IC23, IC26, IC26, IC26, IC26],
    [IC20, IC20, IC20, IC20, IC23, IC23, IC26, IC26, IC26, IC26]
]

# ============== sein_droit ================#
# === Haut-Gauche ===
valeurs_BrRight_hg = [
    [IC22, IC22, IC22, IC19, IC19, IC19, IC19, IC19, IC13, IC13],
    [IC22, IC22, IC22, IC19, IC19, IC19, IC19, IC19, IC13, IC13],
    [IC22, IC22, IC22, IC19, IC19, IC19, IC19, IC19, IC13, IC13],
    [IC22, IC22, IC22, IC19, IC19, IC19, IC19, IC19, IC13, IC13],
    [IC22, IC22, IC22, IC19, IC19, IC19, IC19, IC19, IC13, IC13],
    [IC21, IC21, IC21, IC18, IC18, IC18, IC18, IC18, IC14, IC14],
    [IC21, IC21, IC21, IC18, IC18, IC18, IC18, IC18, IC14, IC14],
    [IC21, IC21, IC21, IC18, IC18, IC18, IC18, IC18, IC14, IC14],
    [IC21, IC21, IC21, IC18, IC18, IC18, IC18, IC18, IC14, IC14],
    [IC21, IC21, IC21, IC18, IC18, IC18, IC18, IC18, IC14, IC14],
    [IC16, IC16, IC16, IC17, IC17, IC17, IC17, IC17, IC15, IC15],
    [IC16, IC16, IC16, IC17, IC17, IC17, IC17, IC17, IC15, IC15],
    [IC16, IC16, IC16, IC17, IC17, IC17, IC17, IC17, IC15, IC15],
    [IC16, IC16, IC16, IC17, IC17, IC17, IC17, IC17, IC15, IC15],
    [IC20, IC20, IC20, IC20, IC17, IC17, IC17, IC15, IC15, IC15],
    [IC20, IC20, IC20, IC20, IC17, IC17, IC17, IC15, IC15, IC15],
    [IC20, IC20, IC20, IC20, IC17, IC17, IC17, IC15, IC15, IC15],
    [IC20, IC20, IC20, IC20, IC20, IC20, IC20, IC15, IC15, IC15]
]

# === Haut-Droit ===
valeurs_BrRight_hd = [
    [IC13, IC13, IC1, IC1, IC1, IC1, IC1, IC1, IC10, IC10],
    [IC13, IC13, IC1, IC1, IC1, IC1, IC1, IC1, IC10, IC10],
    [IC13, IC13, IC4, IC4, IC1, IC1, IC2, IC2, IC10, IC10],
    [IC13, IC13, IC4, IC4, IC3, IC3, IC2, IC2, IC10, IC10],
    [IC13, IC13, IC4, IC4, IC3, IC3, IC2, IC2, IC11, IC11],
    [IC13, IC13, IC4, IC4, IC3, IC3, IC2, IC2, IC11, IC11],
    [IC14, IC14, IC4, IC4, IC3, IC3, IC2, IC2, IC11, IC11],
    [IC14, IC14, IC6, IC6, IC3, IC3, IC7, IC7, IC11, IC11],
    [IC14, IC14, IC6, IC6, IC5, IC5, IC7, IC7, IC12, IC12],
    [IC14, IC14, IC6, IC6, IC5, IC5, IC7, IC7, IC12, IC12],
    [IC14, IC14, IC6, IC6, IC5, IC5, IC7, IC7, IC12, IC12],
    [IC15, IC15, IC15, IC8, IC8, IC8, IC8, IC32, IC32, IC32],
    [IC15, IC15, IC15, IC8, IC8, IC8, IC8, IC32, IC32, IC32],
    [IC15, IC15, IC15, IC8, IC8, IC8, IC8, IC32, IC32, IC32],
    [IC15, IC15, IC15, IC9, IC9, IC9, IC9, IC32, IC32, IC32],
    [IC15, IC15, IC15, IC9, IC9, IC9, IC9, IC32, IC32, IC32],
    [IC15, IC15, IC15, IC9, IC9, IC9, IC9, IC32, IC32, IC32],
    [IC15, IC15, IC15, IC9, IC9, IC9, IC9, IC32, IC32, IC32]
]

# === Bas-Gauche ===
valeurs_BrRight_bg = [
    [IC28, IC28, IC28, IC25, IC25, IC25, IC25, IC22, IC22, IC22],
    [IC28, IC28, IC28, IC25, IC25, IC25, IC25, IC22, IC22, IC22],
    [IC28, IC28, IC28, IC25, IC25, IC25, IC25, IC22, IC22, IC22],
    [IC28, IC28, IC28, IC25, IC25, IC25, IC25, IC22, IC22, IC22],
    [IC28, IC28, IC28, IC25, IC25, IC25, IC25, IC22, IC22, IC22],
    [IC28, IC28, IC28, IC25, IC25, IC25, IC25, IC21, IC21, IC21],
    [IC28, IC28, IC28, IC24, IC24, IC24, IC24, IC21, IC21, IC21],
    [IC28, IC28, IC28, IC24, IC24, IC24, IC24, IC21, IC21, IC21],
    [IC28, IC28, IC28, IC24, IC24, IC24, IC24, IC21, IC21, IC21],
    [IC28, IC28, IC28, IC24, IC24, IC24, IC24, IC21, IC21, IC21],
    [IC27, IC27, IC27, IC24, IC24, IC24, IC24, IC16, IC16, IC16],
    [IC27, IC27, IC27, IC23, IC23, IC23, IC23, IC16, IC16, IC16],
    [IC27, IC27, IC27, IC23, IC23, IC23, IC23, IC16, IC16, IC16],
    [IC27, IC27, IC27, IC23, IC23, IC23, IC23, IC16, IC16, IC16],
    [IC26, IC26, IC26, IC23, IC23, IC23, IC23, IC20, IC20, IC20],
    [IC26, IC26, IC26, IC23, IC23, IC23, IC23, IC20, IC20, IC20],
    [IC26, IC26, IC26, IC26, IC23, IC23, IC20, IC20, IC20, IC20],
    [IC26, IC26, IC26, IC26, IC23, IC23, IC20, IC20, IC20, IC20]
]

# === Bas-Droit ===
valeurs_BrRight_bd = [
    [IC10, IC10, IC10, IC31, IC31, IC31, IC31, IC28, IC28, IC28],
    [IC10, IC10, IC10, IC31, IC31, IC31, IC31, IC28, IC28, IC28],
    [IC10, IC10, IC10, IC31, IC31, IC31, IC31, IC28, IC28, IC28],
    [IC10, IC10, IC10, IC31, IC31, IC31, IC31, IC28, IC28, IC28],
    [IC10, IC10, IC10, IC31, IC31, IC31, IC31, IC28, IC28, IC28],
    [IC11, IC11, IC11, IC31, IC31, IC31, IC31, IC28, IC28, IC28],
    [IC11, IC11, IC11, IC31, IC31, IC31, IC31, IC28, IC28, IC28],
    [IC11, IC11, IC11, IC31, IC31, IC31, IC31, IC28, IC28, IC28],
    [IC11, IC11, IC11, IC30, IC30, IC30, IC30, IC28, IC28, IC28],
    [IC12, IC12, IC12, IC30, IC30, IC30, IC30, IC27, IC27, IC27],
    [IC12, IC12, IC12, IC30, IC30, IC30, IC30, IC27, IC27, IC27],
    [IC12, IC12, IC12, IC30, IC30, IC30, IC30, IC27, IC27, IC27],
    [IC32, IC32, IC32, IC29, IC29, IC29, IC29, IC26, IC26, IC26],
    [IC32, IC32, IC32, IC29, IC29, IC29, IC29, IC26, IC26, IC26],
    [IC32, IC32, IC32, IC29, IC29, IC29, IC29, IC26, IC26, IC26],
    [IC32, IC32, IC32, IC29, IC29, IC29, IC29, IC26, IC26, IC26],
    [IC32, IC32, IC32, IC29, IC29, IC29, IC29, IC26, IC26, IC26],
    [IC32, IC32, IC32, IC29, IC29, IC29, IC29, IC26, IC26, IC26]
]

# Organisation des données pour le traitement
valeurs_sein_gauche = [
    valeurs_BrLeft_bg,  # Bas-Gauche (0)
    valeurs_BrLeft_bd,  # Bas-Droit (1)
    valeurs_BrLeft_hd,  # Haut-Droit (2)
    valeurs_BrLeft_hg  # Haut-Gauche (3)
]

valeurs_sein_droit = [
    valeurs_BrRight_bg,  # Bas-Gauche (0)
    valeurs_BrRight_bd,  # Bas-Droit (1)
    valeurs_BrRight_hd,  # Haut-Droit (2)
    valeurs_BrRight_hg  # Haut-Gauche (3)
]

# Centres ajustés pour mieux positionner les seins
centre_gauche = (800, screen_height // 2 + 20)
centre_droit = (1500, screen_height // 2 + 20)


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


def render_heatmap_on_image(img, centre, grid_x, grid_y, grid_z, mask, tmin, tmax, gamma=1.2):
    grid_z_filled = np.nan_to_num(grid_z, nan=tmin)
    grid_z_smooth = gaussian_filter(grid_z_filled, sigma=lissage_sigma)
    denom = max(1e-6, (tmax - tmin))
    grid_norm = np.clip((grid_z_smooth - tmin) / denom, 0, 1)
    grid_norm = (grid_norm ** gamma * 255).astype(np.uint8)
    heatmap = cv2.applyColorMap(grid_norm, cv2.COLORMAP_JET)

    max_r = max(rayons)
    x0 = max(0, centre[0] - max_r);
    y0 = max(0, centre[1] - max_r)
    x1 = min(screen_width, centre[0] + max_r);
    y1 = min(screen_height, centre[1] + max_r)
    w = x1 - x0;
    h = y1 - y0
    heatmap_resized = cv2.resize(heatmap, (w, h), interpolation=cv2.INTER_CUBIC)
    mask_resized = cv2.resize(mask.astype(np.uint8), (w, h), interpolation=cv2.INTER_NEAREST).astype(bool)
    roi = img[y0:y1, x0:x1]
    np.copyto(roi, heatmap_resized, where=np.dstack([mask_resized] * 3))
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
        label = f"{pct_area:.1f}%"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(img, (cx - tw // 2 - 6, cy - th - 10), (cx + tw // 2 + 6, cy + 4), (255, 255, 255), -1)
        cv2.putText(img, label, (cx - tw // 2, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (10, 10, 10), 1, cv2.LINE_AA)
        annotations.append((cx, cy, pct_area))
    return annotations


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
win_name = "Thermo IA - Clinique (o = toggle overlay)"
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(win_name, 1200, 700)
cv2.createTrackbar("Tmin x10", win_name, int(tmin_init * 10), 500, lambda v: None)
cv2.createTrackbar("Tmax x10", win_name, int(tmax_init * 10), 500, lambda v: None)
cv2.createTrackbar("Seuil chaud x10", win_name, int(seuil_chaud_init * 10), 500, lambda v: None)
cv2.createTrackbar("Gamma x10", win_name, int(12), 50, lambda v: None)

last_grids = {'gauche': None, 'droit': None}
param_images = {}
overlay_on = True
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
zoom_window_name = "Zoom (clic gauche pour fermer)"


def on_mouse(event, x, y, flags, param):
    global overlay_on
    if event == cv2.EVENT_LBUTTONDOWN:
        for label, centre in [('gauche', centre_gauche), ('droit', centre_droit)]:
            if (x - centre[0]) ** 2 + (y - centre[1]) ** 2 <= max_radius ** 2:
                img_for_zoom = param_images.get('img_for_mouse', None)
                if img_for_zoom is not None:
                    w = int(max_radius * 1.0);
                    h = int(max_radius * 1.0)
                    x0 = int(np.clip(x - w // 2, 0, screen_width - w))
                    y0 = int(np.clip(y - h // 2, 0, screen_height - h))
                    crop = img_for_zoom[y0:y0 + h, x0:x0 + w].copy()
                    crop_zoomed = cv2.resize(crop, (int(w * 2.2), int(h * 2.2)), interpolation=cv2.INTER_CUBIC)
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
            if (x - centre[0]) ** 2 + (y - centre[1]) ** 2 <= max_radius ** 2:
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
        cv2.imshow(win_name, img_temp)


cv2.setMouseCallback(win_name, on_mouse)


# -------------------- Panneau d'information À GAUCHE --------------------
def draw_info_panel(img, x, y, width, height,
                    min_g, max_g, mean_g,
                    min_d, max_d, mean_d,
                    pct_g, pct_d, asym, seuil,
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

    cv2.putText(panel, "ANALYSE GLOBALE", (width//2 - 120, analysis_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 100, 0), 2)
    analysis_y += line_height

    # === MODIFICATION : Afficher asymétrie seulement si > 0.1°C ===
    if display_asym > 0.1:
        cv2.putText(panel, f"Asymetrie: {display_asym:.2f}C", (width//2 - 100, analysis_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    else:
        cv2.putText(panel, "Asymetrie: < 0.1C", (width//2 - 100, analysis_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 150, 0), 2)
    analysis_y += line_height

    cv2.putText(panel, f"Seuil chaud: {seuil:.1f}C", (width//2 - 100, analysis_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
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


# -------------------- Boucle principale --------------------
while True:
    tmin = cv2.getTrackbarPos("Tmin x10", win_name) / 10.0
    tmax = cv2.getTrackbarPos("Tmax x10", win_name) / 10.0
    seuil = cv2.getTrackbarPos("Seuil chaud x10", win_name) / 10.0
    gamma_track = max(0.5, cv2.getTrackbarPos("Gamma x10", win_name) / 10.0)
    if tmax <= tmin + 0.1: tmax = tmin + 0.1

    img = img_base.copy()

    # ---------------- Sein gauche ----------------
    gx_g, gy_g, gz_g, mask_g = compute_grid(centre_gauche, rayons, nb_sections, valeurs_sein_gauche, grid_res=360)
    gz_smooth_g, mask_roi_g, offset_g = render_heatmap_on_image(img, centre_gauche, gx_g, gy_g, gz_g, mask_g, tmin,
                                                                tmax, gamma=gamma_track)
    chaud_g, pct_g = detect_hot_zones_and_smooth(gz_smooth_g, mask_g, seuil)
    annotations_g = draw_contours_and_boxes(img, centre_gauche, chaud_g, gz_smooth_g, offset_info=offset_g,
                                            couleur=(0, 0, 200))

    # ---------------- Sein droit ----------------
    gx_d, gy_d, gz_d, mask_d = compute_grid(centre_droit, rayons, nb_sections, valeurs_sein_droit, grid_res=360)
    gz_smooth_d, mask_roi_d, offset_d = render_heatmap_on_image(img, centre_droit, gx_d, gy_d, gz_d, mask_d, tmin, tmax,
                                                                gamma=gamma_track)
    chaud_d, pct_d = detect_hot_zones_and_smooth(gz_smooth_d, mask_d, seuil)
    annotations_d = draw_contours_and_boxes(img, centre_droit, chaud_d, gz_smooth_d, offset_info=offset_d,
                                            couleur=(0, 0, 200))

    # ---------------- Stockage grilles ----------------
    last_grids['gauche'] = (gx_g, gy_g, gz_smooth_g, mask_g)
    last_grids['droit'] = (gx_d, gy_d, gz_smooth_d, mask_d)

    # ---------------- Statistiques ----------------
    mean_g, mean_d = float(np.nanmean(gz_smooth_g)), float(np.nanmean(gz_smooth_d))
    min_g, max_g = float(np.nanmin(gz_smooth_g)), float(np.nanmax(gz_smooth_g))
    min_d, max_d = float(np.nanmin(gz_smooth_d)), float(np.nanmax(gz_smooth_d))


    # === CORRECTION : Calcul de l'asymétrie par zones symétriques ===
    def calculer_asymetrie_par_zones(grid_g, grid_d):
        # Pour chaque pixel valide, calculer la différence avec son symétrique
        differences = []
        for i in range(grid_g.shape[0]):
            for j in range(grid_g.shape[1]):
                if not np.isnan(grid_g[i, j]) and not np.isnan(grid_d[i, j]):
                    diff = abs(grid_g[i, j] - grid_d[i, j])
                    differences.append(diff)

        if differences:
            # Prendre la différence maximale entre zones symétriques
            asym_max = max(differences)
            # Ou la moyenne des différences significatives
            differences_significatives = [d for d in differences if d > 0.1]
            if differences_significatives:
                asym_moy = np.mean(differences_significatives)
                return round(max(asym_max, asym_moy), 2)
            else:
                return round(asym_max, 2)
        return 0.0


    asym = calculer_asymetrie_par_zones(gz_smooth_g, gz_smooth_d)

    # Afficher l'asymétrie seulement si > 0.1°C
    display_asym = asym if asym > 0.1 else 0.0

    alert = (pct_g > 10.0 or pct_d > 10.0 or asym > 1.5)

    # ---------------- Colorbar centrale ----------------
    bar_h, bar_w = 450, 10
    bar = np.linspace(tmax, tmin, bar_h).reshape(bar_h, 1)
    denom = max(1e-6, tmax - tmin)
    bar_norm = ((bar - tmin) / denom * 255).astype(np.uint8)
    bar_img = cv2.applyColorMap(bar_norm, cv2.COLORMAP_JET)
    x_bar = (centre_gauche[0] + centre_droit[0]) // 2 - bar_w // 2
    y_bar = (screen_height // 2) - bar_h // 2
    img[y_bar:y_bar + bar_h, x_bar:x_bar + bar_w] = cv2.resize(bar_img, (bar_w, bar_h))

    cv2.putText(img, f"{tmax:.1f}", (x_bar + bar_w + 10, y_bar + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 10, 10), 2)
    cv2.putText(img, f"{tmin:.1f}", (x_bar + bar_w + 10, y_bar + bar_h - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (10, 10, 10), 2)
    cv2.putText(img, "Temp (C)", (x_bar - 15, y_bar - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (20, 20, 20), 2)

    # ---------------- Overlay anatomique ----------------
    if overlay_on:
        draw_anatomical_overlay(img, centre_gauche, max_radius, alpha=0.22)
        draw_anatomical_overlay(img, centre_droit, max_radius, alpha=0.22)

    # ---------------- Panneau info À GAUCHE ----------------
    panel_width = 500
    panel_height = 450
    panel_x = 20
    panel_y = (screen_height - panel_height) // 2

    draw_info_panel(img, panel_x, panel_y, panel_width, panel_height,
                    min_g, max_g, mean_g,
                    min_d, max_d, mean_d,
                    pct_g, pct_d, asym, seuil,
                    alert)

    # ---------------- Info bas ----------------
    cv2.putText(img, "Touches: s=save PNG | c=CSV | o=overlay | q/Esc=quit",
                (20, screen_height - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 30), 2)

    if last_save_time and time.time() - last_save_time < 2.0:
        cv2.putText(img, "Rapport sauvegarde", (screen_width - 250, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 120, 20), 2)

    param_images['img_for_mouse'] = img.copy()
    cv2.imshow(win_name, img)

    # ---------------- Gestion clavier ----------------
    key = cv2.waitKey(50) & 0xFF
    if key == ord('q') or key == 27: break
    if key == ord('o'): overlay_on = not overlay_on
    if key == ord('s'):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = os.path.join(out_dir, f"rapport_thermo_{ts}.png")
        cv2.imwrite(fname, img)
        last_save_time = time.time()
        print(f"[INFO] Rapport sauvegarde -> {fname}")
    if key == ord('c'):
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_g = os.path.join(out_dir, f"grid_gauche_{ts}.csv")
        csv_d = os.path.join(out_dir, f"grid_droit_{ts}.csv")
        try:
            pd.DataFrame(gz_smooth_g).to_csv(csv_g, index=False, header=False)
            pd.DataFrame(gz_smooth_d).to_csv(csv_d, index=False, header=False)
            print(f"[INFO] CSV exportes -> {csv_g} , {csv_d}")
            last_save_time = time.time()
        except Exception as e:
            print("[ERR] Export CSV :", e)

cv2.destroyAllWindows()