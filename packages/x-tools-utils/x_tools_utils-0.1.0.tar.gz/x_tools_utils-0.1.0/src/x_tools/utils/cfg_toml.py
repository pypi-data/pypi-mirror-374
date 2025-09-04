""" Get ignored messages from x_pylint_cfg.py """

import pathlib
from enum import StrEnum

import tomli
from pydantic import BaseModel
from tabulate import tabulate

from x_tools.utils.models.tp_file_path import TpFilePath
from x_tools.pylint.models.tp_msg_id import TpMsgId
from x_tools.pylint.models.mdl_reports import TToml
from x_tools.utils.utils import lg_dbg, TLg


class TTomlKey(StrEnum):
    """ Pole z Toml-cfg-souboru """
    PYLINT  = 'pylint'
    MSG_IDS = 'msg_ids'
    MSG_AT  = 'msg_at'
    IGNORE_PATHS = 'ignore_paths'
    LEGACY  = 'legacy'
    TO_DO   = 'todo'
    OK      = 'ok'


class TMsgAt(BaseModel):
    """ Pole v x_tools_cfg.toml ignore_msgs """
    file    : TpFilePath
    obj     : str
    msg_id  : TpMsgId
    comment : str


class TomlCfgs:
    """ Načtení hodnot z konfiguračních souborů: x_tools_cfg.toml """

    def __init__(self, path: TpFilePath, only_msgids: TToml = None, ignore_msgids: TToml = None):

        self.toml_cfg = None

        self.only_msgids_flags = only_msgids if only_msgids else set()
        self.ignore_msgids_flags = ignore_msgids if ignore_msgids else set()

        self.ignore_paths: set[TpFilePath] = set()
        self.only_msgids = set()     # <- bude naplněno zprávami z Toml sekcí dle only_msgids
        self.ignore_msgids = set()   # <- bude naplněno zprávami z Toml sekcí dle ignore_msgids

        self.msg_at: list[TMsgAt] = []
        self.msg_at_set = set()
        self.err = ''                        # Error message, if any
        self.toml_hdr: list[str] = []          # řádky vytištěné následně do reportu s informací jaké msgid byli ignorovány atd.

        self.import_x_lint_cfg(path)
        lg_dbg('TomlCfgs.__init__() - End', flags=TLg.HDR)


    @staticmethod
    def return_non_empty_lines(txt: str) -> list[str]:
        """ Returns non-empty lines from the multiline cfg-string after removing comments """
        ret_lns = []
        for cfg_ln in txt.splitlines():
            cfg_ln = (cfg_ln + ' #').split('#', 1)[0].strip()  # Remove comments and strip whitespace
            if cfg_ln:
                ret_lns.append( TpMsgId(cfg_ln) )
        lg_dbg( f'return_non_empty_lines() - {ret_lns}')
        return ret_lns


    def get_lns_from_section(self, keys: list[TTomlKey]) -> list[str]:
        """ Returns non-empty lines from cfg-toml sub-section """
        toml_sub_section = self.toml_cfg
        for key in keys:
            if not key in toml_sub_section:
                return []
            toml_sub_section = toml_sub_section[key]
        return self.return_non_empty_lines(toml_sub_section)


    def import_x_lint_cfg(self, path: TpFilePath):
        """ Gets all files from TpFilePath with name `x_tools_cfg.toml` and puts all data to self.WrnMsgs """
        lg_dbg(f"import_x_lint_cfg( path={path} ) - Start", flags=TLg.HDR)

        base = pathlib.Path(str(path)).resolve()
        if not base.exists() or not base.is_dir():
            self.err = f'ERROR: Path does not exist: {base}'
            return

        cfg_paths: list[TpFilePath] = []
        for p in base.rglob("x_tools_cfg.toml"):
            if p.is_file():
                cfg_f_path = TpFilePath(str(p.resolve()).replace("\\", "/"))
                cfg_paths.append( cfg_f_path )
                lg_dbg('Cfg file:', cfg_f_path)


        for fl in cfg_paths:
            fp = pathlib.Path(str(fl)).resolve()
            with open(fp, mode="rb") as fr:

                self.toml_cfg = tomli.load(fr)
                lg_dbg( 'tomli_cfg:', self.toml_cfg ) #, flags=TLg.FORCE )
                # tomli_cfg:
                #     {'pylint':
                #         {'ignore_paths': ' controlledSide.py\n   controlledSideCommon.py\n   controlledSideRabbit.py\n   libs/\n ',
                #          'msg_ids': {
                #              'legacy': ' Cabc\n   Cxyz\n ',
                #              'todo'  : ' Cabc\n   Cxyz\n ',
                #              'ok'    : ' C0321\n  C0410\n '
                #              },
                #          'msg_in': {
                #              'ok'    : ' x_tools/linter/main.py      |          | W0611   | unused-import - Unused WrnMsgFields imported from linter.models\n
                #                          x_tools/linter/src/utils.py | set_dgb  | W0603   | global-statement - Using the global statement\n
                #                          x_tools/linter/src/utils.py | FrozenClass | R0903 | too-few-public-methods - Too few public methods (1/2)\n
                #                        '
                #         }
                #     }

                # --- TOML: ignore_paths ---
                toml_pylint_ignore_path = self.get_lns_from_section([TTomlKey.PYLINT, TTomlKey.IGNORE_PATHS])
                [ self.ignore_paths.add(TpFilePath(cfg_ln))  for cfg_ln  in toml_pylint_ignore_path ]

                # --- TOML: msg_ids ---
                toml_pylint_msgids_legacy = self.get_lns_from_section([TTomlKey.PYLINT, TTomlKey.MSG_IDS, TTomlKey.LEGACY])
                toml_pylint_msgids_todo   = self.get_lns_from_section([TTomlKey.PYLINT, TTomlKey.MSG_IDS, TTomlKey.TO_DO])
                toml_pylint_msgids_ok     = self.get_lns_from_section([TTomlKey.PYLINT, TTomlKey.MSG_IDS, TTomlKey.OK])
                if TToml.LEGACY_IDS in self.only_msgids_flags:   self.only_msgids.update(   toml_pylint_msgids_legacy )
                if TToml.TODO_IDS   in self.only_msgids_flags:   self.only_msgids.update(   toml_pylint_msgids_todo   )
                if TToml.OK_IDS     in self.only_msgids_flags:   self.only_msgids.update(   toml_pylint_msgids_ok     )
                if TToml.LEGACY_IDS in self.ignore_msgids_flags: self.ignore_msgids.update( toml_pylint_msgids_legacy )
                if TToml.TODO_IDS   in self.ignore_msgids_flags: self.ignore_msgids.update( toml_pylint_msgids_todo   )
                if TToml.OK_IDS     in self.ignore_msgids_flags: self.ignore_msgids.update( toml_pylint_msgids_ok     )
                self.toml_hdr.append( f'-------- TOML CFG FILE: {str(fl)} --------')
                self.toml_hdr.append( f'ignore_paths  : {self.ignore_paths}')
                self.toml_hdr.append( f'only_msgids   : { [str(f) for f in self.only_msgids_flags] }  => '
                                      + ( str(self.only_msgids) if self.only_msgids else '{}' )
                                      )
                self.toml_hdr.append( f'ignore_msgids : { [str(f) for f in self.ignore_msgids_flags] }  => '
                                      + ( str(self.ignore_msgids) if self.ignore_msgids else '{}' )
                                      )


                # --- TOML: msg_at (soubor, objekt, msgid) ---
                toml_pylint_msgat_ok     = self.get_lns_from_section([TTomlKey.PYLINT, TTomlKey.MSG_AT, TTomlKey.OK])

                ignore_msgs = toml_pylint_msgat_ok
                # dbg( 'vv--- [pylint][ignore_msgs] ---vv'  )
                # dbg( ignore_msgs )
                for cfg_ln in ignore_msgs:
                    if cfg_ln.count('|') == 2:
                        cfg_ln = cfg_ln + ' | ' # line bez komentáře ... přidej prázdné pole na konec

                    if cfg_ln.count('|') >= 3:
                        f_path, f_obj, f_msg_id, *f_comment = [x.strip() for x in cfg_ln.split('|')]
                        f_comment = ' : '.join(f_comment)   # join the comment parts back together, and in it replace '| ' with ' : '
                        # dbg( f'{f_path:<50} {f_obj:<30} {f_msg_id:<8} {f_comment}' )
                        self.msg_at.append(
                            TMsgAt(file=TpFilePath(f_path), obj=f_obj, msg_id=TpMsgId(f_msg_id), comment=f_comment)
                            )

        # --- set_wrn_msgs_search ... dict with key: (msg_wrn.file, msg_wrn.obj, msg_wrn.msg_id) ---
        for msg_cfg in self.msg_at:
            self.msg_at_set.add((msg_cfg.file, msg_cfg.obj, msg_cfg.msg_id))
        # [ dbg( itm )  for  itm  in  self.__MsgCfgsSearch.items() ]

        lg_dbg('import_x_lint_cfg() - End', flags=TLg.HDR)


    def report(self):
        """ Vytisknutí načtených hodnot ... spíše pro debug účely """
        print( '\n\nvv=== [pylint][ignore_msgs] ===vv\n'  )
        report_hdrs = list(TMsgAt.model_fields.keys())
        msg_wrns = [msg_wrn.model_dump() for msg_wrn in self.msg_at]
        rows = [ [msg_wrn[key] for key in report_hdrs] for msg_wrn in msg_wrns]  # Convert list of dictionaries to a list of lists (values only)
        print( tabulate(rows, headers=report_hdrs, tablefmt='simple') )  # tablefmt='grid'


    def in_ignored_msgs(self, file, obj, msg_id):
        return (file, obj, msg_id) in self.msg_at_set


    def ignore_path(self, path: TpFilePath):
        """ If path is in self.ignore_paths then return True """
        return any( ignore_path in path  for ignore_path  in self.ignore_paths)
