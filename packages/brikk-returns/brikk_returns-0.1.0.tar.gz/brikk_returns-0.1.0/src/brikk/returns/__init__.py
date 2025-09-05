from brikk.returns._errors import (
    OptionError,
    OptionExpectError,
    OptionUnwrapError,
    ResultError,
    ResultExpectError,
    ResultUnwrapError,
    ReturnsError,
)
from brikk.returns._option import (
    Nothing,
    Option,
    Some,
    is_none,
    is_some,
)
from brikk.returns._result import (
    Error,
    Ok,
    Result,
    is_err,
    is_ok,
)
from brikk.returns._utils import (
    as_optional,
    as_result,
    optional_of,
    result_of,
    safe,
)

__all__ = [
    "Error",
    "Nothing",
    "Ok",
    "Option",
    "OptionError",
    "OptionExpectError",
    "OptionUnwrapError",
    "Result",
    "ResultError",
    "ResultExpectError",
    "ResultUnwrapError",
    "ReturnsError",
    "Some",
    "as_optional",
    "as_result",
    "is_err",
    "is_none",
    "is_ok",
    "is_some",
    "optional_of",
    "result_of",
    "safe",
]
