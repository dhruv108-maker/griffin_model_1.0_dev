import ast
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================

PROJECT_ROOT = Path(".").resolve()

FRONTEND_DIR = PROJECT_ROOT / "src"
BACKEND_DIR = PROJECT_ROOT / "backend"

OUTPUT_FILE = PROJECT_ROOT / "CODEBASE_API_MAP.md"

IGNORE_DIRS = {
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".vite",
}


# ============================================================
# HELPERS
# ============================================================

def should_ignore(path):
    return any(part in IGNORE_DIRS for part in path.parts)


def read_file(path):
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


# ============================================================
# BACKEND ANALYSIS
# ============================================================

def analyze_python_file(path):

    content = read_file(path)

    result = {
        "file": str(path.relative_to(PROJECT_ROOT)),
        "functions": [],
        "classes": [],
        "routes": [],
    }

    try:
        tree = ast.parse(content)
    except Exception as e:
        result["error"] = f"Python parse error: {e}"
        return result

    for node in ast.walk(tree):

        # ----------------------------
        # Functions
        # ----------------------------

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

            parameters = []

            for arg in node.args.args:
                parameters.append(arg.arg)

            result["functions"].append({
                "name": node.name,
                "parameters": parameters,
                "line": node.lineno,
            })

        # ----------------------------
        # Classes
        # ----------------------------

        elif isinstance(node, ast.ClassDef):

            result["classes"].append({
                "name": node.name,
                "line": node.lineno,
            })

        # ----------------------------
        # FastAPI / Flask routes
        # ----------------------------

        elif isinstance(node, ast.Call):

            if isinstance(node.func, ast.Attribute):

                method = node.func.attr.lower()

                if method in {
                    "get",
                    "post",
                    "put",
                    "patch",
                    "delete",
                }:

                    if node.args:

                        try:
                            route = ast.literal_eval(node.args[0])
                        except Exception:
                            route = "dynamic"

                        result["routes"].append({
                            "method": method.upper(),
                            "path": route,
                            "line": node.lineno,
                        })

    return result


def scan_backend():

    results = []

    if not BACKEND_DIR.exists():

        print(f"[WARNING] Backend directory not found: {BACKEND_DIR}")

        return results

    for path in BACKEND_DIR.rglob("*.py"):

        if should_ignore(path):
            continue

        results.append(
            analyze_python_file(path)
        )

    return results


# ============================================================
# FRONTEND ANALYSIS
# ============================================================

def analyze_frontend_file(path):

    content = read_file(path)

    result = {
        "file": str(path.relative_to(PROJECT_ROOT)),
        "functions": [],
        "api_calls": [],
    }

    lines = content.splitlines()

    for line_number, line in enumerate(lines, start=1):

        stripped = line.strip()

        # ----------------------------
        # Function declarations
        # ----------------------------

        if (
            stripped.startswith("function ")
            or (
                "const " in stripped
                and "=>" in stripped
            )
            or (
                "async " in stripped
                and "=>" in stripped
            )
        ):

            result["functions"].append({
                "line": line_number,
                "code": stripped[:250],
            })

        # ----------------------------
        # API calls
        # ----------------------------

        api_patterns = [
            ".get(",
            ".post(",
            ".put(",
            ".patch(",
            ".delete(",
            "fetch(",
        ]

        if any(pattern in stripped for pattern in api_patterns):

            result["api_calls"].append({
                "line": line_number,
                "code": stripped[:300],
            })

    return result


def scan_frontend():

    results = []

    if not FRONTEND_DIR.exists():

        print(
            f"[WARNING] Frontend directory not found: "
            f"{FRONTEND_DIR}"
        )

        return results

    extensions = {
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
    }

    for path in FRONTEND_DIR.rglob("*"):

        if path.suffix.lower() not in extensions:
            continue

        if should_ignore(path):
            continue

        results.append(
            analyze_frontend_file(path)
        )

    return results


# ============================================================
# MARKDOWN GENERATION
# ============================================================

def generate_markdown(frontend, backend):

    md = []

    md.append("# Codebase Frontend / Backend API Map")
    md.append("")
    md.append(
        "Generated automatically for frontend/backend "
        "integration analysis."
    )
    md.append("")

    # ========================================================
    # PROJECT STRUCTURE
    # ========================================================

    md.append("# 1. Project Structure")
    md.append("")

    md.append(f"- Project root: `{PROJECT_ROOT}`")
    md.append(f"- Frontend: `{FRONTEND_DIR}`")
    md.append(f"- Backend: `{BACKEND_DIR}`")
    md.append("")

    # ========================================================
    # BACKEND
    # ========================================================

    md.append("# 2. Backend")
    md.append("")

    for item in backend:

        md.append(f"## `{item['file']}`")
        md.append("")

        # Errors

        if "error" in item:

            md.append(
                f"**ERROR:** `{item['error']}`"
            )

            md.append("")
            continue

        # Classes

        if item["classes"]:

            md.append("### Classes")
            md.append("")

            for cls in item["classes"]:

                md.append(
                    f"- `{cls['name']}` "
                    f"(line {cls['line']})"
                )

            md.append("")

        # Functions

        if item["functions"]:

            md.append("### Functions")
            md.append("")

            for fn in item["functions"]:

                params = ", ".join(
                    fn["parameters"]
                )

                md.append(
                    f"- `{fn['name']}({params})` "
                    f"(line {fn['line']})"
                )

            md.append("")

        # Routes

        if item["routes"]:

            md.append("### API Routes")
            md.append("")

            for route in item["routes"]:

                md.append(
                    f"- `{route['method']} "
                    f"{route['path']}` "
                    f"(line {route['line']})"
                )

            md.append("")

    # ========================================================
    # FRONTEND
    # ========================================================

    md.append("# 3. Frontend")
    md.append("")

    for item in frontend:

        md.append(f"## `{item['file']}`")
        md.append("")

        # Functions

        if item["functions"]:

            md.append("### Functions")
            md.append("")

            for fn in item["functions"]:

                md.append(
                    f"- Line {fn['line']}: "
                    f"`{fn['code']}`"
                )

            md.append("")

        # API Calls

        if item["api_calls"]:

            md.append("### API Calls")
            md.append("")

            for call in item["api_calls"]:

                md.append(
                    f"- Line {call['line']}: "
                    f"`{call['code']}`"
                )

            md.append("")

    # ========================================================
    # ALIGNMENT REVIEW
    # ========================================================

    md.append("# 4. Frontend ↔ Backend Alignment Review")
    md.append("")

    md.append(
        "Claude should use this codebase map to investigate "
        "the following:"
    )

    md.append("")

    review_items = [
        "Frontend API calls with no matching backend route.",
        "Backend routes that are never called by the frontend.",
        "HTTP method mismatches.",
        "URL/path mismatches.",
        "Parameter name mismatches.",
        "Request body mismatches.",
        "Response structure mismatches.",
        "Authentication/header mismatches.",
        "Missing frontend methods.",
        "Missing backend methods.",
        "Incorrect imports or function names.",
        "Potential 401 / 403 / 404 / 422 / 500 causes.",
        "Duplicate or conflicting API implementations.",
        "Dead or unreferenced endpoints.",
        "Frontend/backend architectural inconsistencies.",
        "Potential async/sync mismatches.",
        "Potential type mismatches.",
        "Potential naming inconsistencies.",
    ]

    for index, item in enumerate(
        review_items,
        start=1
    ):

        md.append(f"{index}. {item}")

    md.append("")

    # ========================================================
    # CLAUDE INSTRUCTIONS
    # ========================================================

    md.append("# 5. Claude Investigation Instructions")
    md.append("")

    md.append(
        """
Use this document as a codebase map.

IMPORTANT RULES:

- Do not modify business logic.
- Do not rewrite working functionality unnecessarily.
- Do not assume an endpoint is broken only because it cannot
  be statically matched.
- Verify the actual implementation before recommending changes.
- Identify the root cause before suggesting a fix.
- Prefer minimal, targeted fixes.
- Preserve existing API contracts unless a mismatch is confirmed.
- Distinguish confirmed errors from potential issues.
- Do not invent missing endpoints or functions.

For every confirmed or highly probable mismatch, report:

### Issue

- Frontend file:
- Frontend function:
- Frontend line:
- Backend file:
- Backend function/route:
- Backend line:
- HTTP method:
- Endpoint:
- Expected behavior:
- Actual behavior:
- Root cause:
- Recommended fix:
- Confidence:

Classify each issue as:

- CONFIRMED
- LIKELY
- POSSIBLE
- NO ISSUE

Prioritize:

1. Runtime-breaking errors
2. API contract mismatches
3. Authentication problems
4. Request/response schema mismatches
5. Incorrect imports/functions
6. Performance problems
7. Architectural inconsistencies
"""
    )

    md.append("")

    return "\n".join(md)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("FRONTEND / BACKEND CODEBASE ANALYZER")
    print("=" * 70)

    print()
    print("[1/3] Scanning backend...")

    backend = scan_backend()

    print(
        f"      Backend files found: "
        f"{len(backend)}"
    )

    print()
    print("[2/3] Scanning frontend...")

    frontend = scan_frontend()

    print(
        f"      Frontend files found: "
        f"{len(frontend)}"
    )

    print()
    print("[3/3] Generating Markdown...")

    markdown = generate_markdown(
        frontend,
        backend
    )

    OUTPUT_FILE.write_text(
        markdown,
        encoding="utf-8"
    )

    print()
    print("=" * 70)
    print("DONE")
    print("=" * 70)

    print(f"Output: {OUTPUT_FILE}")
    print(f"Backend files: {len(backend)}")
    print(f"Frontend files: {len(frontend)}")
    print("=" * 70)


if __name__ == "__main__":
    main()