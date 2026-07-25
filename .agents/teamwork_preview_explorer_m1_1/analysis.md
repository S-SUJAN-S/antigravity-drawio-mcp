# Milestone 1: R1 Parser Security & XML Integrity Analysis Report

## Executive Summary
This analysis evaluates `src/antigravity_drawio_mcp/parser.py` and associated test coverage in `tests/test_mcp_server.py` to establish a precise implementation strategy for Milestone 1 (R1 Parser Security & XML Integrity).

The three core requirements analyzed are:
1. **Enforcing `defusedxml.ElementTree` Security**: Ensuring entity expansion and XML bomb vulnerabilities (XXE, Billion Laughs) are prevented across all parsing calls.
2. **Narrowing Decoding Exception Handling**: Restricting `_decode_diagram_text` exception handling strictly to `(binascii.Error, zlib.error, UnicodeDecodeError)` by removing generic `ValueError`.
3. **Adding Diagnostic Error Tracebacks**: Wrapping `ET.fromstring` parsing operations in structured exception handlers that format and raise diagnostic error tracebacks when malformed XML or XXE entities are encountered.

---

## Detailed Investigation Findings

### 1. XML Security & `defusedxml` Integration
- **Location**: `src/antigravity_drawio_mcp/parser.py`, Lines 1, 27, 42.
- **Current Code**:
  ```python
  import defusedxml.ElementTree as ET
  ...
  root = ET.fromstring(xml_content)
  ...
  page_root = ET.fromstring(decoded_xml)
  ```
- **Observations**:
  - `parser.py` already imports `defusedxml.ElementTree as ET`.
  - Calling `defusedxml.ElementTree.fromstring()` guards against XML Entity Expansion (XXE) and DTD attacks by raising `defusedxml.common.DefusedXmlException` (`EntitiesForbidden`, `DTDForbidden`, `QuadraticSelectForbidden`).
  - Standard `xml.etree.ElementTree` in `builder.py` is used only for element creation (`ET.Element`, `ET.SubElement`) and element serialization (`ET.tostring`), which is safe.
  - However, `parser.py` lacks explicit handling of `defusedxml.common.DefusedXmlException` and standard `ET.ParseError`. When an attacker passes an XXE payload or malformed XML string, an unhandled low-level exception is raised without diagnostic context.

### 2. Exception Handling in `_decode_diagram_text`
- **Location**: `src/antigravity_drawio_mcp/parser.py`, Lines 17–23.
- **Current Code**:
  ```python
  def _decode_diagram_text(self, text):
      try:
          compressed = base64.b64decode(text)
          decompressed = zlib.decompress(compressed, -15)
          return urllib.parse.unquote(decompressed.decode("utf-8"))
      except (binascii.Error, zlib.error, UnicodeDecodeError, ValueError):
          return text
  ```
- **Observations**:
  - Catching `ValueError` at line 22 is overly permissive. `ValueError` can obscure underlying bugs (e.g. data type mismatches, programming logic errors) rather than true decoding failures.
  - Base64 decoding, zlib decompression, and UTF-8 decoding failures are fully covered by `binascii.Error`, `zlib.error`, and `UnicodeDecodeError`.
  - Removing `ValueError` ensures that only expected string/compression decoding failures trigger fallback to returning raw `text`.

### 3. Diagnostic Error Tracebacks for Malformed XML
- **Location**: `src/antigravity_drawio_mcp/parser.py`, Lines 27 and 42.
- **Current Code**:
  ```python
  root = ET.fromstring(xml_content)
  ...
  page_root = ET.fromstring(decoded_xml)
  ```
- **Observations**:
  - Currently, when malformed XML is passed into `parse()`, `ET.fromstring(xml_content)` or `ET.fromstring(decoded_xml)` raises `xml.etree.ElementTree.ParseError` or `defusedxml.common.DefusedXmlException` directly.
  - The callers (such as MCP tool handlers in `server.py` or unit tests) receive unformatted error messages without diagnostic tracebacks specifying which XML block or page failed.
  - Integrating `traceback.format_exc()` into a structured `try ... except (ET.ParseError, defusedxml.common.DefusedXmlException) as e:` block allows `DrawIOParser` to raise a `ValueError` containing an explicit error message and full diagnostic stack trace.

---

## Proposed Implementation Plan

### Target File: `src/antigravity_drawio_mcp/parser.py`

#### 1. Required Imports
Add `traceback` and `defusedxml.common`:
```python
import defusedxml.ElementTree as ET
import defusedxml.common
import zlib
import base64
import binascii
import urllib.parse
import traceback
```

#### 2. Refactored `_decode_diagram_text` Method
```python
    def _decode_diagram_text(self, text):
        try:
            compressed = base64.b64decode(text)
            decompressed = zlib.decompress(compressed, -15)
            return urllib.parse.unquote(decompressed.decode("utf-8"))
        except (binascii.Error, zlib.error, UnicodeDecodeError):
            return text
```

#### 3. Refactored `parse` Method with Diagnostic Tracebacks
```python
    def parse(self):
        xml_content = self._load_xml()
        try:
            root = ET.fromstring(xml_content)
        except (ET.ParseError, defusedxml.common.DefusedXmlException) as e:
            tb = traceback.format_exc()
            raise ValueError(
                f"Malformed XML document or security policy violation: {e}\n"
                f"Diagnostic Traceback:\n{tb}"
            ) from e

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
                try:
                    page_root = ET.fromstring(decoded_xml)
                except (ET.ParseError, defusedxml.common.DefusedXmlException) as e:
                    tb = traceback.format_exc()
                    raise ValueError(
                        f"Malformed diagram page XML in page '{page_name}' (id: '{page_id}'): {e}\n"
                        f"Diagnostic Traceback:\n{tb}"
                    ) from e
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
```

---

## Patch Summary (Diff Format)

```diff
--- a/src/antigravity_drawio_mcp/parser.py
+++ b/src/antigravity_drawio_mcp/parser.py
@@ -1,5 +1,7 @@
 import defusedxml.ElementTree as ET
+import defusedxml.common
 import zlib
 import base64
 import binascii
 urllib.parse
+import traceback
 
 class DrawIOParser:
     def __init__(self, filepath_or_xml):
@@ -21,6 +23,6 @@
-        except (binascii.Error, zlib.error, UnicodeDecodeError, ValueError):
+        except (binascii.Error, zlib.error, UnicodeDecodeError):
             return text
 
     def parse(self):
         xml_content = self._load_xml()
-        root = ET.fromstring(xml_content)
+        try:
+            root = ET.fromstring(xml_content)
+        except (ET.ParseError, defusedxml.common.DefusedXmlException) as e:
+            tb = traceback.format_exc()
+            raise ValueError(
+                f"Malformed XML document or security policy violation: {e}\n"
+                f"Diagnostic Traceback:\n{tb}"
+            ) from e
 
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
-                page_root = ET.fromstring(decoded_xml)
+                try:
+                    page_root = ET.fromstring(decoded_xml)
+                except (ET.ParseError, defusedxml.common.DefusedXmlException) as e:
+                    tb = traceback.format_exc()
+                    raise ValueError(
+                        f"Malformed diagram page XML in page '{page_name}' (id: '{page_id}'): {e}\n"
+                        f"Diagnostic Traceback:\n{tb}"
+                    ) from e
             else:
                 mx_model = diagram.find("mxGraphModel")
                 page_root = mx_model if mx_model is not None else diagram
```

---

## Recommended Verification Strategy

To verify this implementation when changes are applied:
1. **XXE Protection Verification**:
   - Pass an XML payload with `<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>` to `DrawIOParser`.
   - Confirm that `defusedxml.common.EntitiesForbidden` / `DefusedXmlException` is caught and raised as a `ValueError` with diagnostic traceback.
2. **Exception Narrowing Verification**:
   - Pass invalid Base64 or non-zlib string to `_decode_diagram_text` to ensure fallback returns raw text.
   - Confirm that any raised `ValueError` inside decoding logic is no longer silently suppressed by `_decode_diagram_text`.
3. **Malformed XML Diagnostic Verification**:
   - Pass corrupted XML (`<mxfile><diagram>unclosed element`) to `DrawIOParser`.
   - Confirm that `ValueError` is raised with a message containing `"Malformed XML"` and `"Diagnostic Traceback:"`.
