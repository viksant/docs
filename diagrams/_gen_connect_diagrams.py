"""Genera los 8 diagramas .excalidraw de flujo de conexion de integraciones.

Cada diagrama comparte el MISMO layout (5 pasos horizontales) y solo varia el
nombre del proveedor y la accion de valor final. Generarlos por script evita
la deriva manual entre 8 ficheros casi identicos y garantiza JSON valido.

Branding BestChatBot: accent naranja (#F97316) + texto oscuro (#1e1e1e),
fondo blanco. Exportar a PNG transparente para que sirva en tema claro/oscuro.
"""

import json
import os

# --- Paleta de marca BestChatBot ---
ORANGE = "#F97316"   # accent principal (cajas de valor + flechas)
DARK = "#1e1e1e"     # texto y bordes principales
GRAY = "#adb5bd"     # texto secundario / decorativo

# --- Las 8 integraciones: slug de fichero, nombre comercial, accion de valor ---
# La accion esta verificada contra el codigo de los connectors (capacidades activas).
INTEGRATIONS = [
    ("cal-com", "Cal.com", "Book meetings"),
    ("calendly", "Calendly", "Book meetings"),
    ("freshdesk", "Freshdesk", "Manage tickets"),
    ("zendesk", "Zendesk", "Manage tickets"),
    ("hubspot", "HubSpot", "Capture leads"),
    ("stripe", "Stripe", "View billing"),
    ("shopify", "Shopify", "Track orders"),
    ("woocommerce", "WooCommerce", "Track orders"),
]

# Los 5 pasos del flujo de conexion de cara al usuario. El ultimo se sustituye
# por la accion concreta de cada proveedor (es la caja de valor, en naranja).
BASE_STEPS = ["Open Integrations", "Click Connect", "Grant secure access", "Connected"]

# --- Geometria del lienzo ---
CANVAS_W = 1400
BOX_W, BOX_H = 200, 90
GAP = 40
N_BOXES = 5
BAND_Y = 250  # banda vertical centrada (el comando pide y entre ~140 y 460)

# x de la primera caja para centrar la fila completa en el lienzo
TOTAL_ROW = N_BOXES * BOX_W + (N_BOXES - 1) * GAP
START_X = (CANVAS_W - TOTAL_ROW) // 2

# Contador global para ids/seeds deterministas (sin Math.random => reproducible)
_counter = [1000]


def _next() -> int:
    _counter[0] += 7
    return _counter[0]


def _base(el_type: str, x: float, y: float, w: float, h: float) -> dict:
    """Campos comunes que TODO elemento excalidraw necesita."""
    n = _next()
    return {
        "id": f"el{n}",
        "type": el_type,
        "x": x, "y": y, "width": w, "height": h,
        "angle": 0,
        "strokeColor": DARK,
        "backgroundColor": "transparent",
        "fillStyle": "solid",
        "strokeWidth": 1,
        "strokeStyle": "solid",
        "roughness": 1,
        "opacity": 100,
        "groupIds": [],
        "frameId": None,
        "roundness": None,
        "seed": n,
        "version": 1,
        "versionNonce": n * 3,
        "isDeleted": False,
        "boundElements": [],
        "updated": 1,
        "link": None,
        "locked": False,
    }


def make_box(x: float, y: float, accent: bool) -> dict:
    """Caja (rectangulo redondeado). Si accent=True se rellena naranja hachure."""
    el = _base("rectangle", x, y, BOX_W, BOX_H)
    el["roundness"] = {"type": 3}
    if accent:
        # Caja de valor: borde y relleno naranja translucido.
        el["strokeColor"] = ORANGE
        el["backgroundColor"] = ORANGE
        el["fillStyle"] = "hachure"
        el["strokeWidth"] = 2
    return el


def make_label(x: float, y: float, w: float, text: str, size: int = 16,
               color: str = DARK, align: str = "center") -> dict:
    """Texto independiente centrado dentro de un ancho dado."""
    el = _base("text", x, y, w, size * 1.25)
    el.update({
        "text": text,
        "fontSize": size,
        "fontFamily": 1,
        "textAlign": align,
        "verticalAlign": "top",
        "baseline": size,
        "containerId": None,
        "originalText": text,
        "lineHeight": 1.25,
    })
    el["strokeColor"] = color
    return el


def make_arrow(x: float, y: float, dx: float) -> dict:
    """Flecha horizontal discontinua naranja entre dos cajas."""
    el = _base("arrow", x, y, dx, 0)
    el.update({
        "points": [[0, 0], [dx, 0]],
        "lastCommittedPoint": None,
        "startBinding": None,
        "endBinding": None,
        "startArrowhead": None,
        "endArrowhead": "arrow",
    })
    el["strokeColor"] = ORANGE
    el["strokeStyle"] = "dashed"
    el["strokeWidth"] = 2
    return el


def build_diagram(provider: str, action: str) -> dict:
    """Construye el documento excalidraw completo para un proveedor."""
    elements = []
    steps = BASE_STEPS + [action]

    # --- Titulo (arriba, centrado) ---
    title = f"Connect {provider} to BestChatBot"
    elements.append(make_label(0, 70, CANVAS_W, title, size=24, color=DARK))

    # --- Subtitulo de contexto (gris, debajo del titulo) ---
    elements.append(make_label(0, 110, CANVAS_W,
                               "From your dashboard, in a few clicks",
                               size=14, color=GRAY))

    # --- Cajas + etiquetas + flechas ---
    for i, label in enumerate(steps):
        bx = START_X + i * (BOX_W + GAP)
        is_value = (i == len(steps) - 1)  # ultima caja = accion de valor (naranja)

        elements.append(make_box(bx, BAND_Y, accent=is_value))

        # Texto centrado verticalmente dentro de la caja
        ty = BAND_Y + (BOX_H - 16) / 2
        txt_color = ORANGE if is_value else DARK
        # La caja "Connected" lleva un check; la de valor lleva el prefijo "AI:"
        shown = label
        if label == "Connected":
            shown = "Connected  ✓"
        elements.append(make_label(bx, ty, BOX_W, shown, size=16, color=txt_color))

        # Flecha hacia la siguiente caja (todas menos la ultima)
        if i < len(steps) - 1:
            ax = bx + BOX_W + 4
            ay = BAND_Y + BOX_H / 2
            elements.append(make_arrow(ax, ay, GAP - 8))

    return {
        "type": "excalidraw",
        "version": 2,
        "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"},
        "files": {},
    }


def main() -> None:
    out_dir = os.path.dirname(os.path.abspath(__file__))
    written = []
    for slug, provider, action in INTEGRATIONS:
        # Reiniciar contador por fichero para ids estables entre ejecuciones
        _counter[0] = 1000
        doc = build_diagram(provider, action)
        path = os.path.join(out_dir, f"connect-{slug}.excalidraw")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        written.append((f"connect-{slug}.excalidraw", len(doc["elements"])))
    for name, n in written:
        print(f"OK  {name}  ({n} elementos)")


if __name__ == "__main__":
    main()
