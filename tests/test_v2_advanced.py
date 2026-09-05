import unittest
import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from antigravity_drawio_mcp.layout_engine import HierarchicalLayout, GridLayout, ContainerBoundaryCalculator
from antigravity_drawio_mcp.themes import get_theme, get_node_style, get_edge_style, get_container_style, THEMES
from antigravity_drawio_mcp.templates import generate_smart_diagram, generate_c4_diagram, generate_er_diagram, generate_sequence_diagram
from antigravity_drawio_mcp.editor import DiagramEditor
from antigravity_drawio_mcp.analyzer import DiagramAnalyzer
from antigravity_drawio_mcp.server import (
    generate_smart_diagram as mcp_smart,
    generate_c4_diagram as mcp_c4,
    generate_er_diagram as mcp_er,
    generate_sequence_diagram as mcp_seq,
    patch_diagram as mcp_patch,
    beautify_diagram as mcp_beautify,
    analyze_diagram as mcp_analyze
)

class TestV2AdvancedMCP(unittest.TestCase):
    def setUp(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), "output_v2")
        os.makedirs(self.output_dir, exist_ok=True)

    def test_01_hierarchical_layout_engine(self):
        engine = HierarchicalLayout(direction="TB")
        nodes = [{"id": "a"}, {"id": "b"}, {"id": "c"}, {"id": "d"}]
        edges = [{"source": "a", "target": "b"}, {"source": "b", "target": "c"}, {"source": "c", "target": "d"}, {"source": "d", "target": "b"}] # contains cycle

        coords = engine.layout(nodes, edges)
        self.assertEqual(len(coords), 4)
        for nid in ["a", "b", "c", "d"]:
            self.assertIn("x", coords[nid])
            self.assertIn("y", coords[nid])
        # Root 'a' must be above 'b'
        self.assertLess(coords["a"]["y"], coords["b"]["y"])
        print("Test 01: Hierarchical Layout & Cycle Tolerance PASSED!")

    def test_02_grid_layout_and_bounds(self):
        grid = GridLayout(columns=2)
        nodes = [{"id": f"s{i}"} for i in range(4)]
        coords = grid.layout(nodes)
        self.assertEqual(len(coords), 4)
        self.assertEqual(coords["s0"]["x"], coords["s2"]["x"]) # same column

        bounds = ContainerBoundaryCalculator.compute_bounds([coords["s0"], coords["s1"]])
        self.assertIsNotNone(bounds)
        self.assertLess(bounds["x"], coords["s0"]["x"])
        print("Test 02: Grid Layout & Container Bounds PASSED!")

    def test_03_themes_and_styles(self):
        for name in THEMES:
            t = get_theme(name)
            self.assertIn("primary", t)
            style = get_node_style(shape="cylinder", role="primary", theme_name=name)
            self.assertIn("cylinder", style)
            edge_style = get_edge_style(style_type="curved", theme_name=name, dashed=True)
            self.assertIn("curved=1", edge_style)
            self.assertIn("dashed=1", edge_style)
        print("Test 03: Theme Palettes & Shape Styles PASSED!")

    def test_04_generate_smart_diagram(self):
        out = os.path.join(self.output_dir, "smart_test.drawio")
        nodes = [
            {"id": "user", "label": "Client User", "shape": "actor", "role": "warning"},
            {"id": "gw", "label": "API Gateway", "shape": "hexagon", "role": "secondary", "group": "cloud_vpc"},
            {"id": "svc", "label": "Order Service", "shape": "rounded_rect", "role": "primary", "group": "cloud_vpc"},
            {"id": "db", "label": "PostgreSQL DB", "shape": "cylinder", "role": "accent", "group": "cloud_vpc"}
        ]
        edges = [
            {"source": "user", "target": "gw", "label": "HTTPS"},
            {"source": "gw", "target": "svc", "label": "gRPC"},
            {"source": "svc", "target": "db", "label": "SQL"}
        ]
        containers = [{"id": "cloud_vpc", "title": "AWS Production VPC"}]

        path = generate_smart_diagram(out, nodes, edges, containers=containers, layout_direction="TB", theme="cloud_aws")
        self.assertTrue(os.path.exists(path))
        print("Test 04: Smart Diagram Generation PASSED!")

    def test_05_c4_diagram_generator(self):
        out = os.path.join(self.output_dir, "c4_test.drawio")
        spec = {
            "title": "FinTech Core Banking",
            "people": [{"id": "cust", "name": "Customer", "role": "Personal Banking"}],
            "systems": [{"id": "bank", "name": "Internet Banking System", "description": "Core customer portal", "external": False}],
            "containers": [{"id": "spa", "name": "Single Page App", "technology": "React"}],
            "relations": [{"source": "cust", "target": "spa", "description": "Views accounts", "technology": "HTTPS"}]
        }
        path = generate_c4_diagram(out, spec)
        self.assertTrue(os.path.exists(path))
        with open(path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Single Page App", content)
        self.assertIn("React", content)
        print("Test 05: C4 Architecture Diagram Generator PASSED!")

    def test_06_er_diagram_generator(self):
        out = os.path.join(self.output_dir, "er_test.drawio")
        spec = {
            "title": "Shop DB Schema",
            "entities": [
                {
                    "name": "users",
                    "fields": [
                        {"name": "id", "type": "INT", "is_pk": True},
                        {"name": "username", "type": "VARCHAR(50)"}
                    ]
                },
                {
                    "name": "orders",
                    "fields": [
                        {"name": "id", "type": "INT", "is_pk": True},
                        {"name": "user_id", "type": "INT", "is_fk": True}
                    ]
                }
            ],
            "relationships": [
                {"source": "users", "target": "orders", "cardinality": "1:N", "label": "places"}
            ]
        }
        path = generate_er_diagram(out, spec)
        self.assertTrue(os.path.exists(path))
        print("Test 06: Database ER Diagram Generator PASSED!")

    def test_07_sequence_diagram_generator(self):
        out = os.path.join(self.output_dir, "seq_test.drawio")
        spec = {
            "title": "Auth Sequence",
            "participants": [{"id": "client", "name": "Browser"}, {"id": "auth", "name": "Auth0"}],
            "messages": [
                {"source": "client", "target": "auth", "label": "POST /oauth/token"},
                {"source": "auth", "target": "client", "label": "200 JWT Token", "type": "return"}
            ]
        }
        path = generate_sequence_diagram(out, spec)
        self.assertTrue(os.path.exists(path))
        print("Test 07: Sequence Diagram Generator PASSED!")

    def test_08_diagram_editor_patching(self):
        base_path = os.path.join(self.output_dir, "smart_test.drawio")
        patched_path = os.path.join(self.output_dir, "smart_patched.drawio")

        ops = [
            {"op": "add_node", "id": "redis_cache", "label": "Redis Cache", "shape": "cylinder", "connect_from": "svc", "connect_to": "db"},
            {"op": "update_node", "id": "gw", "label": "API Gateway v2", "color": "#00F0FF"},
            {"op": "highlight_path", "nodes": ["user", "gw", "svc", "redis_cache"], "color": "#FF007F"},
            {"op": "delete_node", "id": "user", "reconnect": True}
        ]

        res = DiagramEditor.patch(base_path, ops, output_path=patched_path)
        self.assertEqual(res["status"], "success")
        self.assertTrue(os.path.exists(patched_path))
        with open(patched_path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Redis Cache", content)
        self.assertIn("API Gateway v2", content)
        print("Test 08: Surgical Diagram Patching PASSED!")

    def test_09_diagram_analyzer(self):
        path = os.path.join(self.output_dir, "smart_test.drawio")
        metrics = DiagramAnalyzer.analyze(path)
        self.assertEqual(metrics["node_count"], 5) # 1 container + 4 nodes
        self.assertFalse(metrics["has_cycles"])
        self.assertGreater(len(metrics["root_entry_points"]), 0)
        self.assertGreater(len(metrics["terminal_sinks"]), 0)
        print("Test 09: Diagram Topological Analyzer PASSED!")

    def test_10_mcp_server_v2_tool_wrappers(self):
        out_smart = os.path.join(self.output_dir, "mcp_smart.drawio")
        res1 = json.loads(mcp_smart(out_smart, [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}], [{"source": "a", "target": "b"}]))
        self.assertEqual(res1["status"], "success")

        res2 = json.loads(mcp_c4(os.path.join(self.output_dir, "mcp_c4.drawio"), {"title": "C4 Test"}))
        self.assertEqual(res2["status"], "success")

        res3 = json.loads(mcp_er(os.path.join(self.output_dir, "mcp_er.drawio"), {"title": "ER Test", "entities": [{"name": "t1"}]}))
        self.assertEqual(res3["status"], "success")

        res4 = json.loads(mcp_seq(os.path.join(self.output_dir, "mcp_seq.drawio"), {"title": "Seq Test", "participants": [{"id": "p1"}]}))
        self.assertEqual(res4["status"], "success")

        res5 = json.loads(mcp_patch(out_smart, [{"op": "add_node", "id": "c", "label": "C"}]))
        self.assertEqual(res5["status"], "success")

        res6 = json.loads(mcp_beautify(out_smart, theme="cyberpunk_dark"))
        self.assertEqual(res6["status"], "success")

        res7 = json.loads(mcp_analyze(out_smart))
        self.assertEqual(res7["status"], "success")

        print("Test 10: All New v2.0 Server Tool Wrappers PASSED!")

if __name__ == "__main__":
    unittest.main()
