import unittest
from rich.text import Text
from meow.__main__ import wrap_paragraph, blockquote, render_markdown


class TestMarkdownRenderer(unittest.TestCase):
    def test_wrap_paragraph_basic(self):
        text = Text("Hello world, this is a test.")
        wrapped = wrap_paragraph(text, width=10)
        self.assertIsInstance(wrapped, Text)
        self.assertIn("Hello", wrapped.plain)

    def test_blockquote_prefix(self):
        text = Text("Blockquote content")
        bq = blockquote(text, width=20)
        self.assertIsInstance(bq, Text)
        self.assertTrue(bq.plain.startswith("❙ "))

    def test_render_markdown_heading(self):
        md_text = "# Heading\n\nSome text"
        output = render_markdown(md_text)
        self.assertIsInstance(output, list)
        self.assertTrue(any("Heading" in chunk.plain for chunk in output))

    def test_render_markdown_list(self):
        md_text = "- Item 1\n- Item 2"
        output = render_markdown(md_text)
        self.assertTrue(any("•" in chunk.plain for chunk in output))

    def test_render_markdown_inline(self):
        md_text = "This is `code` and a [link](https://example.com)"
        output = render_markdown(md_text)
        self.assertTrue(any("code" in chunk.plain for chunk in output))
        self.assertTrue(any("link" in chunk.plain for chunk in output))

    def test_render_markdown_blockquote(self):
        md_text = "> A blockquote line"
        output = render_markdown(md_text)
        self.assertTrue(any("A blockquote line" in chunk.plain for chunk in output))

    def test_render_markdown_skip_yaml(self):
        md_text = "---\nname: Test\n---\n# Heading\nContent"
        output = render_markdown(md_text)
        # YAML frontmatter should not appear
        self.assertFalse(any("name: Test" in chunk.plain for chunk in output))
        self.assertTrue(any("Heading" in chunk.plain for chunk in output))

    def test_render_markdown_code_block_indent(self):
        md_text = "```\nprint('hello')\n```"
        output = render_markdown(md_text)
        # Look for a line starting with exactly two spaces
        code_lines = [chunk.plain for chunk in output if "print" in chunk.plain]
        self.assertTrue(any(line.startswith("  ") for line in code_lines))

    def test_render_markdown_bold_and_italic(self):
        md_text = (
            "This has *italic* and **bold** text, "
            "and ***both*** styles together."
        )
        output = render_markdown(md_text)

        italics_found = False
        bold_found = False
        both_found = False

        for chunk in output:
            for (start, end, style) in chunk.spans:
                if "italic" in style and "bold" not in style:
                    if "italic" in chunk.plain[start:end]:
                        italics_found = True
                if "bold" in style and "italic" not in style:
                    if "bold" in chunk.plain[start:end]:
                        bold_found = True
                if "bold" in style and "italic" in style:
                    if "both" in chunk.plain[start:end]:
                        both_found = True

        self.assertTrue(italics_found, "Italic text not styled correctly")
        self.assertTrue(bold_found, "Bold text not styled correctly")
        self.assertTrue(both_found, "Bold+italic text not styled correctly")

    def test_render_markdown_inline_code_style(self):
        md_text = "Here is some `inline` code."
        output = render_markdown(md_text)

        code_found = False
        for chunk in output:
            for (start, end, style) in chunk.spans:
                if "red" in style and "black" in style:
                    if "inline" in chunk.plain[start:end]:
                        code_found = True

        self.assertTrue(code_found, "Inline code not styled red on black")

if __name__ == "__main__":
    unittest.main()
