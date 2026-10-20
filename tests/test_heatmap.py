"""Regression coverage for the BuridanHeatmap day-range generation.

The heatmap component in ``components/ui/heatmap.py`` embeds an inline JS
string (``BURIDAN_HEATMAP_JS``) whose ``getAllDays`` helper builds the list
of days between ``start_date`` and ``end_date``. Commit ``bede445`` ("fix:
heatmap in safari bug") added an infinite-loop safety guard of
``while (curr <= endD && safety++ < 1500)`` as the *sole* iteration
condition, which silently capped any date range longer than ~4.1 years
(1500 days) at 1500 entries: the chart rendered as a plausible-looking but
truncated grid, missing the final year+ of cells (and their month labels)
with no error, warning, or documentation.

The fix keeps the per-iteration ``safety`` guard (Safari infinite-loop
protection) but wraps it in an outer ``while (curr <= endD)`` loop so the
guard becomes a per-chunk cap rather than a total range cap.

These tests pin the fix with both static source-shape assertions and a
Node.js runtime harness that evaluates the *real* ``getAllDays`` source
extracted from ``heatmap.py`` against multi-year ranges (the case the demo
examples never exercise — every in-repo example uses a ≤ 1-year range).
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).parent.parent
HEATMAP_SOURCE = ROOT_DIR / "components" / "ui" / "heatmap.py"

# Per-chunk iteration guard carried over from the Safari fix (commit bede445).
# Kept as a constant so the runtime harness assertions stay in lock-step with
# the value actually embedded in ``getAllDays``.
PER_CHUNK_CAP = 1500

# Expected calendar-day counts for the runtime-harness date ranges. These are
# the spec: e.g. 2020-01-01..2025-01-01 is exactly 1828 days, so the heatmap
# MUST render 1828 cells for that range — pre-fix it rendered PER_CHUNK_CAP.
FIVE_YEAR_DAYS = 1828
TEN_YEAR_DAYS = 3654
ONE_YEAR_DAYS = 365
LEAP_YEAR_DAYS = 366
DST_SPAN_DAYS = 11


def _heatmap_js() -> str:
    """Return the inline JS string literal embedded in ``heatmap.py``."""
    text = HEATMAP_SOURCE.read_text(encoding="utf-8")
    match = re.search(r'BURIDAN_HEATMAP_JS\s*=\s*"""', text)
    assert match, "BURIDAN_HEATMAP_JS literal not found in heatmap.py"
    start = match.end()
    end = text.index('"""', start)
    return text[start:end]


def _extract_function(name: str) -> str:
    """Return the full source of a top-level JS ``function name(...) { ... }``.

    Brace-matched extraction stays valid even if the body later grows inner
    brace blocks (e.g. the nested ``while`` loop in ``getAllDays``).
    """
    source = _heatmap_js()
    start = source.index(f"function {name}(")
    open_brace = source.index("{", start)
    depth = 0
    for idx in range(open_brace, len(source)):
        char = source[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[start : idx + 1]
    msg = f"unterminated function {name} in heatmap.py"
    raise AssertionError(msg)


def _get_all_days_source() -> str:
    """Return ``getAllDays`` plus the helpers it calls, in source order.

    The runtime harness evaluates this standalone; function declarations are
    hoisted in JS so order is not load-bearing, but emitting them in source
    order keeps failure diagnostics readable.
    """
    return "\n".join(
        _extract_function(name) for name in ("formatDate", "parseDate", "getAllDays")
    )


# ---------------------------------------------------------------------------
# Static source-shape assertions
# ---------------------------------------------------------------------------


def test_get_all_days_preserves_isnan_date_guard() -> None:
    """The Safari hardening that rejects invalid date inputs must remain."""
    body = _extract_function("getAllDays")
    assert re.search(
        r"isNaN\(\s*curr\.getTime\(\)\s*\)\s*\|\|\s*isNaN\(\s*endD\.getTime\(\)\s*\)",
        body,
    ), "getAllDays must guard against invalid start/end dates (Safari crash fix)."


def test_get_all_days_does_not_silently_cap_range() -> None:
    """The ``safety++ < 1500`` guard must not be the sole iteration condition.

    Before the fix, ``while (curr <= endD && safety++ < 1500)`` was the only
    loop, so any range longer than 1500 days was silently truncated. The fix
    wraps the guarded loop in an outer ``while (curr <= endD)`` so the
    per-chunk safety guard can never become a total range cap.
    """
    body = _extract_function("getAllDays")

    # The outer "while (curr <= endD)" loop must be present, so the helper
    # keeps consuming 1500-day chunks until curr passes endD.
    assert body.count("while (curr <= endD)") >= 1, (
        "getAllDays must keep consuming the range in an outer loop until "
        "curr passes endD; the per-chunk safety guard alone silently "
        "truncates ranges longer than 1500 days."
    )

    # The per-iteration safety guard must still be present — it is the
    # Safari infinite-loop protection from bede445 and must not be removed.
    assert re.search(r"safety\+\+\s*<\s*1500", body), (
        "getAllDays must retain the per-chunk 1500-iteration safety guard."
    )

    # The progress guard must be present to prevent the outer loop from
    # spinning forever if a chunk somehow makes no progress.
    assert re.search(r"curr\.getTime\(\)\s*===\s*before", body), (
        "getAllDays must detect a stuck cursor between chunks and break, "
        "otherwise the per-chunk guard could turn the outer loop into an "
        "infinite loop."
    )

    # The buggy single-loop shape must NOT reappear: a `while` whose
    # condition ANDs `curr <= endD` with `safety++ < 1500` as the only loop
    # would silently truncate. The fix has the guarded loop *nested inside*
    # an outer `while (curr <= endD)`, so the guarded condition appears
    # exactly once and the bare condition also appears exactly once.
    guarded = len(
        re.findall(
            r"while\s*\(\s*curr\s*<=\s*endD\s*&&\s*safety\+\+\s*<\s*1500\s*\)",
            body,
        ),
    )
    bare = body.count("while (curr <= endD)")
    assert guarded == 1, f"expected exactly one guarded inner loop, found {guarded}."
    assert bare == 1, (
        f"expected exactly one bare outer `while (curr <= endD)` loop, found {bare}."
    )


def test_safari_hardening_in_other_helpers_is_preserved() -> None:
    """Regression guard for the rest of the Safari fix from commit bede445.

    ``getAllDays`` is one of several helpers hardened in that commit; the
    fix must not regress the others.
    """
    source = _heatmap_js()
    assert "Number.isFinite(firstDow)" in source, (
        "padToWeekStart must keep the Number.isFinite guard on firstDow."
    )
    assert "week.slice().reverse()" in source, (
        "getMonthLabel must keep week.slice().reverse() (Safari spread sensitivity)."
    )
    assert re.search(r"data\.reduce\(\s*\(\s*max\s*,\s*d\s*\)\s*=>", source), (
        "maxValue must keep the data.reduce form (Safari Math.max spread limit)."
    )
    assert "padding.concat(days)" in source, (
        "padToWeekStart must keep padding.concat(days) (Safari spread sensitivity)."
    )


# ---------------------------------------------------------------------------
# Runtime harness — evaluates the real getAllDays in Node.js
# ---------------------------------------------------------------------------


def test_get_all_days_renders_full_multi_year_range() -> None:
    """The real ``getAllDays`` must render every day of a multi-year range.

    This is the core regression: pre-fix, ``getAllDays("2020-01-01",
    "2025-01-01")`` returned exactly 1500 days ending at "2024-02-08"; the
    final ~11 months silently vanished. Post-fix it must return all 1828
    days ending at "2025-01-01" with no gaps.

    Also exercises boundary cases that pin the per-chunk guard semantics:
    ranges of exactly 1500 days, 1501 days (the first day the old cap
    would drop), and 3654 days (>2 chunks, proving the outer loop iterates
    more than once); plus happy-path (1-year / leap-year / single-day),
    reversed range, invalid-date, and DST-spanning ranges.
    Preconditions: Node.js on PATH (skipped, not failed, when absent —
    following the ``test_toc_scrollspy.py`` precedent so this test never
    blocks the ``uv run pytest`` gate in a Node-less environment).
    """
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required to run the getAllDays runtime harness")
    assert node is not None

    js = _RUNTIME_HARNESS.replace("__GET_ALL_DAYS_SRC__", _get_all_days_source())
    result = subprocess.run(
        [node, "-e", js],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 0, (
        f"runtime harness failed:\nstdout={result.stdout}\nstderr={result.stderr}"
    )
    assert result.stderr.strip() == "", f"unexpected stderr:\n{result.stderr}"

    payload = json.loads(result.stdout)

    # ── core regression: 5-year range ──────────────────────────────────
    five_year = payload["five_year"]
    assert five_year["length"] == FIVE_YEAR_DAYS, (
        f"5-year range must render all {FIVE_YEAR_DAYS} days, "
        f"got {five_year['length']} (pre-fix cap returned {PER_CHUNK_CAP})."
    )
    assert five_year["first"] == "2020-01-01"
    assert five_year["last"] == "2025-01-01", (
        f"5-year range must end on end_date, got {five_year['last']} "
        f"(pre-fix ended on 2024-02-08)."
    )
    assert payload["five_year_gaps"] == 0, (
        "5-year day list must be contiguous (no missing days between chunks)."
    )

    # ── per-chunk boundaries ───────────────────────────────────────────
    assert payload["exactly_1500"]["length"] == PER_CHUNK_CAP, (
        f"a {PER_CHUNK_CAP}-day range must render all {PER_CHUNK_CAP} days "
        f"(boundary, single chunk)."
    )
    assert payload["one_over_cap"]["length"] == PER_CHUNK_CAP + 1, (
        f"a {PER_CHUNK_CAP + 1}-day range must render all {PER_CHUNK_CAP + 1} "
        f"days; pre-fix returned {PER_CHUNK_CAP}."
    )
    assert payload["one_over_cap"]["last"] == "2024-02-09"

    # ── multi-chunk (>2 chunks) ────────────────────────────────────────
    three_chunks = payload["three_chunks"]
    assert three_chunks["length"] == TEN_YEAR_DAYS, (
        f"10-year range must render all {TEN_YEAR_DAYS} days (needs 3 chunks "
        f"of {PER_CHUNK_CAP}), got {three_chunks['length']}."
    )
    assert three_chunks["first"] == "2015-01-01"
    assert three_chunks["last"] == "2025-01-01"

    # ── happy paths (mirrors the in-repo example ranges) ───────────────
    assert payload["one_year"]["length"] == ONE_YEAR_DAYS
    assert payload["one_year"]["first"] == "2025-01-01"
    assert payload["one_year"]["last"] == "2025-12-31"
    assert payload["leap_year"]["length"] == LEAP_YEAR_DAYS

    # ── edge cases ─────────────────────────────────────────────────────
    single = payload["single_day"]
    assert single["length"] == 1
    assert single["first"] == "2025-06-15"
    assert single["last"] == "2025-06-15"

    assert payload["reversed_range"]["length"] == 0, (
        "start > end must yield an empty day list, not an error."
    )
    assert payload["invalid_start"]["length"] == 0, (
        "invalid start_date must yield an empty day list (Safari guard)."
    )
    assert payload["invalid_end"]["length"] == 0, (
        "invalid end_date must yield an empty day list (Safari guard)."
    )

    # ── DST: count is by calendar day, not by 24h periods ──────────────
    dst = payload["dst_span"]
    assert dst["length"] == DST_SPAN_DAYS, (
        f"range spanning US spring-forward (2025-03-09) must still count "
        f"{DST_SPAN_DAYS} calendar days, got {dst['length']}."
    )
    assert dst["first"] == "2025-03-05"
    assert dst["last"] == "2025-03-15"


_RUNTIME_HARNESS = r"""
__GET_ALL_DAYS_SRC__

function daysBetween(start, end) {
  const days = getAllDays(start, end);
  return {
    length: days.length,
    first: days.length > 0 ? days[0] : null,
    last: days.length > 0 ? days[days.length - 1] : null,
  };
}

const fiveYear = getAllDays("2020-01-01", "2025-01-01");
let gaps = 0;
for (let i = 1; i < fiveYear.length; i++) {
  const prev = new Date(fiveYear[i - 1] + "T00:00:00");
  const curr = new Date(fiveYear[i] + "T00:00:00");
  const diffDays = Math.round((curr.getTime() - prev.getTime()) / 86400000);
  if (diffDays !== 1) gaps++;
}

const result = {
  five_year: daysBetween("2020-01-01", "2025-01-01"),
  five_year_gaps: gaps,
  exactly_1500: daysBetween("2020-01-01", "2024-02-08"),
  one_over_cap: daysBetween("2020-01-01", "2024-02-09"),
  three_chunks: daysBetween("2015-01-01", "2025-01-01"),
  one_year: daysBetween("2025-01-01", "2025-12-31"),
  leap_year: daysBetween("2024-01-01", "2024-12-31"),
  single_day: daysBetween("2025-06-15", "2025-06-15"),
  reversed_range: daysBetween("2025-12-31", "2025-01-01"),
  invalid_start: daysBetween("not-a-date", "2025-01-01"),
  invalid_end: daysBetween("2025-01-01", "not-a-date"),
  dst_span: daysBetween("2025-03-05", "2025-03-15"),
};

console.log(JSON.stringify(result));
"""
