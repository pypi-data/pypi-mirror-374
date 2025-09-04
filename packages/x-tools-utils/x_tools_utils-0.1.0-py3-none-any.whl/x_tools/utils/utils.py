""" Small Utility Functions """

import sys, collections, inspect
from enum import IntFlag, auto


__DBG = False    # Global debug flag to control debug output

class TLg(IntFlag):
    """ Seznam reportů z kterých je možné si vybrat k tisku """
    def _generate_next_value_(name, start, count, last_values):      # noqa # pylint: disable=no-self-argument
        return 1 << count  # powers of two
    NONE        = auto()     # No flags set
    FORCE       = auto()     # Force printing even if __DBG is False
    HDR         = auto()     # Print as header
    EXIT        = auto()     # sys.exit() after printing debug message
    ASK_TO_EXIT = auto()     # ask to exit


def set_dgb(dbg: bool) -> None:
    global __DBG
    __DBG = dbg


def print_to_str(*args, **kwargs) -> str:
    """ Acts as a built-in print but returns a string instead of printing to stdout. """
    sep = kwargs.get('sep', ' ')
    # end = kwargs.get('end',  '\n')
    return sep.join(map(str, args))  # + end


def add_hdr(txt: str):
    return f'--- {txt} ---'


def lg_dbg(*args, flags:TLg = TLg.NONE, **kwargs):   # f: int = 0, hdr:int = 0, ext: int = 0,  ):
    """ Debug function to print debug messages.
        f ~ force - if True, forces printing even if __DBG is False.
        exit: 0 - don't extit, 1 - ask, 9 - exit without asking.    # ToDo
    """

    frame = inspect.currentframe().f_back
    file_path = frame.f_code.co_filename
    line_no = frame.f_lineno

    if __DBG or (TLg.FORCE in flags) or (TLg.EXIT in flags):
        txt = print_to_str(*args, **kwargs)
        if TLg.HDR in flags:
            print()
            txt = add_hdr(txt)

        pth_ln = f'{file_path}:{line_no}'
        print(f'{pth_ln:<60}', txt)

    if TLg.EXIT in flags:
        print( '  *-->>', '#'*10, 'lg.exit !!!', "#"*10 )
        print( '\n' )
        sys.exit()



def collect(*items) -> list:
    """ Collects all items into a list, flattening 1st level iterables. """
    res = []
    for item in items:
        if isinstance(item, collections.abc.Iterable) and not isinstance(item, str):
            res.extend(item)
            # res.extend(collect(*item))  # for flattening deeper levels
        else:
            res.append(item)
    return res
