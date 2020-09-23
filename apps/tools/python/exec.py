# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# dependency
# pip install RestrictedPython
# https://stackoverflow.com/a/63161071/6396981

from RestrictedPython import safe_builtins, compile_restricted
from RestrictedPython.Eval import default_guarded_getitem

from apps.tools.python.restricts import (_import, _getiter)


def execute_user_code(user_code, user_func, *args, **kwargs):
    """ Executed user code in restricted env
        Args:
            user_code(str) - String containing the unsafe code
            user_func(str) - Function inside user_code to execute and return value
            *args, **kwargs - arguments passed to the user function
        Return:
            Return value of the user_func
    """

    def _apply(f, *a, **kw):
        return f(*a, **kw)

    try:
        # This is the variables we allow user code to see. @result will contain return value.
        restricted_locals = {
            "result": None,
            "args": args,
            "kwargs": kwargs,
        }

        # If you want the user to be able to use some of your functions inside his code,
        # you should add this function to this dictionary.
        # By default many standard actions are disabled. Here I add _apply_ to be able to access
        # args and kwargs and _getitem_ to be able to use arrays. Just think before you add
        # something else. I am not saying you shouldn't do it. You should understand what you
        # are doing thats all.

        safe_builtins['__import__'] = _import  # Must be a part of builtins

        restricted_globals = {
            "__builtins__": safe_builtins,
            "_getitem_": default_guarded_getitem,
            "_getiter_": _getiter,
            "_apply_": _apply,
        }

        # Add another line to user code that executes @user_func
        user_code += "\nresult = {0}(*args, **kwargs)".format(user_func)

        # Compile the user code
        byte_code = compile_restricted(user_code, filename="<user_code>", mode="exec")

        # Run it
        exec(byte_code, restricted_globals, restricted_locals)

        # User code has modified result inside restricted_locals. Return it.
        return restricted_locals["result"]

    except SyntaxError as e:
        # Do whaever you want if the user has code that does not compile
        raise
    except Exception as e:
        # The code did something that is not allowed. Add some nasty punishment to the user here.
        raise
