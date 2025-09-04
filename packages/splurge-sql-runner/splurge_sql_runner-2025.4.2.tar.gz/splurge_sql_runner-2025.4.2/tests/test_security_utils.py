"""
Unit tests for `splurge_sql_runner.utils.security_utils`.

Covers happy paths and error branches for:
- sanitize_shell_arguments
- is_safe_shell_argument
"""

import pytest

from splurge_sql_runner.utils.security_utils import (
    sanitize_shell_arguments,
    is_safe_shell_argument,
)


@pytest.mark.unit
def test_sanitize_shell_arguments_accepts_simple_flags() -> None:
    args = ["--help", "--verbose", "subcommand"]
    assert sanitize_shell_arguments(args) == args


@pytest.mark.unit
def test_sanitize_shell_arguments_rejects_non_list() -> None:
    with pytest.raises(ValueError, match="args must be a list of strings"):
        # type: ignore[arg-type]
        sanitize_shell_arguments("--help")


@pytest.mark.unit
def test_sanitize_shell_arguments_rejects_non_string_items() -> None:
    with pytest.raises(ValueError, match="All command arguments must be strings"):
        # type: ignore[list-item]
        sanitize_shell_arguments(["--ok", 123])


@pytest.mark.unit
@pytest.mark.parametrize(
    "bad_arg",
    [
        ";rm -rf /",
        "unsafe|pipe",
        "double && chain",
        "back`tick`",
        "$(substitution)",
        "${expansion}",
        ">> out",
        "<< in",
        "<<< here",
        "brackets[",
        "]brackets",
        "quote'",
        '"quote"',
        "history!bang",
        "space space",  # contains space
        "tab\tchar",
        "newline\nchar",
        "carriage\rreturn",
        "<(process)",
        ">(process)",
    ],
)
def test_sanitize_shell_arguments_blocks_dangerous_characters(bad_arg: str) -> None:
    with pytest.raises(ValueError, match="Potentially dangerous characters"):
        sanitize_shell_arguments([bad_arg])


@pytest.mark.unit
def test_is_safe_shell_argument_true_for_clean_arg() -> None:
    assert is_safe_shell_argument("--flag") is True


@pytest.mark.unit
def test_is_safe_shell_argument_false_for_non_string() -> None:
    # type: ignore[arg-type]
    assert is_safe_shell_argument(None) is False


@pytest.mark.unit
@pytest.mark.parametrize(
    "bad_arg",
    [
        ";",
        "|",
        "&&",
        "||",
        "`",
        "$(",
        "${",
        ">>",
        "<<",
        "<<<",
        "[",
        "]",
        "'",
        '"',
        "!",
        " ",
        "\t",
        "\n",
        "\r",
        "<(",
        ">(",
    ],
)
def test_is_safe_shell_argument_detects_dangerous_characters(bad_arg: str) -> None:
    assert is_safe_shell_argument(f"prefix{bad_arg}suffix") is False


