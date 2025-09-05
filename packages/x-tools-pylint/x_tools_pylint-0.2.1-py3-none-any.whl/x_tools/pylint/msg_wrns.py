""" Hlavní modul pro vygenerování z reportování PyLint Wrn-Msgs """

import sys, io, json
from typing import Final

from tabulate import tabulate
# --- from pylint library ---
from pylint import reporters as PyLintReporters   # noqa
from pylint.lint import pylinter as PyLinter      # noqa
from pylint.lint import Run as PyLintRun
# from pylint.message import MessageDefinition as TMsgDef   # ~ pylint.message.message_definition.MessageDefinition

# --- from my module ---
from .models.mdl_msg_defs import TMsgDefs, get_severity
from .models.mdl_reports import TLintReports, TToml
from .models.mdl_wrn_msg import TWrnMsg, WrnMsgFields, wrn_msg_report_fields
from x_tools.utils.models.tp_file_path import TpFilePath, split_path_to_dir_and_name, get_path
from x_tools.utils.cfg_toml import TomlCfgs
from .msg_defs import MsgDefs
from x_tools.utils.utils import lg_dbg, TLg



class MsgWrns:
    """ Class that runs PyLint checks on a specified module. """

    msg_defs               = MsgDefs()    # Store PyLint Message Definitions
    MSG_MAX_LEN:Final[int] = 200          # Max length of the message in the report

    def __init__(
            self,
            root_dir: TpFilePath = None,
            rc_file : TpFilePath = None
        ) -> None:
        """ Initialize MyPyLint with the root directory, and set wrn_msgs container. """
        self.msg_cfgs: TomlCfgs | None = None        # Konfigurace načtená z Toml cfgs.
        self.root_dir: TpFilePath = root_dir        # Root directory of the packages to check
        self.rc_file : TpFilePath = rc_file         # Path to the PyLint configuration file
        self.module_path: TpFilePath | None = None  # Path to the module being checked

        # Seznam vygenerovaných PyLint WrnMsgs
        self.wrn_msgs: list[TWrnMsg] = []           # PyLint-output: List of warning messages generated during the check



    def add_to_wrn_msg(self, results_out, module_path) -> None:
        """ Add a warning message generated PyLint to self.wrn_msgs. """
        self.module_path = module_path
        for wrn_msg in results_out:
            try:
                # do pylint_msg přidej navíc následující pole ... tyto pole očekává Pydantic model TPyLintWrnMsg
                wrn_msg['msg'] = '?'                                # 'msg' pole obsahující hodnotu z pole 'message' zkrácenou na 200 znaků
                wrn_msg['severity'] = 0
                # ---
                wrn_msg = TWrnMsg(**wrn_msg)                        # convert dict to TPyLintWrnMsg Pydantic model
                wrn_msg.path = get_path( wrn_msg.path )             # replace win path-backslashes to lnx-forward slashes  ToDo ... použij get_paths()
                wrn_msg.message = wrn_msg.message.replace('\n', ' | ')

                wrn_msg.msg = wrn_msg.message                       # napln msg pole zkrácenou zprávou z pole 'message'
                if len(wrn_msg.msg) > self.MSG_MAX_LEN:
                    wrn_msg.msg = wrn_msg.msg[:self.MSG_MAX_LEN-3] + '...'

                wrn_msg.severity = get_severity( wrn_msg.msgid )

                if self.msg_cfgs.in_ignored_msgs(
                        wrn_msg.path.replace( self.root_dir + '/', '' ),     # pylint: disable=no-member
                        wrn_msg.obj,
                        wrn_msg.msgid
                    ):   # file, obj, msg_id):
                    continue

                self.wrn_msgs.append(wrn_msg)

                # --- check pylint_msg against pylint_msg_def
                pylint_msg_def: TMsgDefs = MsgWrns.msg_defs.get(wrn_msg.msgid)
                if wrn_msg.symbol != pylint_msg_def.symbol:
                    print( f'Warning: pylint_msg.symbol >{wrn_msg.symbol}<  diffs-from-pylint_msg_def: >{pylint_msg_def.symbol}<')

            except Exception as e:
                print('\nvvv========== Nepodařilo se konvertovat pylint-msg z JSON do Pydantic TPyLintMsg ==========vvv' )
                print( f'pylint_msg: >{wrn_msg}<')
                print( f'Exception: {e}' )
                print(  '^^^========================================================================================^^^\n' )
                raise



    def sort_wrn_msgs(self):
        """ Sort the warning messages in the self.wrn_msgs list """
        self.wrn_msgs = sorted(self.wrn_msgs, key=lambda wrn_msg: (wrn_msg.path.count('/'), wrn_msg.path, wrn_msg.severity, wrn_msg.msgid) )



    def report_wrn_msgs_as_log(
        self,
        report_hdrs: tuple[WrnMsgFields, ...] = wrn_msg_report_fields,
        print_hdrs = True,
        replace_path_in_report='',
    ):
        """ Print wrn-msgs as table-report """
        lg_dbg('MyPyLint.report_wrnmsgs_as_log - Start', flags=TLg.HDR)
        module_path_old = None
        wrn_msgs_to_report = []
        wrn_msg_count = 0

        for wrn_msg in self.wrn_msgs:

            # path_ln = f"{wrn_msg.path.replace(self.root_dir,'')}:{wrn_msg.line}:{wrn_msg.column}"   # 'endLine', 'endColumn',
            path_and_line = f"{wrn_msg.path}:{wrn_msg.line}:{wrn_msg.column}"   # 'endLine', 'endColumn',

            if any( ignore_path in path_and_line for ignore_path in self.msg_cfgs.ignore_paths ):
                continue

            # Jestli je jsou v msg_cfgs.only_msgids nějaké zprávy tak zobrazuj jen tyto zprávy ~ přeskoč ostatní
            if self.msg_cfgs.only_msgids and (wrn_msg.msgid not in self.msg_cfgs.only_msgids):
                continue

            # + ignoruj všechny zprávy které jsou v msg_cfgs.ignore_msgids
            if wrn_msg.msgid in self.msg_cfgs.ignore_msgids:
                continue

            if self.msg_cfgs.ignore_path(wrn_msg.path):
                continue  # ~ don't append msg to resulst

            # if ignore_path and any(ignore_path in wrn_msg.path for ignore_path in ignore_paths):
            #     # dbg( 'Path exluded:', path_ln )
            #     continue  # ~ don't append msg to resulst

            if (module_path_old is not None) and (module_path_old != wrn_msg.path):
                wrn_msgs_to_report.append( dict.fromkeys( report_hdrs, ''))

            module_path_old = wrn_msg.path
            path_and_line = path_and_line.replace(replace_path_in_report, '')

            wrn_msgs_to_report.append(
                    { WrnMsgFields.PATH_LN   : path_and_line,    # = path + lineno + col
                      WrnMsgFields.OBJ       : wrn_msg.obj,      # jméno funkce nebo třídy kte se wrn vyskytuje nebo prázdno v případě global
                      WrnMsgFields.MSGID     : wrn_msg.msgid,    # E0401  |  W0621    |  C0115       |
                      WrnMsgFields.SYMBOL    : wrn_msg.symbol,   # import-error  |  unused-import  |  broad-exception-raised  |  line-too-long ...
                      WrnMsgFields.MSG       : wrn_msg.msg,      # = message.replace('\n', '|')[:200]
                      # For Other possible fields see:  WrnMsgFields
                      }
            )
            wrn_msg_count += 1  # count only nonempty lines

        # --- Toml header ---
        print()
        for inx, ln in enumerate(self.msg_cfgs.toml_hdr, 1):
            print( '  ' if inx ==1 else '   *', ln )

        print( f'\n\nvvv========== PyLint Wrn-Msgs for {self.module_path} ==========vvv\n' )
        rows = [[wrn_msg[key] for key in report_hdrs] for wrn_msg in wrn_msgs_to_report]         # Convert list of dictionaries to a list of lists (values only)
        print( tabulate(rows, headers=report_hdrs if print_hdrs else [], tablefmt='simple') )    # tablefmt='grid'

        print( f'\n\nTotal messages: {wrn_msg_count}', '' if wrn_msg_count else ' :-)' )



    def check_one_module(self, module_path: TpFilePath, inx=0) :     #  -> tuple[ list[TPlMsgDef], list[ list[str, Any]]] :
        """ Spuštění PyLint-eru pro jeden adresář ~ python package ~ workflow modul
            It fills:
                * MyPyLint.__msgid_to_def     ... definice různých typů PyLint messages
                * self.pylint_out_msgs  ... warning zprávy které PyLint našel pro jednotlivé py soubory
        """
        if not module_path.startswith( self.root_dir ):
            module_path = get_path(self.root_dir, module_path)
        module_dir, module_name = split_path_to_dir_and_name( module_path )    # pylint: disable=unused-variable

        lg_dbg('MyPyLint.pylint_one_module_check - Start', flags=TLg.HDR)
        print( '\n'*3, '-'* 100, sep='' )
        print( '# ', f'{inx}/ ' if inx else '', module_name, sep='' )
        print( '-'* 100, sep='' )

        PyLinter.MANAGER.clear_cache()
        pylint_output = io.StringIO()

        # t1 = time.perf_counter()
        # path = pathlib.Path(package_to_check)

        runner = PyLintRun(
                args=[
                    '--recursive=y',
                    f"--rcfile={self.rc_file}",
                    module_path
                    ],
                reporter=PyLintReporters.json_reporter.JSONReporter(pylint_output),
                exit=False
                )

        pylint_msg_defs, _ = runner.linter.msgs_store.find_emittable_messages()

        MsgWrns.msg_defs.add(pylint_msg_defs)

        generated_wrn_msgs = json.loads(pylint_output.getvalue())
        self.add_to_wrn_msg(generated_wrn_msgs, module_path)
        self.sort_wrn_msgs()

        lg_dbg('MyPyLint.pylint_one_module_check - End', flags=TLg.HDR)



def run_pylint(
    root_dir: TpFilePath,
    check_modules: list[TpFilePath],
    rc_file: TpFilePath,
    only_msgids: set[TToml] = None,       # { TToml.LEGACY_IDS, TToml.TODO_IDS, TToml.OK_IDS }
    ignore_msgids: set[TToml] = None,     # { TToml.LEGACY_IDS, TToml.TODO_IDS, TToml.OK_IDS }
    replace_path_in_report: TpFilePath = '',
    print_reports: TLintReports = TLintReports.WRNMSGS_AS_TAB     # | TLintReports.MSG_DEFS
    ):
    """ Spuštění PyLinteru s předanou konfigurací"""

    lg_dbg('MyPyLint.main_run - Start', flags=TLg.HDR)

    hdr = f'vvv========== PyLint Report for {root_dir} ==========vvv'
    hdr_len = len(hdr)-6
    print( f'\n\n{hdr}' )
    for inx, check_module in enumerate(check_modules, 1):
        print( f'  {inx:>3}/ {check_module}' )
    print( f'^^^{"="*hdr_len}^^^\n' )

    sys_path_orig = sys.path
    for inx, check_module in enumerate(check_modules, 1):
        sys.path = sys_path_orig
        sys.path.append( get_path(root_dir, check_module) )   # Ex: r'c:\__My\__PRJ_Work\PyLint\db_monitor' )

        lnt_msg_wrns = MsgWrns(root_dir, rc_file)

        # ===== Import Toml Cfgs =====
        lnt_msg_wrns.msg_cfgs = TomlCfgs(
                get_path(root_dir, check_module),
                only_msgids = only_msgids,
                ignore_msgids = ignore_msgids
                )
        if lnt_msg_wrns.msg_cfgs.err:
            print( f'\n\n{inx}/ {lnt_msg_wrns.msg_cfgs.err}  !!!!!!!!!!!!!!!!!!!!!!!!' )
            continue
        # lnt_msg_wrns.msg_cfgs.report()

        # ===== Check =====
        lnt_msg_wrns.check_one_module( TpFilePath(check_module), inx=inx )

        # ===== Reports =====
        if TLintReports.MSG_DEFS in print_reports:
            lnt_msg_wrns.msg_defs.report()

        if TLintReports.WRNMSGS_AS_TAB in print_reports:
            lnt_msg_wrns.report_wrn_msgs_as_log(
                # ignore_paths = ignore_paths,
                replace_path_in_report = replace_path_in_report,
                )

    lg_dbg('MyPyLint.main_run - End', flags=TLg.HDR)
