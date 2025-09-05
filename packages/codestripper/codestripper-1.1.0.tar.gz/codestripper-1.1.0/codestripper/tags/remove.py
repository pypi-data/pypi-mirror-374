from codestripper.tags.tag import RangeTag, RangeOpenTag, RangeCloseTag, TagData, SingleTag


class RemoveTag(SingleTag):

    regex = r'cs:remove(?!:)(.*)?'

    def __init__(self, data: TagData):
        super().__init__(data)


class RemoveOpenTag(RangeOpenTag):
    regex = r'cs:remove:start(.*)?'

    def __init__(self, data: TagData) -> None:
        super().__init__(RemoveRangeTag, data)


class RemoveCloseTag(RangeCloseTag):
    regex = r'cs:remove:end(.*)?'

    def __init__(self, data: TagData) -> None:
        super().__init__(RemoveRangeTag, data)


class RemoveRangeTag(RangeTag):

    def __init__(self, open_tag: RemoveOpenTag, close_tag: RemoveCloseTag) -> None:
        super().__init__(open_tag, close_tag)

    def is_valid(self) -> bool:
        return self.end - self.start > 0
