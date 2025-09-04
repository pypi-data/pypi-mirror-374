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


if __name__ == "__main__":
    unittest.main()
