import json
from pyvis.network import Network

INPUT_JSON = r"backend\Tests\Database\Results\curriculum_evidence_final.json"

# --------------------------------------------------
# Configuration
# --------------------------------------------------

MAX_TOPIC_LABEL = 28
MAX_SUBTOPIC_LABEL = 18

COLOR = {
    "SUBJECT": "#3B82F6",     # Blue
    "UNIT": "#10B981",        # Emerald
    "TOPIC": "#F59E0B",       # Amber
    "SUBTOPIC": "#F97316",    # Orange
    "CO": "#8B5CF6",          # Violet
    "DEFAULT": "#64748B"      # Slate
}

STYLE = {
    "SUBJECT": dict(size=45, mass=12),
    "UNIT": dict(size=30, mass=6),
    "TOPIC": dict(size=15, mass=2),
    "SUBTOPIC": dict(size=10, mass=1),
    "CO": dict(size=8, mass=1),
    "DEFAULT": dict(size=6, mass=1)
}

# --------------------------------------------------
# Helpers
# --------------------------------------------------

def shorten(text, limit):
    if len(text) <= limit:
        return text
    return text[:limit-3] + "..."

def add_visual_node(net, node):

    node_id = str(node["id"])
    text = node.get("text", "")
    node_type = node.get("type", "DEFAULT").upper()

    style = STYLE.get(node_type, STYLE["DEFAULT"])
    color = COLOR.get(node_type, COLOR["DEFAULT"])

    # ---------------- Label logic ----------------

    if node_type == "SUBJECT":
        label = text

    elif node_type == "UNIT":
        label = text

    elif node_type == "TOPIC":
        label = shorten(text, MAX_TOPIC_LABEL)

    elif node_type == "SUBTOPIC":
        label = shorten(text, MAX_SUBTOPIC_LABEL)

    else:
        label = ""

    net.add_node(
        node_id,
        label=label,
        title=f"<b>{node_type}</b><br>{text}",
        color=color,
        **style
    )


# --------------------------------------------------
# Build graph
# --------------------------------------------------

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

net = Network(
    height="100vh",
    width="100%",
    bgcolor="#0B1120",      # Deep slate
    font_color="#F8FAFC",   # Near white
    directed=False
)

net.barnes_hut(
    gravity=-30000,
    central_gravity=0.15,
    spring_length=180,
    spring_strength=0.02,
    damping=0.2
)


def traverse(node, parent=None):

    add_visual_node(net, node)

    node_id = str(node["id"])

    if parent is not None:
        net.add_edge(
            parent,
            node_id,
            width=1,
            color="#BDBDBD"
        )

    for child in node.get("children", []):
        traverse(child, node_id)


for root in data["roots"]:
    traverse(root)

# --------------------------------------------------
# Network Options
# --------------------------------------------------

net.set_options("""
{
  "physics": {
    "enabled": true,
    "barnesHut": {
      "gravitationalConstant": -30000,
      "centralGravity": 0.15,
      "springLength": 180,
      "springConstant": 0.02,
      "damping": 0.25
    },
    "stabilization": {
      "enabled": true,
      "iterations": 800
    }
  },

  "nodes": {
    "shape": "dot",
    "borderWidth": 1.5,
    "font": {
      "size": 15,
      "face": "Arial"
    }
  },

  "edges": {
    "smooth": {
      "type": "dynamic"
    },
    "color": {
      "inherit": false
    }
  },

  "interaction": {
    "hover": true,
    "navigationButtons": true,
    "dragNodes": true,
    "dragView": true,
    "zoomView": true
  }
}
""")

net.show("curriculum_bubble.html", notebook=False)