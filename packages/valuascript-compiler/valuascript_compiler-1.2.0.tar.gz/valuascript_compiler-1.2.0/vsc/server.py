import re
import os
import sys
import subprocess
import json
import tempfile
from collections import deque
from lark.exceptions import UnexpectedInput, UnexpectedCharacters, UnexpectedToken
from pygls.server import LanguageServer
from lsprotocol.types import (
    Diagnostic,
    Position,
    Range,
    DiagnosticSeverity,
    MarkupContent,
    MarkupKind,
    TEXT_DOCUMENT_HOVER,
    Hover,
)
from pygls.workspace import Document

# Ensure the server can find its own modules when packaged
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from vsc.compiler import (
    ValuaScriptTransformer,
    _build_dependency_graph,
    _infer_expression_type,
    LARK_PARSER,
    validate_valuascript,
)
from vsc.config import FUNCTION_SIGNATURES
from vsc.exceptions import ValuaScriptError
from vsc.utils import format_lark_error, find_engine_executable

server = LanguageServer("valuascript-server", "v1")


def _format_number_with_separators(n):
    """Formats a number with underscores for thousands separation."""
    if isinstance(n, int):
        return f"{n:,}".replace(",", "_")
    if isinstance(n, float):
        parts = str(n).split(".")
        integer_part = f"{int(parts[0]):,}".replace(",", "_")
        return f"{integer_part}.{parts[1]}"
    return n


def _validate(ls, params):
    text_doc = ls.workspace.get_document(params.text_document.uri)
    source = text_doc.source
    diagnostics = []
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def strip_ansi(text):
        return ansi_escape.sub("", text)

    original_stdout = sys.stdout
    try:
        sys.stdout = open(os.devnull, "w")
        validate_valuascript(source, context="lsp")
    except (UnexpectedInput, UnexpectedCharacters, UnexpectedToken) as e:
        line, col = e.line - 1, e.column - 1
        msg = strip_ansi(format_lark_error(e, source).splitlines()[-1])
        diagnostics.append(Diagnostic(range=Range(start=Position(line, col), end=Position(line, col + 100)), message=msg, severity=DiagnosticSeverity.Error))
    except ValuaScriptError as e:
        msg = strip_ansi(str(e))
        line = 0
        match = re.match(r"L(\d+):", msg)
        if match:
            line = int(match.group(1)) - 1
            msg = msg[len(match.group(0)) :].strip()
        diagnostics.append(Diagnostic(range=Range(start=Position(line, 0), end=Position(line, 100)), message=msg, severity=DiagnosticSeverity.Error))
    finally:
        sys.stdout.close()
        sys.stdout = original_stdout
    ls.publish_diagnostics(params.text_document.uri, diagnostics)


@server.feature("textDocument/didOpen")
async def did_open(ls, params):
    _validate(ls, params)


@server.feature("textDocument/didChange")
def did_change(ls, params):
    _validate(ls, params)


def _get_word_at_position(document: Document, position: Position) -> str:
    line = document.lines[position.line]
    start, end = position.character, position.character
    while start > 0 and line[start - 1].isidentifier():
        start -= 1
    while end < len(line) and line[end].isidentifier():
        end += 1
    return line[start:end]


def _is_udf_stochastic(func_def, user_functions, checked_functions=None):
    if checked_functions is None:
        checked_functions = set()
    if func_def["name"] in checked_functions:
        return False

    checked_functions.add(func_def["name"])

    for item in func_def.get("body", []):
        queue = deque([item])
        while queue:
            current = queue.popleft()
            if isinstance(current, dict):
                func_name = current.get("function")
                if func_name and FUNCTION_SIGNATURES.get(func_name, {}).get("is_stochastic"):
                    return True
                if func_name in user_functions:
                    if _is_udf_stochastic(user_functions[func_name], user_functions, checked_functions):
                        return True
                for value in current.values():
                    if isinstance(value, list):
                        queue.extend(value)
                    elif isinstance(value, dict):
                        queue.append(value)
    return False


def _get_script_analysis(source: str):
    try:
        parse_tree = LARK_PARSER.parse(source)
        raw_recipe = ValuaScriptTransformer().transform(parse_tree)
        execution_steps = raw_recipe.get("execution_steps", [])
        user_functions = {f["name"]: f for f in raw_recipe.get("function_definitions", [])}

        udf_signatures = {}
        for name, definition in user_functions.items():
            udf_signatures[name] = {
                "variadic": False,
                "arg_types": [p["type"] for p in definition["params"]],
                "return_type": definition["return_type"],
                "is_stochastic": _is_udf_stochastic(definition, user_functions),
            }
        all_signatures = {**FUNCTION_SIGNATURES, **udf_signatures}

        defined_vars = {}
        for step in execution_steps:
            try:
                rhs_type = _infer_expression_type(step, defined_vars, set(), step["line"], step["result"], all_signatures)
                defined_vars[step["result"]] = {"type": rhs_type}
            except ValuaScriptError:
                defined_vars[step["result"]] = {"type": "error"}

        dependencies, dependents = _build_dependency_graph(execution_steps)
        stochastic_vars = set()
        queue = deque()
        for step in execution_steps:
            if step.get("type") == "execution_assignment":
                func_name = step.get("function")
                if all_signatures.get(func_name, {}).get("is_stochastic"):
                    stochastic_vars.add(step["result"])
                    queue.append(step["result"])
        while queue:
            current = queue.popleft()
            for dep in dependents.get(current, []):
                if dep not in stochastic_vars:
                    stochastic_vars.add(dep)
                    queue.append(dep)

        return defined_vars, stochastic_vars, user_functions
    except Exception:
        return {}, set(), {}


@server.feature(TEXT_DOCUMENT_HOVER)
def hover(params):
    document = server.workspace.get_document(params.text_document.uri)
    word = _get_word_at_position(document, params.position)
    source = document.source
    defined_vars, stochastic_vars, user_functions = _get_script_analysis(source)

    if word in FUNCTION_SIGNATURES:
        sig = FUNCTION_SIGNATURES[word]
        doc = sig.get("doc")
        if not doc:
            return None
        param_names = [p["name"] for p in doc.get("params", [])]
        signature_str = f"{word}({', '.join(param_names)})"
        contents = [f"```valuascript\n(function) {signature_str}\n```", "---", f"**{doc.get('summary', '')}**"]
        if "params" in doc and doc["params"]:
            param_docs = ["\n#### Parameters:"]
            for p in doc["params"]:
                param_docs.append(f"- `{p.get('name', '')}`: {p.get('desc', '')}")
            contents.append("\n".join(param_docs))
        if "returns" in doc:
            returns_doc = doc.get("returns", "")
            return_type_val = sig.get("return_type", "any")
            return_type_str = "dynamic" if callable(return_type_val) else return_type_val
            contents.append(f"\n**Returns**: `{return_type_str}` — {returns_doc}")
        return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value="\n".join(contents)))

    if word in user_functions:
        func_def = user_functions[word]
        params_str = ", ".join([f"{p['name']}: {p['type']}" for p in func_def["params"]])
        signature = f"(user defined function) {func_def['name']}({params_str}) -> {func_def['return_type']}"
        contents = [f"```valuascript\n{signature}\n```"]
        if func_def.get("docstring"):
            contents.append("---")
            contents.append(func_def["docstring"])
        return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value="\n".join(contents)))

    if word in defined_vars:
        var_info = defined_vars[word]
        var_type = var_info.get("type", "unknown")

        if var_type == "error":
            header = f"```valuascript\n(variable) {word}: error\n```"
            return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value=f"{header}\n\n---\n*This line contains an error. Cannot compute value.*"))

        is_stochastic = word in stochastic_vars
        kind = "stochastic" if is_stochastic else "deterministic"
        header = f"```valuascript\n(variable) {word}: {var_type} ({kind})\n```"

        tmp_recipe_file = None
        try:
            recipe, engine_path = validate_valuascript(source, context="lsp", optimize=True, preview_variable=word), find_engine_executable(None)
            if not engine_path:
                return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value=f"{header}\n\n---\n*Error: Simulation engine 'vse' not found.*"))

            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as tmp_recipe_file:
                json.dump(recipe, tmp_recipe_file)
                recipe_path = tmp_recipe_file.name

            run_proc = subprocess.run([engine_path, "--preview", recipe_path], text=True, capture_output=True, timeout=15)

            if run_proc.stdout:
                try:
                    result_json = json.loads(run_proc.stdout)
                    if result_json.get("status") == "error":
                        message = result_json.get("message", "An unknown error occurred in the engine.")
                        return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value=f"{header}\n\n---\n*Engine Runtime Error:*\n```\n{message}\n```"))
                except json.JSONDecodeError:
                    pass

            if run_proc.returncode != 0:
                error_output = run_proc.stderr.strip() or "Process failed without an error message."
                return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value=f"{header}\n\n---\n*Error during value preview:*\n```\n{error_output}\n```"))

            try:
                result_json = json.loads(run_proc.stdout)
            except json.JSONDecodeError:
                return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value=f"{header}\n\n---\n*Error: Could not parse preview result from engine.*"))

            value = result_json.get("value")
            value_label = "Mean Value (100 trials)" if is_stochastic else "Value"

            formatted_value = value
            if isinstance(value, (int, float)):
                formatted_value = _format_number_with_separators(value)
            elif isinstance(value, list):
                formatted_value = [_format_number_with_separators(item) for item in value]

            value_str = json.dumps(formatted_value, indent=2)
            md_value = f"**{value_label}:**\n```\n{value_str.replace("\"", "")}\n```"
            return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value=f"{header}\n\n---\n{md_value}"))
        except Exception as e:
            return Hover(contents=MarkupContent(kind=MarkupKind.Markdown, value=f"{header}\n\n---\n*An error occurred while fetching live value: {e}*"))
        finally:
            if tmp_recipe_file and os.path.exists(tmp_recipe_file.name):
                os.remove(tmp_recipe_file.name)

    return None


def start_server():
    server.start_io()


if __name__ == "__main__":
    start_server()
