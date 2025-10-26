from enum import Enum

class TextType(Enum):
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    TEXT = "text"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    def __init__(self, text, text_type, url):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        #check if two TextNodes are the same, making sure to check the type of the other object
        if not isinstance(other, TextNode):
            return False
        return(
            self.text == other.text and
            self.text_type == other.text_type and
            self.url == other.url
        )
        
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"
        #returns string representation