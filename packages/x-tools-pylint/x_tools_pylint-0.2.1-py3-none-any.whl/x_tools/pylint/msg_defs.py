""" PyLint message definitions for MyPyLint. """

from tabulate import tabulate

from .models.mdl_msg_defs import TMsgDefs, get_severity
from .models.tp_msg_id import TpMsgId
from x_tools.utils.utils import lg_dbg, TLg



class MsgDefs:
    """ Definitions for PyLint messages and categories. """

    __msgid_to_def: dict[TpMsgId, TMsgDefs] = {}

    @classmethod
    def get(cls, msgid: TpMsgId) -> TMsgDefs | None:
        """ Get PyLint message definition by msgid. """
        if msgid not in cls.__msgid_to_def:
            raise ValueError( f'MsgId {msgid} not found in PyLintDefs.__msgid_to_def' )
        return cls.__msgid_to_def[msgid]



    @classmethod
    def add(cls, pylint_msg_defs):
        """ Add all MSG Definitions to  MyPyLint.__msgid_to_def """
        lg_dbg( 'PyLintDefs.add_to_msg_defs - Start', flags=TLg.HDR)
        msg_def_added = False
        for emtb in pylint_msg_defs:

            # 1) Convert each Mes-Definition returned from PyLint to a Pydantic model
            attrs_kv_str = { str(k):str(v) for k,v in emtb.__dict__.items() }   # convert keys and values to strings
            pylint_msg_def = TMsgDefs(**attrs_kv_str)                        # convert to TPyLintMsgDefs Pydantic model
            # print( pylint_msg_defs.model_dump() )
            msgid: TpMsgId = pylint_msg_def.msgid
            # transform some fields to be more readable:
            pylint_msg_def.msg = pylint_msg_def.msg.replace('\n', ' | ')
            pylint_msg_def.description = pylint_msg_def.description.replace('\n', ' | ')
            pylint_msg_def.severity = get_severity( msgid )

            # 2) and add them to the class variable __msgid_to_def
            if msgid not in cls.__msgid_to_def:
                cls.__msgid_to_def[msgid] = pylint_msg_def
                msg_def_added = True
            # pokud už msg-def v zeznamu je tak zkontroluj, že jednotlivá pole nové zprávy jsou stejná jako ty již dříve uložená
            elif cls.__msgid_to_def[msgid] != pylint_msg_def:
                raise ValueError('Same MsgId but diffrent values !!')

        if msg_def_added:
            # v případě přidání dalších definic jejich list zase setřiď
            cls.__msgid_to_def = dict(sorted(cls.__msgid_to_def.items(), key=lambda x: f'{x[1].severity} {x[1].msgid}'))

        lg_dbg( 'PyLintDefs.add_to_msg_defs - End', flags=TLg.HDR)


    @classmethod
    def report(
            cls,
            max_field_len = ( ('msg', 100), ('description', 200) )
        ):
        """ List all __msgid_to_def """
        print( '\nvvv========== Msg-Definitions Report ==========vvv\n' )
        max_field_len = dict(max_field_len)      # Convert to dictionary for easy access
        msg_defs_hdrs = list(TMsgDefs.model_fields.keys())
        # List of dictionaries 'field_name: value' for each msg_def
        msg_defs_list: list[dict] = []
        for _msg_id, msg_def in cls.__msgid_to_def.items():
            msg_def_dict = msg_def.model_dump()
            for field_name, max_len in max_field_len.items():
                if len(msg_def_dict[field_name])>max_len:
                    msg_def_dict[field_name] = msg_def_dict[field_name][:max_len - 3] + '...'
            msg_defs_list.append(msg_def_dict)
            # print( msg_def_dict )

        # Convert list of dictionaries to a list of rows: lists-values-only
        rows = [ [msg_def[key] for key in msg_defs_hdrs] for msg_def in msg_defs_list ]
        print( tabulate(rows, headers=msg_defs_hdrs, tablefmt='simple') )   # tablefmt='grid'
