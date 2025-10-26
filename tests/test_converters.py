import unittest
from src.htmlnode import *
from src.textnode import *
from src.converters import *

def test_text(self):
    node = TextNode("This is a text node", TextType.TEXT)
    html_node = text_node_to_html_node(node)
    self.assertEqual(html_node.tag, None)
    self.assertEqual(html_node.value, "This is a text node")
if __name__ == "__main__":
    unittest.main()
