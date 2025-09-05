import re
from typing import Optional, Set, Dict, Callable, List, Pattern, Tuple, Type

from codestripper.errors import TokenizerError
from codestripper.tags import ReplaceTag, UncommentCloseTag, IgnoreFileTag, RemoveOpenTag, RemoveCloseTag, \
    UncommentOpenTag, LegacyOpenTag, LegacyCloseTag, RemoveTag, AddTag
from codestripper.tags.tag import SingleTag, Tag, RangeOpenTag, RangeCloseTag, RangeTag, TagData
from codestripper.utils.comments import Comment

default_tags: Set[Type[SingleTag]] = {
    IgnoreFileTag,
    RemoveOpenTag,
    RemoveCloseTag,
    RemoveTag,
    ReplaceTag,
    UncommentOpenTag,
    UncommentCloseTag,
    LegacyOpenTag,
    LegacyCloseTag,
    AddTag
}

# Type for lambda that creates a tag based on the type
CreateTagLambda = Callable[[TagData], SingleTag]
# Type for mapping of name to CreateTagLambda
CreateTagMapping = Dict[str, CreateTagLambda]


def calculate_mappings(tags: Set[Type[SingleTag]], comment: Comment) -> Tuple[CreateTagMapping, Pattern]:
    strings = [r"(?P<newline>\n)"]
    mappings = {}
    for tag in tags:
        name = f"{tag.__name__}"
        mappings[name] = lambda data, constructor=tag: constructor(data)
        reg = f"(?P<{name}>{re.escape(comment.open)}{tag.regex})"
        if comment.close is not None:
            reg += re.escape(comment.close)
        strings.append(reg)
    regex = re.compile("|".join(strings), flags=re.MULTILINE)
    return mappings, regex  # type: ignore


class Tokenizer:
    mapping_cache: Dict[str, Tuple[CreateTagMapping, Pattern]] = {}
    mappings: CreateTagMapping = {}
    regex: Pattern = re.compile("")
    comment: Comment

    def __init__(self, content: str, comment: Comment) -> None:
        self.content = content
        self.ordered_tags: List[Tag] = []
        self.open_stack: List[RangeOpenTag] = []
        self.range_stack: Dict[int, Optional[List[Tag]]] = {}
        Tokenizer.comment = comment
        if not str(comment) in Tokenizer.mapping_cache:
            Tokenizer.mapping_cache[str(comment)] = calculate_mappings(default_tags, comment)
        Tokenizer.mappings = Tokenizer.mapping_cache[str(comment)][0]
        Tokenizer.regex = Tokenizer.mapping_cache[str(comment)][1]
        self.group_count = self.regex.groups

    def tokenize(self) -> List[Tag]:
        line_number = 1
        line_start = 0
        for match in self.regex.finditer(self.content):
            kind = match.lastgroup
            # Parameter should directly follow the encompassing regex
            # Type ignore: we have a match, so we must have a lastindex
            param_index = match.lastindex + 1  # type: ignore
            parameter: Optional[Tuple[int, int]] = None
            if param_index < len(match.regs):
                parameter = match.regs[param_index]

            line_end = match.end()
            if kind == "newline":
                line_number += 1
                line_start = line_end
            elif kind is None:
                continue  # All groups should be named
            else:
                data = self.__create_tag_data(self.content, line_number, line_start, line_end, match, parameter)
                tag = Tokenizer.mappings[kind](data)
                self.__handle_tag(tag)
        if len(self.open_stack) != 0:
            t = self.open_stack[0]
            raise TokenizerError(t, f"There is still an unclosed {t.__class__.__name__} tag!")
        # if len(self.range_stack) != 0:
        #     raise TokenizerError(self.range_stack[0][0], f"")
        return self.ordered_tags

    def __add_range_stack(self, index: int, tag: Tag) -> None:
        if index not in self.range_stack:
            self.range_stack[index] = []
        self.range_stack[index].append(tag)  # type: ignore

    def __handle_tag(self, tag: Tag) -> None:
        if isinstance(tag, RangeOpenTag):
            self.open_stack.append(tag)
        elif isinstance(tag, RangeCloseTag):
            if len(self.open_stack) == 0:
                raise TokenizerError(tag, f"Cannot close tag {tag.__class__.__name__}, as there is no matching open tag")
            range_open = self.open_stack.pop()
            if range_open.parent != tag.parent:
                raise TokenizerError(tag, f"Cannot match closing tag: {tag.__class__.__name__} to open tag: {range_open.__class__.__name__}")
            range_tag: RangeTag = tag.parent(range_open, tag)
            index = len(self.open_stack)
            embedded = self.range_stack.pop(index + 1, None)
            if embedded is not None:
                range_tag.add_tags(embedded)

            if index > 0:
                self.__add_range_stack(index, range_tag)
            else:
                self.ordered_tags.append(range_tag)
        else:
            index: int = len(self.open_stack)  # type: ignore
            if index > 0:
                self.__add_range_stack(index, tag)
            else:
                self.ordered_tags.append(tag)

    def __create_tag_data(self, content: str, line_number: int, line_start: int, line_end: int,
                          match: re.Match, param: Optional[Tuple[int, int]] = None) -> TagData:
        # All matches are based on column values in the complete content
        # We want the match to be an index in the current line
        line = content[line_start:line_end]
        command_start = match.start() - line_start
        command_end = match.end() - line_start
        if param is not None and param[0] != -1 and param[1] != -1:
            parameter_start = param[0] - line_start
            parameter_end = param[1] - line_start
        else:
            parameter_start = command_end
            parameter_end = command_start
        parameter = line[parameter_start:parameter_end]
        return TagData(line=line,
                       line_number=line_number,
                       line_start=line_start,
                       line_end=line_end,
                       regex_start=command_start,
                       regex_end=command_end,
                       parameter_start=parameter_start,
                       parameter_end=parameter_end,
                       comment=self.comment)
