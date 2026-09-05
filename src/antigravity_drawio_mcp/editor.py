"""
Surgical Diagram Patching and Beautification Engine for Antigravity Draw.io MCP v2.0.
Allows incremental modification (add/delete/update nodes, rewire edges, group into containers,
highlight execution paths) with intelligent geometric placement and automated restyling.
"""

from .parser import DrawIOParser
from .builder import DrawIOBuilder
from .layout_engine import HierarchicalLayout, ContainerBoundaryCalculator
from .themes import get_node_style, get_edge_style, get_container_style

class DiagramEditor:
    @classmethod
    def patch(cls, drawio_path, operations, output_path=None):
        """
        Applies a sequence of atomic operations to an existing .drawio file with
        intelligent coordinate placement and automatic container boundary expansion.
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

                w = float(op_info.get("width", 150.0))
                h = float(op_info.get("height", 65.0))

                # Intelligent relative placement
                conn_from = str(op_info["connect_from"]) if op_info.get("connect_from") else None
                conn_to = str(op_info["connect_to"]) if op_info.get("connect_to") else None

                if conn_from and conn_to and conn_from in nodes_dict and conn_to in nodes_dict:
                    src_n = nodes_dict[conn_from]
                    tgt_n = nodes_dict[conn_to]
                    # Place horizontally adjacent between the two
                    x = max(src_n["x"], tgt_n["x"]) + max(src_n["width"], tgt_n["width"]) + 60.0
                    y = (src_n["y"] + tgt_n["y"]) / 2.0
                elif conn_from and conn_from in nodes_dict:
                    src_n = nodes_dict[conn_from]
                    x = src_n["x"] + src_n["width"] + 60.0
                    y = src_n["y"]
                elif conn_to and conn_to in nodes_dict:
                    tgt_n = nodes_dict[conn_to]
                    x = tgt_n["x"]
                    y = max(80.0, tgt_n["y"] - h - 60.0)
                else:
                    x = float(op_info.get("x", 200.0))
                    y = float(op_info.get("y", 200.0))

                nodes_dict[nid] = {
                    "id": nid, "value": label, "x": round(x, 1), "y": round(y, 1),
                    "width": w, "height": h, "style": style
                }

                # Auto-connect edges
                if conn_from and conn_from in nodes_dict:
                    edges_list.append({
                        "id": f"e_{conn_from}_{nid}", "source": conn_from, "target": nid,
                        "value": op_info.get("edge_label", ""),
                        "style": get_edge_style()
                    })
                if conn_to and conn_to in nodes_dict:
                    edges_list.append({
                        "id": f"e_{nid}_{conn_to}", "source": nid, "target": conn_to,
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
                    bounds = ContainerBoundaryCalculator.compute_bounds(child_coords, padding=40.0, header_height=32.0)
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

                for i in range(len(path_nodes) - 1):
                    u = path_nodes[i]
                    v = path_nodes[i + 1]
                    for e in edges_list:
                        if e.get("source") == u and e.get("target") == v:
                            e["style"] = e.get("style", "") + f"strokeColor={color};strokeWidth={stroke_w};"

                for nid in path_nodes:
                    if nid in nodes_dict:
                        nodes_dict[nid]["style"] = nodes_dict[nid]["style"] + f"strokeColor={color};strokeWidth={stroke_w};"

                applied_ops.append(f"Highlighted execution path {path_nodes} with {color}")

        # Automatically update any existing container bounding boxes
        containers = [n for n in nodes_dict.values() if n.get("is_container") or "swimlane" in n.get("style", "")]
        content_nodes = [n for n in nodes_dict.values() if not (n.get("is_container") or "swimlane" in n.get("style", ""))]

        for c in containers:
            # Find children whose centers are within or near container
            enclosed_children = [
                n for n in content_nodes
                if (c["x"] - 20 <= n["x"] <= c["x"] + c["width"] + 20) and
                   (c["y"] - 10 <= n["y"] <= c["y"] + c["height"] + 20)
            ]
            if enclosed_children:
                bounds = ContainerBoundaryCalculator.compute_bounds(enclosed_children, padding=40.0, header_height=32.0)
                if bounds:
                    c["x"] = bounds["x"]
                    c["y"] = bounds["y"]
                    c["width"] = bounds["width"]
                    c["height"] = bounds["height"]

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

        content_nodes = [n for n in raw_nodes if "swimlane" not in n.get("style", "")]
        container_nodes = [n for n in raw_nodes if "swimlane" in n.get("style", "")]

        engine = HierarchicalLayout(direction=layout_direction)
        coords = engine.layout(content_nodes, raw_edges)

        builder = DrawIOBuilder(page_name=page_name)

        # Update and add containers
        for c in container_nodes:
            child_coords = [
                coords[n["id"]] for n in content_nodes
                if n["id"] in coords and (
                    c["x"] - 50 <= n["x"] <= c["x"] + c["width"] + 50 and
                    c["y"] - 50 <= n["y"] <= c["y"] + c["height"] + 50
                )
            ]
            bounds = ContainerBoundaryCalculator.compute_bounds(child_coords, padding=40.0, header_height=32.0) or c
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
            shape = "cylinder" if "cylinder" in n.get("style", "") else ("rhombus" if "rhombus" in n.get("style", "") else ("shape=umlActor" if "umlActor" in n.get("style", "") else "rounded_rect"))
            role = "primary" if idx == 0 else ("secondary" if idx % 2 == 1 else "accent")
            new_style = get_node_style(shape=shape, role=role, theme_name=theme)

            builder.add_node(
                node_id=nid, value=n["value"],
                x=pos["x"], y=pos["y"], width=pos["width"], height=pos["height"],
                style=new_style
            )

        # Add restyled edges with protective badge labels
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
