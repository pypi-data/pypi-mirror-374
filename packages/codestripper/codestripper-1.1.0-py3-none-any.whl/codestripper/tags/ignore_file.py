from typing import Union

from codestripper.tags.errors import IgnoreFileError
from codestripper.tags.tag import SingleTag, TagData


class IgnoreFileTag(SingleTag):
    regex = r'cs:ignore'

    def __init__(self, data: TagData) -> None:
        super().__init__(data)

    def is_valid(self) -> bool:
        return self.data.line_number == 1

    def execute(self, content: str) -> Union[str, None]:
        raise IgnoreFileError(self)
