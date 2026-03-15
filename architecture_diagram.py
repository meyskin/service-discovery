"""
Generates architecture_diagram.png showing the service discovery flow.
Run: python3 architecture_diagram.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

fig, ax = plt.subplots(figsize=(12, 7))
ax.set_xlim(0, 12)
ax.set_ylim(0, 7)
ax.axis("off")
fig.patch.set_facecolor("#0d1117")
ax.set_facecolor("#0d1117")

def box(x, y, w, h, color, label, sublabel=""):
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.1",
        facecolor=color, edgecolor="white", linewidth=1.5,
    )
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2 + (0.15 if sublabel else 0), label,
            ha="center", va="center", color="white",
            fontsize=11, fontweight="bold")
    if sublabel:
        ax.text(x + w/2, y + h/2 - 0.25, sublabel,
                ha="center", va="center", color="#aaaaaa", fontsize=8)

def arrow(x1, y1, x2, y2, label="", color="#58a6ff"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=2))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.1, my, label, color=color, fontsize=8, style="italic")

# ── Components ──────────────────────────────────────────────────────────────
box(4.5, 5.0, 3, 1.2, "#1a3a5c", "Service Registry", "registry.py  :8000")

box(0.3, 2.8, 2.4, 1.0, "#1a4a2a", "order-service-1", "service.py  :8001")
box(0.3, 1.3, 2.4, 1.0, "#1a4a2a", "order-service-2", "service.py  :8002")

box(9.0, 3.0, 2.5, 1.2, "#4a1a1a", "Client", "client.py")

# ── Arrows: Registration ─────────────────────────────────────────────────────
arrow(2.7,  3.55, 4.5,  5.5,  "① register", "#3fb950")
arrow(2.7,  1.95, 4.5,  5.2,  "① register", "#3fb950")

# ── Arrows: Heartbeat ────────────────────────────────────────────────────────
arrow(4.5, 5.35, 2.7, 3.40, "♥ heartbeat", "#d29922")

# ── Arrows: Discovery ────────────────────────────────────────────────────────
arrow(9.0, 3.6,  7.5, 5.6,  "② discover", "#58a6ff")
arrow(7.5, 5.2,  9.0, 3.4,  "instances↩", "#58a6ff")

# ── Arrows: Service Call ─────────────────────────────────────────────────────
arrow(9.0, 3.0, 2.7, 3.4, "③ call random instance", "#f78166")

# ── Legend ───────────────────────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(color="#3fb950", label="Registration / Heartbeat"),
    mpatches.Patch(color="#58a6ff", label="Discovery (client-side)"),
    mpatches.Patch(color="#f78166", label="Service call"),
]
ax.legend(handles=legend_items, loc="lower right",
          facecolor="#161b22", edgecolor="gray",
          labelcolor="white", fontsize=9)

ax.set_title("Service Discovery Architecture – CMPE 273 Week 7",
             color="white", fontsize=14, fontweight="bold", pad=15)

plt.tight_layout()
plt.savefig("architecture_diagram.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print("Saved architecture_diagram.png")
plt.show()
