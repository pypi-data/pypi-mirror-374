import re
from typing import Union

from codestripper.tags.tag import RangeTag, RangeOpenTag, RangeCloseTag, TagData, Tag


class UncommentOpenTag(RangeOpenTag):
    regex = r'cs:uncomment:start(.*)?'

    def __init__(self, data: TagData) -> None:
        super().__init__(UncommentRangeTag, data)


class UncommentCloseTag(RangeCloseTag):
    regex = 'cs:uncomment:end(.*)?'

    def __init__(self, data: TagData) -> None:
        super().__init__(UncommentRangeTag, data)


class UncommentRangeTag(RangeTag):
    regex = None

    def __init__(self, open_tag: RangeOpenTag, close_tag: RangeCloseTag):
        super().__init__(open_tag, close_tag)

    def execute(self, content: str) -> Union[str, None]:
        if UncommentRangeTag.regex is None:
            whitespace = r"(?P<whitespace>\s*)"
            UncommentRangeTag.regex = re.compile(f"{whitespace}{self.open_tag.data.comment.open}")
        range = content[self.start:self.end]
        replacement = UncommentRangeTag.regex.sub(r"\g<whitespace>", range)
        return replacement
