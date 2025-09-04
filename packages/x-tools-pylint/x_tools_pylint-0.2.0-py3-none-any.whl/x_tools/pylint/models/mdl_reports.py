""" Reporty z Pylintu k tisku """

from enum import IntFlag, auto, StrEnum


class TToml(StrEnum):
    """ Seznam MsgIds které budou vytištěny v reportu """
    LEGACY_IDS = 'legacy_ids'
    TODO_IDS   = 'todo_ids'
    OK_IDS     = 'ok_ids'
    MSGS_AT    = 'msgs_at'


class TLintReports(IntFlag):
    """ Seznam reportů z kterých je možné si vybrat k tisku """
    def _generate_next_value_(name, start, count, last_values):      # noqa # pylint: disable=no-self-argument
        return 1 << count  # powers of two

    MSG_DEFS = auto()
    WRNMSGS_AS_TAB = auto()
