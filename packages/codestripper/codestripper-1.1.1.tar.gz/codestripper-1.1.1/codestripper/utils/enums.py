import enum


class UnexpectedInputOptions(enum.Enum):
    FAIL = "fail",
    IGNORE = "ignore",
    INCLUDE = "include"