# core/formatter.py
"""
Improved formatter utilities for CodeScribe AI.

Features:
- truncate long file summaries safely (doesn't chop inside fenced code blocks)
- optional HTML <details> folding (useful for preview pages)
- option to truncate by lines or by characters
- closes unclosed code fences after truncation
"""

from typing import Dict, Optional, Tuple


def _find_safe_cut(lines: list[str], max_lines: int) -> Tuple[int, bool]:
    """
    Helper function (internal).
    Finds a safe cut index (<= max_lines) that does not split a fenced code block.

    Note: called by collapse_long_sections below.
    Returns (cut_index, was_truncated)
    """
    in_code = False
    fence_delim = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        # detect start/end of fenced code block (``` or ```lang)
        if stripped.startswith("```"):
            # toggle code block
            if not in_code:
                in_code = True
                fence_delim = stripped  # store delim to ensure consistent close
            else:
                in_code = False
                fence_delim = None
        # if we've reached the max_lines and we're not inside a code fence, cut here
        if i + 1 == max_lines and not in_code:
            return (i + 1, True)
        # if i+1 reaches max_lines but inside code block, find the next fence closure
        if i + 1 >= max_lines and in_code:
            # find next fence close index
            for j in range(i + 1, len(lines)):
                if lines[j].strip().startswith("```"):
                    return (j + 1, True)  # cut after closing fence
            # if no closing fence found, cut at max_lines and mark truncated
            return (max_lines, True)
    # never needed to truncate
    return (len(lines), False)


def _close_open_fence(short_lines: list[str]) -> None:
    """
    Helper function (internal).
    If truncated content leaves an unclosed fenced code block, append a closing fence.
    Modifies short_lines in-place.
    """
    in_code = False
    for line in short_lines:
        if line.strip().startswith("```"):
            in_code = not in_code
    if in_code:
        # add a closing fence to avoid broken rendering
        short_lines.append("```")


def collapse_long_sections(
    summary_dict: Dict[str, str],
    max_lines: int = 300,
    max_chars: Optional[int] = None,
    use_html: bool = False,
    fallback_truncate_text: str = "... [Content truncated]",
) -> Dict[str, str]:
    """
    Truncate/collapse long file summaries safely.

    Args:
        summary_dict: mapping file path -> summary string.
        max_lines: primary limit in lines (if longer, will try to cut safely).
        max_chars: optional absolute character cap per summary (applied after line truncation).
        use_html: if True, wrap full summary inside an HTML <details> block and show a short preview;
                  if False, append a short truncation note.
        fallback_truncate_text: text to append when not using HTML.

    Returns:
        dict: updated mapping file path -> (possibly collapsed) markdown string.

    Notes:
    - This function tries NOT to split fenced code blocks (```), and will close an unclosed fence if needed.
    - Called by run_pipeline.py after collecting file summaries (so that README previews stay compact).
    """
    collapsed: Dict[str, str] = {}

    for filepath, summary in summary_dict.items():
        if not summary:
            collapsed[filepath] = summary
            continue

        lines = summary.rstrip("\n").splitlines()

        # if length within limit and chars limit not exceeded -> keep original
        if len(lines) <= max_lines and (max_chars is None or len(summary) <= max_chars):
            collapsed[filepath] = summary
            continue

        # find a safe line cut that doesn't break fenced code sections
        cut_idx, was_truncated = _find_safe_cut(lines, max_lines)

        # produce short preview lines and ensure code fences are closed
        short_lines = lines[:cut_idx]
        _close_open_fence(short_lines)
        short_preview = "\n".join(short_lines).rstrip()

        # apply char-level cap if requested
        if max_chars is not None and len(short_preview) > max_chars:
            short_preview = short_preview[: max_chars - 3].rstrip() + "..."

        # build final representation
        if use_html:
            # Put the full content inside <details> for HTML preview (good for web preview)
            safe_full = summary.rstrip()
            # ensure code fences in full also closed
            full_lines = safe_full.splitlines()
            _close_open_fence(full_lines)
            safe_full = "\n".join(full_lines)
            details = (
                f"{short_preview}\n\n"
                f"<details>\n<summary>Show more</summary>\n\n{safe_full}\n\n</details>"
            )
            collapsed[filepath] = details
        else:
            # Markdown/plain text fallback — show preview + truncation note
            collapsed[filepath] = f"{short_preview}\n\n{fallback_truncate_text}"

    return collapsed
