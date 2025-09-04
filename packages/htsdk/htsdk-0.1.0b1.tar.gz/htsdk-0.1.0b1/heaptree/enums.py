from enum import Enum


class NodeType(Enum):
    UBUNTU = "ubuntu"
    BROWSER = "browser"
    BROWSER_IDENTITY = "browser-identity"


class NodeSize(Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class OperatingSystem(Enum):
    LINUX = "linux"


class Language(Enum):
    PYTHON = "py"
    JAVASCRIPT = "js"
    TYPESCRIPT = "ts"
    CPP = "cpp"
