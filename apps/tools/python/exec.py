# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import os
import sys
import traceback
import contextlib
from io import StringIO
from threading import Thread


@contextlib.contextmanager
def stdoutIO(stdout=None):
    """
    function to get the print output in an exec statement.
    https://stackoverflow.com/a/3906390/6396981
    """
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


def secure_builtins(obj):
    to_delete = ['quit', 'exit', 'system']
    for func in to_delete:
        try:
            del obj.__builtins__[func]
        except:
            pass
    return obj


def sandbox(to_exec):
    """
    function to exec the user python scripts.
    https://repl.it/@mat1/sandbox-exec#main.py
    https://trypython.jcubic.pl/ (TODO: TRY THIS)

    :param `to_exec` is string to execute.
    :return {'success': <bool>, 'result': <None>}

    >>> to_exec = '''
        print('hi')
        '''
    >>> sandbox(to_exec)
    'hi'
    """
    response = {'success': False, 'result': None}
    allowed_methods = ['math', 'random']
    sys_modules = dict(sys.modules)

    try:
        code = compile(to_exec, 'sandbox', 'exec')
    except Exception as error:
        # Error Compiling
        cass_name = type(error).__name__
        message = str(error)
        error_message = '%s: %s' % (cass_name, message)
        response.update({'result': error_message})

    else:
        with stdoutIO() as s:
            try:
                sandbox_global = dict(globals())
                del sandbox_global['Thread']
                fix_modules = ['os', 'sys']

                for i in fix_modules:
                    sandbox_global[i] = secure_builtins(sandbox_global[i])

                # FIXME: when I uncomment this, it will causing an error
                # to another case, because `del` in sys.modules
                # to_delete = []
                # for module in sys_modules:
                #     if module not in allowed_methods:
                #         del sys.modules[module]

                exec(code, sandbox_global, {})
                result = s.getvalue().strip() or None
                response.update({'success': True, 'result': result})

                # re-update the original modules
                sys.modules = sys_modules

                return response

            except Exception as error:
                # print('error executing:', error, type(error), sys.exc_info()[-1].tb_lineno)
                # error_message = str(traceback.format_exc(chain=False))
                # response.update({'result': error_message})

                cass_name = type(error).__name__
                message = str(error)
                error_message = '%s: %s' % (cass_name, message)
                response.update({'result': error_message})

    # re-update the original modules
    sys.modules = sys_modules

    return response
