from typing import Optional

from codestripper.tags.tag import SingleTag, TagData


class AddTag(SingleTag):
    regex = r'cs:add:(.*)?'

    def __init__(self, data: TagData) -> None:
        super().__init__(data)

    def execute(self, content: str) -> Optional[str]:
        return self.leading_characters + self.parameter
