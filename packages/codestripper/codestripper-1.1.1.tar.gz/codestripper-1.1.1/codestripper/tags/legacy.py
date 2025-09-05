from typing import Union

from codestripper.tags.tag import RangeTag, RangeOpenTag, RangeCloseTag, TagData


class LegacyOpenTag(RangeOpenTag):
    regex = r'Start Solution::replacewith::(.*)'

    def __init__(self, data: TagData) -> None:
        super().__init__(LegacyRangeTag, data)

    def execute(self, content: str) -> Union[str, None]:
        # Legacy command "End Solution::replacewith::" does both remove and replace
        # To support that command we need to check if we need to replace or remove
        param = self.parameter
        if len(param) > 0:
            return self.whitespace + self.parameter
        else:
            return None


class LegacyCloseTag(RangeCloseTag):
    regex = r'End Solution::replacewith::(.*)'

    def __init__(self, data: TagData) -> None:
        super().__init__(LegacyRangeTag, data)

    def execute(self, content: str) -> Union[str, None]:
        # Legacy command "End Solution::replacewith::" does both remove and replace
        # To support that command we need to check if we need to replace or remove
        param = self.parameter
        if len(param) > 0:
            return self.whitespace + self.parameter
        else:
            return None


class LegacyRangeTag(RangeTag):

    def __init__(self, open_tag: LegacyOpenTag, close_tag: LegacyCloseTag) -> None:
        super().__init__(open_tag, close_tag)

    def is_valid(self) -> bool:
        return self.end - self.start > 0

    def execute(self, content: str) -> Union[str, None]:
        # old_open_size = self.open_tag.end - self.open_tag.start
        # open = self.open_tag.execute(content, offset)
        # offset += (len(open) - old_open_size)
        return None

