from enum import Enum


class APP(str, Enum):
    SLACK = "slack"


class AT(str, Enum):
    BOTH = "both"
    START = "start"
    END = "end"


class ON(str, Enum):
    ALWAYS = "always"
    SUCCESS = "success"
    ERROR = "error"