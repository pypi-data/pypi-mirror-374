# -*- coding: utf-8 -*-
#
#   Copyright (C) 2024-2025
#   Rocky Bernstein <rocky@gnu.org>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Debugger class and top-level debugger functions.

This module contains the ``DebugREPL`` class
"""

import os
import sys

from term_background import is_dark_background
from typing import Any
from trepan.interfaces.user import UserInterface
from trepan.lib.default import DEBUGGER_SETTINGS

import pymathics.trepan.lib.core

from pymathics.trepan.debug_evaluation import DebugEvaluation
from pymathics.trepan.lib.sighandler import SignalManager
from pymathics.trepan.lib.core import DebuggerCore

# Default settings used here
from trepan.misc import option_set

# Set to ignore entry and exit calls to Mathics3 DebugEvaluation[]
pymathics.trepan.lib.core.IGNORE_CODE.add(DebugEvaluation.eval.__code__)

is_dark_bg = is_dark_background()

# If TREPAN_PYGMENTS_STYLE has been set, use that as the defalt.
pygments_style_from_environment = os.environ.get("TREPAN_PYGMENTS_STYLE", None)

if pygments_style_from_environment is not None:
    default_style = pygments_style_from_environment
else:
    default_style = "zenburn" if is_dark_bg else "tango"

try:
    from readline import get_line_buffer
except ImportError:

    def get_line_buffer():
        return None

    pass


class DebugREPL:
    """
    Class for a Debugger REPL.
    """

    def __init__(self, opts=None):
        """Create a debugger object. But depending on the value of
        key 'start' inside hash 'opts', we may or may not initially
        start debugging.

        See also ``Debugger.start`` and ``Debugger.stop``.
        """
        from pymathics.trepan.stacktrace import (
            eval_Stacktrace as trepan_eval_Stacktrace,
        )
        # from pymathics.trepan.tracing import (
        #     print_evaluate as trepan_print_evaluate
        # )

        self.thread = None
        self.eval_string = None
        self.settings = DEBUGGER_SETTINGS.copy()
        self.settings["events"] = {
            "Get",  # Get[]
            "SymPy",  # SymPy call
            "apply",  # Builtin function call
            "evaluate-entry",  # before evaluate()
            "evaluate-result",  # after evaluate()
            "evalMethod",  # calling a built-in evaluation
            "interrupt",  # interrupt, e.g. Ctrl-C
            # method Class.eval_xxx()
            "debugger",  # explicit call via "Debugger"
            "mpmath",  # mpmath call
        }
        self.settings["style"] = default_style

        def get_option(key: str) -> Any:
            return option_set(opts, key, DEBUGGER_SETTINGS)

        def completer(text: str, state):
            return self.complete(text, state)

        # set the instance variables that come directly from options.
        for opt in []:
            setattr(self, opt, get_option(opt))
            pass

        # How are I/O for this debugger handled? This should
        # be set before calling DebuggerCore.
        interface_opts = {
            "complete": completer,
            "debugger_name": "Mathics3 Debug",
        }

        interface = UserInterface(inp=None, opts=interface_opts)
        self.intf = [interface]

        self.core = DebuggerCore(self, {})
        self.core.add_ignore(self.core.stop)

        # When set True, we'll also suspend our debug-hook tracing.
        # This gives us a way to prevent or allow self debugging.
        self.core.trace_hook_suspend = False

        if get_option("save_sys_argv"):
            # Save the debugged program's sys.argv? We do this so that
            # when the debugged script munges these, we have a good
            # copy to use for an exec restart
            self.program_sys_argv = list(sys.argv)
        else:
            self.program_sys_argv = None
            pass

        self.sigmgr = SignalManager(self)

        # Were we requested to activate immediately?
        if get_option("activate"):
            self.core.start(get_option("start_opts"))
            pass
        return

    def complete(self, last_token: str, state: int):
        """
        In place expansion of top-level debugger command
        for `last_token`` that we are in ``state``.
        """
        if hasattr(self.core.processor, "completer"):
            string_seen = get_line_buffer() or last_token
            results = self.core.processor.completer(string_seen, state)
            return results[state]
        return

    pass


# Demo it
if __name__ == "__main__":
    dbg = DebugREPL()  # noqa
    print(dbg.settings)
    import inspect

    current_frame = inspect.currentframe()
    dbg.core.trace_dispatch(current_frame, "debugger", [])
    pass
