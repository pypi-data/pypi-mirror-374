"""
PyserSSH - A Scriptable SSH server. For more info visit https://github.com/DPSoftware-Foundation/PyserSSH
Copyright (C) 2023-present DPSoftware Foundation (MIT)

Visit https://github.com/DPSoftware-Foundation/PyserSSH

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from ..interactive import Send
from ..system.clientype import Client


def ShowCursor(client, show=True):
    """
    Shows or hides the cursor for a specific client.

    Args:
        client (Client): The client to show/hide the cursor for.
        show (bool, optional): A flag to determine whether to show or hide the cursor. Defaults to True (show cursor).
    """
    if show:
        Send(client, "\033[?25h", ln=False)  # Show cursor
    else:
        Send(client, "\033[?25l", ln=False)  # Hide cursor

def SendBell(client):
    """
    Sends a bell character (alert) to a client.

    Args:
        client (Client): The client to send the bell character to.
    """
    Send(client, "\x07", ln=False)  # Bell character (alert)
