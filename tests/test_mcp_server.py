import unittest
import os
import sys

# Ensure src path is in sys.path for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from antigravity_drawio_mcp.builder import DrawIOBuilder
from antigravity_drawio_mcp.parser import DrawIOParser
from antigravity_drawio_mcp.mermaid_converter import MermaidToDrawIO
from antigravity_drawio_mcp.verifier import DrawIOVerifier
from antigravity_drawio_mcp.exporter import DrawIOExporter

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
        A[Client] -->|HTTP Request| B[Load Balancer]
        B -->|Forward| C[API Gateway]"""
        xml_res = MermaidToDrawIO.convert(mermaid_code)
        self.assertIn("Client", xml_res)
        self.assertIn("Load Balancer", xml_res)
        print("Test 02: Mermaid Conversion PASSED!")

    def test_03_verifier(self):
        audit = DrawIOVerifier.verify(self.test_drawio)
        self.assertTrue(audit["is_clean"])
        self.assertEqual(audit["node_count"], 2)
        print("Test 03: Verifier PASSED!")

    def test_04_exporter_check(self):
        exe = DrawIOExporter.get_drawio_executable()
        self.assertIsNotNone(exe, "Draw.io Desktop executable should be found on system")
        print(f"Test 04: Exporter executable found at: {exe} PASSED!")

if __name__ == "__main__":
    unittest.main()
