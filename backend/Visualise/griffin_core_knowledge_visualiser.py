import json
from collections import defaultdict
from pyvis.network import Network

INPUT_JSON = r"backend\Tests\Results\griffin_core_result.json"
OUTPUT_HTML = "knowledge_bubbles.html"

# --------------------------------------------------
# Load Graph
# --------------------------------------------------

with open(INPUT_JSON, "r", encoding="utf-8") as f:
    graph = json.load(f)

nodes = graph["nodes"]
edges = graph["edges"]

# Convert list -> dict if needed
if isinstance(nodes, list):
    nodes = {n["id"]: n for n in nodes}

# --------------------------------------------------
# Count children
# --------------------------------------------------

children = defaultdict(int)

for edge in edges:
    children[edge["source"]] += 1

# --------------------------------------------------
# Appearance
# --------------------------------------------------

COLORS = {
    "SUBJECT": "#2563EB",
    "UNIT": "#10B981",
    "TOPIC": "#F59E0B",
    "SUBTOPIC": "#EF4444",
    "CONCEPT": "#8B5CF6",
}

BASE_SIZE = {
    "SUBJECT": 42,
    "UNIT": 30,
    "TOPIC": 20,
    "SUBTOPIC": 14,
    "CONCEPT": 10,
}

# --------------------------------------------------
# Create Network
# --------------------------------------------------

net = Network(
    height="900px",
    width="100%",
    bgcolor="white",
    font_color="black",
)

# Simple physics
net.barnes_hut()

# --------------------------------------------------
# Add Nodes
# --------------------------------------------------

for node_id, node in nodes.items():

    node_type = node.get("node_type", "TOPIC")
    label = node.get("label", str(node_id))

    short = label if len(label) <= 45 else label[:45] + "..."

    size = BASE_SIZE.get(node_type, 12) + min(children[node_id], 18)

    net.add_node(
        node_id,
        label=short,
        title=f"""
<b>{node_type}</b><br>
{label}<br><br>
Children: {children[node_id]}
""",
        color=COLORS.get(node_type, "#999999"),
        size=size,
        shape="dot",
    )

# --------------------------------------------------
# Add Edges
# --------------------------------------------------

for edge in edges:
    net.add_edge(
        edge["source"],
        edge["target"],
        color="#cccccc",
        width=1,
    )

# --------------------------------------------------
# Save
# --------------------------------------------------

net.show_buttons(filter_=["physics"])

net.save_graph(OUTPUT_HTML)

print(f"Saved to {OUTPUT_HTML}")

# --------------------------------------------------
# Save & Open
# --------------------------------------------------

net.show_buttons(filter_=["physics"])

net.show(OUTPUT_HTML, notebook=False)

print(f"Saved to {OUTPUT_HTML}")