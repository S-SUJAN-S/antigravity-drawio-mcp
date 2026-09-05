"""
Surgical Diagram Patching and Beautification Engine for Antigravity Draw.io MCP v2.0.
Allows incremental modification (add/delete/update nodes, rewire edges, group into containers,
highlight execution paths) and automated aesthetic restyling.
"""

from .parser import DrawIOParser
from .builder import DrawIOBuilder
from .layout_engine import HierarchicalLayout, ContainerBoundaryCalculator
from .themes import get_node_style, get_edge_style, get_container_style

class DiagramEditor:
    @classmethod
    def patch(cls, drawio_path, operations, output_path=None):
        """
        Applies a sequence of atomic operations to an existing .drawio file.
        Operations:
        - add_node: {'op': 'add_node', 'id': '...', 'label': '...', 'shape': '...', 'role': '...', 'connect_from': '...', 'connect_to': '...'}
        - delete_node: {'op': 'delete_node', 'id': '...', 'reconnect': bool}
        - update_node: {'op': 'update_node', 'id': '...', 'label': '...', 'shape': '...', 'role': '...', 'color': '...'}
        - add_edge: {'op': 'add_edge', 'source': '...', 'target': '...', 'label': '...', 'style': '...'}
        - delete_edge: {'op': 'delete_edge', 'source': '...', 'target': '...'}
        - group_nodes: {'op': 'group_nodes', 'container_id': '...', 'title': '...', 'node_ids': [...]}
        - highlight_path: {'op': 'highlight_path', 'nodes': [...], 'color': '#FF0055'}
        """
        output_path = output_path or drawio_path
        parser = DrawIOParser(drawio_path)
        parsed = parser.parse()

        if not parsed["pages"]:
            raise ValueError(f"No pages found in diagram file: {drawio_path}")

        page = parsed["pages"][0]
        page_name = page.get("name", "Page-1")
        nodes_dict = {n["id"]: dict(n) for n in page["nodes"]}
        edges_list = [dict(e) for e in page["edges"]]

        applied_ops = []

        for op_info in operations:
            op = op_info.get("op")

            if op == "add_node":
                nid = str(op_info["id"])
                label = op_info.get("label", nid)
                shape = op_info.get("shape", "rounded_rect")
                role = op_info.get("role", "primary")
                style = op_info.get("style") or get_node_style(shape=shape, role=role)

                # Default initial placement near center or target
                x = float(op_info.get("x", 200.0))
                y = float(op_info.get("y", 200.0))
                w = float(op_info.get("width", 150.0))
                h = float(op_info.get("height", 65.0))

                nodes_dict[nid] = {
                    "id": nid, "value": label, "x": x, "y": y,
                    "width": w, "height": h, "style": style
                }

                # Auto-connect if requested
                if op_info.get("connect_from") and str(op_info["connect_from"]) in nodes_dict:
                    src = str(op_info["connect_from"])
                    edges_list.append({
                        "id": f"e_{src}_{nid}", "source": src, "target": nid,
                        "value": op_info.get("edge_label", ""),
                        "style": get_edge_style()
                    })
                if op_info.get("connect_to") and str(op_info["connect_to"]) in nodes_dict:
                    tgt = str(op_info["connect_to"])
                    edges_list.append({
                        "id": f"e_{nid}_{tgt}", "source": nid, "target": tgt,
                        "value": op_info.get("edge_label", ""),
                        "style": get_edge_style()
                    })
                applied_ops.append(f"Added node '{nid}'")

            elif op == "delete_node":
                nid = str(op_info["id"])
                reconnect = op_info.get("reconnect", False)

                if nid in nodes_dict:
                    in_edges = [e for e in edges_list if e.get("target") == nid]
                    out_edges = [e for e in edges_list if e.get("source") == nid]

                    # Reconnect incoming sources to outgoing targets if requested
                    if reconnect:
                        for ie in in_edges:
                            for oe in out_edges:
                                edges_list.append({
                                    "id": f"e_{ie['source']}_{oe['target']}_heal",
                                    "source": ie["source"],
                                    "target": oe["target"],
                                    "value": ie.get("value", ""),
                                    "style": ie.get("style", get_edge_style())
                                })

                    # Remove all connected edges
                    edges_list = [e for e in edges_list if e.get("source") != nid and e.get("target") != nid]
                    del nodes_dict[nid]
                    applied_ops.append(f"Deleted node '{nid}' (reconnect={reconnect})")

            elif op == "update_node":
                nid = str(op_info["id"])
                if nid in nodes_dict:
                    curr = nodes_dict[nid]
                    if "label" in op_info:
                        curr["value"] = op_info["label"]
                    if "color" in op_info:
                        col = op_info["color"]
                        # Patch fillColor in style
                        curr["style"] = curr["style"] + f"fillColor={col};"
                    if "shape" in op_info or "role" in op_info:
                        curr["style"] = get_node_style(
                            shape=op_info.get("shape", "rounded_rect"),
                            role=op_info.get("role", "primary")
                        )
                    if "width" in op_info:
                        curr["width"] = float(op_info["width"])
                    if "height" in op_info:
                        curr["height"] = float(op_info["height"])
                    applied_ops.append(f"Updated node '{nid}'")

            elif op == "add_edge":
                src = str(op_info["source"])
                tgt = str(op_info["target"])
                eid = str(op_info.get("id", f"e_{src}_{tgt}_{len(edges_list)+1}"))
                style = op_info.get("style") or get_edge_style()
                edges_list.append({
                    "id": eid, "source": src, "target": tgt,
                    "value": op_info.get("label", ""), "style": style
                })
                applied_ops.append(f"Added edge '{src}' -> '{tgt}'")

            elif op == "delete_edge":
                src = op_info.get("source")
                tgt = op_info.get("target")
                eid = op_info.get("id")

                if eid:
                    edges_list = [e for e in edges_list if e.get("id") != str(eid)]
                    applied_ops.append(f"Deleted edge ID '{eid}'")
                elif src and tgt:
                    edges_list = [e for e in edges_list if not (e.get("source") == str(src) and e.get("target") == str(tgt))]
                    applied_ops.append(f"Deleted edge '{src}' -> '{tgt}'")

            elif op == "group_nodes":
                cid = str(op_info["container_id"])
                title = op_info.get("title", cid)
                nids = [str(n) for n in op_info.get("node_ids", []) if str(n) in nodes_dict]

                if nids:
                    child_coords = [nodes_dict[nid] for nid in nids]
                    bounds = ContainerBoundaryCalculator.compute_bounds(child_coords)
                    if bounds:
                        c_style = get_container_style()
                        nodes_dict[cid] = {
                            "id": cid, "value": title,
                            "x": bounds["x"], "y": bounds["y"],
                            "width": bounds["width"], "height": bounds["height"],
                            "style": c_style, "is_container": True
                        }
                        applied_ops.append(f"Grouped nodes {nids} into container '{cid}'")

            elif op == "highlight_path":
                path_nodes = [str(n) for n in op_info.get("nodes", [])]
                color = op_info.get("color", "#FF0055")
                stroke_w = str(op_info.get("strokeWidth", 2.5))

                # Highlight edges along path
                for i in range(len(path_nodes) - 1):
                    u = path_nodes[i]
                    v = path_nodes[i + 1]
                    for e in edges_list:
                        if e.get("source") == u and e.get("target") == v:
                            e["style"] = e.get("style", "") + f"strokeColor={color};strokeWidth={stroke_w};"

                # Highlight nodes along path
                for nid in path_nodes:
                    if nid in nodes_dict:
                        nodes_dict[nid]["style"] = nodes_dict[nid]["style"] + f"strokeColor={color};strokeWidth={stroke_w};"

                applied_ops.append(f"Highlighted execution path {path_nodes} with {color}")

        # Re-build and save patched diagram
        builder = DrawIOBuilder(page_name=page_name)

        # Containers first
        for nid, n in nodes_dict.items():
            if n.get("is_container") or "swimlane" in n.get("style", ""):
                builder.add_node(
                    node_id=nid, value=n["value"],
                    x=n["x"], y=n["y"], width=n["width"], height=n["height"],
                    style=n["style"]
                )

        # Child nodes second
        for nid, n in nodes_dict.items():
            if not (n.get("is_container") or "swimlane" in n.get("style", "")):
                builder.add_node(
                    node_id=nid, value=n["value"],
                    x=n["x"], y=n["y"], width=n["width"], height=n["height"],
                    style=n["style"]
                )

        # Edges third
        for e in edges_list:
            if e.get("source") in nodes_dict and e.get("target") in nodes_dict:
                builder.add_edge(
                    edge_id=e["id"], source=e["source"], target=e["target"],
                    label=e.get("value", ""), style=e.get("style", get_edge_style())
                )

        builder.save(output_path)
        return {
            "status": "success",
            "path": output_path,
            "applied_operations": applied_ops,
            "node_count": len(nodes_dict),
            "edge_count": len(edges_list)
        }

    @classmethod
    def beautify(cls, drawio_path, output_path=None, theme="modern_slate", layout_direction="TB"):
        """
        Reads any existing .drawio file, runs topological auto-layout,
        applies a cohesive color theme, untangles crisscrossing lines, and formats cleanly.
        """
        output_path = output_path or drawio_path
        parser = DrawIOParser(drawio_path)
        parsed = parser.parse()

        if not parsed["pages"]:
            raise ValueError(f"No pages in diagram: {drawio_path}")

        page = parsed["pages"][0]
        page_name = page.get("name", "Page-1")
        raw_nodes = page["nodes"]
        raw_edges = page["edges"]

        # Filter out container boxes from initial layout pass
        content_nodes = [n for n in raw_nodes if "swimlane" not in n.get("style", "")]
        container_nodes = [n for n in raw_nodes if "swimlane" in n.get("style", "")]

        # Run auto-layout
        engine = HierarchicalLayout(direction=layout_direction)
        coords = engine.layout(content_nodes, raw_edges)

        builder = DrawIOBuilder(page_name=page_name)

        # Update and add containers
        for c in container_nodes:
            # Recompute bounds around any enclosed children
            child_coords = [
                coords[n["id"]] for n in content_nodes
                if n["id"] in coords and (
                    c["x"] <= n["x"] <= c["x"] + c["width"] and
                    c["y"] <= n["y"] <= c["y"] + c["height"]
                )
            ]
            bounds = ContainerBoundaryCalculator.compute_bounds(child_coords) or c
            c_style = get_container_style(theme_name=theme)
            builder.add_node(
                node_id=c["id"], value=c["value"],
                x=bounds["x"], y=bounds["y"], width=bounds["width"], height=bounds["height"],
                style=c_style
            )

        # Add restyled content nodes
        for idx, n in enumerate(content_nodes):
            nid = n["id"]
            pos = coords.get(nid, n)
            shape = "cylinder" if "cylinder" in n.get("style", "") else ("rhombus" if "rhombus" in n.get("style", "") else "rounded_rect")
            role = "primary" if idx == 0 else ("secondary" if idx % 2 == 1 else "accent")
            new_style = get_node_style(shape=shape, role=role, theme_name=theme)

            builder.add_node(
                node_id=nid, value=n["value"],
                x=pos["x"], y=pos["y"], width=pos["width"], height=pos["height"],
                style=new_style
            )

        # Add restyled edges
        for idx, e in enumerate(raw_edges):
            e_style = get_edge_style(style_type="orthogonal", theme_name=theme)
            builder.add_edge(
                edge_id=e["id"], source=e["source"], target=e["target"],
                label=e.get("value", ""), style=e_style
            )

        builder.save(output_path)
        return {
            "status": "success",
            "path": output_path,
            "theme_applied": theme,
            "layout_direction": layout_direction,
            "node_count": len(raw_nodes),
            "edge_count": len(raw_edges)
        }
