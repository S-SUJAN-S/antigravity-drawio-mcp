import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src")))

from antigravity_drawio_mcp.mermaid_converter import MermaidToDrawIO
from antigravity_drawio_mcp.parser import DrawIOParser

def test_complex_mermaid():
    code = """
    graph TD
    %% Comment line
    subgraph sub_1 [Backend Microservices]
        node-a{Auth Gateway} -->|Validate JWT| node-b(User Service)
        node-b -->|Query User DB| node-c[Postgres DB]
    end

    subgraph sub_2 [Cache Cluster]
        node-d[Redis Master] <--> node-e[Redis Replica]
    end

    node-a --> node-d
    node-c --> node-a
    """
    xml_output = MermaidToDrawIO.convert(code)
    print("Generated XML Length:", len(xml_output))
    assert "<mxfile" in xml_output
    assert 'value="Auth Gateway"' in xml_output
    assert 'style="rhombus;' in xml_output
    assert 'style="rounded=1;' in xml_output
    assert 'style="rounded=0;' in xml_output
    assert 'swimlane;' in xml_output
    
    # Save to temp file and parse using DrawIOParser
    tmp_path = os.path.join(os.path.dirname(__file__), "tmp_complex.drawio")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(xml_output)
    
    parser = DrawIOParser(tmp_path)
    parsed = parser.parse()
    print("Parsed pages:", len(parsed["pages"]))
    print("Parsed nodes:", len(parsed["pages"][0]["nodes"]))
    print("Parsed edges:", len(parsed["pages"][0]["edges"]))
    
    if os.path.exists(tmp_path):
        os.remove(tmp_path)
    
    print("Complex Mermaid Edge Case Test PASSED!")

if __name__ == "__main__":
    test_complex_mermaid()
