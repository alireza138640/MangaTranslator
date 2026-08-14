from pathlib import Path
import ast
import re
import json


# =========================================================
# CONFIG
# =========================================================

ROOT = Path(__file__).resolve().parent

IGNORED_DIRS = {
    "ocr_venv",
    "venv",
    ".venv",
    "__pycache__",
    ".git",
}

OUTPUT_FILE = ROOT / "PROJECT_AUDIT.txt"


# =========================================================
# HELPERS
# =========================================================

def is_ignored(path: Path):
    return any(part in IGNORED_DIRS for part in path.parts)


def read_file(path: Path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="utf-8-sig")
        except Exception:
            return ""
    except Exception:
        return ""


def relative(path: Path):
    return str(path.relative_to(ROOT)).replace("/", "\\")


def get_python_files():
    files = []

    for path in ROOT.rglob("*.py"):
        if is_ignored(path):
            continue

        files.append(path)

    return sorted(files, key=lambda p: relative(p).lower())


# =========================================================
# AST ANALYSIS
# =========================================================

def analyze_python(path: Path, code: str):
    result = {
        "imports": [],
        "functions": [],
        "classes": [],
        "calls": [],
        "syntax_error": None,
    }

    try:
        tree = ast.parse(code, filename=str(path))
    except SyntaxError as exc:
        result["syntax_error"] = (
            f"{exc.msg} | line={exc.lineno} | column={exc.offset}"
        )
        return result

    for node in ast.walk(tree):

        # -----------------------------
        # imports
        # -----------------------------

        if isinstance(node, ast.Import):

            for name in node.names:
                result["imports"].append(name.name)

        elif isinstance(node, ast.ImportFrom):

            module = node.module or ""

            if node.level:
                module = "." * node.level + module

            result["imports"].append(module)

        # -----------------------------
        # functions
        # -----------------------------

        elif isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            result["functions"].append(
                node.name
            )

        # -----------------------------
        # classes
        # -----------------------------

        elif isinstance(node, ast.ClassDef):
            result["classes"].append(
                node.name
            )

        # -----------------------------
        # function calls
        # -----------------------------

        elif isinstance(node, ast.Call):

            name = None

            if isinstance(node.func, ast.Name):
                name = node.func.id

            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr

            if name:
                result["calls"].append(name)

    return result


# =========================================================
# FILE STATUS
# =========================================================

def analyze_file(path: Path):

    code = read_file(path)

    lines = code.splitlines()

    analysis = analyze_python(
        path,
        code
    )

    stripped_lines = [
        line.strip()
        for line in lines
        if line.strip()
    ]

    return {
        "path": relative(path),
        "lines": len(lines),
        "non_empty": len(stripped_lines),
        "empty": len(stripped_lines) == 0,
        "bytes": path.stat().st_size,
        "analysis": analysis,
        "code": code,
    }


# =========================================================
# IMPORT GRAPH
# =========================================================

def normalize_module_name(path: Path):

    rel = path.relative_to(ROOT)

    parts = list(rel.parts)

    if parts[-1] == "__init__.py":
        parts.pop()
    else:
        parts[-1] = Path(parts[-1]).stem

    return ".".join(parts)


def build_module_map(files):

    mapping = {}

    for info in files:

        path = ROOT / info["path"]

        module = normalize_module_name(path)

        mapping[module] = info["path"]

    return mapping


def resolve_import(
    imported,
    current_path,
    module_map
):

    if not imported:
        return None

    # Direct match
    if imported in module_map:
        return module_map[imported]

    # Relative imports
    if imported.startswith("."):

        current_module = normalize_module_name(
            ROOT / current_path
        )

        current_parts = current_module.split(".")

        dots = len(imported) - len(
            imported.lstrip(".")
        )

        remainder = imported.lstrip(".")

        base_parts = current_parts[:-dots]

        if remainder:
            base_parts += remainder.split(".")

        candidate = ".".join(
            x for x in base_parts if x
        )

        if candidate in module_map:
            return module_map[candidate]

    return None


# =========================================================
# REFERENCES
# =========================================================

def find_string_references(
    files,
    target
):

    target_name = Path(target).stem

    references = []

    patterns = [
        target_name,
        target.replace("\\", "/"),
        target,
    ]

    for info in files:

        if info["path"] == target:
            continue

        code = info["code"]

        for pattern in patterns:

            if pattern in code:

                references.append(
                    info["path"]
                )

                break

    return references


# =========================================================
# MAIN AUDIT
# =========================================================

def main():

    print()
    print("=" * 80)
    print(" MangaTranslator - FULL PROJECT AUDIT")
    print("=" * 80)
    print()
    print(f"Project root : {ROOT}")
    print("Ignored      : ocr_venv, venv, .venv, __pycache__, .git")
    print()

    paths = get_python_files()

    files = [
        analyze_file(path)
        for path in paths
    ]

    module_map = build_module_map(files)

    # =====================================================
    # COUNTS
    # =====================================================

    total = len(files)

    empty_files = [
        x for x in files
        if x["empty"]
    ]

    non_empty_files = [
        x for x in files
        if not x["empty"]
    ]

    syntax_errors = [
        x for x in files
        if x["analysis"]["syntax_error"]
    ]

    total_lines = sum(
        x["lines"]
        for x in files
    )

    # =====================================================
    # OUTPUT
    # =====================================================

    report = []

    def add(text=""):
        report.append(text)

    add("=" * 80)
    add(" MangaTranslator - FULL PROJECT AUDIT")
    add("=" * 80)
    add()
    add(f"Project root : {ROOT}")
    add(f"Python files : {total}")
    add(f"Total lines  : {total_lines}")
    add(f"Non-empty    : {len(non_empty_files)}")
    add(f"Empty        : {len(empty_files)}")
    add(f"Syntax errors: {len(syntax_errors)}")
    add("Excluded     : ocr_venv / venv / .venv")
    add()

    # =====================================================
    # FILE LIST
    # =====================================================

    add("=" * 80)
    add("1. FILE STATUS")
    add("=" * 80)
    add()

    for index, info in enumerate(files, 1):

        status = (
            "EMPTY"
            if info["empty"]
            else "OK"
        )

        add(
            f"{index:03d} | "
            f"{status:<5} | "
            f"{info['lines']:5d} lines | "
            f"{info['path']}"
        )

    add()

    # =====================================================
    # EMPTY FILES
    # =====================================================

    add("=" * 80)
    add("2. EMPTY FILES")
    add("=" * 80)
    add()

    if empty_files:

        for info in empty_files:
            add(info["path"])

    else:
        add("NONE")

    add()

    # =====================================================
    # SYNTAX ERRORS
    # =====================================================

    add("=" * 80)
    add("3. SYNTAX ERRORS")
    add("=" * 80)
    add()

    if syntax_errors:

        for info in syntax_errors:

            add(
                f"{info['path']}"
            )

            add(
                f"    {info['analysis']['syntax_error']}"
            )

    else:
        add("NONE")

    add()

    # =====================================================
    # IMPORTS
    # =====================================================

    add("=" * 80)
    add("4. IMPORT GRAPH")
    add("=" * 80)
    add()

    unresolved_internal = []

    for info in files:

        imports = info["analysis"]["imports"]

        if not imports:
            continue

        add(
            f"[{info['path']}]"
        )

        for imported in imports:

            resolved = resolve_import(
                imported,
                info["path"],
                module_map
            )

            if resolved:

                add(
                    f"    {imported:<35} -> {resolved}"
                )

            else:

                add(
                    f"    {imported:<35} -> external/unknown"
                )

        add()

    # =====================================================
    # FUNCTIONS / CLASSES
    # =====================================================

    add("=" * 80)
    add("5. FUNCTIONS AND CLASSES")
    add("=" * 80)
    add()

    for info in files:

        analysis = info["analysis"]

        if (
            not analysis["functions"]
            and not analysis["classes"]
        ):
            continue

        add(
            f"[{info['path']}]"
        )

        if analysis["classes"]:

            add(
                "    Classes:"
            )

            for name in analysis["classes"]:
                add(
                    f"        - {name}"
                )

        if analysis["functions"]:

            add(
                "    Functions:"
            )

            for name in analysis["functions"]:
                add(
                    f"        - {name}"
                )

        add()

    # =====================================================
    # IMPORTANT PROJECT FILES
    # =====================================================

    add("=" * 80)
    add("6. IMPORTANT FILES")
    add("=" * 80)
    add()

    important_dirs = [
        "ocr",
        "translator",
        "renderer",
        "ui",
        "image",
        "core",
        "ai",
        "config",
        "utils",
        "tests",
    ]

    for directory in important_dirs:

        directory_files = [
            x for x in files
            if x["path"].lower().startswith(
                directory.lower() + "\\"
            )
        ]

        add(
            f"[{directory}/]"
        )

        if not directory_files:
            add("    EMPTY / NOT FOUND")
            add()
            continue

        for info in directory_files:

            status = (
                "EMPTY"
                if info["empty"]
                else "CODE"
            )

            add(
                f"    {status:<5} "
                f"{info['lines']:5d} lines "
                f"{info['path']}"
            )

        add()

    # =====================================================
    # CROSS REFERENCES
    # =====================================================

    add("=" * 80)
    add("7. FILE REFERENCES")
    add("=" * 80)
    add()

    for info in files:

        refs = find_string_references(
            files,
            info["path"]
        )

        if refs:

            add(
                f"{info['path']}"
            )

            for ref in refs:
                add(
                    f"    <- {ref}"
                )

            add()

    # =====================================================
    # FULL SOURCE
    # =====================================================

    add("=" * 80)
    add("8. COMPLETE SOURCE CODE")
    add("=" * 80)
    add()

    for index, info in enumerate(files, 1):

        add()
        add("#" * 80)
        add(
            f"# FILE {index:03d}: {info['path']}"
        )
        add("#" * 80)
        add()

        if info["empty"]:
            add("# EMPTY FILE")
        else:
            add(info["code"])

        add()

    # =====================================================
    # SAVE
    # =====================================================

    OUTPUT_FILE.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    # =====================================================
    # CONSOLE SUMMARY
    # =====================================================

    print("=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    print()
    print(f"Python files : {total}")
    print(f"Total lines  : {total_lines}")
    print(f"Code files   : {len(non_empty_files)}")
    print(f"Empty files  : {len(empty_files)}")
    print(f"Syntax errors: {len(syntax_errors)}")
    print()
    print("Report:")
    print(OUTPUT_FILE)
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()