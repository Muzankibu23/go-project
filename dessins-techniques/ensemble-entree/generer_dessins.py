"""Vues extérieures cotées – ensemble d'entrée (ALU monobloc + variante PVC couplée).

Génère un PNG par vue (A4 paysage) et un PDF regroupant toutes les vues.
Seules les cotes listées ci-dessous sont affichées ; les largeurs de profilés,
positions de quincaillerie et de boîtes aux lettres sont purement graphiques.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, Polygon, Rectangle

OUT = Path(__file__).resolve().parent

PROFIL = "#3b2a22"      # brun foncé (proche F822 / P822)
MITRE = "#6e5547"       # lignes d'onglet
VITRAGE = "#dde2e5"     # gris clair
SABLE = "#eceeef"       # vitrage dépoli
PANNEAU = "#ead9bd"     # beige clair
METAL = "#a7a9ab"
TRAIT = "black"

A4 = (11.69, 8.27)

# Cotes du devis (mm)
L_TOT, H_TOT = 1820, 3160
H_IMP, H_BAS = 910, 2250
L_LAT, L_PORTE = 385, 1050
# Variante PVC : cotes cadres + profilé de couplage
COUPL = 24
L_LAT_CADRE = 361       # 385 - 24
H_IMP_CADRE = 886       # 910 - 24

# Épaisseurs purement graphiques (non cotées)
EP_ALU, EP_PVC, EP_OUV = 60, 65, 90


# ---------------------------------------------------------------- primitives
def rect(ax, x, y, w, h, fc, lw=0.8, z=1, **kw):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=TRAIT, lw=lw, zorder=z, **kw))


def cadre(ax, x, y, w, h, t, remplissage, bas=True, z=2, hatch=None):
    """Cadre profilé avec onglets ; remplissage = couleur de l'intérieur."""
    tb = t if bas else 0
    rect(ax, x, y, w, h, PROFIL, z=z)
    ax.add_patch(Rectangle((x + t, y + tb), w - 2 * t, h - t - tb, fc=remplissage,
                           ec=TRAIT, lw=0.8, zorder=z + 0.1, hatch=hatch))
    coins = [((x, y + h), (x + t, y + h - t)), ((x + w, y + h), (x + w - t, y + h - t))]
    if bas:
        coins += [((x, y), (x + t, y + t)), ((x + w, y), (x + w - t, y + t))]
    for (x1, y1), (x2, y2) in coins:
        ax.plot([x1, x2], [y1, y2], color=MITRE, lw=0.6, zorder=z + 0.2)


def vitrage_sable(ax, x, y, w, h, z=3):
    plt.rcParams["hatch.color"] = "#b9bdc0"
    plt.rcParams["hatch.linewidth"] = 0.4
    ax.add_patch(Rectangle((x, y), w, h, fc=SABLE, ec=TRAIT, lw=0.8, zorder=z, hatch="...."))


def triangle_ouverture(ax, x, y, w, h, paumelles="gauche"):
    """Triangle d'ouverture, pointe côté paumelles."""
    if paumelles == "gauche":
        pts = [(x + w, y + h), (x, y + h / 2), (x + w, y)]
    else:
        pts = [(x, y + h), (x + w, y + h / 2), (x, y)]
    ax.plot(*zip(*pts), color=TRAIT, lw=0.45, zorder=6)


def paumelles(ax, x, y_bas, h, cote="gauche"):
    for yy in (y_bas + 0.12 * h, y_bas + 0.5 * h, y_bas + 0.88 * h):
        dx = -14 if cote == "gauche" else 0
        rect(ax, x + dx, yy - 50, 14, 100, METAL, lw=0.5, z=7)


def poignee_ext(ax, x, y):
    """Plaque de propreté + bouton fixe extérieur + cylindre (graphique)."""
    rect(ax, x - 22, y - 230, 44, 330, METAL, lw=0.6, z=7)
    ax.add_patch(Circle((x, y), 26, fc="#8d8f91", ec=TRAIT, lw=0.6, zorder=8))
    ax.add_patch(Circle((x, y - 160), 11, fc="#555", ec=TRAIT, lw=0.5, zorder=8))


def boites_aux_lettres(ax, cx, y_haut, note=True, x_note=None, note_bas=False):
    """3 clapets superposés (ouverture 230 × 40) avec porte-nom."""
    pas = 170
    for i in range(3):
        y = y_haut - i * pas
        rect(ax, cx - 115, y - 40, 230, 40, "#7b7e80", lw=0.6, z=8)
        ax.plot([cx - 100, cx + 100], [y - 20, y - 20], color="#222", lw=0.6, zorder=9)
        rect(ax, cx - 80, y - 85, 160, 30, "white", lw=0.5, z=8)
    if note:
        xt = x_note if x_note is not None else cx
        ax.annotate("3 clapets B.A.L.\n230 × 40\n+ porte-nom",
                    xy=(cx, y_haut - 20), xytext=(xt, y_haut - 1000 if note_bas else y_haut + 330),
                    ha="center", va="bottom", fontsize=7,
                    arrowprops=dict(arrowstyle="-", lw=0.5, color=TRAIT), zorder=10)


# ---------------------------------------------------------------- cotation
def _fl(ax, a, b):
    ax.annotate("", xy=a, xytext=b, zorder=10,
                arrowprops=dict(arrowstyle="<|-|>", lw=0.6, color=TRAIT,
                                shrinkA=0, shrinkB=0, mutation_scale=7))


def cote_h(ax, x1, x2, y, ref, txt=None, dessus=True, petit_a_gauche=False):
    """Cote horizontale entre x1 et x2 sur la ligne y ; ref = y de l'objet."""
    for x in (x1, x2):
        ax.plot([x, x], [ref, y + (25 if y > ref else -25)], color=TRAIT, lw=0.4, zorder=10)
    _fl(ax, (x1, y), (x2, y))
    txt = txt or f"{round(x2 - x1)}"
    petit = (x2 - x1) < 150
    dy = 18 if dessus else -18
    x_petit, ha_petit = (x1 - 25, "right") if petit_a_gauche else (x2 + 25, "left")
    ax.text((x1 + x2) / 2 if not petit else x_petit, y + (dy if not petit else 0), txt,
            ha="center" if not petit else ha_petit,
            va=("bottom" if dessus else "top") if not petit else "center",
            fontsize=9, zorder=11,
            bbox=dict(fc="white", ec="none", pad=0.5) if petit else None)


def cote_v(ax, y1, y2, x, ref, txt=None, gauche=True):
    for y in (y1, y2):
        ax.plot([ref, x + (-25 if x < ref else 25)], [y, y], color=TRAIT, lw=0.4, zorder=10)
    _fl(ax, (x, y1), (x, y2))
    txt = txt or f"{round(y2 - y1)}"
    petit = (y2 - y1) < 150
    dx = -18 if gauche else 18
    if petit:
        ax.text(x + dx, y2 + 20, txt, ha="right" if gauche else "left", va="bottom",
                fontsize=9, zorder=11)
    else:
        ax.text(x + dx, (y1 + y2) / 2, txt, rotation=90, ha="right" if gauche else "left",
                va="center", fontsize=9, zorder=11)


# ---------------------------------------------------------------- page
def page(titre, legende, xlim, ylim, dessin, pdf):
    fig = plt.figure(figsize=A4)
    ax = fig.add_axes([0.04, 0.13, 0.92, 0.80])
    ax.set_aspect("equal")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    dessin(ax)
    fig.text(0.5, 0.955, "Vue extérieure", ha="center", fontsize=11, style="italic",
             weight="bold")
    fig.add_artist(plt.Line2D([0.25, 0.75], [0.085, 0.085], color=TRAIT, lw=0.6))
    fig.text(0.5, 0.055, legende, ha="center", fontsize=13, weight="bold")
    fig.text(0.5, 0.025, "Cotes en mm – dimensions hors tout – dessin non à l'échelle d'impression",
             ha="center", fontsize=8, color="#444")
    fig.savefig(OUT / f"{titre}.png", dpi=200, facecolor="white")
    pdf.savefig(fig, facecolor="white")
    plt.close(fig)


def cadrage(w, h, marge_g=520, marge_d=520, marge_b=380, marge_h=380):
    """Fenêtre de dessin au ratio de l'axe (A4 paysage), centrée sur l'objet."""
    ratio = (A4[0] * 0.92) / (A4[1] * 0.80)
    x0, x1, y0, y1 = -marge_g, w + marge_d, -marge_b, h + marge_h
    lw, lh = x1 - x0, y1 - y0
    if lw / lh < ratio:
        extra = (lh * ratio - lw) / 2
        x0, x1 = x0 - extra, x1 + extra
    else:
        extra = (lw / ratio - lh) / 2
        y0, y1 = y0 - extra, y1 + extra
    return (x0, x1), (y0, y1)


# ---------------------------------------------------------------- éléments
def porte(ax, x, y, w, h, ep_dormant, ep_ouvrant):
    """Porte 1 vantail : dormant sans traverse basse (seuil), ouvrant, vitrage sablé."""
    seuil = 20
    cadre(ax, x, y, w, h, ep_dormant, PROFIL, bas=False, z=3)
    rect(ax, x, y, w, seuil, "#5a4a40", lw=0.6, z=3.5)
    ox, oy = x + ep_dormant, y + seuil
    ow, oh = w - 2 * ep_dormant, h - ep_dormant - seuil
    cadre(ax, ox, oy, ow, oh, ep_ouvrant, SABLE, z=4)
    vitrage_sable(ax, ox + ep_ouvrant, oy + ep_ouvrant, ow - 2 * ep_ouvrant, oh - 2 * ep_ouvrant, z=4.5)
    triangle_ouverture(ax, ox, oy, ow, oh, paumelles="gauche")
    paumelles(ax, ox, oy, oh, "gauche")
    poignee_ext(ax, ox + ow - ep_ouvrant / 2, y + 1050)
    ax.text(x + w / 2, y + h * 0.62, "vitrage sablé", ha="center", fontsize=7.5,
            style="italic", color="#444", zorder=7,
            bbox=dict(fc=SABLE, ec="none", pad=1))


def panneau_lateral(ax, x, y, w, h, ep, note_x=None, note_bas=False):
    cadre(ax, x, y, w, h, ep, PANNEAU, z=3)
    boites_aux_lettres(ax, x + w / 2, y + 1320, x_note=note_x, note_bas=note_bas)


def imposte(ax, x, y, w, h, ep):
    cadre(ax, x, y, w, h, ep, VITRAGE, z=3)
    ax.text(x + w / 2, y + h / 2, "vitrage fixe", ha="center", va="center", fontsize=7.5,
            style="italic", color="#444", zorder=5)


def couplage(ax, x, y, w, h):
    rect(ax, x, y, w, h, "#5a4a40", lw=0.6, z=5)


# ---------------------------------------------------------------- vues
def vue_alu(ax):
    W, H = L_TOT, H_TOT
    # cadre monobloc + traverse
    rect(ax, 0, 0, W, H, PROFIL, z=2)
    imposte_y = H_BAS
    ax.add_patch(Rectangle((EP_ALU, imposte_y + 70), W - 2 * EP_ALU, H_IMP - 70 - EP_ALU,
                           fc=VITRAGE, ec=TRAIT, lw=0.8, zorder=3))
    ax.text(W / 2, imposte_y + H_IMP / 2, "vitrage fixe", ha="center", va="center",
            fontsize=7.5, style="italic", color="#444", zorder=5)
    for x in (EP_ALU, L_LAT + L_PORTE):
        ax.add_patch(Rectangle((x, EP_ALU), L_LAT - EP_ALU, H_BAS - EP_ALU,
                               fc=PANNEAU, ec=TRAIT, lw=0.8, zorder=3))
    for (x1, y1), (x2, y2) in [((0, H), (EP_ALU, H - EP_ALU)), ((W, H), (W - EP_ALU, H - EP_ALU)),
                               ((0, 0), (EP_ALU, EP_ALU)), ((W, 0), (W - EP_ALU, EP_ALU))]:
        ax.plot([x1, x2], [y1, y2], color=MITRE, lw=0.6, zorder=3.2)
    porte(ax, L_LAT, 0, L_PORTE, H_BAS, 55, EP_OUV)
    boites_aux_lettres(ax, L_LAT / 2 + EP_ALU / 2, 1320, x_note=-560)
    boites_aux_lettres(ax, L_LAT + L_PORTE + (L_LAT - EP_ALU) / 2, 1320, x_note=W + 800, note_bas=True)
    # cotes
    cote_h(ax, 0, W, H + 180, H)
    for x1, x2 in [(0, L_LAT), (L_LAT, L_LAT + L_PORTE), (L_LAT + L_PORTE, W)]:
        cote_h(ax, x1, x2, -160, 0, dessus=False)
    cote_v(ax, 0, H_BAS, -170, 0)
    cote_v(ax, H_BAS, H, -170, 0)
    cote_v(ax, 0, H, W + 170, W, gauche=False)


def vue_pvc_imposte(ax):
    imposte(ax, 0, COUPL, L_TOT, H_IMP_CADRE, EP_PVC)
    couplage(ax, 0, 0, L_TOT, COUPL)
    ax.annotate("profilé de couplage 24", xy=(L_TOT * 0.75, COUPL / 2),
                xytext=(L_TOT * 0.75, -260), ha="center", fontsize=7.5,
                arrowprops=dict(arrowstyle="-", lw=0.5))
    cote_h(ax, 0, L_TOT, H_IMP + 160, H_IMP)
    cote_v(ax, COUPL, H_IMP, L_TOT + 150, L_TOT, gauche=False)
    cote_v(ax, 0, COUPL, L_TOT + 150, L_TOT, gauche=False)
    cote_v(ax, 0, H_IMP, L_TOT + 420, L_TOT, gauche=False)


def _vue_pvc_lateral(ax, couplage_cote):
    if couplage_cote == "droite":     # panneau gauche (vu de l'extérieur)
        x_cadre, x_coupl = 0, L_LAT_CADRE
    else:                             # panneau droit
        x_cadre, x_coupl = COUPL, 0
    panneau_lateral(ax, x_cadre, 0, L_LAT_CADRE, H_BAS, EP_PVC, note_x=-420 if couplage_cote == "droite" else L_LAT + 420)
    couplage(ax, x_coupl, 0, COUPL, H_BAS)
    cote_h(ax, 0, L_LAT, H_BAS + 330, H_BAS)
    cote_h(ax, x_cadre, x_cadre + L_LAT_CADRE, H_BAS + 140, H_BAS)
    cote_h(ax, x_coupl, x_coupl + COUPL, H_BAS + 140, H_BAS,
           petit_a_gauche=couplage_cote != "droite")
    cote_v(ax, 0, H_BAS, L_LAT + 170 if couplage_cote == "droite" else -170,
           L_LAT if couplage_cote == "droite" else 0, gauche=couplage_cote != "droite")


def vue_pvc_porte(ax):
    porte(ax, 0, 0, L_PORTE, H_BAS, EP_PVC, EP_OUV)
    cote_h(ax, 0, L_PORTE, H_BAS + 170, H_BAS)
    cote_h(ax, 0, L_PORTE, -160, 0, dessus=False)
    cote_v(ax, 0, H_BAS, L_PORTE + 170, L_PORTE, gauche=False)


def vue_pvc_assemble(ax):
    imposte(ax, 0, H_BAS + COUPL, L_TOT, H_IMP_CADRE, EP_PVC)
    couplage(ax, 0, H_BAS, L_TOT, COUPL)
    xg, xp, xd = 0, L_LAT_CADRE + COUPL, L_TOT - L_LAT_CADRE
    panneau_lateral(ax, xg, 0, L_LAT_CADRE, H_BAS, EP_PVC, note_x=-700)
    couplage(ax, L_LAT_CADRE, 0, COUPL, H_BAS)
    porte(ax, xp, 0, L_PORTE, H_BAS, EP_PVC, EP_OUV)
    couplage(ax, xp + L_PORTE, 0, COUPL, H_BAS)
    panneau_lateral(ax, xd, 0, L_LAT_CADRE, H_BAS, EP_PVC, note_x=L_TOT + 700, note_bas=True)
    cote_h(ax, 0, L_TOT, H_TOT + 180, H_TOT)
    for x1, x2 in [(0, L_LAT_CADRE), (L_LAT_CADRE, L_LAT), (L_LAT, L_LAT + L_PORTE),
                   (L_LAT + L_PORTE, xd), (xd, L_TOT)]:
        cote_h(ax, x1, x2, -150, 0, dessus=False)
    for x1, x2 in [(0, L_LAT), (L_LAT, L_LAT + L_PORTE), (L_LAT + L_PORTE, L_TOT)]:
        cote_h(ax, x1, x2, -360, 0, dessus=False)
    cote_v(ax, 0, H_BAS, -150, 0)
    cote_v(ax, H_BAS, H_BAS + COUPL, -150, 0)
    cote_v(ax, H_BAS + COUPL, H_TOT, -150, 0)
    cote_v(ax, 0, H_BAS, -380, 0)
    cote_v(ax, H_BAS, H_TOT, -380, 0)
    cote_v(ax, 0, H_TOT, L_TOT + 170, L_TOT, gauche=False)


VUES = [
    ("1_ALU_ensemble_complet", "Ensemble d'entrée – vue extérieure – ×3",
     (L_TOT, H_TOT), vue_alu, dict(marge_g=800, marge_d=1050)),
    ("2-1_PVC_imposte_fixe", "Variante PVC – élément 1/ imposte fixe vitrée – vue extérieure – ×3",
     (L_TOT, H_IMP), vue_pvc_imposte, dict(marge_d=700, marge_b=420)),
    ("2-2_PVC_panneau_lateral_gauche",
     "Variante PVC – élément 2/ panneau latéral gauche (3 B.A.L.) – vue extérieure – ×3",
     (L_LAT, H_BAS), lambda ax: _vue_pvc_lateral(ax, "droite"), dict(marge_h=520)),
    ("2-3_PVC_porte", "Variante PVC – élément 3/ porte 1 vantail, vitrage sablé – vue extérieure – ×3",
     (L_PORTE, H_BAS), vue_pvc_porte, {}),
    ("2-4_PVC_panneau_lateral_droit",
     "Variante PVC – élément 4/ panneau latéral droit (3 B.A.L.) – vue extérieure – ×3",
     (L_LAT, H_BAS), lambda ax: _vue_pvc_lateral(ax, "gauche"), dict(marge_h=520)),
    ("2-5_PVC_ensemble_assemble",
     "Variante PVC – éléments 1 à 4 assemblés – vue extérieure – ×3",
     (L_TOT, H_TOT), vue_pvc_assemble, dict(marge_g=950, marge_d=950, marge_b=480)),
]


if __name__ == "__main__":
    with PdfPages(OUT / "ensemble_entree_vues_exterieures.pdf") as pdf:
        for nom, legende, (w, h), fn, marges in VUES:
            xlim, ylim = cadrage(w, h, **marges)
            page(nom, legende, xlim, ylim, fn, pdf)
            print("ok", nom)
