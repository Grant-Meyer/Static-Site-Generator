from src.textnode import TextNode, TextType
from enum import Enum
import re

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def block_to_block_type(block):
    stripped = block.strip()
    
    if stripped.startswith("#"):
        heading_level = len(stripped.split(" ")[0])
        if 1 <= heading_level <= 6:
            return BlockType.HEADING

    if stripped.startswith("```") and stripped.endswith("```"):
        return BlockType.CODE

    if all(line.strip().startswith(">") for line in stripped.splitlines()):
        return BlockType.QUOTE

    if all(line.strip().startswith("-") for line in stripped.splitlines()):
        return BlockType.UNORDERED_LIST

    if all(line.strip().split(".", 1)[0].isdigit() and line.strip().split(".", 1)[1].startswith(" ")
           for line in stripped.splitlines() if "." in line):
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH
 
def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for node in old_nodes:
        if not isinstance(node, TextNode) or node.text_type != TextType.TEXT:
            # If it's not plain text, just append it as-is
            new_nodes.append(node)
            continue
        # Split the text of the node by the delimiter

        segments = node.text.split(delimiter)
        

        if len(segments) % 2 == 0:
            raise ValueError(f"Unmatched delimiter '{delimiter}' in: {node.text}")
        
        for i, segment in enumerate(segments):
            if segment == "":
                continue  # Skip empty segments
            if i % 2 == 0:
                # Even index segments are plain text
                new_nodes.append(TextNode(segment, TextType.TEXT, None))
            else:
                # Odd index segments are formatted text
                new_nodes.append(TextNode(segment, text_type, None))

    return new_nodes


def extract_markdown_images(text):
    return re.findall(r"!\[([^\]]+)\]\(([^\)]+)\)", text)

def extract_markdown_links(text):
    return re.findall(r"(?<!\!)\[([^\]]+)\]\(([^\)]+)\)", text)

def split_nodes_image(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if not isinstance(node, TextNode) or node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        matches = list(re.finditer(r"!\[([^\]]+)\]\(([^)]+)\)", node.text))
        if not matches:
            new_nodes.append(node)
            continue

        last_index = 0
        for match in matches:
            start, end = match.span()
            alt_text, url = match.groups()

            if start > last_index:
                new_nodes.append(TextNode(node.text[last_index:start], TextType.TEXT, None))
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            last_index = end

        if last_index < len(node.text):
            new_nodes.append(TextNode(node.text[last_index:], TextType.TEXT, None))

    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if not isinstance(node, TextNode) or node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        matches = list(re.finditer(r"(?<!\!)\[([^\]]+)\]\(([^)]+)\)", node.text))
        if not matches:
            new_nodes.append(node)
            continue

        last_index = 0
        for match in matches:
            start, end = match.span()
            link_text, url = match.groups()

            if start > last_index:
                new_nodes.append(TextNode(node.text[last_index:start], TextType.TEXT, None))
            new_nodes.append(TextNode(link_text, TextType.LINK, url))
            last_index = end

        if last_index < len(node.text):
            new_nodes.append(TextNode(node.text[last_index:], TextType.TEXT, None))

    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT, None)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes

def markdown_to_blocks(markdown):
    lines = markdown.split("\n\n")
    return [block.strip() for block in lines if block.strip()]

def extract_title(markdown: str) -> str:
    """
    Extracts the first level-1 heading ('# ') from markdown text.
    Raises ValueError if none is found.
    """
    for line in markdown.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    raise ValueError("Markdown does not contain a top-level heading (# ).")


