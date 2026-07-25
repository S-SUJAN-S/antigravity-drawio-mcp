import sys
import os
import unittest

sys.path.insert(0, os.path.abspath("src"))

from antigravity_drawio_mcp.mermaid_converter import MermaidToDrawIO
from antigravity_drawio_mcp.parser import DrawIOParser
from antigravity_drawio_mcp.verifier import DrawIOVerifier

class TestForensicEdgeCases(unittest.TestCase):
    def test_deeply_nested_subgraphs(self):
        mermaid = """graph TD
        subgraph level1 [Level 1]
            subgraph level2 [Level 2]
                subgraph level3 [Level 3]
                    A[Root Node] --> B[Leaf Node]
                end
            end
        end"""
        xml_res = MermaidToDrawIO.convert(mermaid)
        out_path = os.path.abspath(".agents/auditor_m2_remediation/deep_nested.drawio")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(xml_res)
        
        audit = DrawIOVerifier.verify(out_path)
        self.assertTrue(audit["is_clean"])
        self.assertEqual(audit["node_count"], 5)
        
        parser = DrawIOParser(out_path)
        parsed = parser.parse()
        nodes = {n["id"]: n for n in parsed["pages"][0]["nodes"]}
        
        l1, l2, l3 = nodes["level1"], nodes["level2"], nodes["level3"]
        self.assertLess(l1["x"], l2["x"])
        self.assertLess(l2["x"], l3["x"])
        self.assertGreater(l1["width"], l2["width"])
        self.assertGreater(l2["width"], l3["width"])
        print("Deeply nested subgraphs check: PASS")

    def test_complex_cycle(self):
        mermaid = """graph LR
        A --> B --> C --> D --> B
        D --> E"""
        xml_res = MermaidToDrawIO.convert(mermaid)
        out_path = os.path.abspath(".agents/auditor_m2_remediation/cycle.drawio")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(xml_res)
        
        audit = DrawIOVerifier.verify(out_path)
        self.assertTrue(audit["is_clean"])
        print("Complex cycle check: PASS")

if __name__ == "__main__":
    unittest.main()
