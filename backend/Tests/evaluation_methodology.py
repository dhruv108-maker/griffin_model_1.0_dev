import ast
import os

# ==========================================================
# Configuration
# ==========================================================

ROOT = r"backend\EvidenceModel\evaluation"
OUTPUT = "evaluation_methodology.md"

# ==========================================================
# Helpers
# ==========================================================

def code(node):
    try:
        return ast.unparse(node)
    except Exception:
        return "<unknown>"


def get_doc(node):
    return ast.get_docstring(node) or ""


def collect_returns(fn):
    vals = []

    for n in ast.walk(fn):
        if isinstance(n, ast.Return) and n.value:
            vals.append(code(n.value))

    return list(dict.fromkeys(vals))


def collect_calls(fn):
    calls = []

    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Attribute):
                calls.append(code(n.func))
            elif isinstance(n.func, ast.Name):
                calls.append(n.func.id)

    return list(dict.fromkeys(calls))


def collect_formulas(fn):
    formulas = []

    for n in ast.walk(fn):

        if isinstance(n, ast.Assign):
            formulas.append(code(n))

        elif isinstance(n, ast.AugAssign):
            formulas.append(code(n))

        elif isinstance(n, ast.Return):
            if n.value:
                formulas.append("return " + code(n.value))

    return formulas


# ==========================================================
# Visitor
# ==========================================================

class EvaluationVisitor(ast.NodeVisitor):

    def __init__(self):
        self.lines = []
        self.cls = None

    def visit_ClassDef(self, node):
        old = self.cls
        self.cls = node.name

        self.lines.append(f"# {node.name}")
        self.lines.append("")

        doc = get_doc(node)
        if doc:
            self.lines.append(doc)
            self.lines.append("")

        self.generic_visit(node)
        self.cls = old

    def visit_FunctionDef(self, node):

        fullname = f"{self.cls}.{node.name}" if self.cls else node.name

        self.lines.append(f"## {fullname}")
        self.lines.append("")

        doc = get_doc(node)
        if doc:
            self.lines.append("### Description")
            self.lines.append(doc)
            self.lines.append("")

        args = []

        for a in node.args.args:
            if a.arg in ("self", "cls"):
                continue
            ann = code(a.annotation) if a.annotation else "Any"
            args.append(f"- {a.arg}: {ann}")

        self.lines.append("### Inputs")
        self.lines.extend(args if args else ["- None"])
        self.lines.append("")

        self.lines.append(f"### Output Type")
        self.lines.append(f"`{code(node.returns) if node.returns else 'Unknown'}`")
        self.lines.append("")

        returns = collect_returns(node)

        self.lines.append("### Returns")
        if returns:
            for r in returns:
                self.lines.append(f"- `{r}`")
        else:
            self.lines.append("- None")
        self.lines.append("")

        calls = collect_calls(node)

        self.lines.append("### Methods Used")
        if calls:
            for c in calls:
                self.lines.append(f"- `{c}()`")
        else:
            self.lines.append("- None")
        self.lines.append("")

        formulas = collect_formulas(node)

        self.lines.append("### Mathematical Procedure")
        if formulas:
            self.lines.append("```python")
            self.lines.extend(formulas)
            self.lines.append("```")
        else:
            self.lines.append("No explicit mathematical statements.")
        self.lines.append("")


# ==========================================================
# Generate
# ==========================================================

md = [
    "# Evaluation Methodology",
    "",
    "Automatically extracted from source code.",
    ""
]

for file in sorted(os.listdir(ROOT)):

    if not file.endswith(".py"):
        continue

    path = os.path.join(ROOT, file)

    md.append("=" * 80)
    md.append("")
    md.append(f"# File: {file}")
    md.append("")

    try:

        with open(path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        visitor = EvaluationVisitor()
        visitor.visit(tree)

        if visitor.lines:
            md.extend(visitor.lines)
        else:
            md.append("No classes or functions found.")

    except Exception as e:
        md.append(f"Parse Error: {e}")

    md.append("")
    md.append("")

# ==========================================================
# Save
# ==========================================================

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print(f"Saved -> {OUTPUT}")