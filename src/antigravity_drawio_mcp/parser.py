import xml.etree.ElementTree as ET
import zlib
import base64
import urllib.parse

class DrawIOParser:
    def __init__(self, filepath_or_xml):
        self.filepath_or_xml = filepath_or_xml

    def _load_xml(self):
        if self.filepath_or_xml.strip().startswith("<"):
            return self.filepath_or_xml
        with open(self.filepath_or_xml, "r", encoding="utf-8") as f:
            return f.read()

    def _decode_diagram_text(self, text):
        try:
            compressed = base64.b64decode(text)
            decompressed = zlib.decompress(compressed, -15)
            return urllib.parse.unquote(decompressed.decode("utf-8"))
        except Exception:
            return text

    def parse(self):
        xml_content = self._load_xml()
        root = ET.fromstring(xml_content)
        pages = []

        diagram_elements = root.findall("diagram")
        if not diagram_elements and root.tag == "diagram":
            diagram_elements = [root]

        for diagram in diagram_elements:
            page_id = diagram.get("id", "page_1")
            page_name = diagram.get("name", "Page-1")
            
            # Check if compressed text
            raw_text = diagram.text or ""
            if raw_text.strip():
                decoded_xml = self._decode_diagram_text(raw_text.strip())
                page_root = ET.fromstring(decoded_xml)
            else:
                mx_model = diagram.find("mxGraphModel")
                page_root = mx_model if mx_model is not None else diagram

            nodes = []
            edges = []

            for cell in page_root.iter("mxCell"):
                cell_id = cell.get("id")
                if cell_id in [None, "0", "1"]:
                    continue

                value = cell.get("value", "")
                style = cell.get("style", "")
                is_vertex = cell.get("vertex") == "1"
                is_edge = cell.get("edge") == "1"
                source = cell.get("source")
                target = cell.get("target")

                geom = cell.find("mxGeometry")
                x = float(geom.get("x", 0)) if geom is not None and geom.get("x") else 0.0
                y = float(geom.get("y", 0)) if geom is not None and geom.get("y") else 0.0
                w = float(geom.get("width", 0)) if geom is not None and geom.get("width") else 0.0
                h = float(geom.get("height", 0)) if geom is not None and geom.get("height") else 0.0

                if is_vertex:
                    nodes.append({
                        "id": cell_id, "value": value, "style": style,
                        "x": x, "y": y, "width": w, "height": h
                    })
                elif is_edge or (source and target):
                    edges.append({
                        "id": cell_id, "value": value, "style": style,
                        "source": source, "target": target
                    })

            pages.append({
                "id": page_id, "name": page_name,
                "nodes": nodes, "edges": edges
            })

        return {"pages": pages}
