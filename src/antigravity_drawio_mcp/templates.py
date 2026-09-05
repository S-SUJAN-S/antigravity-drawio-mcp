"""
High-Level Declarative Diagram Generators for Antigravity Draw.io MCP v2.0.
Provides AI agents with zero-math diagram creation for General Architectures,
C4 Models, ER Database Schemas, and Sequence Diagrams.
"""

from .builder import DrawIOBuilder
from .layout_engine import HierarchicalLayout, GridLayout, ContainerBoundaryCalculator
from .themes import get_node_style, get_edge_style, get_container_style

def generate_smart_diagram(output_path, nodes, edges, containers=None, layout_direction="TB", theme="modern_slate", title="Architecture Diagram"):
    """
    Creates an intelligently styled, auto-laid-out .drawio diagram without requiring
    the AI to compute manual pixel coordinates.
    """
    builder = DrawIOBuilder(page_name=title)
    containers = containers or []

    # 1. Normalize node dimensions and styles
    normalized_nodes = []
    node_meta = {}

    for n in nodes:
        nid = str(n["id"])
        shape = n.get("shape", "rounded_rect")
        role = n.get("role", "primary")

        # Default dimensions by shape
        def_w = 60 if shape == "actor" else (160 if shape == "cylinder" else 150)
        def_h = 80 if shape == "actor" else (70 if shape == "cylinder" else 65)

        w = float(n.get("width", def_w))
        h = float(n.get("height", def_h))

        style = n.get("style") or get_node_style(
            shape=shape,
            role=role,
            theme_name=theme,
            custom_fill=n.get("fill_color"),
            custom_stroke=n.get("stroke_color"),
            custom_font=n.get("font_color")
        )

        n_dict = {
            "id": nid,
            "label": n.get("label", nid),
            "shape": shape,
            "role": role,
            "width": w,
            "height": h,
            "group": n.get("group"),
            "style": style
        }
        normalized_nodes.append(n_dict)
        node_meta[nid] = n_dict

    # 2. Compute Layout Coordinates
    if layout_direction.upper() == "GRID":
        engine = GridLayout()
        coords = engine.layout(normalized_nodes)
    else:
        engine = HierarchicalLayout(direction=layout_direction)
        coords = engine.layout(normalized_nodes, edges)

    # 3. Add Container Swimlanes / Groups FIRST (if any)
    nodes_by_group = {}
    for n in normalized_nodes:
        grp = n.get("group")
        if grp:
            nodes_by_group.setdefault(grp, []).append(n["id"])

    container_dict = {c["id"]: c for c in containers}
    # Also create implied containers if referenced in nodes
    for grp in nodes_by_group.keys():
        if grp not in container_dict:
            container_dict[grp] = {"id": grp, "title": grp.replace("_", " ").title()}

    for cid, cinfo in container_dict.items():
        child_ids = nodes_by_group.get(cid, [])
        child_coords = [coords[child_id] for child_id in child_ids if child_id in coords]
        bounds = ContainerBoundaryCalculator.compute_bounds(child_coords)
        if bounds:
            c_style = get_container_style(theme_name=theme)
            builder.add_node(
                node_id=cid,
                value=cinfo.get("title", cid),
                x=bounds["x"],
                y=bounds["y"],
                width=bounds["width"],
                height=bounds["height"],
                style=c_style
            )

    # 4. Add Nodes SECOND
    for n in normalized_nodes:
        nid = n["id"]
        pos = coords.get(nid, {"x": 100, "y": 100, "width": n["width"], "height": n["height"]})
        builder.add_node(
            node_id=nid,
            value=n["label"],
            x=pos["x"],
            y=pos["y"],
            width=pos["width"],
            height=pos["height"],
            style=n["style"]
        )

    # 5. Add Edges THIRD
    for idx, e in enumerate(edges):
        eid = e.get("id", f"e_{e['source']}_{e['target']}_{idx+1}")
        edge_style_name = e.get("style", "orthogonal")
        is_dashed = e.get("dashed", False) or edge_style_name == "dashed"
        e_style = get_edge_style(
            style_type=edge_style_name,
            theme_name=theme,
            dashed=is_dashed,
            custom_color=e.get("color")
        )

        builder.add_edge(
            edge_id=eid,
            source=e["source"],
            target=e["target"],
            label=e.get("label", ""),
            style=e_style
        )

    builder.save(output_path)
    return output_path


def generate_c4_diagram(output_path, spec):
    """
    Generates an official C4 architecture diagram (Context, Container, or Component view).
    Spec shape:
    {
        "title": "Banking System C4 Model",
        "c4_type": "context" | "container" | "component",
        "people": [{"id": "user", "name": "Customer", "role": "Bank Customer", "description": "Uses web & mobile banking"}],
        "systems": [{"id": "bank_sys", "name": "Internet Banking", "description": "Core customer portal", "external": False}],
        "containers": [{"id": "api_gateway", "name": "API Gateway", "technology": "Kong / Go", "description": "Routes calls"}],
        "boundaries": [{"id": "b1", "title": "Internet Banking Boundary", "container_ids": ["api_gateway"]}],
        "relations": [{"source": "user", "target": "api_gateway", "description": "HTTPS API calls", "technology": "JSON/REST"}]
    }
    """
    nodes = []
    edges = []
    containers = []

    # People (Actors)
    for p in spec.get("people", []):
        lbl = f"<b>{p.get('name', 'User')}</b><br/><i>[Person]</i><br/>{p.get('role', '')}<br/><small>{p.get('description', '')}</small>"
        nodes.append({
            "id": p["id"],
            "label": lbl,
            "shape": "actor",
            "role": "warning",
            "width": 100,
            "height": 110
        })

    # Software Systems
    for s in spec.get("systems", []):
        ext = s.get("external", False)
        role = "danger" if ext else "primary"
        tag = "[External Software System]" if ext else "[Software System]"
        lbl = f"<b>{s.get('name', '')}</b><br/><i>{tag}</i><br/><small>{s.get('description', '')}</small>"
        nodes.append({
            "id": s["id"],
            "label": lbl,
            "shape": "rounded_rect",
            "role": role,
            "width": 170,
            "height": 80
        })

    # Containers
    for c in spec.get("containers", []):
        tech = f"[{c.get('technology', '')}]" if c.get("technology") else "[Container]"
        lbl = f"<b>{c.get('name', '')}</b><br/><i>{tech}</i><br/><small>{c.get('description', '')}</small>"
        nodes.append({
            "id": c["id"],
            "label": lbl,
            "shape": "rounded_rect",
            "role": "secondary",
            "group": c.get("boundary_id"),
            "width": 160,
            "height": 75
        })

    # Components
    for comp in spec.get("components", []):
        tech = f"[{comp.get('technology', '')}]" if comp.get("technology") else "[Component]"
        lbl = f"<b>{comp.get('name', '')}</b><br/><i>{tech}</i><br/><small>{comp.get('description', '')}</small>"
        nodes.append({
            "id": comp["id"],
            "label": lbl,
            "shape": "rounded_rect",
            "role": "accent",
            "group": comp.get("container_id"),
            "width": 150,
            "height": 70
        })

    # Boundaries
    for b in spec.get("boundaries", []):
        containers.append({
            "id": b["id"],
            "title": b.get("title", "Boundary")
        })

    # Relations
    for r in spec.get("relations", []):
        tech_label = f" [{r['technology']}]" if r.get("technology") else ""
        full_label = f"{r.get('description', '')}{tech_label}"
        edges.append({
            "source": r["source"],
            "target": r["target"],
            "label": full_label,
            "style": "orthogonal"
        })

    return generate_smart_diagram(
        output_path=output_path,
        nodes=nodes,
        edges=edges,
        containers=containers,
        layout_direction="TB",
        theme="c4_model",
        title=spec.get("title", "C4 Model Architecture")
    )


def generate_er_diagram(output_path, spec):
    """
    Generates an Entity-Relationship (ER) database schema diagram.
    Spec shape:
    {
        "title": "E-Commerce Database Schema",
        "entities": [
            {
                "name": "users",
                "fields": [
                    {"name": "id", "type": "INT", "is_pk": True},
                    {"name": "email", "type": "VARCHAR(255)", "is_pk": False, "is_fk": False},
                    {"name": "created_at", "type": "TIMESTAMP"}
                ]
            }
        ],
        "relationships": [
            {"source": "users", "target": "orders", "cardinality": "1:N", "label": "places"}
        ]
    }
    """
    nodes = []
    edges = []

    for ent in spec.get("entities", []):
        tname = ent["name"]
        field_rows = []
        for f in ent.get("fields", []):
            pk_badge = "<b>[PK]</b> " if f.get("is_pk") else ("<i>[FK]</i> " if f.get("is_fk") else "")
            ftype = f.get("type", "TEXT")
            field_rows.append(f"{pk_badge}{f['name']} : <small>{ftype}</small>")

        fields_html = "<br/>".join(field_rows)
        card_content = f"<table style='width:100%; border-collapse:collapse;'>" \
                       f"<tr><td style='background:#334155; color:#ffffff; padding:4px; text-align:center;'><b>{tname}</b></td></tr>" \
                       f"<tr><td style='padding:6px; background:#F8FAFC; text-align:left;'>{fields_html}</td></tr>" \
                       f"</table>"

        node_h = max(80, 45 + len(ent.get("fields", [])) * 20)
        nodes.append({
            "id": tname,
            "label": card_content,
            "shape": "rectangle",
            "role": "primary",
            "width": 190,
            "height": node_h
        })

    for rel in spec.get("relationships", []):
        card = rel.get("cardinality", "1:N")
        lbl = f"{rel.get('label', '')} ({card})" if rel.get("label") else card
        edges.append({
            "source": rel["source"],
            "target": rel["target"],
            "label": lbl,
            "style": "orthogonal"
        })

    return generate_smart_diagram(
        output_path=output_path,
        nodes=nodes,
        edges=edges,
        layout_direction="LR",
        theme="modern_slate",
        title=spec.get("title", "Database ER Diagram")
    )


def generate_sequence_diagram(output_path, spec):
    """
    Generates a UML Sequence Diagram showing interaction flows across lifelines.
    Spec shape:
    {
        "title": "User Checkout Sequence",
        "participants": [
            {"id": "user", "name": "User"},
            {"id": "web", "name": "Frontend Web"},
            {"id": "api", "name": "Order API"},
            {"id": "pay", "name": "Payment Gateway"}
        ],
        "messages": [
            {"source": "user", "target": "web", "label": "Click Pay"},
            {"source": "web", "target": "api", "label": "POST /orders"},
            {"source": "api", "target": "pay", "label": "Charge Card"},
            {"source": "pay", "target": "api", "label": "200 OK (Auth Token)", "type": "return"},
            {"source": "api", "target": "web", "label": "Order Created", "type": "return"}
        ]
    }
    """
    builder = DrawIOBuilder(page_name=spec.get("title", "Sequence Diagram"))
    participants = spec.get("participants", [])
    messages = spec.get("messages", [])

    # Calculate layout: Participants across top, lifelines down
    part_w = 120
    part_h = 50
    part_spacing = 160
    start_x = 80
    start_y = 60
    total_messages = max(len(messages), 1)
    line_length = 80 + total_messages * 60

    x_positions = {}
    for idx, p in enumerate(participants):
        x = start_x + idx * (part_w + part_spacing)
        x_positions[p["id"]] = x + part_w / 2.0

        # Header box
        header_style = "rounded=1;whiteSpace=wrap;html=1;fillColor=#E0E7FF;strokeColor=#4338CA;fontColor=#1E1B4B;fontStyle=1;"
        builder.add_node(p["id"], f"<b>{p.get('name', p['id'])}</b>", x, start_y, width=part_w, height=part_h, style=header_style)

        # Lifeline (vertical line)
        lifeline_id = f"line_{p['id']}"
        lifeline_style = "shape=line;dashed=1;strokeColor=#94A3B8;strokeWidth=1.5;direction=south;"
        builder.add_node(lifeline_id, "", x + (part_w / 2.0), start_y + part_h, width=10, height=line_length, style=lifeline_style)

    # Messages (horizontal arrows)
    msg_y = start_y + part_h + 40
    for idx, m in enumerate(messages):
        src_x = x_positions.get(m["source"], start_x)
        tgt_x = x_positions.get(m["target"], start_x + 200)
        is_return = m.get("type") == "return"

        arrow_style = "edgeStyle=none;html=1;endArrow=classic;"
        if is_return:
            arrow_style += "dashed=1;strokeColor=#64748B;"
        else:
            arrow_style += "strokeColor=#2563EB;strokeWidth=1.5;"

        edge_id = f"msg_{idx+1}"
        # We create point-to-point connection or small anchor nodes
        src_anchor_id = f"anc_s_{idx+1}"
        tgt_anchor_id = f"anc_t_{idx+1}"

        anchor_style = "ellipse;whiteSpace=wrap;html=1;fillColor=none;strokeColor=none;"
        builder.add_node(src_anchor_id, "", src_x - 3, msg_y - 3, width=6, height=6, style=anchor_style)
        builder.add_node(tgt_anchor_id, "", tgt_x - 3, msg_y - 3, width=6, height=6, style=anchor_style)

        builder.add_edge(edge_id, src_anchor_id, tgt_anchor_id, label=m.get("label", ""), style=arrow_style)
        msg_y += 55

    builder.save(output_path)
    return output_path
