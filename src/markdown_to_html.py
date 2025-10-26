# src/markdown_to_html.py
import re
from src.htmlnode import ParentNode
from src.textnode import TextNode, TextType
from src.markdown import (
    markdown_to_blocks,
    block_to_block_type,
    text_to_textnodes,
    BlockType,
)
from src.converters import text_node_to_html_node  # use the real converter


def text_to_children(text):
    return [text_node_to_html_node(n) for n in text_to_textnodes(text)]


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []

    for block in blocks:
        block_type = block_to_block_type(block)

        if block_type == BlockType.HEADING:
            heading_level = len(block.split(" ")[0])
            text = block[heading_level + 1 :].strip()
            children.append(ParentNode(f"h{heading_level}", text_to_children(text)))

        elif block_type == BlockType.CODE:
            code_text = block.replace("```", "").strip()
            children.append(
                ParentNode("pre", [text_node_to_html_node(TextNode(code_text, TextType.CODE, None))])
            )

        elif block_type == BlockType.QUOTE:
            # support lines like "> quote"
            quote_lines = []
            for line in block.split("\n"):
                s = line.lstrip()
                quote_lines.append(s[2:] if s.startswith("> ") else s)
            quote_text = " ".join([q for q in quote_lines if q.strip()])
            children.append(ParentNode("blockquote", text_to_children(quote_text)))

        elif block_type == BlockType.UNORDERED_LIST:
            li_nodes = []
            for raw in block.split("\n"):
                item = raw.strip()
                if not item:
                    continue
                # accept "- foo", "* foo", "+ foo", allow extra spaces
                m = re.match(r"^[\-\*\+]\s+(.*)$", item)
                text = (m.group(1) if m else re.sub(r"^[\-\*\+]\s*", "", item)).strip()
                if text:
                    li_nodes.append(ParentNode("li", text_to_children(text)))
            children.append(ParentNode("ul", li_nodes))

        elif block_type == BlockType.ORDERED_LIST:
            li_nodes = []
            for raw in block.split("\n"):
                item = raw.strip()
                if not item:
                    continue
                # prefer "1. text", tolerate "1.text", spaces, indentation
                m = re.match(r"^\s*\d+\.\s*(.*)$", item)
                if m:
                    text = m.group(1).strip()
                else:
                    # fallback: strip leading digits + dot and optional space
                    text = re.sub(r"^\s*\d+\.\s*", "", item).strip()
                if text:
                    li_nodes.append(ParentNode("li", text_to_children(text)))
            children.append(ParentNode("ol", li_nodes))

        else:
            children.append(ParentNode("p", text_to_children(block)))

    return ParentNode("div", children)
