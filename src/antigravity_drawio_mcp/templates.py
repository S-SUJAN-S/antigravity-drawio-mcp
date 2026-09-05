"""
High-Level Declarative Diagram Generators for Antigravity Draw.io MCP v2.0.
Provides AI agents with zero-math diagram creation for General Architectures,
C4 Models, ER Database Schemas, and Sequence Diagrams with publication-grade aesthetics.
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
        def_w = 70 if shape == "actor" else (160 if shape == "cylinder" else 150)
        def_h = 100 if shape == "actor" else (75 if shape == "cylinder" else 65)

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

    # 3. Add Container Swimlanes / Groups FIRST
    nodes_by_group = {}
    for n in normalized_nodes:
        grp = n.get("group")
        if grp:
            nodes_by_group.setdefault(grp, []).append(n["id"])

    container_dict = {c["id"]: c for c in containers}
    for grp in nodes_by_group.keys():
        if grp not in container_dict:
            container_dict[grp] = {"id": grp, "title": grp.replace("_", " ").title()}

    for cid, cinfo in container_dict.items():
        child_ids = nodes_by_group.get(cid, [])
        child_coords = [coords[child_id] for child_id in child_ids if child_id in coords]
        bounds = ContainerBoundaryCalculator.compute_bounds(child_coords, padding=40.0, header_height=32.0)
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
    Generates an authentic C4 architecture diagram (Context, Container, or Component view)
    with high-contrast typography, official card proportions, and clear actor figures.
    """
    nodes = []
    edges = []
    containers = []

    # People (Actors)
    for p in spec.get("people", []):
        lbl = (
            f"<b>{p.get('name', 'User')}</b><br/>"
            f"<span style='font-size:11px; color:#475569;'><i>[Person]</i></span><br/>"
            f"<span style='font-size:10px; color:#64748B;'>{p.get('role', '')}</span>"
        )
        nodes.append({
            "id": p["id"],
            "label": lbl,
            "shape": "actor",
            "role": "warning",
            "width": 80,
            "height": 105
        })

    # Software Systems
    for s in spec.get("systems", []):
        ext = s.get("external", False)
        role = "danger" if ext else "primary"
        tag = "[External Software System]" if ext else "[Software System]"
        sub_color = "#E2E8F0" if not ext else "#334155"
        text_color = "#FFFFFF" if not ext else "#1E293B"
        lbl = (
            f"<div style='text-align:center; padding:6px; color:{text_color};'>"
            f"<b style='font-size:13px;'>{s.get('name', '')}</b><br/>"
            f"<span style='font-size:11px; opacity:0.85; color:{sub_color};'><i>{tag}</i></span><br/><br/>"
            f"<span style='font-size:11px;'>{s.get('description', '')}</span>"
            f"</div>"
        )
        nodes.append({
            "id": s["id"],
            "label": lbl,
            "shape": "rounded_rect",
            "role": role,
            "width": 190,
            "height": 95
        })

    # Containers
    for c in spec.get("containers", []):
        tech = f"[{c.get('technology', '')}]" if c.get("technology") else "[Container]"
        lbl = (
            f"<div style='text-align:center; padding:6px; color:#FFFFFF;'>"
            f"<b style='font-size:13px;'>{c.get('name', '')}</b><br/>"
            f"<span style='font-size:11px; opacity:0.85; color:#E0E7FF;'><i>{tech}</i></span><br/><br/>"
            f"<span style='font-size:11px;'>{c.get('description', '')}</span>"
            f"</div>"
        )
        nodes.append({
            "id": c["id"],
            "label": lbl,
            "shape": "rounded_rect",
            "role": "secondary",
            "group": c.get("boundary_id"),
            "width": 180,
            "height": 90
        })

    # Components
    for comp in spec.get("components", []):
        tech = f"[{comp.get('technology', '')}]" if comp.get("technology") else "[Component]"
        lbl = (
            f"<div style='text-align:center; padding:6px; color:#0F172A;'>"
            f"<b style='font-size:12px;'>{comp.get('name', '')}</b><br/>"
            f"<span style='font-size:10px; color:#475569;'><i>{tech}</i></span><br/><br/>"
            f"<span style='font-size:10px;'>{comp.get('description', '')}</span>"
            f"</div>"
        )
        nodes.append({
            "id": comp["id"],
            "label": lbl,
            "shape": "rounded_rect",
            "role": "accent",
            "group": comp.get("container_id"),
            "width": 170,
            "height": 85
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
    Generates a professional Entity-Relationship (ER) database schema diagram
    with clean table cards, primary/foreign key badges, and crow's foot relationships.
    """
    nodes = []
    edges = []

    for ent in spec.get("entities", []):
        tname = ent["name"]
        field_rows = []
        for idx, f in enumerate(ent.get("fields", [])):
            pk_badge = "<b style='color:#E11D48;'>[PK]</b> " if f.get("is_pk") else ("<i style='color:#2563EB;'>[FK]</i> " if f.get("is_fk") else "")
            ftype = f.get("type", "TEXT")
            bg = "#F8FAFC" if idx % 2 == 0 else "#FFFFFF"
            field_rows.append(
                f"<tr style='background:{bg};'>"
                f"<td style='padding:4px 8px; text-align:left; border-top:1px solid #E2E8F0; font-family:Courier New, monospace; font-size:11px;'>"
                f"{pk_badge}<b>{f['name']}</b> : <span style='color:#64748B;'>{ftype}</span></td></tr>"
            )

        fields_html = "".join(field_rows)
        card_content = (
            f"<table style='width:100%; border-collapse:collapse; font-family:Helvetica;'>"
            f"<thead><tr><td style='background:#1E293B; color:#FFFFFF; padding:6px 10px; font-size:12px; font-weight:bold; text-align:center;'>"
            f"{tname}</td></tr></thead>"
            f"<tbody>{fields_html}</tbody>"
            f"</table>"
        )

        node_h = max(75, 36 + len(ent.get("fields", [])) * 24)
        nodes.append({
            "id": tname,
            "label": card_content,
            "shape": "rectangle",
            "role": "primary",
            "style": "rounded=0;whiteSpace=wrap;html=1;overflow=fill;strokeColor=#334155;strokeWidth=1.5;fillColor=#FFFFFF;shadow=1;",
            "width": 200,
            "height": node_h
        })

    for rel in spec.get("relationships", []):
        card = rel.get("cardinality", "1:N").upper()
        if card in ["1:N", "1:*"]:
            style_name = "er_one_to_many"
        elif card in ["M:N", "*:*"]:
            style_name = "er_many_to_many"
        else:
            style_name = "er_one_to_one"

        edges.append({
            "source": rel["source"],
            "target": rel["target"],
            "label": rel.get("label", card),
            "style": style_name
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
    Generates an authentic UML Sequence Diagram with vertical lifelines,
    execution activation blocks, message call arrows, and return dashes.
    """
    builder = DrawIOBuilder(page_name=spec.get("title", "Sequence Diagram"))
    participants = spec.get("participants", [])
    messages = spec.get("messages", [])

    part_w = 130
    part_h = 45
    part_spacing = 170
    start_x = 80
    start_y = 60
    total_messages = max(len(messages), 1)
    line_length = 80 + total_messages * 60

    x_positions = {}
    for idx, p in enumerate(participants):
        x = start_x + idx * (part_w + part_spacing)
        x_positions[p["id"]] = x + part_w / 2.0

        # Header box
        header_style = "rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=#EEF2FF;strokeColor=#4F46E5;fontColor=#1E1B4B;fontStyle=1;shadow=1;"
        builder.add_node(p["id"], f"<b>{p.get('name', p['id'])}</b>", x, start_y, width=part_w, height=part_h, style=header_style)

        # Lifeline (vertical line)
        lifeline_id = f"line_{p['id']}"
        lifeline_style = "shape=line;dashed=1;strokeColor=#94A3B8;strokeWidth=1.5;direction=south;"
        builder.add_node(lifeline_id, "", x + (part_w / 2.0), start_y + part_h, width=10, height=line_length, style=lifeline_style)

    # Messages and Activation Boxes
    msg_y = start_y + part_h + 40
    for idx, m in enumerate(messages):
        src_id = m["source"]
        tgt_id = m["target"]
        src_x = x_positions.get(src_id, start_x)
        tgt_x = x_positions.get(tgt_id, start_x + 200)
        is_return = m.get("type") == "return"

        # Target Activation box centered symmetrically around msg_y
        act_box_id = f"act_{idx+1}"
        act_style = "rounded=0;whiteSpace=wrap;html=1;fillColor=#F1F5F9;strokeColor=#475569;strokeWidth=1;"
        builder.add_node(act_box_id, "", tgt_x - 6, msg_y - 15, width=12, height=30, style=act_style)

        # Anchor points for strictly horizontal arrows
        src_anchor_id = f"anc_s_{idx+1}"
        tgt_anchor_id = f"anc_t_{idx+1}"
        anchor_style = "ellipse;whiteSpace=wrap;html=1;fillColor=none;strokeColor=none;"
        builder.add_node(src_anchor_id, "", src_x - 2, msg_y - 2, width=4, height=4, style=anchor_style)
        builder.add_node(tgt_anchor_id, "", tgt_x - 6 if tgt_x > src_x else tgt_x + 6, msg_y - 2, width=4, height=4, style=anchor_style)

        arrow_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=classic;entryY=0.5;exitY=0.5;labelBackgroundColor=#FFFFFF;fontColor=#334155;fontSize=11;fontFamily=Helvetica;"
        if is_return:
            arrow_style += "dashed=1;strokeColor=#64748B;"
        else:
            arrow_style += "strokeColor=#2563EB;strokeWidth=1.5;"

        edge_id = f"msg_{idx+1}"
        builder.add_edge(edge_id, src_anchor_id, tgt_anchor_id, label=m.get("label", ""), style=arrow_style)
        msg_y += 55

    builder.save(output_path)
    return output_path
