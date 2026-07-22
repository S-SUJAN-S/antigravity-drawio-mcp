import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import datetime

class DrawIOBuilder:
    def __init__(self, page_name="Page-1", width=1200, height=900):
        self.page_name = page_name
        self.width = width
        self.height = height
        self.nodes = []
        self.edges = []
        
    def add_node(self, node_id, value, x, y, width=140, height=60, style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#000000;strokeWidth=1.5;"):
        self.nodes.append({
            "id": str(node_id),
            "value": str(value),
            "x": str(x), "y": str(y),
            "width": str(width), "height": str(height),
            "style": str(style)
        })
        return str(node_id)
        
    def add_edge(self, edge_id, source, target, label="", style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=classic;strokeColor=#000000;strokeWidth=1.5;"):
        self.edges.append({
            "id": str(edge_id),
            "source": str(source),
            "target": str(target),
            "label": str(label),
            "style": str(style)
        })
        return str(edge_id)

    def to_xml(self):
        mxfile = ET.Element("mxfile", {
            "host": "Electron",
            "modified": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "agent": "Antigravity Draw.io MCP Builder",
            "version": "30.3.14",
            "type": "device"
        })
        
        diagram = ET.SubElement(mxfile, "diagram", {
            "id": "diagram_1",
            "name": self.page_name
        })
        
        graph_model = ET.SubElement(diagram, "mxGraphModel", {
            "dx": str(self.width), "dy": str(self.height), "grid": "1", "gridSize": "10",
            "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
            "fold": "1", "page": "1", "pageScale": "1", "pageWidth": str(self.width),
            "pageHeight": str(self.height), "math": "0", "shadow": "1"
        })
        
        root = ET.SubElement(graph_model, "root")
        ET.SubElement(root, "mxCell", {"id": "0"})
        ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})

        for n in self.nodes:
            cell = ET.SubElement(root, "mxCell", {
                "id": n["id"],
                "value": n["value"],
                "style": n["style"],
                "vertex": "1", "parent": "1"
            })
            ET.SubElement(cell, "mxGeometry", {
                "x": n["x"], "y": n["y"],
                "width": n["width"], "height": n["height"],
                "as": "geometry"
            })

        for e in self.edges:
            edge_cell = ET.SubElement(root, "mxCell", {
                "id": e["id"],
                "value": e["label"],
                "style": e["style"],
                "edge": "1", "parent": "1",
                "source": e["source"],
                "target": e["target"]
            })
            ET.SubElement(edge_cell, "mxGeometry", {"relative": "1", "as": "geometry"})

        return minidom.parseString(ET.tostring(mxfile)).toprettyxml(indent="  ")

    def save(self, filepath):
        xml_str = self.to_xml()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xml_str)
        return filepath
