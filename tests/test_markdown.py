import unittest
from src.textnode import TextNode, TextType
from src.markdown_to_html import markdown_to_html_node
from src.markdown import (
    BlockType,
    split_nodes_delimiter, 
    extract_markdown_images, 
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
    markdown_to_blocks,
    block_to_block_type,
    extract_title
)

class TestSplitNodesDelimiter(unittest.TestCase):
    def test_block_to_block_type_heading(self):
        from src.markdown import block_to_block_type
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Deep heading"), BlockType.HEADING)

def test_block_to_block_type_code_block(self):
    block = """```
code
```"""
    self.assertEqual(block_to_block_type(block), BlockType.CODE)


    def test_block_to_block_type_quote(self):
        self.assertEqual(block_to_block_type("> quoted\n> again"), BlockType.QUOTE)

    def test_block_to_block_type_unordered_list(self):
        self.assertEqual(block_to_block_type("- item\n- item"), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_ordered_list(self):
        self.assertEqual(block_to_block_type("1. item\n2. item"), BlockType.ORDERED_LIST)

    def test_block_to_block_type_paragraph(self):
        self.assertEqual(block_to_block_type("Just a plain paragraph."), BlockType.PARAGRAPH)
    
    
    def test_basic_code_split(self):
        node = TextNode("This is a `code` block", TextType.TEXT, None)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is a ", TextType.TEXT, None),
            TextNode("code", TextType.CODE, None),
            TextNode(" block", TextType.TEXT, None),
        ]
        self.assertEqual(result, expected)

    def test_multiple_inline_elements(self):
        node = TextNode("Say `hi` and `bye`", TextType.TEXT, None)
        result = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("Say ", TextType.TEXT, None),
            TextNode("hi", TextType.CODE, None),
            TextNode(" and ", TextType.TEXT, None),
            TextNode("bye", TextType.CODE, None),
        ]
        self.assertEqual(result, expected)

    def test_no_delimiter(self):
        node = TextNode("No formatting here", TextType.TEXT, None)
        result = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertEqual(result, [node])

    def test_ignores_non_text_type(self):
        node = TextNode("Don't split me", TextType.BOLD, None)
        result = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertEqual(result, [node])

    def test_unmatched_delimiter_raises(self):
        node = TextNode("Unmatched *delimiter", TextType.TEXT, None)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "*", TextType.ITALIC)

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        expected = [("image", "https://i.imgur.com/zjjcJKZ.png")]
        self.assertListEqual(matches, expected)

    def test_extract_multiple_markdown_images(self):
        text = "![one](url1) and ![two](url2)"
        matches = extract_markdown_images(text)
        expected = [("one", "url1"), ("two", "url2")]
        self.assertListEqual(matches, expected)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is a [link](https://example.com) in text."
        )
        expected = [("link", "https://example.com")]
        self.assertListEqual(matches, expected)

    def test_extract_multiple_markdown_links(self):
        text = "[Boot](https://boot.dev) and [YouTube](https://youtube.com)"
        matches = extract_markdown_links(text)
        expected = [("Boot", "https://boot.dev"), ("YouTube", "https://youtube.com")]
        self.assertListEqual(matches, expected)

    def test_does_not_confuse_image_with_link(self):
        text = "![alt](https://image.url) and [text](https://link.url)"
        images = extract_markdown_images(text)
        links = extract_markdown_links(text)
        self.assertListEqual(images, [("alt", "https://image.url")])
        self.assertListEqual(links, [("text", "https://link.url")])

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT, None
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT, None),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT, None),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_links(self):
        node = TextNode(
            "Here's a [link](https://example.com) in the sentence.",
            TextType.TEXT, None
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Here's a ", TextType.TEXT, None),
            TextNode("link", TextType.LINK, "https://example.com"),
            TextNode(" in the sentence.", TextType.TEXT, None),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_links_with_multiple(self):
        node = TextNode(
            "[one](url1) and [two](url2) with [three](url3)",
            TextType.TEXT,
            None
        )
        result = split_nodes_link([node])
        expected = [
            TextNode("one", TextType.LINK, "url1"),
            TextNode(" and ", TextType.TEXT, None),
            TextNode("two", TextType.LINK, "url2"),
            TextNode(" with ", TextType.TEXT, None),
            TextNode("three", TextType.LINK, "url3"),
        ]
        self.assertListEqual(result, expected)

    def test_text_to_textnodes(self):
        input_text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        expected = [
            TextNode("This is ", TextType.TEXT, None),
            TextNode("text", TextType.BOLD, None),
            TextNode(" with an ", TextType.TEXT, None),
            TextNode("italic", TextType.ITALIC, None),
            TextNode(" word and a ", TextType.TEXT, None),
            TextNode("code block", TextType.CODE, None),
            TextNode(" and an ", TextType.TEXT, None),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT, None),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(text_to_textnodes(input_text), expected)

    def test_text_to_textnodes_empty_string(self):
        self.assertListEqual(text_to_textnodes(""), [])

    def test_text_to_textnodes_plain_text(self):
        text = "Just a boring sentence."
        expected = [TextNode("Just a boring sentence.", TextType.TEXT, None)]
        self.assertListEqual(text_to_textnodes(text), expected)

    def test_text_to_textnodes_adjacent_formatting(self):
        text = "**bold**_italic_`code`"
        expected = [
            TextNode("bold", TextType.BOLD, None),
            TextNode("italic", TextType.ITALIC, None),
            TextNode("code", TextType.CODE, None),
        ]
        self.assertListEqual(text_to_textnodes(text), expected)

    def test_markdown_to_blocks(self):
        md = """# This is a heading

This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items"""

        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "# This is a heading",
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )
    def test_markdown_to_blocks_with_leading_and_trailing_whitespace(self):
        md = """


Paragraph one



Paragraph two


"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            ["Paragraph one", "Paragraph two"]
        )

    def test_markdown_to_blocks_single_line(self):
        md = "Just a single line."
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Just a single line."])
    
    def test_markdown_to_html_node_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here


This is another paragraph with _italic_ text and `code` here
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
        html,
"<div><p>This is <b>bolded</b> paragraph\ntext in a p\ntag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>"
)


    def test_markdown_to_html_node_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
        html,
"<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff</code></pre></div>"
)



class TestExtractTitle(unittest.TestCase):
    def test_simple_h1(self):
        md = "# Hello"
        self.assertEqual(extract_title(md), "Hello")

    def test_h1_trims_whitespace(self):
        md = "#   Hello world   "
        self.assertEqual(extract_title(md), "Hello world")

    def test_ignores_subheadings(self):
        md = "## Sub\n### Deep\n# Real Title"
        self.assertEqual(extract_title(md), "Real Title")

    def test_returns_first_h1_only(self):
        md = "# First\n\nSome text\n\n# Second"
        self.assertEqual(extract_title(md), "First")

    def test_indented_h1_allowed(self):
        md = "   # Indented Title"
        self.assertEqual(extract_title(md), "Indented Title")

    def test_no_h1_raises(self):
        md = "## Not top level\nSome text"
        with self.assertRaises(ValueError):
            extract_title(md)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            extract_title("")

    def test_hash_without_space_not_h1(self):
        md = "#Hello (not valid h1)\nText"
        with self.assertRaises(ValueError):
            extract_title(md)

    def test_inline_hash_not_h1(self):
        md = "Text before # Not a header"
        with self.assertRaises(ValueError):
            extract_title(md)



if __name__ == "__main__":
    unittest.main()
