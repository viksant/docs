"""Genera las 16 paginas de guia por integracion (8 proveedores x EN/ES).

Estructura identica por pagina (capacidades + diagrama + como conectar +
exclusion mutua + disponibilidad). Generarlas por script garantiza
consistencia entre las 8 y permite regenerar si cambian datos.

Salida:
  EN -> integrations/guides/<slug>.mdx
  ES -> es/integrations/guides/<slug>.mdx   (estilo ASCII, sin tildes/enie)

Datos verificados:
  - Capacidades: contra el codigo de cada connector (tools activas).
  - Tipo de conexion: cal-com/stripe/freshdesk/woocommerce = credencial manual;
    calendly/zendesk/hubspot/shopify = OAuth (confirmado por el usuario + catalog_data.py).
  - Diagramas: imagenes <slug>-integration.png ya en images/.
"""

import os

# --- Definicion de los 8 proveedores ---
# connect: "oauth" (login + autorizar) o "manual" (pegar credencial).
# excl: nombre del proveedor con el que comparte categoria (None si unico).
# cred_en / cred_es: pista de credencial para el flujo manual (nivel alto, sin
#   labels internos inventados). Solo se usa cuando connect == "manual".
PROVIDERS = [
    {
        "slug": "cal-com", "name": "Cal.com", "icon": "calendar",
        "cat_en": "Scheduling", "cat_es": "Agendamiento",
        "diagram": "calcom-integration.png", "excl": "Calendly",
        "connect": "manual",
        "cred_en": "your Cal.com API key",
        "cred_es": "tu API key de Cal.com",
        "value_en": "book and manage meetings",
        "value_es": "agendar y gestionar reuniones",
        "caps": [
            ("Check availability", "Show the visitor open time slots from your calendar.",
             "Consultar disponibilidad", "Muestra al visitante los horarios libres de tu calendario."),
            ("Book a meeting", "Schedule the meeting and confirm it in the chat.",
             "Agendar una reunion", "Agenda la reunion y la confirma en el chat."),
            ("Cancel a meeting", "Let the visitor cancel a meeting they booked.",
             "Cancelar una reunion", "Permite al visitante cancelar una reunion que agendo."),
        ],
    },
    {
        "slug": "calendly", "name": "Calendly", "icon": "calendar",
        "cat_en": "Scheduling", "cat_es": "Agendamiento",
        "diagram": "calendly-integration.png", "excl": "Cal.com",
        "connect": "oauth",
        "cred_en": "", "cred_es": "",
        "value_en": "book and manage meetings",
        "value_es": "agendar y gestionar reuniones",
        "caps": [
            ("Check availability", "Show the visitor open time slots from your calendar.",
             "Consultar disponibilidad", "Muestra al visitante los horarios libres de tu calendario."),
            ("Book a meeting", "Schedule the meeting and confirm it in the chat.",
             "Agendar una reunion", "Agenda la reunion y la confirma en el chat."),
            ("Cancel a meeting", "Let the visitor cancel a meeting they booked.",
             "Cancelar una reunion", "Permite al visitante cancelar una reunion que agendo."),
        ],
    },
    {
        "slug": "freshdesk", "name": "Freshdesk", "icon": "headset",
        "cat_en": "Help Desk", "cat_es": "Mesa de ayuda",
        "diagram": "freshdesk-integration.png", "excl": "Zendesk",
        "connect": "manual",
        "cred_en": "your Freshdesk API key and domain",
        "cred_es": "tu API key y dominio de Freshdesk",
        "value_en": "open and track support tickets",
        "value_es": "abrir y seguir tickets de soporte",
        "caps": [
            ("Open a support ticket", "Turn a visitor's issue into a tracked ticket.",
             "Abrir un ticket de soporte", "Convierte el problema del visitante en un ticket rastreable."),
            ("Check a ticket's status", "Look up the status of an existing ticket.",
             "Consultar el estado de un ticket", "Consulta el estado de un ticket existente."),
        ],
    },
    {
        "slug": "zendesk", "name": "Zendesk", "icon": "headset",
        "cat_en": "Help Desk", "cat_es": "Mesa de ayuda",
        "diagram": "zendesk-integration.png", "excl": "Freshdesk",
        "connect": "oauth",
        "cred_en": "", "cred_es": "",
        "value_en": "open and track support tickets",
        "value_es": "abrir y seguir tickets de soporte",
        "caps": [
            ("Open a support ticket", "Turn a visitor's issue into a tracked ticket.",
             "Abrir un ticket de soporte", "Convierte el problema del visitante en un ticket rastreable."),
            ("Check a ticket's status", "Look up the status of an existing ticket.",
             "Consultar el estado de un ticket", "Consulta el estado de un ticket existente."),
        ],
    },
    {
        "slug": "hubspot", "name": "HubSpot", "icon": "address-book",
        "cat_en": "CRM", "cat_es": "CRM",
        "diagram": "hubspot-integration.png", "excl": None,
        "connect": "oauth",
        "cred_en": "", "cred_es": "",
        "value_en": "capture leads",
        "value_es": "capturar leads",
        "caps": [
            ("Capture a lead", "Save the visitor's details so your sales team can follow up.",
             "Capturar un lead", "Guarda los datos del visitante para que tu equipo de ventas haga seguimiento."),
        ],
    },
    {
        "slug": "stripe", "name": "Stripe", "icon": "credit-card",
        "cat_en": "Payments", "cat_es": "Pagos",
        "diagram": "stripe-integration.png", "excl": None,
        "connect": "manual",
        "cred_en": "your Stripe API key",
        "cred_es": "tu API key de Stripe",
        "value_en": "handle billing and subscriptions",
        "value_es": "gestionar facturacion y suscripciones",
        "caps": [
            ("View a subscription", "Show the visitor their current plan.",
             "Ver una suscripcion", "Muestra al visitante su plan actual."),
            ("View invoices and payment methods", "Let the visitor see invoices and saved payment methods.",
             "Ver facturas y metodos de pago", "Permite al visitante ver facturas y metodos de pago guardados."),
            ("Manage subscription", "Open the billing portal so the visitor can update their plan.",
             "Gestionar suscripcion", "Abre el portal de facturacion para que el visitante actualice su plan."),
            ("Start a purchase", "Generate a checkout link for the visitor.",
             "Iniciar una compra", "Genera un enlace de checkout para el visitante."),
            ("Browse products and prices", "List what's available to buy.",
             "Explorar productos y precios", "Lista lo que esta disponible para comprar."),
        ],
    },
    {
        "slug": "shopify", "name": "Shopify", "icon": "cart-shopping",
        "cat_en": "E-commerce", "cat_es": "E-commerce",
        "diagram": "shopify-integration.png", "excl": "WooCommerce",
        "connect": "oauth",
        "cred_en": "", "cred_es": "",
        "value_en": "browse products and track orders",
        "value_es": "explorar productos y consultar pedidos",
        "caps": [
            ("Browse products", "Help the visitor find products from your catalog.",
             "Explorar productos", "Ayuda al visitante a encontrar productos de tu catalogo."),
            ("Check order status", "Look up an order's status by the visitor's email.",
             "Consultar estado de un pedido", "Consulta el estado de un pedido por el email del visitante."),
        ],
    },
    {
        "slug": "woocommerce", "name": "WooCommerce", "icon": "cart-shopping",
        "cat_en": "E-commerce", "cat_es": "E-commerce",
        "diagram": "woocommerce-integration.png", "excl": "Shopify",
        "connect": "manual",
        "cred_en": "your store URL and WooCommerce API keys (consumer key and secret)",
        "cred_es": "la URL de tu tienda y tus claves de la API de WooCommerce (consumer key y secret)",
        "value_en": "browse products and track orders",
        "value_es": "explorar productos y consultar pedidos",
        "caps": [
            ("Browse products", "Help the visitor find products from your catalog.",
             "Explorar productos", "Ayuda al visitante a encontrar productos de tu catalogo."),
            ("Check order status", "Look up an order's status by the visitor's email.",
             "Consultar estado de un pedido", "Consulta el estado de un pedido por el email del visitante."),
        ],
    },
]


def render_en(p: dict) -> str:
    """Construye el MDX en ingles para un proveedor."""
    name = p["name"]
    cat = p["cat_en"]

    # --- Nota de cabecera: plan + exclusion de categoria si aplica ---
    excl_note = ""
    if p["excl"]:
        excl_note = (f" {name} shares the {cat} category with {p['excl']}, "
                     f"so only one of the two can be active at a time.")
    header_note = (f"<Note>Integrations are available on the **Pro** and "
                   f"**Business** plans.{excl_note}</Note>")

    # --- Tabla de capacidades ---
    cap_rows = "\n".join(f"| **{a}** | {d} |" for a, d, _, _ in p["caps"])

    # --- Paso de conexion segun el tipo (OAuth vs credencial manual) ---
    if p["connect"] == "oauth":
        connect_step = (f"Click **Connect**. A secure popup opens. Sign in to "
                        f"{name} and authorize access. You never type credentials "
                        f"into BestChatBot.")
    else:
        connect_step = (f"Click **Connect**. A secure popup opens. Enter "
                        f"{p['cred_en']}. Your credentials go to the secure form, "
                        f"never into the chat.")

    # --- Nota de reemplazo automatico en el paso final si hay exclusion ---
    live_note = ""
    if p["excl"]:
        live_note = f" If {p['excl']} was connected, it's disconnected automatically."

    # --- Seccion de exclusion mutua (Warning) o nota de "no conflicto" ---
    if p["excl"]:
        excl_section = (
            f"## One per Category\n\n"
            f"{name} is in the **{cat}** category together with {p['excl']}. "
            f"Connecting one disconnects the other, so your bot always has a single, "
            f"clear tool for {cat.lower()}.\n\n"
            f"<Warning>If you connect {name} while {p['excl']} is active, "
            f"{p['excl']} is turned off automatically.</Warning>\n"
        )
    else:
        excl_section = (
            f"## One per Category\n\n"
            f"{name} is the only option in the **{cat}** category, so it never "
            f"conflicts with another integration.\n"
        )

    return f"""---
title: "{name}"
description: "Connect {name} so your chatbot can {p['value_en']} for visitors, right inside the chat."
icon: "{p['icon']}"
---

# {name}

**Category: {cat}.** Connect {name} and your widget can {p['value_en']} for visitors, right inside the chat.

{header_note}

## What Your Bot Can Do

| Action | What happens |
|--------|--------------|
{cap_rows}

## Connection Flow

<Frame>
  <img src="/images/{p['diagram']}" alt="{name} connection flow from the dashboard to a connected, action-ready bot" />
</Frame>

## How to Connect

<Steps>
  <Step title="Open Integrations" icon="plug">
    In your workspace dashboard, open the **Integrations** tab and find **{name}**.
  </Step>
  <Step title="Connect" icon="link">
    {connect_step}
  </Step>
  <Step title="You're live" icon="circle-check">
    Once connected, {name}'s actions become available to your widget right away.{live_note}
  </Step>
</Steps>

<Note>Need a different role to connect? Connecting integrations requires an **Editor**, **Admin**, or **Owner** role. See [Members & Roles](/workspace/members-roles).</Note>

{excl_section}
## Availability

| Plan | {name} |
|------|--------|
| Free | — |
| Starter | — |
| Pro | ✅ |
| Business | ✅ |

## Next Steps

<CardGroup cols={{2}}>
  <Card title="All Integrations" icon="plug" href="/integrations/available-integrations">
    See the full catalog and how categories work.
  </Card>
  <Card title="Agentic Actions" icon="wand-magic-sparkles" href="/integrations/agentic-actions">
    Learn how the bot turns a request into a real action.
  </Card>
</CardGroup>
"""


def render_es(p: dict) -> str:
    """Construye el MDX en espanol (ASCII) para un proveedor."""
    name = p["name"]
    cat = p["cat_es"]

    excl_note = ""
    if p["excl"]:
        excl_note = (f" {name} comparte la categoria {cat} con {p['excl']}, "
                     f"asi que solo una de las dos puede estar activa a la vez.")
    header_note = (f"<Note>Las integraciones estan disponibles en los planes "
                   f"**Pro** y **Business**.{excl_note}</Note>")

    cap_rows = "\n".join(f"| **{a}** | {d} |" for _, _, a, d in p["caps"])

    if p["connect"] == "oauth":
        connect_step = (f"Haz clic en **Conectar**. Se abre un popup seguro. Inicia "
                        f"sesion en {name} y autoriza el acceso. Nunca tecleas "
                        f"credenciales en BestChatBot.")
    else:
        connect_step = (f"Haz clic en **Conectar**. Se abre un popup seguro. Introduce "
                        f"{p['cred_es']}. Tus credenciales van al formulario seguro, "
                        f"nunca al chat.")

    live_note = ""
    if p["excl"]:
        live_note = f" Si {p['excl']} estaba conectada, se desconecta automaticamente."

    if p["excl"]:
        excl_section = (
            f"## Una por categoria\n\n"
            f"{name} esta en la categoria **{cat}** junto con {p['excl']}. "
            f"Conectar una desconecta la otra, para que tu bot tenga siempre una "
            f"unica herramienta clara de {cat.lower()}.\n\n"
            f"<Warning>Si conectas {name} mientras {p['excl']} esta activa, "
            f"{p['excl']} se desactiva automaticamente.</Warning>\n"
        )
    else:
        excl_section = (
            f"## Una por categoria\n\n"
            f"{name} es la unica opcion en la categoria **{cat}**, asi que nunca "
            f"entra en conflicto con otra integracion.\n"
        )

    return f"""---
title: "{name}"
description: "Conecta {name} para que tu chatbot pueda {p['value_es']} por tus visitantes, dentro del chat."
icon: "{p['icon']}"
---

# {name}

**Categoria: {cat}.** Conecta {name} y tu widget podra {p['value_es']} por tus visitantes, dentro del propio chat.

{header_note}

## Que puede hacer tu bot

| Accion | Que ocurre |
|--------|------------|
{cap_rows}

## Flujo de conexion

<Frame>
  <img src="/images/{p['diagram']}" alt="Flujo de conexion de {name} desde el dashboard hasta un bot conectado y listo para actuar" />
</Frame>

## Como conectar

<Steps>
  <Step title="Abre Integraciones" icon="plug">
    En el dashboard de tu workspace, abre la pestana **Integraciones** y busca **{name}**.
  </Step>
  <Step title="Conecta" icon="link">
    {connect_step}
  </Step>
  <Step title="Listo" icon="circle-check">
    Una vez conectada, las acciones de {name} quedan disponibles en tu widget de inmediato.{live_note}
  </Step>
</Steps>

<Note>Necesitas un rol adecuado para conectar: conectar integraciones requiere rol **Editor**, **Admin** u **Owner**. Consulta [Miembros y roles](/es/workspace/members-roles).</Note>

{excl_section}
## Disponibilidad

| Plan | {name} |
|------|--------|
| Free | — |
| Starter | — |
| Pro | ✅ |
| Business | ✅ |

## Siguientes pasos

<CardGroup cols={{2}}>
  <Card title="Todas las integraciones" icon="plug" href="/es/integrations/available-integrations">
    Mira el catalogo completo y como funcionan las categorias.
  </Card>
  <Card title="Acciones agenticas" icon="wand-magic-sparkles" href="/es/integrations/agentic-actions">
    Descubre como el bot convierte una peticion en una accion real.
  </Card>
</CardGroup>
"""


def main() -> None:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    en_dir = os.path.join(root, "integrations", "guides")
    es_dir = os.path.join(root, "es", "integrations", "guides")
    os.makedirs(en_dir, exist_ok=True)
    os.makedirs(es_dir, exist_ok=True)

    written = []
    for p in PROVIDERS:
        en_path = os.path.join(en_dir, f"{p['slug']}.mdx")
        es_path = os.path.join(es_dir, f"{p['slug']}.mdx")
        with open(en_path, "w", encoding="utf-8") as f:
            f.write(render_en(p))
        with open(es_path, "w", encoding="utf-8") as f:
            f.write(render_es(p))
        written.append(p["slug"])

    for slug in written:
        print(f"OK  integrations/guides/{slug}.mdx  +  es/integrations/guides/{slug}.mdx")
    print(f"Total: {len(written) * 2} paginas")


if __name__ == "__main__":
    main()
