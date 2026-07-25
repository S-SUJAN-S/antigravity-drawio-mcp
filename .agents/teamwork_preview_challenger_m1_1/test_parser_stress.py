import sys
import os
import traceback
import zlib
import base64

# Add src directory to python path
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from antigravity_drawio_mcp.parser import DrawIOParser
import defusedxml.common

results = []

def record(test_name, success, details):
    status = "PASS" if success else "FAIL"
    results.append((test_name, status, details))
    print(f"[{status}] {test_name}: {details}")

print("=== STARTING PARSER SECURITY & EXCEPTION STRESS TEST SUITE ===")

# ==============================================================================
# SECTION 1: ENTITY EXPANSION (XXE / ENTITY BOMB) SECURITY TESTS
# ==============================================================================

# Test 1.1: Outer Document Billion Laughs Entity Bomb Payload
billion_laughs_xml = """<?xml version="1.0"?>
<!DOCTYPE lolz [
 <!ENTITY lol "lol">
 <!ELEMENT lolz (#PCDATA)>
 <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
 <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
 <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
]>
<mxfile><diagram>&lol3;</diagram></mxfile>"""

try:
    parser = DrawIOParser(billion_laughs_xml)
    parser.parse()
    record("1.1 Outer XML Billion Laughs Entity Bomb", False, "FAILED: Entity bomb was not rejected!")
except ValueError as e:
    err_str = str(e)
    if ("security policy violation" in err_str or "EntitiesForbidden" in err_str) and "Diagnostic Traceback:" in err_str:
        record("1.1 Outer XML Billion Laughs Entity Bomb", True, f"Cleanly rejected by defusedxml: {err_str.splitlines()[0]}")
    else:
        record("1.1 Outer XML Billion Laughs Entity Bomb", False, f"ValueError missing required security message or traceback: {err_str}")
except Exception as e:
    record("1.1 Outer XML Billion Laughs Entity Bomb", False, f"Unexpected exception: {type(e).__name__}: {e}")

# Test 1.2: Outer Document XXE External Entity Attack
xxe_xml = """<?xml version="1.0"?>
<!DOCTYPE foo [
 <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<mxfile><diagram>&xxe;</diagram></mxfile>"""

try:
    parser = DrawIOParser(xxe_xml)
    parser.parse()
    record("1.2 Outer XML XXE Payload", False, "FAILED: External entity attack was not rejected!")
except ValueError as e:
    err_str = str(e)
    if ("security policy violation" in err_str or "EntitiesForbidden" in err_str) and "Diagnostic Traceback:" in err_str:
        record("1.2 Outer XML XXE Payload", True, f"Cleanly rejected by defusedxml: {err_str.splitlines()[0]}")
    else:
        record("1.2 Outer XML XXE Payload", False, f"ValueError missing required text: {err_str}")
except Exception as e:
    record("1.2 Outer XML XXE Payload", False, f"Unexpected exception: {type(e).__name__}: {e}")

# Test 1.3: Inner Diagram Page XML Billion Laughs Entity Bomb (Compressed Payload)
inner_bomb_str = """<!DOCTYPE lolz [
 <!ENTITY lol "lol">
 <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
]>
<mxGraphModel><root><mxCell id="0"/><mxCell id="1"/>&lol1;</root></mxGraphModel>"""

comp_obj_bomb = zlib.compressobj(9, zlib.DEFLATED, -15)
bomb_bytes = comp_obj_bomb.compress(inner_bomb_str.encode('utf-8')) + comp_obj_bomb.flush()
bomb_b64 = base64.b64encode(bomb_bytes).decode('utf-8')
inner_bomb_outer_xml = f"<mxfile><diagram id='page_bomb' name='Bomb Page'>{bomb_b64}</diagram></mxfile>"

try:
    parser = DrawIOParser(inner_bomb_outer_xml)
    parser.parse()
    record("1.3 Inner Diagram Page Entity Bomb", False, "FAILED: Inner XML entity bomb was not rejected!")
except ValueError as e:
    err_str = str(e)
    if "Malformed diagram page XML in page 'Bomb Page' (id: 'page_bomb')" in err_str and ("EntitiesForbidden" in err_str or "DTDForbidden" in err_str) and "Diagnostic Traceback:" in err_str:
        record("1.3 Inner Diagram Page Entity Bomb", True, f"Cleanly decompressed and rejected inner page entity bomb with page context and traceback")
    else:
        record("1.3 Inner Diagram Page Entity Bomb", False, f"ValueError missing page details or entity rejection: {err_str}")
except Exception as e:
    record("1.3 Inner Diagram Page Entity Bomb", False, f"Unexpected exception: {type(e).__name__}: {e}")

# Test 1.4: Inner Diagram Page XXE External Entity Attack (Compressed Payload)
inner_xxe_str = """<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<mxGraphModel><root><mxCell id="0"/><mxCell id="1"/>&xxe;</root></mxGraphModel>"""

comp_obj_xxe = zlib.compressobj(9, zlib.DEFLATED, -15)
xxe_bytes = comp_obj_xxe.compress(inner_xxe_str.encode('utf-8')) + comp_obj_xxe.flush()
xxe_b64 = base64.b64encode(xxe_bytes).decode('utf-8')
inner_xxe_outer_xml = f"<mxfile><diagram id='page_xxe' name='XXE Page'>{xxe_b64}</diagram></mxfile>"

try:
    parser = DrawIOParser(inner_xxe_outer_xml)
    parser.parse()
    record("1.4 Inner Diagram Page XXE Payload", False, "FAILED: Inner XML XXE was not rejected!")
except ValueError as e:
    err_str = str(e)
    if "Malformed diagram page XML in page 'XXE Page' (id: 'page_xxe')" in err_str and ("EntitiesForbidden" in err_str or "DTDForbidden" in err_str) and "Diagnostic Traceback:" in err_str:
        record("1.4 Inner Diagram Page XXE Payload", True, f"Cleanly decompressed and rejected inner page XXE with page context and traceback")
    else:
        record("1.4 Inner Diagram Page XXE Payload", False, f"ValueError missing page details or XXE rejection: {err_str}")
except Exception as e:
    record("1.4 Inner Diagram Page XXE Payload", False, f"Unexpected exception: {type(e).__name__}: {e}")

# ==============================================================================
# SECTION 2: MALFORMED INPUTS & EXCEPTION HANDLING TESTS
# ==============================================================================

# Test 2.1: Malformed Outer XML String
malformed_outer = "<mxfile><diagram>unclosed element tag"
try:
    parser = DrawIOParser(malformed_outer)
    parser.parse()
    record("2.1 Malformed Outer XML Syntax", False, "FAILED: Malformed outer XML did not raise exception!")
except ValueError as e:
    err_str = str(e)
    if "Malformed XML document or security policy violation" in err_str and "Diagnostic Traceback:" in err_str:
        record("2.1 Malformed Outer XML Syntax", True, "Successfully caught ET.ParseError and formatted traceback into ValueError")
    else:
        record("2.1 Malformed Outer XML Syntax", False, f"ValueError format incorrect: {err_str}")
except Exception as e:
    record("2.1 Malformed Outer XML Syntax", False, f"Unexpected exception: {type(e).__name__}: {e}")

# Test 2.2: Invalid Base64 Diagram Text (Fallback to Raw String -> ParseError)
invalid_b64 = "<mxfile><diagram id='p_b64' name='B64 Page'>!!! NOT BASE64 DATA !!!</diagram></mxfile>"
try:
    parser = DrawIOParser(invalid_b64)
    parser.parse()
    record("2.2 Invalid Base64 Diagram Text", False, "FAILED: Invalid base64 did not produce ValueError!")
except ValueError as e:
    err_str = str(e)
    if "Malformed diagram page XML in page 'B64 Page' (id: 'p_b64')" in err_str and "Diagnostic Traceback:" in err_str:
        record("2.2 Invalid Base64 Diagram Text", True, "Base64 decode error safely caught in _decode_diagram_text; raw text failed XML parse with traceback")
    else:
        record("2.2 Invalid Base64 Diagram Text", False, f"ValueError missing context details: {err_str}")
except Exception as e:
    record("2.2 Invalid Base64 Diagram Text", False, f"Unexpected exception: {type(e).__name__}: {e}")

# Test 2.3: Truncated Zlib Compressed Stream
valid_inner = "<mxGraphModel><root><mxCell id='0'/><mxCell id='1'/></root></mxGraphModel>"
comp_obj = zlib.compressobj(9, zlib.DEFLATED, -15)
compressed_bytes = comp_obj.compress(valid_inner.encode('utf-8')) + comp_obj.flush()
truncated_bytes = compressed_bytes[:len(compressed_bytes)//2]
truncated_b64 = base64.b64encode(truncated_bytes).decode('utf-8')
truncated_zlib_xml = f"<mxfile><diagram id='p_zlib' name='Zlib Page'>{truncated_b64}</diagram></mxfile>"

try:
    parser = DrawIOParser(truncated_zlib_xml)
    parser.parse()
    record("2.3 Truncated Zlib Stream", False, "FAILED: Truncated zlib stream did not produce ValueError!")
except ValueError as e:
    err_str = str(e)
    if "Malformed diagram page XML in page 'Zlib Page' (id: 'p_zlib')" in err_str and "Diagnostic Traceback:" in err_str:
        record("2.3 Truncated Zlib Stream", True, "Zlib decompression error safely caught in _decode_diagram_text; inner XML parse failed with traceback")
    else:
        record("2.3 Truncated Zlib Stream", False, f"ValueError missing context details: {err_str}")
except Exception as e:
    record("2.3 Truncated Zlib Stream", False, f"Unexpected exception: {type(e).__name__}: {e}")

# Test 2.4: Decompressed Malformed Inner XML
comp_obj2 = zlib.compressobj(9, zlib.DEFLATED, -15)
bad_inner_bytes = comp_obj2.compress(b"<mxGraphModel><root><mxCell id='0'></mxGraphModel>") + comp_obj2.flush()
bad_inner_b64 = base64.b64encode(bad_inner_bytes).decode('utf-8')
malformed_inner_xml = f"<mxfile><diagram id='p_inner' name='Inner XML Page'>{bad_inner_b64}</diagram></mxfile>"

try:
    parser = DrawIOParser(malformed_inner_xml)
    parser.parse()
    record("2.4 Decompressed Malformed Inner XML", False, "FAILED: Malformed inner XML did not produce ValueError!")
except ValueError as e:
    err_str = str(e)
    if "Malformed diagram page XML in page 'Inner XML Page' (id: 'p_inner')" in err_str and "Diagnostic Traceback:" in err_str:
        record("2.4 Decompressed Malformed Inner XML", True, "Decompressed successfully; inner XML parse error raised with page name, id, and traceback")
    else:
        record("2.4 Decompressed Malformed Inner XML", False, f"ValueError missing context details: {err_str}")
except Exception as e:
    record("2.4 Decompressed Malformed Inner XML", False, f"Unexpected exception: {type(e).__name__}: {e}")

# Test 2.5: Valid Base64 + Zlib Compressed Diagram Page Parsing
comp_obj3 = zlib.compressobj(9, zlib.DEFLATED, -15)
good_inner = "<mxGraphModel><root><mxCell id='0'/><mxCell id='1'/><mxCell id='n1' value='Node1' vertex='1'/></root></mxGraphModel>"
good_bytes = comp_obj3.compress(good_inner.encode('utf-8')) + comp_obj3.flush()
good_b64 = base64.b64encode(good_bytes).decode('utf-8')
good_compressed_xml = f"<mxfile><diagram id='p_good' name='Good Page'>{good_b64}</diagram></mxfile>"

try:
    parser = DrawIOParser(good_compressed_xml)
    res = parser.parse()
    if len(res["pages"]) == 1 and res["pages"][0]["nodes"][0]["id"] == "n1":
        record("2.5 Compressed Diagram Decoding & Parsing", True, "Successfully decompressed and parsed valid diagram XML")
    else:
        record("2.5 Compressed Diagram Decoding & Parsing", False, f"Structure mismatch: {res}")
except Exception as e:
    record("2.5 Compressed Diagram Decoding & Parsing", False, f"Unexpected exception: {type(e).__name__}: {e}")

print("\n=== SUMMARY OF RESULTS ===")
total = len(results)
passed = sum(1 for _, status, _ in results if status == "PASS")
print(f"Passed {passed}/{total} tests.")

if passed == total:
    print("\nFINAL VERDICT: CONFIRMED")
else:
    print("\nFINAL VERDICT: REJECTED")
