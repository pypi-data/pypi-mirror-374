from codestripper.tags.tag import Tag, RangeTag, SingleTag


class InvalidTagError(Exception):
    """Raise if the tag is not valid"""
    def __init__(self, tag: Tag):
        self.tag = tag

    @property
    def line_number(self) -> int:
        if isinstance(self.tag, SingleTag):
            return self.tag.data.line_number
        return -1

    @property
    def message(self) -> str:
        return self.__str__()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Tag {self.tag.__class__.__name__} is invalid"


class TokenizerError(Exception):

    def __init__(self, tag: Tag, message: str):
        self.tag = tag
        self.message = message

    @property
    def line_number(self) -> int:
        if isinstance(self.tag, SingleTag):
            return self.tag.data.line_number
        else:
            return -1
