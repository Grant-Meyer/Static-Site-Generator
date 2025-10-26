import unittest

from src.textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD, None)
        node2 = TextNode("This is a text node", TextType.BOLD, None)
        self.assertEqual(node, node2)

    def test_neq_text(self):
        node = TextNode("This is a text node", TextType.BOLD, None)
        node2 = TextNode("Different text", TextType.BOLD, None)
        self.assertNotEqual(node, node2)

    def test_neq_type(self):
        node = TextNode("Same text", TextType.ITALIC, None)
        node2 = TextNode("Same text", TextType.BOLD, None)
        self.assertNotEqual(node, node2)

    def test_neq_url(self):
        node = TextNode("Same text", TextType.LINK, "https://a.com")
        node2 = TextNode("Same text", TextType.LINK, "https://b.com")
        self.assertNotEqual(node, node2)

    def test_eq_with_none(self):
        node = TextNode("text", TextType.TEXT, None)
        self.assertNotEqual(node, None)

    def test_eq_with_different_type(self):
        node = TextNode("text", TextType.TEXT, None)
        self.assertNotEqual(node, "not a TextNode")

        
if __name__ == "__main__":
    unittest.main()