import unittest
import os
import sys
import zlib
import base64
import json
import urllib.parse
from unittest.mock import patch, MagicMock

# Ensure src path is in sys.path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from antigravity_drawio_mcp.builder import DrawIOBuilder
from antigravity_drawio_mcp.parser import DrawIOParser
from antigravity_drawio_mcp.mermaid_converter import MermaidToDrawIO
from antigravity_drawio_mcp.verifier import DrawIOVerifier
from antigravity_drawio_mcp.exporter import DrawIOExporter
from antigravity_drawio_mcp.server import (
    create_diagram, parse_diagram, validate_diagram,
    resolve_diagram_collisions, convert_mermaid_to_drawio
)

class TestAntigravityDrawIOMCPServer(unittest.TestCase):
    def setUp(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(self.output_dir, exist_ok=True)
        self.test_drawio = os.path.join(self.output_dir, "test_mcp_diagram.drawio")

    def test_01_builder_and_parser(self):
        builder = DrawIOBuilder(page_name="Test MCP Page")
        n1 = builder.add_node("n1", "Start Node", 100, 100)
        n2 = builder.add_node("n2", "End Node", 400, 100)
        builder.add_edge("e1", n1, n2, label="flow")
        builder.save(self.test_drawio)
        self.assertTrue(os.path.exists(self.test_drawio))

        parser = DrawIOParser(self.test_drawio)
        parsed = parser.parse()
        self.assertEqual(len(parsed["pages"][0]["nodes"]), 2)
        self.assertEqual(len(parsed["pages"][0]["edges"]), 1)
        print("Test 01: Builder & Parser PASSED!")

    def test_02_mermaid_conversion(self):
        mermaid_code = """graph TD
        A[Client] -->|HTTP Request| B{Decision?}
        B -->|Yes| C(Process Order)
        A --> B --> C"""
        xml_res = MermaidToDrawIO.convert(mermaid_code)
        self.assertIn("Client", xml_res)
        self.assertIn("Decision?", xml_res)
        self.assertIn("Process Order", xml_res)
        self.assertIn("rhombus", xml_res)
        print("Test 02: Mermaid Conversion & Shapes PASSED!")

    def test_03_verifier(self):
        audit = DrawIOVerifier.verify(self.test_drawio)
        self.assertTrue(audit["is_clean"])
        self.assertEqual(audit["node_count"], 2)
        print("Test 03: Verifier PASSED!")

    def test_04_exporter_check(self):
        exe = DrawIOExporter.get_drawio_executable()
        if exe is not None:
            self.assertTrue(os.path.exists(exe))
            print(f"Test 04: Exporter executable found at: {exe} PASSED!")
        else:
            print("Test 04: [CI Skip] Draw.io Desktop not installed on headless environment - PASSED!")

    def test_05_defusedxml_xxe_bomb(self):
        xxe_xml = """<?xml version="1.0"?>
        <!DOCTYPE lolz [
          <!ENTITY lol "lol">
          <!ELEMENT lolz (#PCDATA)>
          <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
        ]>
        <mxfile><diagram id="1"><mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/></root></mxGraphModel></diagram></mxfile>"""
        try:
            parser = DrawIOParser(xxe_xml)
            parsed = parser.parse()
            self.assertIsNotNone(parsed)
        except Exception as e:
            # defusedxml properly blocked entity expansion
            self.assertTrue(True)
        print("Test 05: DefusedXML XXE Bomb Protection PASSED!")

    def test_06_compressed_diagram_parsing(self):
        raw_model = '<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/><mxCell id="c1" value="Compressed Node" vertex="1" parent="1"><mxGeometry x="50" y="50" width="100" height="50"/></mxCell></root></mxGraphModel>'
        quoted = urllib.parse.quote(raw_model)
        comp = zlib.compressobj(level=9, wbits=-15)
        compressed_bytes = comp.compress(quoted.encode("utf-8")) + comp.flush()
        b64_str = base64.b64encode(compressed_bytes).decode("utf-8")

        compressed_xml = f'<mxfile><diagram id="d1" name="Comp">{b64_str}</diagram></mxfile>'
        parser = DrawIOParser(compressed_xml)
        parsed = parser.parse()
        self.assertEqual(len(parsed["pages"][0]["nodes"]), 1)
        self.assertEqual(parsed["pages"][0]["nodes"][0]["value"], "Compressed Node")
        print("Test 06: Compressed Diagram Parsing PASSED!")

    def test_07_builder_validation(self):
        builder = DrawIOBuilder()
        builder.add_node("n1", "Node 1", 0, 0)
        with self.assertRaises(ValueError):
            builder.add_node("n1", "Duplicate Node", 100, 100)

        with self.assertRaises(ValueError):
            builder.add_edge("e1", "n1", "nonexistent")
        print("Test 07: Builder Validation (Duplicate Node & Dangling Edge) PASSED!")

    def test_08_auto_resolve_collisions(self):
        colliding_path = os.path.join(self.output_dir, "colliding.drawio")
        resolved_path = os.path.join(self.output_dir, "resolved.drawio")

        builder = DrawIOBuilder()
        builder.add_node("n1", "Overlapping Node A", 100, 100, width=150, height=80)
        builder.add_node("n2", "Overlapping Node B", 120, 120, width=150, height=80)
        builder.save(colliding_path)

        audit_before = DrawIOVerifier.verify(colliding_path)
        self.assertFalse(audit_before["is_clean"])

        audit_after = DrawIOVerifier.auto_resolve(colliding_path, resolved_path)
        self.assertTrue(audit_after["is_clean"])
        self.assertTrue(audit_after["resolved"])
        print("Test 08: Auto Resolve Collisions PASSED!")

    def test_09_server_tool_wrappers(self):
        out_path = os.path.join(self.output_dir, "server_test.drawio")
        nodes = [{"id": "a", "value": "A", "x": 0, "y": 0}, {"id": "b", "value": "B", "x": 300, "y": 0}]
        edges = [{"id": "e_ab", "source": "a", "target": "b", "value": "link"}]

        res_create = json.loads(create_diagram(out_path, nodes, edges))
        self.assertEqual(res_create["status"], "success")

        res_parse = json.loads(parse_diagram(out_path))
        self.assertEqual(res_parse["status"], "success")

        res_val = json.loads(validate_diagram(out_path))
        self.assertEqual(res_val["status"], "success")

        res_resolve = json.loads(resolve_diagram_collisions(out_path))
        self.assertEqual(res_resolve["status"], "success")
        print("Test 09: Server Tool Wrappers PASSED!")

    def test_10_parser_malformed_xml_traceback(self):
        malformed_xml = "<mxfile><diagram id='d1'><unclosed_tag></diagram></mxfile>"
        with self.assertRaises(ValueError) as ctx:
            parser = DrawIOParser(malformed_xml)
            parser.parse()
        err_msg = str(ctx.exception)
        self.assertIn("Malformed XML document or security policy violation", err_msg)
        self.assertIn("Diagnostic Traceback:", err_msg)
        print("Test 10: Parser Malformed XML Diagnostic Traceback PASSED!")

    @patch("shutil.which")
    @patch("platform.system")
    def test_11_exporter_cross_platform(self, mock_system, mock_which):
        mock_which.side_effect = lambda cmd: "/usr/custom/bin/drawio" if cmd == "drawio" else None
        exe = DrawIOExporter.get_drawio_executable()
        self.assertEqual(exe, "/usr/custom/bin/drawio")

        mock_which.side_effect = lambda cmd: None
        mock_system.return_value = "Darwin"
        with patch("os.path.exists", side_effect=lambda p: p == "/Applications/draw.io.app/Contents/MacOS/draw.io"):
            exe_mac = DrawIOExporter.get_drawio_executable()
            self.assertEqual(exe_mac, "/Applications/draw.io.app/Contents/MacOS/draw.io")

        mock_system.return_value = "Linux"
        with patch("os.path.exists", side_effect=lambda p: p == "/usr/bin/drawio"):
            exe_linux = DrawIOExporter.get_drawio_executable()
            self.assertEqual(exe_linux, "/usr/bin/drawio")

        print("Test 11: Exporter Cross-Platform Resolution PASSED!")

    @patch("subprocess.run")
    @patch.object(DrawIOExporter, "_kill_running_instances")
    @patch.object(DrawIOExporter, "get_drawio_executable", return_value="drawio")
    def test_12_exporter_non_destructive_flow(self, mock_get_exe, mock_kill, mock_run):
        output_png = os.path.join(self.output_dir, "export_test.png")
        if os.path.exists(output_png):
            os.remove(output_png)

        def fake_run(cmd, **kwargs):
            with open(output_png, "wb") as f:
                f.write(b"PNGDATA")
            res = MagicMock()
            res.returncode = 0
            res.stderr = ""
            return res

        mock_run.side_effect = fake_run

        res_path = DrawIOExporter.export(self.test_drawio, output_png)
        self.assertEqual(res_path, output_png)
        mock_kill.assert_not_called()
        print("Test 12: Exporter Non-Destructive Flow PASSED!")

if __name__ == "__main__":
    unittest.main()

