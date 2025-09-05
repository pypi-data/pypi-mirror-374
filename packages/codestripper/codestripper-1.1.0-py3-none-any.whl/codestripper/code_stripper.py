import logging
import os.path
import shutil
from pathlib import Path
from typing import Union, Iterable, List, Optional

from codestripper.errors import InvalidTagError, TokenizerError
from codestripper.tags import IgnoreFileError
from codestripper.tags.tag import Tag, RangeTag
from codestripper.tokenizer import Tokenizer
from codestripper.utils import get_working_directory
from codestripper.utils.comments import comments_mapping, Comment
from codestripper.utils.enums import UnexpectedInputOptions

logger = logging.getLogger("codestripper")


def strip_files(files: Iterable[str], working_directory: Union[str, None] = None, * ,comments: Optional[List[str]] = None,
                output: Union[Path, str] = "out", dry_run: bool = False, fail_on_error: bool = False,
                binary: UnexpectedInputOptions = UnexpectedInputOptions.FAIL, unknown_extension: UnexpectedInputOptions = UnexpectedInputOptions.FAIL) -> List[str]:

    if comments is not None:
        for comment in comments:
            parts = comment.split(":")
            if len(parts) == 2:
                comments_mapping[parts[0]] = Comment(parts[1])
            else:
                comments_mapping[parts[0]] = Comment(parts[1], parts[2])

    cwd = get_working_directory(working_directory)
    out = os.path.join(os.getcwd(), output)
    if os.path.isdir(out):
        shutil.rmtree(out)
    stripped_files: List[str] = []
    has_errors: bool = False
    for file in files:
        try:
            with open(os.path.join(cwd, file), 'r') as handle:
                content = handle.read()
        except UnicodeDecodeError as e:
            if binary == UnexpectedInputOptions.FAIL:
                raise e
            elif binary == UnexpectedInputOptions.IGNORE:
                logger.info(f"Ignoring binary file: '{file}'")
                continue
            else:
                path = os.path.join(out, file)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                shutil.copy2(os.path.join(cwd, file), path)
                stripped_files.append(file)
                continue
        if content is not None:
            stripped = ""
            try:
                _, file_extension = os.path.splitext(file)
                file_extension = file_extension.lower()
                if not file_extension in comments_mapping:
                    if unknown_extension == UnexpectedInputOptions.FAIL:
                        logger.error(f"Unknown extension: '{file_extension}', "
                                 f"please specify which comment to use for this file extension.")
                        has_errors = True
                        break
                    elif unknown_extension == UnexpectedInputOptions.IGNORE:
                        logger.info(f"Unknown extension: '{file_extension}' ignored")
                        continue
                    else:
                        # Keep the complete content
                        stripped = content
                else:
                    com = comments_mapping[file_extension]
                    stripped = CodeStripper(content, com).strip()
            except IgnoreFileError:
                logger.info(f"File '{file}' is ignored, because of ignore tag")
                continue
            except (TokenizerError, InvalidTagError) as ex:
                has_errors = True
                message = f"{file}:{ex.line_number}: {ex.message}"
                logger.error(message)
                continue
            stripped_files.append(file)
            if dry_run:
                logger.info(stripped)
            else:
                path = os.path.join(out, file)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w+') as handle:
                    handle.write(stripped)
    if has_errors and fail_on_error:
        raise Exception("There were errors stripping some files, see log for details")
    return stripped_files


class CodeStripper:

    def __init__(self, content: str, comment: Comment) -> None:
        self.content = content
        self.comment = comment

    def strip(self) -> str:

        if self.content is not None:
            tokenizer = Tokenizer(self.content, self.comment)
            tags = tokenizer.tokenize()
            self.__traverse(tags)
        return self.content

    def __traverse(self, tags: List[Tag], offset=0) -> int:
        old_offset = offset
        if len(tags) == 0:
            return offset - old_offset
        for tag in tags:
            tag.offset = offset
            if isinstance(tag, RangeTag):
                changed = self.__traverse(tag.tags, offset)
                tag.inset = changed
                delta = self.__execute_tag(tag)
                tag.open_tag.offset = offset
                offset += self.__execute_tag(tag.open_tag)
                offset += delta + changed
                tag.close_tag.offset = offset
                offset += self.__execute_tag(tag.close_tag)
            else:
                offset += self.__execute_tag(tag)
        return offset - old_offset

    def __execute_tag(self, tag: Tag):
        if not tag.is_valid():
            raise InvalidTagError(tag)
        processed = tag.execute(self.content)
        old_size = tag.end - tag.start
        new_size = len(processed) if processed is not None else 0
        before = self.content[:tag.start]

        # Return of None means remove the complete line
        if processed is None:
            # Check if there is a newline at the end of the line
            # The tags don't capture newlines, so manually make sure to remove
            last_char = self.content[tag.end:tag.end+1]
            if "\n" in last_char:
                after = self.content[tag.end+1:]
                old_size += 1
            else:
                after = self.content[tag.end:]
            self.content = before + after
            return -1 * old_size
        else:
            after = self.content[tag.end:]
            self.content = before + processed + after
            return new_size - old_size
