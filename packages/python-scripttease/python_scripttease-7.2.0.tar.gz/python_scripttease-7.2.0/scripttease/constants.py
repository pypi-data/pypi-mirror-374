EXCLUDED_KWARGS = [
    "cd",
    "comment",
    "condition",
    "environments",
    "name",
    "prefix",
    "register",
    "shell",
    "stop",
    "sudo",
    "tags",
]

LOGGER_NAME = "script-tease"


class PROFILE:
    """Supported operating system profiles."""

    CENTOS = "centos"
    DEBIAN = "debian"
    FEDORA = "fedora"
    REDHAT = "redhat"
    POP_OS = "pop_os"
    UBUNTU = "ubuntu"
