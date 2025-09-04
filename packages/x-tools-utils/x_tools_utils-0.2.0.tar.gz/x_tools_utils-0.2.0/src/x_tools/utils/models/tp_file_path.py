""" FilePath type representing FS-dir/file-path  and utility functions. """
from typing import NewType                # Optional, Any, TypeAlias

from ..utils import lg_dbg, collect, TLg



TpFilePath = NewType('TpFilePath', str)     # Ex: 'C:/__My/__PRJ_Work/AdmTool_Srv_2/api_management'


def split_path_to_dir_and_name(file_path: TpFilePath) -> tuple[TpFilePath, TpFilePath]:
    """ Split a package path into directory and name. """
    dir_ph, file_ph = [TpFilePath(ph) for ph in str(file_path).rsplit('/', 1)]
    return dir_ph, file_ph


def get_path(*paths) -> TpFilePath:
    """ Join and normalize multiple path parts into a SINGLE path TpFilePath with Lnx / as separator. """
    path_ret = '/'.join( str(p) for p in paths )
    while '\\' in path_ret:
        path_ret = path_ret.replace('\\', '/')
    while '//' in path_ret:
        path_ret = path_ret.replace('//', '/')
    ret = TpFilePath(path_ret)
    lg_dbg( f'get_path( {str(paths)} ) -> {str(ret)}' )
    return ret


def get_paths(*paths) -> list[TpFilePath]:
    """ Join and normalize multiple paths into a LIST of TpFilePath with Lnx / as separator. """
    all_paths = collect( *paths )
    ret =  [get_path(p) for p in all_paths]
    lg_dbg( f'get_path( {str(paths)} ) ->  {ret}', flags=TLg.HDR )
    return ret
