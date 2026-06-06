"""Genera las 16 paginas de guia por integracion (8 proveedores x EN/ES).

Cada pagina dice EXACTAMENTE que puede y que NO puede hacer cada integracion,
extraido del codigo fuente real de cada connector (_definitions.py: tools
activas, parametros, identity_required, y tools desactivadas/comentadas).

Salida:
  EN -> integrations/guides/<slug>.mdx
  ES -> es/integrations/guides/<slug>.mdx   (estilo ASCII, sin tildes/enie)

Fuente de verdad (backend/agentic/connectors/<provider>/_definitions.py):
  - caps: tools ACTIVAS con sus matices reales (rango 7 dias, last-4 only, etc.).
  - cannot: tools desactivadas/comentadas + acciones que el connector no expone.
  - auth (Needs sign-in): el flag identity_required de cada ToolDef.
"""

import os

# connect: "oauth" (login + autorizar) o "manual" (pegar credencial).
# caps: lista de dicts {act_en, desc_en, act_es, desc_es, auth} (auth = identity_required).
# cannot_en/cannot_es: lo que la integracion NO puede hacer (verificado en codigo).
PROVIDERS = [
    {
        "slug": "cal-com", "name": "Cal.com", "icon": "calendar",
        "cat_en": "Scheduling", "cat_es": "Agendamiento",
        "diagram": "calcom-integration.png", "excl": "Calendly", "connect": "manual",
        "cred_en": "your Cal.com API key", "cred_es": "tu API key de Cal.com",
        "value_en": "book and cancel meetings", "value_es": "agendar y cancelar reuniones",
        "caps": [
            {"act_en": "Check availability", "auth": False,
             "desc_en": "Show the visitor open time slots from your calendar, up to 7 days per request.",
             "act_es": "Consultar disponibilidad",
             "desc_es": "Muestra al visitante los horarios libres de tu calendario, hasta 7 dias por consulta."},
            {"act_en": "Book a meeting", "auth": False,
             "desc_en": "Schedule a meeting once the visitor picks a slot and gives their name and email.",
             "act_es": "Agendar una reunion",
             "desc_es": "Agenda una reunion cuando el visitante elige un hueco y da su nombre y email."},
            {"act_en": "Cancel a meeting", "auth": True,
             "desc_en": "Cancel a meeting the visitor booked, found by their email. The bot asks for confirmation first.",
             "act_es": "Cancelar una reunion",
             "desc_es": "Cancela una reunion que agendo el visitante, buscandola por su email. El bot pide confirmacion antes."},
        ],
        "cannot_en": [
            "Reschedule a meeting (the visitor cancels and books a new time instead)",
            "List or show all of a visitor's meetings",
            "Check availability more than 7 days ahead in a single request",
        ],
        "cannot_es": [
            "Reprogramar una reunion (el visitante cancela y agenda un nuevo horario)",
            "Listar o mostrar todas las reuniones de un visitante",
            "Consultar disponibilidad de mas de 7 dias en una sola peticion",
        ],
    },
    {
        "slug": "calendly", "name": "Calendly", "icon": "calendar",
        "cat_en": "Scheduling", "cat_es": "Agendamiento",
        "diagram": "calendly-integration.png", "excl": "Cal.com", "connect": "oauth",
        "cred_en": "", "cred_es": "",
        "value_en": "book and cancel meetings", "value_es": "agendar y cancelar reuniones",
        "caps": [
            {"act_en": "Check availability", "auth": False,
             "desc_en": "Show the visitor open time slots from your calendar, up to 7 days per request.",
             "act_es": "Consultar disponibilidad",
             "desc_es": "Muestra al visitante los horarios libres de tu calendario, hasta 7 dias por consulta."},
            {"act_en": "Book a meeting", "auth": False,
             "desc_en": "Schedule a meeting once the visitor picks a slot and gives their name and email.",
             "act_es": "Agendar una reunion",
             "desc_es": "Agenda una reunion cuando el visitante elige un hueco y da su nombre y email."},
            {"act_en": "Cancel a meeting", "auth": True,
             "desc_en": "Cancel a meeting the visitor booked, found by their email. The bot asks for confirmation first.",
             "act_es": "Cancelar una reunion",
             "desc_es": "Cancela una reunion que agendo el visitante, buscandola por su email. El bot pide confirmacion antes."},
        ],
        "cannot_en": [
            "Reschedule a meeting (the visitor cancels and books a new time instead)",
            "List or show all of a visitor's meetings",
            "Check availability more than 7 days ahead in a single request",
        ],
        "cannot_es": [
            "Reprogramar una reunion (el visitante cancela y agenda un nuevo horario)",
            "Listar o mostrar todas las reuniones de un visitante",
            "Consultar disponibilidad de mas de 7 dias en una sola peticion",
        ],
    },
    {
        "slug": "freshdesk", "name": "Freshdesk", "icon": "headset",
        "cat_en": "Help Desk", "cat_es": "Mesa de ayuda",
        "diagram": "freshdesk-integration.png", "excl": "Zendesk", "connect": "manual",
        "cred_en": "your Freshdesk API key and domain", "cred_es": "tu API key y dominio de Freshdesk",
        "value_en": "open and check support tickets", "value_es": "abrir y consultar tickets de soporte",
        "caps": [
            {"act_en": "Open a support ticket", "auth": False,
             "desc_en": "Create a ticket with a subject, description, and priority (low, medium, high, or urgent).",
             "act_es": "Abrir un ticket de soporte",
             "desc_es": "Crea un ticket con asunto, descripcion y prioridad (low, medium, high o urgent)."},
            {"act_en": "Check a ticket's status", "auth": True,
             "desc_en": "Look up a ticket's status and the latest replies from your team, by email or ticket ID.",
             "act_es": "Consultar el estado de un ticket",
             "desc_es": "Consulta el estado de un ticket y las ultimas respuestas de tu equipo, por email o ID de ticket."},
        ],
        "cannot_en": [
            "Reply to or comment on a ticket",
            "Close, resolve, or reassign a ticket",
            "Attach files to a ticket",
        ],
        "cannot_es": [
            "Responder o comentar en un ticket",
            "Cerrar, resolver o reasignar un ticket",
            "Adjuntar archivos a un ticket",
        ],
    },
    {
        "slug": "zendesk", "name": "Zendesk", "icon": "headset",
        "cat_en": "Help Desk", "cat_es": "Mesa de ayuda",
        "diagram": "zendesk-integration.png", "excl": "Freshdesk", "connect": "oauth",
        "cred_en": "", "cred_es": "",
        "value_en": "open and check support tickets", "value_es": "abrir y consultar tickets de soporte",
        "caps": [
            {"act_en": "Open a support ticket", "auth": False,
             "desc_en": "Create a ticket with a subject, description, and priority (low, normal, high, or urgent).",
             "act_es": "Abrir un ticket de soporte",
             "desc_es": "Crea un ticket con asunto, descripcion y prioridad (low, normal, high o urgent)."},
            {"act_en": "Check a ticket's status", "auth": True,
             "desc_en": "Look up a ticket's status and the latest replies from your team, by email or ticket ID.",
             "act_es": "Consultar el estado de un ticket",
             "desc_es": "Consulta el estado de un ticket y las ultimas respuestas de tu equipo, por email o ID de ticket."},
        ],
        "cannot_en": [
            "Reply to or comment on a ticket",
            "Close, resolve, or reassign a ticket",
            "Attach files to a ticket",
        ],
        "cannot_es": [
            "Responder o comentar en un ticket",
            "Cerrar, resolver o reasignar un ticket",
            "Adjuntar archivos a un ticket",
        ],
    },
    {
        "slug": "hubspot", "name": "HubSpot", "icon": "address-book",
        "cat_en": "CRM", "cat_es": "CRM",
        "diagram": "hubspot-integration.png", "excl": None, "connect": "oauth",
        "cred_en": "", "cred_es": "",
        "value_en": "capture leads", "value_es": "capturar leads",
        "caps": [
            {"act_en": "Capture a lead", "auth": False,
             "desc_en": "Save the visitor as a new contact with their name, email, company, and what they're interested in.",
             "act_es": "Capturar un lead",
             "desc_es": "Guarda al visitante como un contacto nuevo con su nombre, email, empresa y lo que le interesa."},
        ],
        "cannot_en": [
            "Look up, search, or update existing contacts",
            "View deals, companies, or pipelines",
            "Do anything beyond capturing a new lead",
        ],
        "cannot_es": [
            "Buscar, consultar o actualizar contactos existentes",
            "Ver negocios (deals), empresas o pipelines",
            "Hacer cualquier cosa mas alla de capturar un lead nuevo",
        ],
    },
    {
        "slug": "stripe", "name": "Stripe", "icon": "credit-card",
        "cat_en": "Payments", "cat_es": "Pagos",
        "diagram": "stripe-integration.png", "excl": None, "connect": "manual",
        "cred_en": "your Stripe API key", "cred_es": "tu API key de Stripe",
        "value_en": "answer billing questions and start purchases", "value_es": "responder dudas de facturacion e iniciar compras",
        "caps": [
            {"act_en": "Check a subscription", "auth": True,
             "desc_en": "Show the visitor their current plan and next billing date.",
             "act_es": "Ver una suscripcion",
             "desc_es": "Muestra al visitante su plan actual y la proxima fecha de cobro."},
            {"act_en": "Check invoice history", "auth": True,
             "desc_en": "List the visitor's recent invoices with amounts, dates, and payment status.",
             "act_es": "Ver historial de facturas",
             "desc_es": "Lista las facturas recientes del visitante con importes, fechas y estado de pago."},
            {"act_en": "Check payment methods", "auth": True,
             "desc_en": "Show saved payment methods (card brand and last 4 digits only).",
             "act_es": "Ver metodos de pago",
             "desc_es": "Muestra los metodos de pago guardados (solo marca de la tarjeta y ultimos 4 digitos)."},
            {"act_en": "Open the billing portal", "auth": True,
             "desc_en": "Give the visitor a secure portal link to cancel, upgrade, or update payment themselves.",
             "act_es": "Abrir el portal de facturacion",
             "desc_es": "Da al visitante un enlace seguro al portal para cancelar, mejorar o actualizar el pago por su cuenta."},
            {"act_en": "Start a purchase", "auth": False,
             "desc_en": "Generate a checkout link so the visitor can buy a plan or product.",
             "act_es": "Iniciar una compra",
             "desc_es": "Genera un enlace de checkout para que el visitante compre un plan o producto."},
        ],
        "cannot_en": [
            "Cancel or change a subscription directly (it hands the visitor a secure portal link instead)",
            "Issue refunds or charge a card",
            "Create or edit products and prices",
            "Show full card numbers (only the brand and last 4 digits)",
        ],
        "cannot_es": [
            "Cancelar o cambiar una suscripcion directamente (entrega al visitante un enlace seguro al portal)",
            "Emitir reembolsos o cobrar una tarjeta",
            "Crear o editar productos y precios",
            "Mostrar el numero completo de la tarjeta (solo marca y ultimos 4 digitos)",
        ],
    },
    {
        "slug": "shopify", "name": "Shopify", "icon": "cart-shopping",
        "cat_en": "E-commerce", "cat_es": "E-commerce",
        "diagram": "shopify-integration.png", "excl": "WooCommerce", "connect": "oauth",
        "cred_en": "", "cred_es": "",
        "value_en": "find products and check orders", "value_es": "encontrar productos y consultar pedidos",
        "caps": [
            {"act_en": "Search products", "auth": False,
             "desc_en": "Search your catalog by keyword and show product cards with price, image, and a buy link (up to 10).",
             "act_es": "Buscar productos",
             "desc_es": "Busca en tu catalogo por palabra clave y muestra tarjetas con precio, imagen y enlace de compra (hasta 10)."},
            {"act_en": "Check order status", "auth": True,
             "desc_en": "Look up an order's status, tracking, and delivery by the visitor's email.",
             "act_es": "Consultar estado de un pedido",
             "desc_es": "Consulta el estado, el seguimiento y la entrega de un pedido por el email del visitante."},
        ],
        "cannot_en": [
            "Add items to a cart or check out from the chat (visitors do that on your store)",
            "Process returns or change an order from the chat",
            "Look up an order without the visitor's email",
        ],
        "cannot_es": [
            "Anadir productos al carrito o pagar desde el chat (el visitante lo hace en tu tienda)",
            "Gestionar devoluciones o modificar un pedido desde el chat",
            "Consultar un pedido sin el email del visitante",
        ],
    },
    {
        "slug": "woocommerce", "name": "WooCommerce", "icon": "cart-shopping",
        "cat_en": "E-commerce", "cat_es": "E-commerce",
        "diagram": "woocommerce-integration.png", "excl": "Shopify", "connect": "manual",
        "cred_en": "your store URL and WooCommerce API keys (consumer key and secret)",
        "cred_es": "la URL de tu tienda y tus claves de la API de WooCommerce (consumer key y secret)",
        "value_en": "find products and check orders", "value_es": "encontrar productos y consultar pedidos",
        "caps": [
            {"act_en": "Search products", "auth": False,
             "desc_en": "Search your catalog by keyword and show products with price and image (up to 100).",
             "act_es": "Buscar productos",
             "desc_es": "Busca en tu catalogo por palabra clave y muestra productos con precio e imagen (hasta 100)."},
            {"act_en": "Check order status", "auth": True,
             "desc_en": "Look up an order's status and details by the visitor's email.",
             "act_es": "Consultar estado de un pedido",
             "desc_es": "Consulta el estado y los detalles de un pedido por el email del visitante."},
        ],
        "cannot_en": [
            "Add items to a cart or check out from the chat (visitors do that on your store)",
            "Process returns or change an order from the chat",
            "Look up an order without the visitor's email",
        ],
        "cannot_es": [
            "Anadir productos al carrito o pagar desde el chat (el visitante lo hace en tu tienda)",
            "Gestionar devoluciones o modificar un pedido desde el chat",
            "Consultar un pedido sin el email del visitante",
        ],
    },
]


def _caps_table(p: dict, lang: str) -> str:
    """Tabla de capacidades con columna 'requiere identidad'."""
    if lang == "en":
        header = "| Action | What it does | Needs sign-in |\n|--------|--------------|:-------------:|"
        rows = [
            f"| **{c['act_en']}** | {c['desc_en']} | {'Yes' if c['auth'] else 'No'} |"
            for c in p["caps"]
        ]
    else:
        header = "| Accion | Que hace | Requiere identidad |\n|--------|----------|:------------------:|"
        rows = [
            f"| **{c['act_es']}** | {c['desc_es']} | {'Si' if c['auth'] else 'No'} |"
            for c in p["caps"]
        ]
    return header + "\n" + "\n".join(rows)


def render_en(p: dict) -> str:
    """Construye el MDX en ingles para un proveedor."""
    name, cat = p["name"], p["cat_en"]

    excl_note = ""
    if p["excl"]:
        excl_note = (f" {name} shares the {cat} category with {p['excl']}, "
                     f"so only one of the two can be active at a time.")
    header_note = (f"<Note>Integrations are available on the **Pro** and "
                   f"**Business** plans.{excl_note}</Note>")

    cant_rows = "\n".join(f"- {item}" for item in p["cannot_en"])

    if p["connect"] == "oauth":
        connect_step = (f"Click **Connect**. A secure popup opens. Sign in to "
                        f"{name} and authorize access. You never type credentials "
                        f"into BestChatBot.")
    else:
        connect_step = (f"Click **Connect**. A secure popup opens. Enter "
                        f"{p['cred_en']}. Your credentials go to the secure form, "
                        f"never into the chat.")

    live_note = f" If {p['excl']} was connected, it's disconnected automatically." if p["excl"] else ""

    if p["excl"]:
        excl_section = (
            f"## One per Category\n\n"
            f"{name} is in the **{cat}** category with {p['excl']}. Connecting one "
            f"disconnects the other, so your bot always has a single, clear tool for "
            f"{cat.lower()}.\n\n"
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
description: "What the {name} integration can and can't do, and how to connect it."
icon: "{p['icon']}"
---

# {name}

**Category: {cat}.** Connect {name} and your widget can {p['value_en']} for visitors, right inside the chat.

{header_note}

## What This Bot Can Do

The bot does exactly these actions, nothing more. "Needs sign-in" means the visitor must be identified first; otherwise the bot gives a safe, neutral answer.

{_caps_table(p, "en")}

## What It Can't Do

{name} is scoped to the actions above. It does **not**:

{cant_rows}

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

<Note>Connecting integrations requires an **Editor**, **Admin**, or **Owner** role. See [Members & Roles](/workspace/members-roles).</Note>

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
    name, cat = p["name"], p["cat_es"]

    excl_note = ""
    if p["excl"]:
        excl_note = (f" {name} comparte la categoria {cat} con {p['excl']}, "
                     f"asi que solo una de las dos puede estar activa a la vez.")
    header_note = (f"<Note>Las integraciones estan disponibles en los planes "
                   f"**Pro** y **Business**.{excl_note}</Note>")

    cant_rows = "\n".join(f"- {item}" for item in p["cannot_es"])

    if p["connect"] == "oauth":
        connect_step = (f"Haz clic en **Conectar**. Se abre un popup seguro. Inicia "
                        f"sesion en {name} y autoriza el acceso. Nunca tecleas "
                        f"credenciales en BestChatBot.")
    else:
        connect_step = (f"Haz clic en **Conectar**. Se abre un popup seguro. Introduce "
                        f"{p['cred_es']}. Tus credenciales van al formulario seguro, "
                        f"nunca al chat.")

    live_note = f" Si {p['excl']} estaba conectada, se desconecta automaticamente." if p["excl"] else ""

    if p["excl"]:
        excl_section = (
            f"## Una por categoria\n\n"
            f"{name} esta en la categoria **{cat}** con {p['excl']}. Conectar una "
            f"desconecta la otra, para que tu bot tenga siempre una unica herramienta "
            f"clara de {cat.lower()}.\n\n"
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
description: "Que puede y que NO puede hacer la integracion de {name}, y como conectarla."
icon: "{p['icon']}"
---

# {name}

**Categoria: {cat}.** Conecta {name} y tu widget podra {p['value_es']} por tus visitantes, dentro del propio chat.

{header_note}

## Que puede hacer este bot

El bot hace exactamente estas acciones, nada mas. "Requiere identidad" significa que el visitante debe estar identificado primero; si no, el bot da una respuesta segura y neutra.

{_caps_table(p, "es")}

## Que NO puede hacer

{name} se limita a las acciones de arriba. **No** puede:

{cant_rows}

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

<Note>Conectar integraciones requiere rol **Editor**, **Admin** u **Owner**. Consulta [Miembros y roles](/es/workspace/members-roles).</Note>

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

    for p in PROVIDERS:
        with open(os.path.join(en_dir, f"{p['slug']}.mdx"), "w", encoding="utf-8") as f:
            f.write(render_en(p))
        with open(os.path.join(es_dir, f"{p['slug']}.mdx"), "w", encoding="utf-8") as f:
            f.write(render_es(p))
        print(f"OK  {p['slug']} (EN+ES)  caps={len(p['caps'])} cannot={len(p['cannot_en'])}")
    print(f"Total: {len(PROVIDERS) * 2} paginas")


if __name__ == "__main__":
    main()
