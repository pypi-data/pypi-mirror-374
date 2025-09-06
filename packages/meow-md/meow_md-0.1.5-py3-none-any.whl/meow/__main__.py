#!/usr/bin/env python3

import sys
from pathlib import Path
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.lexers import get_lexer_by_name
from pygments.lexers import TextLexer
from pygments.formatters import TerminalFormatter
from rich.console import Console
from rich.text import Text


console = Console(width=120)
md = MarkdownIt(
        "commonmark",
        { "breaks": True }
        ).enable("table")


HEADING_STYLES = {
        1: "bold white on blue",
        2: "bold green",
        3: "bold yellow",
        4: "bold blue",
        5: "bold magenta",
        6: "bold cyan"
        }


def wrap_paragraph(text_obj: Text, width: int = 120) -> Text:
    """Wrap a Rich Text object to specified width."""
    wrapped = Text()
    lines = []

    for line in text_obj.wrap(console, width):
        if line is not None:
            lines.append(line)

    for i, line in enumerate(lines):
        wrapped.append(line)
        # only add newlines between wrapped lines, not after the last one
        if i < len(lines) - 1:
            wrapped.append("\n")

    return wrapped


def blockquote(text_obj: Text, width: int = 120) -> Text:
    """Wrap blockquotes to start every line with a bar prefix."""
    prefix = "❙ "
    wrapped = Text()
    lines = []

    # wrap text according to available width
    for line in text_obj.wrap(console, width - len(prefix)):
        if line is not None:
            lines.append(line)

    # append each line with styled prefix
    for i, line in enumerate(lines):
        wrapped.append(prefix, style="magenta")
        wrapped.append(line)
        if i < len(lines) - 1:
            wrapped.append("\n")

    return wrapped


def strip_yaml_frontmatter(text: str) -> str:
    """Remove YAML frontmatter (--- at start and end) if present."""
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            return parts[2].lstrip("\n")
    return text


def strip_anchor_links(text: str) -> str:
    """Remove standalone HTML anchor links like <a name="foo"></a>."""
    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("<a") and stripped.endswith("</a>"):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).lstrip("\n")


def render_markdown(text: str):
    """Render Markdown text to Rich Text objects, skipping YAML frontmatter and fenced YAML blocks."""
    # remove YAML frontmatter first
    text = strip_yaml_frontmatter(text)
    text = strip_anchor_links(text)

    tokens = md.parse(text)
    output = []

    current_heading_level = None
    list_stack = []
    pending_list_marker = None
    in_blockquote = False
    in_list = False

    for token in tokens:

        # HEADINGS
        if token.type == "heading_open":
            current_heading_level = int(token.tag[1])

        elif token.type == "inline" and current_heading_level is not None:
            # extract text content from children
            content_parts = [child.content for child in token.children if child.type == "text"]
            content = "".join(content_parts)

            # skip headings that are just '---' (they were YAML frontmatter)
            if content.strip() == "---":
                current_heading_level = None
                continue

            hashes = "#" * current_heading_level
            style = HEADING_STYLES.get(current_heading_level, "bold")

            if current_heading_level == 1:
                output.append(Text(f" {content} ", style=style))
            else:
                output.append(Text(f"{hashes} {content}", style=style))
            output.append(Text())
            current_heading_level = None

        elif token.type == "heading_close":
            continue

        # CODE BLOCKS
        elif token.type == "fence":
            lang = token.info.lower().strip() if token.info else ""
            code = token.content.rstrip("\n")

            # detect YAML frontmatter
            is_yaml = (lang in ("yaml", "yml")) or code.startswith("---")
            if is_yaml:
                continue  # skip YAML completely

            try:
                if lang:
                    lexer = get_lexer_by_name(lang)
                else:
                    lexer = TextLexer()
            except Exception:
                lexer = TextLexer()

            formatter = TerminalFormatter(bg="dark")
            highlighted = highlight(code, lexer, formatter)

            # prefix each line with 2 spaces
            for line in highlighted.rstrip("\n").split("\n"):
                indented = Text("  ")
                indented.append(Text.from_ansi(line, no_wrap=True))
                output.append(indented)

            # add bottom margin
            output.append(Text())

        # LISTS
        elif token.type == "bullet_list_open":
            list_stack.append(("ul", 0))
            in_list = True
        elif token.type == "ordered_list_open":
            list_stack.append(("ol", 1))
            in_list = True

        elif token.type == "list_item_open":
            if list_stack:
                depth = len(list_stack)
                typ, num = list_stack[-1]
                indent = "  " * (depth - 1)
                if typ == "ul":
                    pending_list_marker = f"{indent}• "
                elif typ == "ol":
                    pending_list_marker = f"{indent}{num}. "
                    list_stack[-1] = (typ, num + 1)

        elif token.type == "list_item_close":
            pending_list_marker = None

        elif token.type in ("bullet_list_close", "ordered_list_close"):
            list_stack.pop()
            if not list_stack:
                in_list = False
                output.append(Text())

        # BLOCKQUOTES
        elif token.type == "blockquote_open":
            in_blockquote = True

        elif token.type == "blockquote_close":
            in_blockquote = False

        # PARAGRAPH MARKERS
        elif token.type == "paragraph_open":
            pass
        elif token.type == "paragraph_close":
            if not in_list:
                output.append(Text())

        # INLINE
        elif token.type == "inline":
            line_text = Text()

            if pending_list_marker:
                line_text.append(pending_list_marker, style="bold")

            children = token.children or []
            style_stack = []

            i = 0
            while i < len(children):
                child = children[i]

                if child.type == "text":
                    style = ""
                    if "em" in style_stack:
                        style += " italic"
                    if "strong" in style_stack:
                        style += " bold"
                    if in_blockquote:
                        style += " italic"
                    line_text.append(child.content, style=style.strip())

                elif child.type == "code_inline":
                    line_text.append(f" {child.content} ", style="red on black")

                elif child.type == "strong_open":
                    style_stack.append("strong")
                elif child.type == "strong_close":
                    style_stack.remove("strong")

                elif child.type == "em_open":
                    style_stack.append("em")
                elif child.type == "em_close":
                    style_stack.remove("em")

                elif child.type == "link_open":
                    href = child.attrs.get("href", "")
                    label = ""
                    j = i + 1
                    while j < len(children) and children[j].type != "link_close":
                        if children[j].type == "text":
                            label += children[j].content
                        j += 1

                    line_text.append(label, style="bold bright_cyan")
                    if href and href != label:
                        line_text.append(" ")
                        line_text.append(href, style="underline cyan")

                    i = j

                i += 1

            if in_blockquote:
                output.append(blockquote(line_text, console.width))
            else:
                output.append(wrap_paragraph(line_text, console.width))

    return output


def main():
    if len(sys.argv) < 2:
        print ("Usage: meow FILE.md")
        sys.exit(1)

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")

    print()

    for chunk in render_markdown(text):
        console.print(chunk)


if __name__ == "__main__":
    main()
