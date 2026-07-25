import os
import defusedxml.ElementTree as ET
import xml.dom.minidom as minidom
from .parser import DrawIOParser
from .builder import DrawIOBuilder

class DrawIOVerifier:
    @staticmethod
    def verify(drawio_filepath):
        parser = DrawIOParser(drawio_filepath)
        parsed = parser.parse()
        
        issues = []
        if not parsed["pages"]:
            return {
                "node_count": 0,
                "edge_count": 0,
                "is_clean": True,
                "issues": []
            }

        page = parsed["pages"][0]
        nodes = page["nodes"]

        # Helper to check if node A strictly contains node B (parent container relationship)
        def is_container_of(nA, nB):
            return (nA["x"] <= nB["x"] and
                    nA["y"] <= nB["y"] and
                    nA["x"] + nA["width"] >= nB["x"] + nB["width"] and
                    nA["y"] + nA["height"] >= nB["y"] + nB["height"] and
                    (nA["width"] > nB["width"] or nA["height"] > nB["height"]))

        # Check for node collisions (excluding container box wrappers)
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                n1 = nodes[i]
                n2 = nodes[j]

                # Ignore container box wrappers
                if is_container_of(n1, n2) or is_container_of(n2, n1):
                    continue

                # Bounding box collision check
                if not (n1["x"] + n1["width"] <= n2["x"] or
                        n2["x"] + n2["width"] <= n1["x"] or
                        n1["y"] + n1["height"] <= n2["y"] or
                        n2["y"] + n2["height"] <= n1["y"]):
                    issues.append(f"Node Collision detected between '{n1['id']}' and '{n2['id']}'")

        # Check for small shape boundary text overflow
        for n in nodes:
            text_len = len(n["value"].replace("<br/>", "").replace("<br>", "").replace("<b>", "").replace("</b>", ""))
            if text_len > 25 and n["width"] < 90:
                issues.append(f"Potential Text Overflow: Node '{n['id']}' width={n['width']}px may be too small for text '{n['value']}'")

        return {
            "node_count": len(nodes),
            "edge_count": len(page["edges"]),
            "is_clean": len(issues) == 0,
            "issues": issues
        }

    @classmethod
    def auto_resolve(cls, drawio_filepath, output_path=None):
        if output_path is None:
            output_path = drawio_filepath

        parser = DrawIOParser(drawio_filepath)
        parsed = parser.parse()
        if not parsed["pages"]:
            return {
                "node_count": 0,
                "edge_count": 0,
                "resolved": True,
                "passes": 0,
                "is_clean": True,
                "issues": []
            }

        page = parsed["pages"][0]
        nodes = page["nodes"]
        edges = page["edges"]

        def is_container_of(nA, nB):
            return (nA["x"] <= nB["x"] and
                    nA["y"] <= nB["y"] and
                    nA["x"] + nA["width"] >= nB["x"] + nB["width"] and
                    nA["y"] + nA["height"] >= nB["y"] + nB["height"] and
                    (nA["width"] > nB["width"] or nA["height"] > nB["height"]))

        passes = 0
        max_passes = 10
        resolved = False

        while passes < max_passes:
            passes += 1
            collided = False

            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    n1 = nodes[i]
                    n2 = nodes[j]

                    if is_container_of(n1, n2) or is_container_of(n2, n1):
                        continue

                    # Collision test
                    if not (n1["x"] + n1["width"] <= n2["x"] or
                            n2["x"] + n2["width"] <= n1["x"] or
                            n1["y"] + n1["height"] <= n2["y"] or
                            n2["y"] + n2["height"] <= n1["y"]):
                        collided = True
                        # Shift n2 down below n1
                        n2["y"] = n1["y"] + n1["height"] + 30.0

            if not collided:
                resolved = True
                break

        # Re-build diagram with resolved coordinates
        builder = DrawIOBuilder(page_name=page.get("name", "Page-1"))
        for n in nodes:
            builder.add_node(
                node_id=n["id"],
                value=n["value"],
                x=n["x"],
                y=n["y"],
                width=n["width"],
                height=n["height"],
                style=n["style"]
            )
        for e in edges:
            builder.add_edge(
                edge_id=e["id"],
                source=e["source"],
                target=e["target"],
                label=e["value"],
                style=e["style"]
            )

        builder.save(output_path)
        final_audit = cls.verify(output_path)
        final_audit["resolved"] = resolved
        final_audit["passes"] = passes
        return final_audit
