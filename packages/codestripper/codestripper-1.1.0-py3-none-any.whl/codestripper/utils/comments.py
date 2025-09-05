from dataclasses import dataclass
from typing import Optional, Dict


@dataclass(frozen=True)
class Comment:
    open: str
    close: Optional[str] = None

comments_mapping: Dict[str, Comment] = {
    ".java": Comment("//"),
    ".cs": Comment("//"),
    ".js": Comment("//"),
    ".php": Comment("//"),
    ".swift": Comment("//"),
    ".xml": Comment("<!--", "-->"),
    ".tex": Comment("%"),
    ".m": Comment("%"),
    ".sql": Comment("--"),
    ".lua": Comment("--"),
    ".ml": Comment("(*", "*)"),
    ".r": Comment("#"),
    ".py": Comment("#"),
    ".ps1": Comment("#"),
    ".rb": Comment("#")
}