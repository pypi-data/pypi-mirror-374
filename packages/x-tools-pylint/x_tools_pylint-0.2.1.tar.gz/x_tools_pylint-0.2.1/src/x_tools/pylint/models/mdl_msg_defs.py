""" Definice různých typů PyLint zpráv  """

from enum import IntEnum, StrEnum

from pydantic import BaseModel, ConfigDict     # ValidationError, Field,

from .tp_msg_id import TpMsgId


class TLntCheckerNames(StrEnum):
    """ List of PyLint Checker Names. """
    ASYNC                   = 'async'
    BAD_CHAINED_COMPARISON  = 'bad-chained-comparison'
    BASIC                   = 'basic'
    CLASSES                 = 'classes'
    DATACLASS               = 'dataclass'
    DESIGN                  = 'design'
    ENUM                    = 'enum'
    EXCEPTIONS              = 'exceptions'
    FORMAT                  = 'format'
    IMPORTS                 = 'imports'
    LAMBDA_EXPRESSIONS      = 'lambda-expressions'
    LOGGING                 = 'logging'
    MAIN                    = 'main'
    METHOD_ARGS             = 'method_args'
    MISCELLANEOUS           = 'miscellaneous'
    MODIFIED_ITERATION      = 'modified_iteration'
    NESTED_MIN_MAX          = 'nested_min_max'
    NEWSTYLE                = 'newstyle'
    NONASCII_CHECKER        = 'nonascii-checker'
    REFACTORING             = 'refactoring'
    SIMILARITIES            = 'similarities'
    SPELLING                = 'spelling'
    STDLIB                  = 'stdlib'
    STRING                  = 'string'
    THREADING               = 'threading'
    TYPECHECK               = 'typecheck'
    UNICODE_CHECKER         = 'unicode_checker'
    UNNECESSARY_DUNDER_CALL = 'unnecessary-dunder-call'
    UNNECESSARY_ELLIPSIS    = 'unnecessary_ellipsis'
    UNSUPPORTED_VERSION     = 'unsupported_version'
    VARIABLES               = 'variables'



class TLntSeverity(IntEnum):
    """ Severita PyLint zpráv odvozená z prvního písmene msgid """
    _ = 0    # Not set
    F = 1    # Fatal
    E = 2    # Error
    W = 3    # Warning
    R = 4    # Refactor
    C = 5    # Convention
    I = 6    # Informational


def get_severity(msgid: TpMsgId) -> int:
    """ Gets severity from msgid: Fxxx -> 1, ... Ixxx -> 6"""
    severity_dict = {member.name: member.value for member in TLntSeverity}
    severity_int = severity_dict[ msgid[0] ]
    return severity_int


class TMsgDefs(BaseModel):       # Ex values:
    """ Definice různých typů PyLint zpráv """
    msgid:  TpMsgId                       # 'W1116'
    checker_name: TLntCheckerNames       # TLntCheckerNames:  'basic' / 'refactoring' / 'spelling' ....
    symbol: str                          # 'isinstance-second-argument-not-valid-type'
    msg:    str                          # '%s name "%s" doesn't conform to %s'.replace('\n', ' | ')
    description: str                     # 'Emitted when the 2nd argument of an isinstance call ...'.replace('\n', ' | ')
    # --- Not interesting ... so dont print these in report ---
    shared:     str                      # 'False' / 'True'
    default_enabled: str                 # 'False' / 'True'
    maxversion: str                      # None
    minversion: str                      # None / (3, 6)
    scope:      str                      # 'node-based-msg' / 'line-based-msg'
    old_names:  str                      #  [('W0132', 'old-empty-docstring')]
    # --- Computed fields ---
    severity: int = 0                    # E - 1, F - 2, W - 3, R - 4, C - 5, I - 6
    # --- Pydantic ---
    model_config = ConfigDict(extra='forbid')
