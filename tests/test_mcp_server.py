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
        with self.assertRaises(Exception):
            parser = DrawIOParser(xxe_xml)
            parser.parse()
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
        with self.assertRaises(ValueError) as ctx1:
            builder.add_node("n1", "Duplicate Node", 100, 100)
        self.assertIn("Duplicate node_id 'n1'", str(ctx1.exception))

        with self.assertRaises(ValueError) as ctx2:
            builder.add_edge("e1", "n1", "nonexistent_target")
        self.assertIn("Dangling edge target 'nonexistent_target'", str(ctx2.exception))

        with self.assertRaises(ValueError) as ctx3:
            builder.add_edge("e2", "nonexistent_source", "n1")
        self.assertIn("Dangling edge source 'nonexistent_source'", str(ctx3.exception))

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

    def test_18_m3_create_diagram_error_responses(self):
        err_path = os.path.join(self.output_dir, "m3_error_test.drawio")
        # 1. Duplicate node ID error
        dup_nodes = [{"id": "n1", "value": "N1"}, {"id": "n1", "value": "Duplicate N1"}]
        res1 = json.loads(create_diagram(err_path, dup_nodes, []))
        self.assertEqual(res1["status"], "error")
        self.assertIn("Duplicate node_id 'n1'", res1["message"])

        # 2. Dangling edge missing source error
        dangling_src_edges = [{"id": "e1", "source": "missing_src", "target": "n1"}]
        res2 = json.loads(create_diagram(err_path, [{"id": "n1", "value": "N1"}], dangling_src_edges))
        self.assertEqual(res2["status"], "error")
        self.assertIn("Dangling edge source 'missing_src'", res2["message"])

        # 3. Dangling edge missing target error
        dangling_tgt_edges = [{"id": "e2", "source": "n1", "target": "missing_tgt"}]
        res3 = json.loads(create_diagram(err_path, [{"id": "n1", "value": "N1"}], dangling_tgt_edges))
        self.assertEqual(res3["status"], "error")
        self.assertIn("Dangling edge target 'missing_tgt'", res3["message"])

        print("Test 18: M3 Create Diagram Error Responses PASSED!")

    def test_19_m3_multi_node_auto_resolve(self):
        multi_colliding = os.path.join(self.output_dir, "multi_colliding.drawio")
        multi_resolved = os.path.join(self.output_dir, "multi_resolved.drawio")

        builder = DrawIOBuilder()
        builder.add_node("n1", "Node 1", 100, 100, width=140, height=60)
        builder.add_node("n2", "Node 2", 110, 110, width=140, height=60)
        builder.add_node("n3", "Node 3", 120, 120, width=140, height=60)
        builder.add_edge("e1", "n1", "n2")
        builder.add_edge("e2", "n2", "n3")
        builder.save(multi_colliding)

        audit_before = DrawIOVerifier.verify(multi_colliding)
        self.assertFalse(audit_before["is_clean"])
        self.assertGreater(len(audit_before["issues"]), 0)

        res = json.loads(resolve_diagram_collisions(multi_colliding, output_path=multi_resolved))
        self.assertEqual(res["status"], "success")
        audit_after = res["audit"]
        self.assertTrue(audit_after["is_clean"])
        self.assertTrue(audit_after["resolved"])
        self.assertEqual(len(audit_after["issues"]), 0)
        print("Test 19: M3 Multi-Node Auto Resolve PASSED!")

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

    def test_13_mermaid_shapes_exact_style(self):
        mermaid_code = """graph TD
        r1{Decision Node}
        rn1(Rounded Node)
        rec1[Rectangle Node]"""
        xml_res = MermaidToDrawIO.convert(mermaid_code)
        self.assertIn('style="rhombus;whiteSpace=wrap;html=1;', xml_res)
        self.assertIn('style="rounded=1;whiteSpace=wrap;html=1;arcSize=30;', xml_res)
        self.assertIn('style="rounded=0;whiteSpace=wrap;html=1;', xml_res)
        print("Test 13: Mermaid Shapes Exact Style PASSED!")

    def test_14_mermaid_multi_hop_chain(self):
        mermaid_code = """graph LR
        A -- HTTP Request --> B --> C
        D -->|Pipe Label| E --> F"""
        xml_res = MermaidToDrawIO.convert(mermaid_code)
        self.assertIn('source="A" target="B"', xml_res)
        self.assertIn('source="B" target="C"', xml_res)
        self.assertIn('value="HTTP Request"', xml_res)
        self.assertIn('source="D" target="E"', xml_res)
        self.assertIn('source="E" target="F"', xml_res)
        self.assertIn('value="Pipe Label"', xml_res)
        print("Test 14: Mermaid Multi-Hop Chain PASSED!")

    def test_15_mermaid_subgraph_containers(self):
        mermaid_code = """graph TD
        subgraph sub1 [Frontend Services]
            A[React UI] --> B[API Gateway]
        end"""
        xml_res = MermaidToDrawIO.convert(mermaid_code)
        self.assertIn('value="Frontend Services"', xml_res)
        self.assertIn('swimlane;', xml_res)
        
        # Save and verify container with DrawIOParser & DrawIOVerifier
        subgraph_path = os.path.join(self.output_dir, "test_subgraph.drawio")
        with open(subgraph_path, "w", encoding="utf-8") as f:
            f.write(xml_res)
        
        audit = DrawIOVerifier.verify(subgraph_path)
        self.assertTrue(audit["is_clean"])
        self.assertEqual(audit["node_count"], 3)  # 1 swimlane + 2 child nodes
        print("Test 15: Mermaid Subgraph Containers & Verifier PASSED!")

    def test_16_mermaid_topological_depth_layout(self):
        mermaid_code = """graph LR
        A --> B --> C
        C --> A"""
        xml_res = MermaidToDrawIO.convert(mermaid_code)
        # Verify node coordinate calculation: x = 80 + depth * 250
        parser_path = os.path.join(self.output_dir, "test_topo.drawio")
        with open(parser_path, "w", encoding="utf-8") as f:
            f.write(xml_res)
        
        parser = DrawIOParser(parser_path)
        parsed = parser.parse()
        nodes_by_id = {n["id"]: n for n in parsed["pages"][0]["nodes"]}
        
        self.assertEqual(nodes_by_id["A"]["x"], 80.0)
        self.assertEqual(nodes_by_id["B"]["x"], 330.0)
        self.assertEqual(nodes_by_id["C"]["x"], 580.0)
        print("Test 16: Mermaid Topological Depth Layout & Cycle Tolerance PASSED!")

    def test_17_mermaid_nested_subgraphs(self):
        mermaid_code = """graph TD
        subgraph outer [Outer Container]
            subgraph inner [Inner Container]
                A[Node A] --> B[Node B]
            end
        end"""
        xml_res = MermaidToDrawIO.convert(mermaid_code)
        self.assertIn('value="Outer Container"', xml_res)
        self.assertIn('value="Inner Container"', xml_res)

        nested_path = os.path.join(self.output_dir, "test_nested_subgraphs.drawio")
        with open(nested_path, "w", encoding="utf-8") as f:
            f.write(xml_res)

        audit = DrawIOVerifier.verify(nested_path)
        self.assertTrue(audit["is_clean"])
        self.assertEqual(audit["node_count"], 4)  # 2 swimlane containers + 2 child nodes

        parser = DrawIOParser(nested_path)
        parsed = parser.parse()
        nodes_by_id = {n["id"]: n for n in parsed["pages"][0]["nodes"]}

        outer_node = nodes_by_id["outer"]
        inner_node = nodes_by_id["inner"]

        # Verify outer bounding box strictly encloses inner bounding box
        self.assertLess(outer_node["x"], inner_node["x"])
        self.assertLess(outer_node["y"], inner_node["y"])
        self.assertGreater(outer_node["width"], inner_node["width"])
        self.assertGreater(outer_node["height"], inner_node["height"])

        # Check right and bottom bounds enclosure
        outer_right = outer_node["x"] + outer_node["width"]
        inner_right = inner_node["x"] + inner_node["width"]
        self.assertGreaterEqual(outer_right, inner_right + 20)

        outer_bottom = outer_node["y"] + outer_node["height"]
        inner_bottom = inner_node["y"] + inner_node["height"]
        self.assertGreaterEqual(outer_bottom, inner_bottom + 10)

        print("Test 17: Mermaid Nested Subgraphs Bounding Box Enclosure PASSED!")

    def test_20_identical_coordinates_collision_resolution(self):
        identical_colliding = os.path.join(self.output_dir, "identical_colliding.drawio")
        identical_resolved = os.path.join(self.output_dir, "identical_resolved.drawio")

        builder = DrawIOBuilder()
        builder.add_node("n1", "Node A", 100, 100, width=140, height=60)
        builder.add_node("n2", "Node B", 100, 100, width=140, height=60)
        builder.save(identical_colliding)

        audit_before = DrawIOVerifier.verify(identical_colliding)
        self.assertFalse(audit_before["is_clean"])
        self.assertGreater(len(audit_before["issues"]), 0)
        self.assertTrue(any("Node Collision" in issue for issue in audit_before["issues"]))

        res = json.loads(resolve_diagram_collisions(identical_colliding, output_path=identical_resolved))
        self.assertEqual(res["status"], "success")
        audit_after = res["audit"]
        self.assertTrue(audit_after["is_clean"])
        self.assertTrue(audit_after["resolved"])
        self.assertEqual(len(audit_after["issues"]), 0)
        print("Test 20: Identical Coordinates Collision Resolution PASSED!")

if __name__ == "__main__":
    unittest.main()



