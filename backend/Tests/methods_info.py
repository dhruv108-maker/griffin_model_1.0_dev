import ast
import os

ROOT = "backend"
OUTPUT = "backend_api_map.md"

IGNORE = {
    "__pycache__", ".git", ".idea", ".vscode",
    ".venv", "venv", "env", "build", "dist",
    "node_modules"
}


# ==========================================================
# Helpers
# ==========================================================

def src(node):
    try:
        return ast.unparse(node)
    except Exception:
        return "<unknown>"


def fmt_args(fn):
    args = []

    for a in fn.args.posonlyargs + fn.args.args:
        ann = src(a.annotation) if a.annotation else "Any"
        args.append(f"{a.arg}: {ann}")

    if fn.args.vararg:
        args.append("*" + fn.args.vararg.arg)

    for a in fn.args.kwonlyargs:
        ann = src(a.annotation) if a.annotation else "Any"
        args.append(f"{a.arg}: {ann}")

    if fn.args.kwarg:
        args.append("**" + fn.args.kwarg.arg)

    return args or ["None"]


def outputs(fn):
    """
    Collect only explicit outputs written by developer.
    No inference.
    """

    result = []

    for n in ast.walk(fn):

        if isinstance(n, ast.Return):
            if n.value is None:
                result.append(("None", "None"))
            else:
                expr = src(n.value)

                if isinstance(n.value, ast.Name):
                    result.append((expr, expr))

                elif isinstance(n.value, ast.Dict):
                    result.append(("dict", expr))

                elif isinstance(n.value, ast.List):
                    result.append(("list", expr))

                elif isinstance(n.value, ast.Tuple):
                    result.append(("tuple", expr))

                elif isinstance(n.value, ast.Call):
                    name = src(n.value.func)
                    result.append((name, expr))

                else:
                    result.append(("expression", expr))

        elif isinstance(n, ast.Yield):
            result.append(("yield", src(n.value)))

        elif isinstance(n, ast.YieldFrom):
            result.append(("yield from", src(n.value)))

    if not result:
        result.append(("None", "No explicit return"))

    # remove duplicates while preserving order
    seen = set()
    final = []

    for x in result:
        if x not in seen:
            seen.add(x)
            final.append(x)

    return final


def schema_fields(cls):
    """
    Dataclass / Pydantic style schema fields.
    """

    fields = []

    for n in cls.body:

        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            typ = src(n.annotation) if n.annotation else "Any"
            fields.append(f"{n.target.id}: {typ}")

        elif isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    fields.append(t.id)

    return fields


# ==========================================================
# AST
# ==========================================================

class Visitor(ast.NodeVisitor):

    def __init__(self):
        self.lines = []
        self.stack = []

    def visit_ClassDef(self, node):

        self.stack.append(node.name)

        fields = schema_fields(node)

        if fields:
            self.lines.append(f"### Schema/Class `{node.name}`")
            self.lines.append("")
            self.lines.append("Fields")
            for f in fields:
                self.lines.append(f"- {f}")
            self.lines.append("")
        else:
            self.lines.append(f"### Class `{node.name}`")
            self.lines.append("")

        self.generic_visit(node)

        self.stack.pop()

    def visit_FunctionDef(self, node):
        self.func(node)

    def visit_AsyncFunctionDef(self, node):
        self.func(node, True)

    def func(self, node, async_=False):

        name = ".".join(self.stack + [node.name]) if self.stack else node.name
        prefix = "async " if async_ else ""

        self.lines.append(f"#### {prefix}{name}")
        self.lines.append("")

        self.lines.append("Input")

        for a in fmt_args(node):
            self.lines.append(f"- {a}")

        self.lines.append("")
        self.lines.append(f"Output Type : `{src(node.returns) if node.returns else 'Unknown'}`")
        self.lines.append("")
        self.lines.append("Output")

        for kind, value in outputs(node):
            self.lines.append(f"- {kind} -> `{value}`")

        self.lines.append("")


# ==========================================================
# Scan
# ==========================================================

md = ["# Backend API Map", ""]

for root, dirs, files in os.walk(ROOT):

    dirs[:] = [d for d in dirs if d not in IGNORE]

    py = sorted(f for f in files if f.endswith(".py"))

    if not py:
        continue

    for file in py:

        path = os.path.join(root, file)
        rel = os.path.relpath(path, ROOT).replace("\\", "/")

        md.append(f"## {rel}")
        md.append("")

        try:

            with open(path, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=rel)

            v = Visitor()
            v.visit(tree)

            if v.lines:
                md.extend(v.lines)
            else:
                md.append("*No classes or methods.*")

        except Exception as e:
            md.append(f"Parse Error : `{e}`")

        md.append("")

# ==========================================================
# Save
# ==========================================================

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(md))

print(f"Saved -> {OUTPUT}")