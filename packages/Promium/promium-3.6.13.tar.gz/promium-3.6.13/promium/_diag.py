import contextvars
import inspect
import os
import re
from collections.abc import Callable, Generator
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Any


STEP_BUFFER = int(os.getenv("PROMIUM_STEP_BUFFER", "50"))

LOCATORS_TO_SHOW = int(
    os.getenv("PROMIUM_LOCATORS_TO_SHOW", os.getenv("LOC_CHAIN_LEN", "6"))
)

STEPS_EXCLUDE = [
    s
    for s in os.getenv(
        "PROMIUM_STEPS_EXCLUDE",
        "find_elements(",
    ).split(",")
    if s.strip()
]

_DEF_SECTIONS = {"steps"}

SHOW_CALLSITE = os.getenv("PROMIUM_SHOW_CALLSITE", "1").lower() not in {
    "0",
    "false",
    "no",
}

SHOW_CALLSITE_CODELINE = os.getenv(
    "PROMIUM_SHOW_CALLSITE_CODELINE", "1"
).lower() not in {"0", "false", "no"}

FAIL_EMOJI = os.getenv("PROMIUM_FAIL_EMOJI", "✖️")

CALLSITE_CODE_INDENT = int(os.getenv("PROMIUM_CALLSITE_CODE_INDENT", "2"))

CALLSITE_CODE_MAXLEN = int(os.getenv("PROMIUM_CALLSITE_CODE_MAXLEN", "180"))

_steps_var: contextvars.ContextVar[list[str] | None] = contextvars.ContextVar(
    "_promium_steps", default=None
)
_steps_var.set([])


def _sections_enabled() -> set[str]:
    """Return enabled sections from PROMIUM_FAILURE_SECTIONS or defaults."""
    raw = os.getenv("PROMIUM_FAILURE_SECTIONS", "").strip()
    if not raw:
        return _DEF_SECTIONS
    return {s.strip() for s in raw.split(",") if s.strip()}


def _rel(path: str) -> str:
    """Return relative path from current working directory, or the original
    path on error."""
    try:
        return os.path.relpath(path, Path.cwd())
    except Exception:
        return path


def _user_callsite() -> tuple[str, int] | None:
    """Return (filename, lineno) for a relevant stack frame: prefer /tests/,
    otherwise outside promium/pytest/site-packages."""
    try:
        stack = inspect.stack()
    except Exception:
        return None
    for f in stack:
        fn = f.filename.replace("\\", "/")
        if "/tests/" in fn:
            return (f.filename, f.lineno)
    for f in stack:
        fn = f.filename.replace("\\", "/")
        if "/promium/" in fn or "site-packages/" in fn or "/_pytest/" in fn:
            continue
        return (f.filename, f.lineno)
    return None


def _dedup_consecutive(items: list[str]) -> list[str]:
    """Return list without consecutive duplicates, preserving order."""
    out: list[str] = []
    last = None
    for s in items:
        if s != last:
            out.append(s)
            last = s
    return out


def push_step(title: str) -> None:
    """Append a step title to the in-memory buffer with a rolling window."""
    steps = _steps_var.get()
    if steps is None:
        steps = []
        _steps_var.set(steps)
    steps.append(title)
    if len(steps) > STEP_BUFFER:
        del steps[:-STEP_BUFFER]


@contextmanager
def step(title: str) -> Generator[None]:
    """Context manager that records a step title while the block runs."""
    push_step(title)
    try:
        yield
    finally:
        pass


def stepped(
    title: str | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that records a step when the function is called."""

    def deco(fn: Callable[..., Any]) -> Callable[..., Any]:
        name = title or fn.__name__

        @wraps(fn)
        def wrap(*args: Any, **kwargs: Any) -> Any:
            push_step(name)
            return fn(*args, **kwargs)

        return wrap

    return deco


def get_steps() -> list[str]:
    """Return a copy of the current steps buffer."""
    steps = _steps_var.get()
    return list(steps) if steps else []


def _filter_exclude(steps: list[str], exclude_prefixes: list[str]) -> list[str]:
    """Return steps excluding those whose text starts
    with any of the prefixes."""
    if not exclude_prefixes:
        return steps
    return [
        s for s in steps if not any(s.startswith(p) for p in exclude_prefixes)
    ]


def _looks_like_locator(s: str | None) -> bool:
    """Heuristic check whether a string resembles a locator."""
    if not s:
        return False
    s = s.strip()
    return s.startswith(("css selector=", "//", ".//", "#", ".")) or (
        "[data-qaid" in s or "data-qa-id" in s
    )


def _first_arg_text(step: str) -> str | None:
    """Extract first argument as text from a call-like step string."""
    try:
        left_paren = step.index("(")
        right_paren = step.rindex(")")
        args = step[left_paren + 1 : right_paren]
    except ValueError:
        return None
    first = args.split(",")[0].strip()
    if (first.startswith('"') and first.endswith('"')) or (
        first.startswith("'") and first.endswith("'")
    ):
        first = first[1:-1]
    return first or None


def _extract_locator(step: str) -> str | None:
    """Extract a locator string from a step line."""
    first = _first_arg_text(step)
    if _looks_like_locator(first):
        return first
    for s in re.findall(r'["\']([^"\']+)["\']', step):
        if _looks_like_locator(s):
            return s
    m = re.search(r"css selector=([^\s,)]+)", step)
    if m:
        cand = f"css selector={m.group(1)}"
        if _looks_like_locator(cand):
            return cand
    m = re.search(r'\[(?:data-qaid|data-qa-id)=["\'][^"\']+["\'][^\]]*\]', step)
    if m and _looks_like_locator(m.group(0)):
        return m.group(0)
    return None


def _collect_recent_locators() -> list[str]:
    """Collect the last distinct locators from the buffer, limited
    by LOCATORS_TO_SHOW."""
    all_steps = get_steps()
    if not all_steps:
        return []
    steps = _filter_exclude(all_steps, STEPS_EXCLUDE)
    want = max(1, int(LOCATORS_TO_SHOW))
    rev: list[str] = []
    for s in reversed(steps):
        loc = _extract_locator(s)
        if not loc:
            continue
        if rev and loc == rev[-1]:
            continue
        rev.append(loc)
        if len(rev) >= want:
            break
    return list(reversed(rev))


def _format_actions_chain(
    context_prefix: list[str] | None = None,
) -> str | None:
    """Return a single chain string from context locators and recent
    step locators."""
    parts: list[str] = []
    if context_prefix:
        parts.extend(context_prefix)
    parts.extend(_collect_recent_locators())
    parts = _dedup_consecutive(parts)
    if not parts:
        return None
    return " → ".join(parts)


def _read_source_line(path: str, lineno: int, max_len: int) -> str | None:
    """Read and trim a specific line from file."""
    try:
        with Path(path).open(encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, start=1):
                if i == lineno:
                    s = line.rstrip("\n\r").replace("\t", "    ").strip()
                    if max_len > 0 and len(s) > max_len:
                        s = s[: max_len - 1] + "…"
                    return s
    except Exception:
        return None
    return None


def build_digest(
    driver: Any,
    *,
    title: str,
    locator: str | None = None,
    condition: str | None = None,
    timeout: float | None = None,
    wait_seconds: float | None = None,
    css_for_probe: str | None = None,
    artifacts: list[str] | None = None,
    console_tail: str | None = None,
    origin: tuple[str | None, int | None] | None = None,
    context_prefix: list[str] | None = None,
) -> str:
    """
    Build a compact failure message:

      {emoji} {title} — {seconds:.1f}s — Locator: {locator}
      — Actions: <context + steps>
      ↳ at <file:line>
        <source>
      ↳ locator at <file:line>
    """
    _ = _sections_enabled()
    if wait_seconds is None and timeout is not None:
        wait_seconds = timeout

    head = f"{FAIL_EMOJI} {title}"
    if wait_seconds is not None:
        head += f" — {wait_seconds:.1f}s"
    if locator:
        head += f" — Locator: {locator}"

    blocks: list[str] = [head]

    actions = _format_actions_chain(context_prefix)
    if actions:
        blocks.append("— Actions: " + actions)

    if SHOW_CALLSITE:
        cs = _user_callsite()
        if cs:
            abs_path, line_no = cs
            rel = _rel(abs_path)
            lines = [f"↳ at {rel}:{line_no}"]
            if SHOW_CALLSITE_CODELINE:
                src = _read_source_line(abs_path, line_no, CALLSITE_CODE_MAXLEN)
                if src:
                    lines.append(" " * CALLSITE_CODE_INDENT + src)
            blocks.append("\n".join(lines))

    if origin and origin[0]:
        blocks.append(f"↳ locator at {_rel(origin[0])}:{origin[1] or '?'}")

    return "\n" + "\n\n".join(blocks)
