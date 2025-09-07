from .base import Command, Content
from ...exceptions import InvalidInput


def dialog(message, height=15, title="Message", width=100, **kwargs):
    """Display a graphical feedback box to the user. Note that the ``dialog`` command must be available.

    :param message: The message to be displayed.
    :type message: str

    :param height: The height of the dialog box.
    :type height: int

    :param title: The title displayed.
    :type title: str

    :param width: The width of the dialog box.
    :type width: int

    """
    statement = list()
    statement.append("dialog --clear")
    statement.append('--backtitle "%s"' % title)
    statement.append('--msgbox "%s" %s %s;' % (message, height, width))
    statement.append("clear;")

    return Command(" ".join(statement), **kwargs)


def echo(message, **kwargs):
    """Display a message.

    :param message: The message to be displayed.
    :type message: str

    """
    return Command('echo "%s"' % message, **kwargs)


def explain(message, heading=None, **kwargs):
    """Create an explanation for documentation.

    :param message: The message to be displayed.
    :type message: str

    :param heading: Optional heading for the output.
    :type heading: str

    """
    return Content("explain", message=message, heading=heading, **kwargs)


def mattermost(message, url=None, **kwargs):
    """Send a message to a Mattermost channel.

    :param message: The message to be sent.
    :type message: str

    :param url: The URL of the Mattermost channel.
    :type url: str

    """
    if url is None:
        raise InvalidInput("mattermost command requires a url parameter.")

    statement = list()
    statement.append("curl -X POST -H 'Content-type: application/json' --data")
    statement.append('\'{"text": "%s"}\'' % message)
    statement.append(url)

    return Command(" ".join(statement), **kwargs)


def screenshot(image, caption=None, css=None, height=None, width=None, **kwargs):
    """Create a screenshot for documentation.

    :param image: The URL or path to the image file.
    :type image: str

    :param caption: A caption for the image.
    :type caption: str

    :param css: CSS classes to be applied to the image tag.
    :type css: str

    :param height: The maximum height of the image.
    :type height: int

    :param width: The maximum widht of the image.
    :type width: int

    """
    return Content("screenshot", caption=caption, css=css, height=height, image=image, width=width, **kwargs)


def slack(message, url=None, **kwargs):
    """Send a message to Slack.

    :param message: The message to be displayed.
    :type message: str

    :param url: The channel URL.
    :type url: str

    """
    if url is None:
        raise InvalidInput("Slack command requires a url parameter.")

    statement = list()
    statement.append("curl -X POST -H 'Content-type: application/json' --data")
    statement.append('\'{"text": "%s"}\'' % message)
    statement.append(url)

    return Command(" ".join(statement), **kwargs)


def twist(message, title="Notice", url=None, **kwargs):
    """Send a message to Twist.

    :param message: The message to be displayed.
    :type message: str

    :param title: A title for the message.
    :type title: str

    :param url: The channel URL.
    :type url: str

    """
    if url is None:
        raise InvalidInput("Twist command requires a url parameter.")

    statement = list()
    statement.append("curl -X POST -H 'Content-type: application/json' --data")
    statement.append('\'{"content": "%s", "title": "%s"}\'' % (message, title))
    statement.append(url)

    return Command(" ".join(statement), **kwargs)


MESSAGE_MAPPINGS = {
    'dialog': dialog,
    'echo': echo,
    'explain': explain,
    'mattermost': mattermost,
    'screenshot': screenshot,
    'slack': slack,
    'twist': twist,
}
