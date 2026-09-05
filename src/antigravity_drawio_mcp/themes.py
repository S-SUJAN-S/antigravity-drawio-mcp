"""
Theme palettes and Draw.io shape styling definitions for Antigravity Draw.io MCP v2.0.
Provides modern, publication-grade aesthetics for software architecture, cloud topology,
and system flowcharts.
"""

THEMES = {
    "modern_slate": {
        "name": "Modern Slate",
        "primary": {"fill": "#EEF2F6", "stroke": "#334155", "font": "#0F172A"},
        "secondary": {"fill": "#E0E7FF", "stroke": "#4338CA", "font": "#1E1B4B"},
        "accent": {"fill": "#D1FAE5", "stroke": "#059669", "font": "#064E3B"},
        "warning": {"fill": "#FEF3C7", "stroke": "#D97706", "font": "#78350F"},
        "danger": {"fill": "#FEE2E2", "stroke": "#DC2626", "font": "#7F1D1D"},
        "container": {"fill": "#F8FAFC", "stroke": "#94A3B8", "font": "#475569"},
        "edge": {"stroke": "#475569", "strokeWidth": 1.5}
    },
    "cyberpunk_dark": {
        "name": "Cyberpunk Dark",
        "primary": {"fill": "#161B22", "stroke": "#00F0FF", "font": "#E6EDF3"},
        "secondary": {"fill": "#1F2430", "stroke": "#8A2BE2", "font": "#FFFFFF"},
        "accent": {"fill": "#0A2E38", "stroke": "#00FF9D", "font": "#00FF9D"},
        "warning": {"fill": "#2E2412", "stroke": "#FFB800", "font": "#FFD600"},
        "danger": {"fill": "#2E111A", "stroke": "#FF007F", "font": "#FF3399"},
        "container": {"fill": "#0D1117", "stroke": "#30363D", "font": "#8B949E"},
        "edge": {"stroke": "#00F0FF", "strokeWidth": 1.5}
    },
    "cloud_aws": {
        "name": "Cloud AWS",
        "primary": {"fill": "#FFF5EA", "stroke": "#EC7211", "font": "#232F3E"},
        "secondary": {"fill": "#EDF5ED", "stroke": "#277116", "font": "#1B660F"},
        "accent": {"fill": "#F3EBF9", "stroke": "#8C4FFF", "font": "#3C1053"},
        "warning": {"fill": "#FFF9E6", "stroke": "#D05F00", "font": "#441D00"},
        "danger": {"fill": "#FEECEC", "stroke": "#D13212", "font": "#5C1103"},
        "container": {"fill": "#F9FAFB", "stroke": "#7D8998", "font": "#232F3E"},
        "edge": {"stroke": "#232F3E", "strokeWidth": 1.5}
    },
    "cloud_gcp": {
        "name": "Cloud GCP",
        "primary": {"fill": "#E8F0FE", "stroke": "#4285F4", "font": "#1A73E8"},
        "secondary": {"fill": "#E6F4EA", "stroke": "#34A853", "font": "#137333"},
        "accent": {"fill": "#FEF7E0", "stroke": "#FBBC04", "font": "#B06000"},
        "warning": {"fill": "#FFF0E6", "stroke": "#FA7B17", "font": "#A53600"},
        "danger": {"fill": "#FCE8E6", "stroke": "#EA4335", "font": "#C5221F"},
        "container": {"fill": "#F8F9FA", "stroke": "#BDC1C6", "font": "#3C4043"},
        "edge": {"stroke": "#5F6368", "strokeWidth": 1.5}
    },
    "cloud_azure": {
        "name": "Cloud Azure",
        "primary": {"fill": "#E5F2FC", "stroke": "#0078D4", "font": "#004578"},
        "secondary": {"fill": "#DEECF9", "stroke": "#005A9E", "font": "#003966"},
        "accent": {"fill": "#E1DFDD", "stroke": "#50E6FF", "font": "#106EBE"},
        "warning": {"fill": "#FFF4CE", "stroke": "#FFB900", "font": "#795E00"},
        "danger": {"fill": "#FDE7E9", "stroke": "#A80000", "font": "#6B0000"},
        "container": {"fill": "#FAF9F8", "stroke": "#A19F9D", "font": "#323130"},
        "edge": {"stroke": "#0078D4", "strokeWidth": 1.5}
    },
    "c4_model": {
        "name": "C4 Model",
        "primary": {"fill": "#1168BD", "stroke": "#0B4D8C", "font": "#FFFFFF"},      # Software System
        "secondary": {"fill": "#438DD5", "stroke": "#2E6295", "font": "#FFFFFF"},    # Container
        "accent": {"fill": "#85BBF0", "stroke": "#5E83A8", "font": "#000000"},       # Component
        "warning": {"fill": "#08427B", "stroke": "#052E56", "font": "#FFFFFF"},      # Person
        "danger": {"fill": "#999999", "stroke": "#6B6B6B", "font": "#FFFFFF"},       # External
        "container": {"fill": "#F5F5F5", "stroke": "#7F7F7F", "font": "#333333"},
        "edge": {"stroke": "#666666", "strokeWidth": 1.5}
    },
    "ocean_breeze": {
        "name": "Ocean Breeze",
        "primary": {"fill": "#E0F2FE", "stroke": "#0284C7", "font": "#0369A1"},
        "secondary": {"fill": "#CCFBF1", "stroke": "#0D9488", "font": "#115E59"},
        "accent": {"fill": "#F0FDF4", "stroke": "#16A34A", "font": "#15803D"},
        "warning": {"fill": "#FFFBEB", "stroke": "#F59E0B", "font": "#B45309"},
        "danger": {"fill": "#FFF1F2", "stroke": "#F43F5E", "font": "#BE123C"},
        "container": {"fill": "#F8FAFC", "stroke": "#CBD5E1", "font": "#475569"},
        "edge": {"stroke": "#0284C7", "strokeWidth": 1.5}
    },
    "monochrome": {
        "name": "Monochrome Minimal",
        "primary": {"fill": "#FFFFFF", "stroke": "#111827", "font": "#111827"},
        "secondary": {"fill": "#F3F4F6", "stroke": "#374151", "font": "#1F2937"},
        "accent": {"fill": "#E5E7EB", "stroke": "#4B5563", "font": "#111827"},
        "warning": {"fill": "#D1D5DB", "stroke": "#1F2937", "font": "#111827"},
        "danger": {"fill": "#9CA3AF", "stroke": "#111827", "font": "#000000"},
        "container": {"fill": "#FAFAFA", "stroke": "#9CA3AF", "font": "#4B5563"},
        "edge": {"stroke": "#374151", "strokeWidth": 1.5}
    }
}

SHAPE_STYLES = {
    "rectangle": "rounded=0;whiteSpace=wrap;html=1;",
    "rounded_rect": "rounded=1;whiteSpace=wrap;html=1;arcSize=12;",
    "pill_badge": "rounded=1;whiteSpace=wrap;html=1;arcSize=50;",
    "cylinder": "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;",
    "cloud": "ellipse;shape=cloud;whiteSpace=wrap;html=1;",
    "actor": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;",
    "document": "shape=document;whiteSpace=wrap;html=1;boundedLbl=1;",
    "hexagon": "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;",
    "diamond": "rhombus;whiteSpace=wrap;html=1;",
    "queue": "shape=singleRack;whiteSpace=wrap;html=1;",
    "swimlane": "swimlane;whiteSpace=wrap;html=1;collapsible=0;dropTarget=0;startSize=28;horizontal=1;fontStyle=1;fontSize=12;"
}

EDGE_STYLES = {
    "orthogonal": "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=classic;",
    "curved": "edgeStyle=orthogonalEdgeStyle;curved=1;rounded=0;html=1;endArrow=classic;",
    "straight": "rounded=0;html=1;endArrow=classic;",
    "dashed": "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=classic;dashed=1;",
    "dotted": "edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=classic;dashed=1;dashPattern=1 4;"
}

def get_theme(theme_name="modern_slate"):
    return THEMES.get(theme_name, THEMES["modern_slate"])

def get_node_style(shape="rounded_rect", role="primary", theme_name="modern_slate", custom_fill=None, custom_stroke=None, custom_font=None):
    theme = get_theme(theme_name)
    color_role = theme.get(role, theme["primary"])

    fill = custom_fill or color_role["fill"]
    stroke = custom_stroke or color_role["stroke"]
    font = custom_font or color_role.get("font", "#0F172A")
    stroke_w = "1.5"

    base_shape = SHAPE_STYLES.get(shape, SHAPE_STYLES["rounded_rect"])
    return f"{base_shape}fillColor={fill};strokeColor={stroke};strokeWidth={stroke_w};fontColor={font};fontFamily=Helvetica;fontSize=12;"

def get_edge_style(style_type="orthogonal", theme_name="modern_slate", dashed=False, custom_color=None):
    theme = get_theme(theme_name)
    stroke_color = custom_color or theme.get("edge", {}).get("stroke", "#475569")
    stroke_w = theme.get("edge", {}).get("strokeWidth", 1.5)

    base = EDGE_STYLES.get(style_type, EDGE_STYLES["orthogonal"])
    if dashed:
        base += "dashed=1;"
    return f"{base}strokeColor={stroke_color};strokeWidth={stroke_w};"

def get_container_style(theme_name="modern_slate", title_align="left"):
    theme = get_theme(theme_name)
    c = theme.get("container", theme["primary"])
    return (
        f"swimlane;whiteSpace=wrap;html=1;collapsible=0;dropTarget=0;startSize=28;"
        f"fillColor={c['fill']};strokeColor={c['stroke']};strokeWidth=1.5;"
        f"fontColor={c['font']};fontStyle=1;fontSize=12;align={title_align};"
    )
