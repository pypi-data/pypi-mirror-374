"""Commit For Free: An Intelligent Git Commit Message Generator.

This module provides an automated solution for generating meaningful Git commit messages
based on the changes in your repository. It analyzes file changes, categorizes them by type,
and generates descriptive commit messages using AI assistance.

Example:
    To use as a command-line tool:

    ```
    python -m c4f.main
    ```

    This will analyze changes in your Git repository and generate appropriate
    commit messages based on the file changes.
"""

from __future__ import annotations

import concurrent.futures
import os
import re
import sys
import time
from collections import defaultdict
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError  # noqa: A004
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Optional, Tuple, TypeVar, cast

from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table

from c4f._purifier import Purify, can_display_emojis, get_ascii_icon_for_type
from c4f.config import Config
from c4f.ssl_utils import with_ssl_workaround
from c4f.utils import (  # type: ignore
    STATUS_TYPE,
    FileChange,
    SecureSubprocess,
    SubprocessConfig,
    client,
    console,
)

__dir__ = ["main"]

T = TypeVar("T")

GREEN_FORMAT_THRESHOLD = 10
YELLOW_FORMAT_THRESHOLD = 50


def run_git_command(
    command: list[str], timeout: int | None = None
) -> tuple[str, str, int]:
    """Run a git command and return its output.

    Args:
        command: The git command to run as a list of strings.
        timeout: Maximum time in seconds to wait for the process to complete.

    Returns:
        Tuple[str, str, int]: stdout, stderr, and return code.
    """
    config = SubprocessConfig(
        timeout=timeout,
        allowed_commands={"git"},  # Allow git command
        restricted_env=False,  # Use full environment for git commands
    )
    handler = SecureSubprocess(config)
    return handler.run_command(command, timeout)


def get_root_git_workspace() -> Path:
    """Get the root directory of the current workspace.

    Returns the directory containing this file.
    """
    return Path(__file__).parent


def get_git_status_output() -> tuple[str, str, int]:
    """Get the raw output from git status command.

    Returns:
        Tuple[str, str, int]: stdout, stderr, and return code from git status command.
    """
    return run_git_command(["git", "status", "--porcelain"])


def handle_git_status_error(stderr: str) -> None:
    """Handle error from git status command.

    Args:
        stderr: Error output from git status command.

    Exits the program if the git status command fails.
    """
    console.print(f"[red]Error getting git status:[/red] {stderr}", style="bold red")
    sys.exit(1)


def process_untracked_file(
    status: STATUS_TYPE, file_path: str
) -> List[Tuple[STATUS_TYPE, str]]:
    """Process untracked files and directories.

    Args:
        status: Git status code.
        file_path: Path to the file or directory.

    Returns:
        List of tuples containing status and file path.
    """
    changes = []
    status = "A"  # Treat untracked as new/added files
    path = Path(file_path)
    if path.is_dir():
        # For untracked directories, add all files recursively
        for file in list_untracked_files(path):
            changes.append((status, str(file)))
    else:
        changes.append((status, file_path))
    return changes  # type: ignore


def process_renamed_file(file_path: str) -> str:
    """Process renamed files to extract the new file path.

    Args:
        file_path: Original file path string containing the rename information.

    Returns:
        The new file path after rename.
    """
    return file_path.split(" -> ")[1]


def process_git_status_line(line: str) -> List[tuple[STATUS_TYPE, str]]:
    """Process a single line from git status output.

    Args:
        line: A line from git status --porcelain output.

    Returns:
        List of tuples containing status and file path.
    """
    if not line.strip():
        return []

    status, file_path = line[:2].strip(), line[2:].strip()

    # Handle untracked files (marked as '??')
    if status == "??":
        return process_untracked_file(cast(STATUS_TYPE, status), file_path)
    # Handle renamed files
    if status == "R":
        file_path = process_renamed_file(file_path)
        return [(status, file_path)]  # type: ignore
    # Handle regular changes
    return [(status, file_path)]  # type: ignore


def parse_git_status() -> List[Tuple[STATUS_TYPE, str]]:
    """Parse the output of 'git status --porcelain' to get file changes.

    Retrieves and processes git status output to identify changed files.
    Exits the program if the git status command fails.
    Handles special cases like untracked and renamed files.

    Returns:
        List of tuples containing status and file path.
    """
    stdout, stderr, code = get_git_status_output()
    if code != 0:
        handle_git_status_error(stderr)

    changes = []
    for line in stdout.splitlines():
        changes.extend(process_git_status_line(line))
    return changes


def list_untracked_files(directory: Path) -> list[Path]:
    """Recursively list all files in an untracked directory."""
    files = []
    for item in directory.glob("**/*"):
        if item.is_file():
            files.append(item)
    return files


def get_file_diff(file_path: str) -> str:
    """Get the diff for a file.

    Handles different cases including directories and untracked files.
    """
    console.print(f"Getting diff for {file_path}...", style="blue")
    path = Path(file_path)

    if path.is_dir():
        return handle_directory(file_path)

    if is_untracked(file_path):
        return handle_untracked_file(path)

    return get_tracked_file_diff(file_path)


def shorten_diff(diff: str, config: Config) -> str:
    """Shorten a diff to a maximum number of lines.

    Truncates diffs that are longer than DIFF_MAX_LENGTH and adds an indicator.

    Args:
        diff: The diff to shorten.
        config: Configuration object with settings for the commit message generator.

    Returns:
        str: The shortened diff.
    """
    lines = diff.strip().splitlines()

    if len(lines) > config.diff_max_length:
        lines = lines[: config.diff_max_length] + ["\n...\n\n"]

    return "\n".join(lines)


def get_tracked_file_diff(file_path: str) -> str:
    """Get the diff for a tracked file.

    First tries to get the diff from staged changes, then from unstaged changes.
    Returns an empty string if no diff is available.
    """
    stdout, _, code = run_git_command(["git", "diff", "--cached", "--", file_path])
    if code == 0 and stdout:
        return stdout
    stdout, _, code = run_git_command(["git", "diff", "--", file_path])
    return stdout if code == 0 else ""


def handle_directory(file_path: str) -> str:
    """Handle directories in diff generation."""
    path = Path(file_path)

    # If it's an untracked directory, we'll handle the files individually
    if is_untracked(file_path) and path.is_dir():
        return f"Untracked directory: {file_path}"

    return f"Directory: {file_path}"


def is_untracked(file_path: str) -> bool:
    """Check if a file is untracked by git.

    A file is untracked if git status returns '??' at the start of the line.
    """
    stdout, _, code = run_git_command(["git", "status", "--porcelain", file_path])
    return code == 0 and stdout.startswith("??")


def handle_untracked_file(path: Path) -> str:
    """Handle untracked files by reading their content.

    Returns appropriate messages for files that don't exist or can't be read.
    Explicitly handles empty files with a special indicator.
    """
    if not path.exists():
        return f"File not found: {path}"
    if not os.access(path, os.R_OK):
        return f"Permission denied: {path}"
    # Check for empty files
    if path.is_file() and path.stat().st_size == 0:
        return f"Empty file: {path}"

    try:
        return read_file_content(path)
    except Exception as e:
        console.print(f"[red]Error reading file {path}:[/red] {e}", style="bold red")
        return f"Error: {e!s}"


def read_file_content(path: Path) -> str:
    """Read the content of a file, detecting binary files.

    Checks for null bytes to determine if a file is binary.
    Returns the file content or a message indicating it's a binary file.
    For empty files, returns a special indicator message.
    """
    # Check if the file is empty
    if is_empty_file(path):
        return f"Empty file: {path}"

    try:
        with Path(path).open("r", encoding="utf-8") as f:
            content = f.read(1024)
            if "\0" in content:
                return f"Binary file: {path}"
            f.seek(0)
            return f.read()
    except UnicodeDecodeError:
        return f"Binary file: {path}"


def is_empty_file(path: Path) -> bool:
    return path.exists() and path.stat().st_size == 0


def analyze_file_type(file_path: Path, diff: str) -> str:
    """Determine the type of change based on file path and diff content."""
    file_type_checks: list[Callable[[Path, str], str | None]] = [
        check_python_file,
        check_documentation_file,
        check_configuration_file,
        check_script_file,
        check_test_file,
        check_file_path_patterns,
        check_diff_patterns,
    ]

    for _check in file_type_checks:
        result = _check(file_path, diff)
        if result:
            return result

    return "feat"  # Default case if no other type matches


def check_python_file(file_path: Path, _: str) -> str | None:
    """Check if the file is a Python file and determine its type.

    Python files with 'test' in their path are classified as test files.
    """
    if file_path.suffix == ".py":
        return "test" if "test" in str(file_path).lower() else "feat"
    return None


def check_documentation_file(file_path: Path, _: str) -> str | None:
    """Check if the file is a documentation file.

    Files with .md, .rst, or .txt extensions are classified as docs.
    """
    if file_path.suffix in [".md", ".rst", ".txt"]:
        return "docs"
    return None


def check_configuration_file(file_path: Path, _: str) -> str | None:
    """Check if the file is a configuration file.

    Common configuration files like .gitignore and requirements.txt are classified as chore.
    """
    config_files = [
        ".gitignore",
        "requirements.txt",
        "setup.py",
        "setup.cfg",
        "pyproject.toml",
    ]
    if file_path.name in config_files:
        return "chore"
    return None


def check_script_file(file_path: Path, _: str) -> str | None:
    """Check if the file is in a scripts directory.

    Files in directories named 'scripts' are classified as chore.
    """
    return "chore" if "scripts" in file_path.parts else None


def check_test_file(file_path: Path, _: str) -> str | None:
    return "test" if is_test_file(file_path) else None


def is_test_file(file_path: Path) -> bool:
    """Check if the file is in a dedicated test directory."""
    test_indicators = (
        "tests",
        "test",
        "spec",
        "specs",
        "pytest",
        "unittest",
        "mocks",
        "fixtures",
    )
    return any(part.lower() in test_indicators for part in file_path.parts)


def check_file_path_patterns(file_path: Path, _: str) -> str | None:
    """Check file name patterns to determine file type."""
    # Enhanced patterns based on conventional commits and industry standards
    type_patterns = get_test_patterns()
    return check_patterns(str(file_path), type_patterns)  # type: ignore


def check_diff_patterns(diff: Path, _: str) -> str | None:
    """Check diff content patterns to determine file type."""
    # Enhanced patterns for detecting commit types from diff content
    diff_patterns = get_diff_patterns()
    return check_patterns(str(diff).lower(), diff_patterns)  # type: ignore


def get_test_patterns() -> dict[str, str]:
    """Get a dictionary of regex patterns for identifying file types by path.

    Maps commit types to regex patterns for matching file paths.
    """
    return {
        "test": r"^tests?/|^testing/|^__tests?__/|^test_.*\.py$|^.*_test\.py$|^.*\.spec\.[jt]s$|^.*\.test\.[jt]s$",
        "docs": r"^docs?/|\.md$|\.rst$|\.adoc$|\.txt$|^(README|CHANGELOG|CONTRIBUTING|HISTORY|AUTHORS|SECURITY)(\.[^/]+)?$|^(COPYING|LICENSE)(\.[^/]+)?$|^(api|docs|documentation)/|.*\.docstring$|^jsdoc/|^typedoc/",
        "style": r"\.(css|scss|sass|less|styl)$|^styles?/|^themes?/|\.editorconfig$|\.prettierrc|\.eslintrc|\.flake8$|\.style\.yapf$|\.isort\.cfg$|setup\.cfg$|^\.stylelintrc|^\.prettierrc|^\.prettier\.config\.[jt]s$",
        "ci": r"^\.github/workflows/|^\.gitlab-ci|\.travis\.yml$|^\.circleci/|^\.azure-pipelines|^\.jenkins|^\.github/actions/|\.pre-commit-config\.yaml$|^\.gitlab/|^\.buildkite/|^\.drone\.yml$|^\.appveyor\.yml$",
        "build": r"^pyproject\.toml$|^setup\.(py|cfg)$|^requirements/|^requirements.*\.txt$|^poetry\.lock$|^Pipfile(\.lock)?$|^package(-lock)?\.json$|^yarn\.lock$|^Makefile$|^Dockerfile$|^docker-compose\.ya?ml$|^MANIFEST\.in$|^rollup\.config\.[jt]s$|^webpack\.config\.[jt]s$|^babel\.config\.[jt]s$|^tsconfig\.json$|^vite\.config\.[jt]s$|^\.babelrc$|^\.npmrc$",
        "perf": r"^benchmarks?/|^performance/|\.*.profile$|^profiling/|^\.?cache/|^\.?benchmark/",
        "chore": r"^\.env(\.|$)|\.(ini|cfg|conf|json|ya?ml|toml|properties)$|^config/|^settings/|^\.git.*$|^\.husky/|^\.vscode/|^\.idea/|^\.editorconfig$|^\.env\.example$|^\.nvmrc$",
        "feat": r"^src/|^app/|^lib/|^modules/|^feature/|^features/|^api/|^services/|^controllers/|^routes/|^middleware/|^models/|^schemas/|^types/|^utils/|^helpers/|^core/|^internal/|^pkg/|^cmd/",
        "fix": r"^hotfix/|^bugfix/|^patch/|^fix/",
        "refactor": r"^refactor/|^refactoring/|^redesign/",
        "security": r"^security/|^auth/|^authentication/|^authorization/|^access control/|^permission/|^privilege/|^validation/|^sanitization/|^encryption/|^decryption/|^hashing/|^cipher/|^token/|^session/|^xss/|^sql injection/|^csrf/|^cors/|^firewall/|^waf/|^pen test/|^penetration test/|^audit/|^scan/|^detect/|^protect/|^prevent/|^mitigate/|^remedy/|^fix/|^patch/|^update/|^secure/|^harden/|^fortify/|^safeguard/|^shield/|^guard/|^block/|^filter/|^screen/|^check/|^verify/|^validate/|^confirm/|^ensure/|^ensure/|^trustworthy/|^reliable/|^robust/|^resilient/|^immune/|^impervious/|^invulnerable",
    }


def get_diff_patterns() -> dict[str, str]:
    """Get a dictionary of regex patterns for identifying commit types by diff content.

    Maps commit types to regex patterns for matching content in diffs.
    """
    return {
        "test": r"\bdef test_|\bclass Test|\@pytest|\bunittest|\@test\b|\bit\(['\"]\w+['\"]|describe\(['\"]\w+['\"]|\bexpect\(|\bshould\b|\.spec\.|\.test\.|mock|stub|spy|assert|verify",
        "fix": r"\bfix|\bbug|\bissue|\berror|\bcrash|resolve|closes?\s+#\d+|\bpatch|\bsolve|\baddress|\bfailing|\bbroken|\bregression",
        "refactor": r"\brefactor|\bclean|\bmove|\brename|\brestructure|\brewrite|\bimprove|\bsimplify|\boptimize|\breorganize|\benhance|\bupdate|\bmodernize|\bsimplify|\streamline",
        "perf": r"\boptimiz|\bperformance|\bspeed|\bmemory|\bcpu|\bruntime|\bcache|\bfaster|\bslower|\blatency|\bthroughput|\bresponse time|\befficiency|\bbenchmark|\bprofile|\bmeasure|\bmetric|\bmonitoring",
        "style": r"\bstyle|\bformat|\blint|\bprettier|\beslint|\bindent|\bspacing|\bwhitespace|\btabs|\bspaces|\bsemicolons|\bcommas|\bbraces|\bparens|\bquotes|\bsyntax|\btypo|\bspelling|\bgrammar|\bpunctuation",
        "feat": r"\badd|\bnew|\bfeature|\bimplement|\bsupport|\bintroduce|\benable|\bcreate|\ballow|\bfunctionality",
        "docs": r"\bupdate(d)?\s*README\.md|\bupdate(d)? readme|\bdocument|\bcomment|\bexplain|\bclari|\bupdate changelog|\bupdate license|\bupdate contribution|\bjsdoc|\btypedoc|\bdocstring|\bjavadoc|\bapidoc|\bswagger|\bopenapi|\bdocs",
        "security": r"\bsecurity|\bvulnerability|\bcve|\bauth|\bauthentication|\bauthorization|\baccess control|\bpermission|\bprivilege|\bvalidation|\bsanitization|\bencryption|\bdecryption|\bhashing|\bcipher|\btoken|\bsession|\bxss|\bsql injection|\bcsrf|\bcors|\bfirewall|\bwaf|\bpen test|\bpenetration test|\baudit|\bscan|\bdetect|\bprotect|\bprevent|\bmitigate|\bremedy|\bfix|\bpatch|\bupdate (?!UI|design)|\bsecure|\bharden|\bfortify|\bsafeguard|\bshield|\bguard|\bblock|\bfilter|\bscreen|\bcheck|\bverify|\bvalidate|\bconfirm|\bensure|\btrustworthy|\breliable|\brobust|\bresilient|\bimmune|\bimpervious|\binvulnerable",
        "chore": r"\bchore|\bupdate dependencies|\bupgrade|\bdowngrade|\bpackage|\bbump version|\brelease|\btag|\bversion|\bdeployment|\bci|\bcd|\bpipeline|\bworkflow|\bautomation|\bscripting|\bconfiguration|\bsetup|\bmaintenance|\bcleanup|\bupkeep|\borganize|\btrack|\bmonitor",
    }


def check_patterns(text: str, patterns: dict[Optional[str], str]) -> str | None:
    """Check if text matches any pattern in the given dictionary."""
    for type_name, pattern in patterns.items():
        if re.search(pattern, text, re.I):
            return type_name
    return None


def group_related_changes(changes: list[FileChange]) -> list[list[FileChange]]:
    """Group related file changes together based on their type and location.

    Groups changes by combining their type and parent directory to identify related changes.
    """
    groups = defaultdict(list)
    for change in changes:
        key = (
            f"{change.type}_{change.path.parent}"
            if change.path.parent.name != "."
            else change.type
        )
        groups[key].append(change)
    return list(groups.values())


def generate_commit_message(changes: list[FileChange], config: Config) -> str:
    """Generate a commit message for a list of file changes.

    Uses an AI model to generate appropriate commit messages based on the changes.
    For larger changes, generates a more comprehensive message.
    Falls back to a simple message if message generation fails.

    Args:
        changes: List of file changes to generate a commit message for.
        config: Configuration object with settings for the commit message generator.

    Returns:
        str: The generated commit message.
    """
    combined_context = create_combined_context(changes)
    total_diff_lines = calculate_total_diff_lines(changes)
    is_comprehensive = total_diff_lines >= config.prompt_threshold
    diffs_summary = generate_diff_summary(changes, config) if is_comprehensive else ""

    tool_calls = determine_tool_calls(is_comprehensive, combined_context, diffs_summary)

    for _ in range(config.attempt):
        message = get_formatted_message(
            combined_context, tool_calls, changes, total_diff_lines, config
        )

        if is_corrupted_message(message, config):
            continue

        if is_comprehensive:
            result = handle_comprehensive_message(message, changes, config)
            if result in ["retry", "r"]:
                continue
            if result:
                return result
        else:
            return message  # type: ignore

    return generate_fallback_message(changes, config)


def is_corrupted_message(message: Optional[str], config: Config) -> bool:
    """Check if a generated message is corrupted or invalid.

    A message is considered corrupted if it's empty, doesn't follow conventional commit
    format, or doesn't have brackets when required.
    """
    return (
        not message
        or not is_conventional_type(message)
        or not is_conventional_type_with_brackets(message, config)
    )


def is_conventional_type(message: str) -> bool:
    """Check if a message follows conventional commit type format.

    Verifies that the message follows the conventional commit format: type: message
    or type(scope): message, where type is one of the conventional commit types.
    """
    if not message:
        return False

    # Define valid conventional commit types
    conventional_types = get_conventional_commit_types()

    # Check if the message follows the standard format with regex
    if is_standard_conventional_format(message):
        return True

    # For compatibility, also check simpler format without scope
    return bool(is_simple_conventional_format(message, conventional_types))


def get_conventional_commit_types() -> list[str]:
    """Return a list of valid conventional commit types."""
    return [
        "feat",
        "test",
        "fix",
        "docs",
        "chore",
        "refactor",
        "style",
        "perf",
        "ci",
        "build",
        "security",
        "revert",
    ]


def is_standard_conventional_format(message: str) -> bool:
    """Check if message follows standard conventional format with optional scope."""
    # Pattern checks for valid type followed by optional scope, then colon and space
    pattern = r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert|security)(\([^)]*\))?:\s"

    lower_message = message.lower()

    if re.match(pattern, lower_message):
        # Verify there's only one scope parenthesis pair before the colon
        prefix = lower_message.split(":", 1)[0]
        return prefix.count("(") <= 1 and prefix.count(")") <= 1

    return False


def is_simple_conventional_format(message: str, conventional_types: list[str]) -> bool:
    """Check if message follows simple conventional format without scope."""
    lower_message = message.lower()

    for commit_type in conventional_types:
        if lower_message.startswith((f"{commit_type}:", f"{commit_type} :")):
            # Make sure there are no parentheses before the colon in this case
            prefix = lower_message.split(":", 1)[0]
            return "(" not in prefix and ")" not in prefix

    return False


def is_conventional_type_with_brackets(message: str, config: Config) -> bool:
    """Check if a message follows conventional commit type format with brackets.

    If FORCE_BRACKETS is enabled, ensures the message has brackets in the first word.
    """
    if not config.force_brackets:
        return True

    first_word: str = message.split()[0]
    return not ("(" not in first_word and ")" not in first_word)


def get_formatted_message(
    combined_context: str,
    tool_calls: Dict[str, str],
    changes: List[FileChange],
    total_diff_lines: int,
    config: Config,
) -> Optional[str]:
    """Get a formatted commit message using the model.

    Attempts to generate a message and then purifies it to remove any unwanted content.
    """
    # Attempt to get Message
    message = attempt_generate_message(
        combined_context, tool_calls, changes, total_diff_lines, config
    )

    # Purify Message
    message = Purify.message(message, config)

    # Handle icons based on config
    if message:
        message = Purify.icons(message, config.icon, config)

    return message


def determine_tool_calls(
    is_comprehensive: bool,
    combined_text: str,
    diffs_summary: str = "",
) -> dict[str, Any]:
    """Determine the appropriate tool calls based on the comprehensiveness of the change.

    Selects either a simple or comprehensive tool call based on the size of changes.

    Args:
        is_comprehensive: Whether the change is comprehensive.
        combined_text: The combined text of all changes.
        diffs_summary: A summary of all diffs.

    Returns:
        Dict[str, Any]: The tool calls to use.
    """
    if is_comprehensive:
        return create_comprehensive_tool_call(combined_text, diffs_summary)
    return create_simple_tool_call(combined_text)


def create_simple_tool_call(combined_text: str) -> dict[str, Any]:
    """Create a tool call for generating a simple commit message.

    Configures parameters for a short, conventional commit message.
    """
    return {
        "function": {
            "name": "generate_commit",
            "arguments": {
                "files": combined_text,
                "style": "conventional",
                "format": "inline",
                "max_length": 72,
                "include_scope": True,
                "strict_conventional": True,
            },
        },
        "type": "function",
    }


def create_comprehensive_tool_call(
    combined_text: str, diffs_summary: str
) -> dict[str, Any]:
    """Create a tool call for generating a comprehensive commit message.

    Configures parameters for a detailed commit message with multiple sections.
    """
    return {
        "function": {
            "name": "generate_commit",
            "arguments": {
                "files": combined_text,
                "diffs": diffs_summary,
                "style": "conventional",
                "format": "detailed",
                "max_first_line": 72,
                "include_scope": True,
                "include_breaking": True,
                "include_references": True,
                "sections": ["summary", "changes", "breaking", "references"],
                "strict_conventional": True,
            },
        },
        "type": "function",
    }


def attempt_generate_message(
    combined_context: str,
    tool_calls: dict[str, Any],
    changes: list[FileChange],
    total_diff_lines: int,
    config: Config,
) -> str | None:
    """Attempt to generate a commit message using the model.

    Uses the appropriate prompt based on the size of changes and sends it to the model.
    """
    prompt = determine_prompt(combined_context, changes, total_diff_lines, config)
    return model_prompt(prompt, tool_calls, config)


def handle_comprehensive_message(
    message: str | None, changes: list[FileChange], config: Config
) -> Optional[str]:
    """Handle a comprehensive commit message, with user interaction for short messages.

    For messages shorter than MIN_COMPREHENSIVE_LENGTH, prompts the user to choose whether to
    use the message, retry generation, or use a fallback message.
    """
    if not message:
        return None

    if len(message) < config.min_comprehensive_length:
        action = handle_short_comprehensive_message(message).strip().lower()
        while action not in ["use", "u", "retry", "r", "fallback", "f"]:
            action = input(
                "\nChoose an option between the options above: or leave it empty to use: "
            ).strip()
        if action in ["use", "u", ""]:
            return message
        if action in ["retry", "r"]:
            return "retry"
        if action in ["fallback", "f"]:
            return generate_fallback_message(changes, config)
    return message


def create_combined_context(changes: list[FileChange]) -> str:
    """Create a combined context string from file changes.

    Creates a newline-separated string with the status and path for each change.
    """
    return "\n".join([f"{change.status} {change.path}" for change in changes])


def calculate_total_diff_lines(changes: list[FileChange]) -> int:
    """Calculate the total number of lines changed.

    Sums up the diff_lines attribute of each file change.
    """
    return sum(change.diff_lines for change in changes)


def handle_short_comprehensive_message(model_message: str) -> str:
    """Handle a comprehensive message that is too short, with user interaction.

    Displays a warning and prompts the user to choose between using the message,
    retrying generation, or using an auto-generated message.
    """
    console.print(
        "\n[yellow]Warning: Generated commit message seems too brief for a large change.[/yellow]"
    )
    console.print(f"Generated message: [cyan]{model_message}[/cyan]\n")

    table = Table(show_header=False, style="blue")
    table.add_row("[1] Use this message anyway")
    table.add_row("[2] Try generating again")
    table.add_row("[3] Use auto-generated message")
    console.print(table)

    choice = input("\nChoose an option (1-3): ").strip()

    if choice == "1":
        return "use"
    if choice == "2":
        return "retry"
    return "fallback"


def get_icon_for_type(change_type: Optional[str]) -> str:
    """Get the appropriate icon for a commit type.

    Args:
        change_type: The type of change (feat, fix, etc.).

    Returns:
        str: The corresponding emoji for the change type.
    """
    icons = {
        "feat": "✨",
        "fix": "🐛",
        "docs": "📝",
        "style": "💄",
        "refactor": "♻️",
        "perf": "⚡",
        "test": "✅",
        "build": "👷",
        "ci": "🔧",
        "chore": "🔨",
        "revert": "⏪",
        "security": "🔒",
    }
    return icons.get(str(change_type), "🎯")  # Default icon if type not found


def select_appropriate_icon(
    change_type: Optional[str], config: Optional[Config] = None
) -> str:
    """Select the appropriate icon based on terminal capabilities and config.

    Args:
        change_type: The type of change (feat, fix, etc.)
        config: Configuration object with settings for the commit message generator.

    Returns:
        str: The appropriate icon (emoji or ASCII) based on terminal support.
    """
    # If config is not provided or icons are disabled, return empty string
    if not config or not config.icon:
        return ""

    # Check if we're forcing ASCII mode in the config
    if hasattr(config, "ascii_only") and config.ascii_only:
        return get_ascii_icon_for_type(change_type) + " "

    # Check if terminal can display emojis
    if can_display_emojis():
        return get_icon_for_type(change_type) + " "
    return get_ascii_icon_for_type(change_type) + " "


def generate_fallback_message(
    changes: list[FileChange], config: Optional[Config] = None
) -> str:
    """Generate a simple fallback commit message based on file changes.

    Creates a basic commit message using the type of the first change and
    listing the names of all changed files. Includes icons if enabled in config.

    Args:
        changes: List of file changes to generate a message for.
        config: Configuration object with settings for the commit message generator.

    Returns:
        str: The generated fallback commit message.
    """
    change_type = changes[0].type
    file_names = " ".join(str(c.path.name) for c in changes)

    # Add appropriate icon if icons are enabled
    if config and config.icon:
        icon = select_appropriate_icon(change_type, config)
        return f"{icon}{change_type}: update {file_names}"

    return f"{change_type}: update {file_names}"


def generate_diff_summary(changes: list[FileChange], config: Config) -> str:
    """Generate a summary of diffs for all changes.

    Creates a formatted summary of all diffs, shortening them if necessary.

    Args:
        changes: List of file changes to summarize.
        config: Configuration object with settings for the commit message generator.

    Returns:
        str: A formatted summary of all diffs.
    """
    return "\n".join(
        [
            shorten_diff(
                f"File [{i + 1}]: {change.path}\nStatus: {change.status}\nChanges:\n{change.diff}\n",
                config,
            )
            for i, change in enumerate(changes)
        ]
    )


def determine_prompt(
    combined_text: str, changes: list[FileChange], diff_lines: int, config: Config
) -> str:
    """Determine the appropriate prompt based on the size of changes.

    Uses a simple prompt for small changes and a comprehensive prompt for larger ones.
    """
    # For small changes (less than 50 lines), use a simple inline commit message
    if diff_lines < config.prompt_threshold:
        return generate_simple_prompt(combined_text, config)

    # For larger changes, create a comprehensive commit message with details
    diffs_summary = generate_diff_summary(changes, config)

    return generate_comprehensive_prompt(combined_text, diffs_summary, config)


def get_icon_instruction(icon: bool) -> str:
    """Get the instruction for including icons in the commit message."""
    if icon:
        return """
        7. Include an appropriate emoji at the start of the commit message based on the change type:
           ✨ for new features (feat)
           🐛 for bug fixes (fix)
           ♻️ for refactoring (refactor)
           🔥 for removing code (remove)
           📝 for documentation (docs)
           ✅ for tests (test)
           🚀 for deployment (deploy)
        """
    return "7. Do not include any emojis in the commit message."


def generate_simple_prompt(combined_text: str, config: Config) -> str:
    """Generate a prompt for a simple commit message.

    Creates a prompt instructing the model to generate a conventional commit message
    for smaller changes.
    """
    force_brackets_line = (
        "Please use brackets with conventional commits [e.g. feat(main): ...]"
        if config.force_brackets
        else ""
    )

    icon_instruction = get_icon_instruction(config.icon)

    return f"""
        Analyze these file changes and generate a conventional commit message:
        {combined_text}
        Respond with only a single-line commit message following conventional commits format.
        Keep it brief and focused on the main change.
        {force_brackets_line}
        {icon_instruction}
        """


def generate_comprehensive_prompt(
    combined_text: str, diffs_summary: str, config: Config
) -> str:
    """Generate a prompt for a comprehensive commit message.

    Creates a detailed prompt with rules and guidelines for generating a
    comprehensive conventional commit message.
    """
    force_brackets_line = (
        "Please use brackets with conventional commits [e.g. feat(main): ...]"
        if config.force_brackets
        else ""
    )

    icon_instruction = get_icon_instruction(config.icon)

    return f"""
    Analyze these file changes and generate a detailed conventional commit message:

    Changed Files:
    {combined_text}

    Detailed Changes:
    {diffs_summary}

    Generate a commit message in this format:
    <type>[optional scope]: <description>

    [optional body]
    - Bullet points summarizing main changes
    - Include any breaking changes

    [optional footer]

    Rules:
    1. First line should be a concise summary (50-72 chars)
    2. Use present tense ("add" not "added")
    3. Include relevant scope if changes are focused
    4. Add detailed bullet points for significant changes
    5. Mention breaking changes if any
    6. Reference issues/PRs if applicable
    {icon_instruction}
    
    {force_brackets_line}
    Respond with ONLY the commit message, no explanations.
    """


def model_prompt(
    prompt: str, tool_calls: dict[str, Any], config: Config
) -> Optional[str]:
    """Send a prompt to the model and get a response.

    Wraps the model call with a progress indicator.

    Args:
        prompt: The prompt to send to the model.
        tool_calls: The tool calls to include in the request.
        config: Configuration object with settings for the commit message generator.

    Returns:
        str: The model's response.
    """
    return execute_with_progress(get_model_response, prompt, tool_calls, config)


@with_ssl_workaround
def get_model_response(
    prompt: str, tool_calls: dict[str, Any], config: Config
) -> str | None:
    """Get a response from the model using concurrent requests.

    Makes multiple concurrent API calls to the model with the given prompt and tool calls
    using thread pooling. Returns the first successful response.
    
    This function is decorated with the SSL workaround to handle legacy SSL renegotiation issues
    that may occur when connecting to certain APIs.

    Args:
        prompt: The prompt to send to the model.
        tool_calls: The tool calls to include in the request.
        config: Configuration object with settings for the commit message generator.

    Returns:
        Optional[str]: The first successful model response, or None if all attempts failed.
    """
    # The internal function to make a single model API call
    def make_model_call(_) -> str | None:
        try:
            response = client.chat.completions.create(
                model=config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Follow instructions precisely and respond concisely.",
                    },
                    {"role": "user", "content": prompt},
                ],
                tool_calls=[tool_calls],  # Wrap in list as API expects array of tool calls
            )
            return (
                response.choices[0].message.content
                if response and response.choices
                else None
            )
        except Exception as e:
            # Provide more detailed error message for SSL errors
            if "SSL" in str(e) and "UNSAFE_LEGACY_RENEGOTIATION_DISABLED" in str(e):
                console.print(
                    "⚠️ "
                    f"[yellow]SSL renegotiation error encountered with API. "
                    f"SSL workaround was applied but the issue persists. "
                    f"This might be due to server-side configuration.[/yellow]\n"
                    "[bold orange]🔁 Try to run again[/bold orange]"
                )
            else:
                console.print(f"[dim]Thread encountered error: {e!s}[/dim]")
            return None

    # Use ThreadPoolExecutor to make concurrent API calls
    with ThreadPoolExecutor(max_workers=config.thread_count) as executor:
        # Start multiple concurrent requests
        futures = [executor.submit(make_model_call, i) for i in range(config.thread_count)]
        
        # Wait for the first successful result or until all fail
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:  # If we got a valid response
                    # Cancel remaining futures
                    for f in futures:
                        if not f.done():
                            f.cancel()
                    return result
            except Exception:
                continue  # Skip failed futures
    
    # If all threads failed, report the error
    console.print("[red]All model request threads failed[/red]")
    return None


def execute_with_progress(
    func: Callable[..., Optional[str]], *args: object
) -> Optional[str]:
    """Execute a function with a progress indicator.

    Shows a spinner while waiting for the function to complete.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Waiting for model response...", total=None)
        return execute_with_timeout(func, progress, task, *args)


def execute_with_timeout(
    func: Callable[..., Optional[str]],
    progress: Progress,
    task: TaskID,
    *args: object,
    timeout: Optional[int] = None,
) -> Optional[str]:
    """Execute a function with a timeout.

    Runs the function in a separate thread and cancels it if it takes too long.
    Handles errors and cleans up the progress display.

    Args:
        func: The function to execute.
        progress: The progress object to update.
        task: The task ID to update.
        *args: Arguments to pass to the function.
        timeout: The timeout in seconds. If None, uses the config's fallback_timeout.

    Returns:
        The result of the function, or None if it timed out or raised an exception.
    """
    # Extract config from args if it's the last argument
    config: Optional[Config] = (
        args[-1] if args and isinstance(args[-1], Config) else None
    )
    timeout_value = timeout or (cast(int, config.fallback_timeout) if config else 10)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(func, *args)
        try:
            response = future.result(timeout=timeout_value)
            return process_response(response)
        except (TimeoutError, Exception) as e:
            handle_error(e)
            return None
        finally:
            progress.remove_task(task)


def process_response(response: str | None) -> str | None:
    """Process the response from the model.

    Formats and displays the first line of the response and returns the full message.
    """
    if not response:
        return None
    message = response.strip()
    first_line = message.split("\n")[0] if "\n" in message else message
    console.print(f"[dim]Generated message:[/dim] [cyan]{first_line}[/cyan]")
    return message


def handle_error(error: Exception) -> None:
    """Handle an error that occurred during model response.

    Displays an appropriate message based on the type of error.
    """
    if isinstance(error, TimeoutError):
        console.print(
            "[yellow]Model response timed out, using fallback message[/yellow]"
        )
    else:
        console.print(
            f"[yellow]Error in model response, using fallback message: {error!s}[/yellow]"
        )


def commit_changes(files: list[str], message: str) -> None:
    """Commit the changes to the specified files with the given message.

    Stages the files, commits them with the provided message, and displays the result.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        # Stage files
        stage_files(files, progress)

        # Commit changes
        commit_result = do_commit(message, progress)

        # Display result
        display_commit_result(commit_result, message)


def do_commit(message: str, progress: Progress) -> tuple[str, int]:
    """Perform the actual git commit.

    Executes the git commit command with the given message and tracks progress.
    """
    task = progress.add_task("Committing changes...", total=1)
    stdout, _, code = run_git_command(["git", "commit", "-m", message])
    progress.update(task, advance=1)
    return stdout, code


def stage_files(files: list[str], progress: Progress) -> None:
    """Stage files for commit.

    Adds each file to the git staging area and tracks progress.
    """
    stage_task = progress.add_task("Staging files...", total=len(files))
    for file_path in files:
        run_git_command(["git", "add", "--", file_path])
        progress.advance(stage_task)


def display_commit_result(result: tuple[str, int], message: str) -> None:
    """Display the result of the commit operation.

    Shows a success or error message based on the commit result.
    """
    stderr, code = result
    if code == 0:
        console.print(f"[green]✔ Successfully committed:[/green] {message}")
    else:
        console.print(f"[red]✘ Error committing changes:[/red] {stderr}")


def reset_staging() -> None:
    """Reset the git staging area.

    Unstages all changes by resetting the HEAD pointer.
    """
    run_git_command(["git", "reset", "HEAD"])


def format_diff_lines(lines: int) -> str:
    """Format the number of diff lines with color based on size.

    Uses green for small changes, yellow for medium, and red for large changes.
    """
    if lines < GREEN_FORMAT_THRESHOLD:
        return f"[green]{lines}[/green]"
    if lines < YELLOW_FORMAT_THRESHOLD:
        return f"[yellow]{lines}[/yellow]"
    return f"[red]{lines}[/red]"


def format_time_ago(timestamp: float) -> str:
    """Format a timestamp as a human-readable time ago string.

    Converts a timestamp to a relative time like "5m ago" or "2h ago".
    Returns "N/A" for invalid timestamps.
    """
    if timestamp == 0:
        return "N/A"

    diff = datetime.now(UTC).timestamp() - timestamp
    time_units = [(86400, "d"), (3600, "h"), (60, "m"), (0, "just now")]

    for seconds, unit in time_units:
        if diff >= seconds:
            if seconds == 0:
                return unit
            count = int(diff / seconds)
            return f"{count}{unit} ago"

    # Time units is None
    return "N/A"


def create_staged_table() -> Table:
    """Create a table for displaying staged changes.

    Returns a formatted rich Table with appropriate styling and title.
    """
    return Table(
        title="Staged Changes",
        show_header=True,
        header_style="bold magenta",
        show_lines=True,
    )


def config_staged_table(table: Table) -> None:
    """Configure columns for the staged changes table.

    Adds columns for status, file path, type, changes, and last modified time.
    """
    table.add_column("Status", justify="center", width=8)
    table.add_column("File Path", width=40)
    table.add_column("Type", justify="center", width=10)
    table.add_column("Changes", justify="right", width=10)
    table.add_column("Last Modified", justify="right", width=12)


def apply_table_styling(table: Table, change: FileChange) -> None:
    """Apply styling to a row in the staged changes table.

    Sets colors based on the file status and adds formatted values to the table.
    """
    status_color = {"M": "yellow", "A": "green", "D": "red", "R": "blue"}.get(
        change.status, "white"
    )

    table.add_row(
        f"[{status_color}]{change.status}[/{status_color}]",
        str(change.path),
        f"[green]{change.type}[/green]",
        format_diff_lines(change.diff_lines),
        format_time_ago(change.last_modified),
    )


def display_changes(changes: list[FileChange]) -> None:
    """Display a table of all file changes.

    Creates, configures and populates a table showing all file changes with their details.
    """
    # Create table
    table = create_staged_table()

    # Config the table
    config_staged_table(table)

    for change in changes:
        apply_table_styling(table, change)

    console.print(table)


def find_git_root() -> Path:
    """Find the root directory of the git repository.

    Uses git rev-parse to find the repository root.
    Raises FileNotFoundError if not in a git repository.
    """

    def raise_git_error(message: str, exception: Optional[Exception]) -> NoReturn:
        """Helper function to raise a FileNotFoundError."""
        raise FileNotFoundError(message) from exception

    try:
        # Use git rev-parse to find the root of the repository
        stdout, stderr, code = run_git_command(["git", "rev-parse", "--show-toplevel"])
        if code != 0:
            raise_git_error(f"Git error: {stderr}", None)

        # Get the absolute path and normalize it
        root_path = Path(stdout.strip()).resolve()

        if not root_path.exists() or not (root_path / ".git").exists():
            raise_git_error("Not a git repository", None)

    except Exception as e:
        raise_git_error(f"Failed to determine git root: {e!s}", e)
    else:
        return root_path


def handle_non_existent_git_repo() -> None:
    """Verify git repository exists and change to its root directory.

    Changes the current working directory to the git repository root.
    Exits the program if not in a git repository or unable to change directory.
    """
    try:
        root = find_git_root()
        try:
            os.chdir(root)
        except OSError as e:
            console.print(f"[red]Error: Failed to change directory: {e!s}[/red]")
            sys.exit(1)
    except FileNotFoundError as e:
        console.print(f"[red]Error: {e!s}[/red]")
        sys.exit(1)


def main(config: Optional[Config] = None) -> None:
    """Main entry point for the program.

    Handles repository verification, gets file changes, and processes commit messages.

    Args:
        config: Configuration object with settings for the commit message generator.
               If None, uses default configuration.
    """
    if config is None:
        from c4f.config import default_config

        config = default_config

    handle_non_existent_git_repo()
    reset_staging()
    changes = get_valid_changes()
    if not changes:
        exit_with_no_changes()

    display_changes(changes)
    groups = group_related_changes(changes)

    accept_all = False
    for group in groups:
        if accept_all:
            process_change_group(group, config, accept_all=True)
        else:
            accept_all = process_change_group(group, config)


def get_valid_changes() -> Optional[List[FileChange]]:
    """Get a list of valid file changes.

    Parses git status and processes any changed files found.
    """
    changed_files = parse_git_status()
    if not changed_files:
        return []

    return process_changed_files(changed_files)


def process_changed_files(
    changed_files: List[Tuple[STATUS_TYPE, str]],
) -> List[FileChange]:
    """Process a list of changed files.

    Creates FileChange objects for each changed file with progress tracking.
    """
    changes = []
    with create_progress_bar() as progress:
        analyze_task, diff_task = create_progress_tasks(progress, len(changed_files))
        for status, file_path in changed_files:
            file_change = process_single_file(status, file_path, progress, diff_task)
            if file_change:
                changes.append(file_change)
            progress.advance(analyze_task)
    return changes


def create_progress_bar() -> Progress:
    """Create a progress bar for tracking file analysis.

    Returns a configured rich Progress object.
    """
    return Progress(
        "[progress.description]{task.description}",
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    )


def create_progress_tasks(progress: Progress, total: int) -> Tuple[TaskID, TaskID]:
    """Create tasks for tracking file analysis progress.

    Returns task IDs for analyzing files and getting diffs.
    """
    analyze_task = progress.add_task("Analyzing files...", total=total)
    diff_task = progress.add_task("Getting file diffs...", total=total)
    return analyze_task, diff_task


def process_single_file(
    status: STATUS_TYPE, file_path: str, progress: Progress, diff_task: TaskID
) -> Optional[FileChange]:
    """Process a single changed file.

    Gets the diff for the file and creates a FileChange object if a diff is found.
    For empty files, creates a FileChange object with an empty diff.
    """
    path = Path(file_path)
    diff = get_file_diff(file_path)
    progress.advance(diff_task)

    # Handle empty files (they will have empty diffs but should still be included)
    if not diff and path.exists() and path.is_file() and path.stat().st_size == 0:
        file_type = analyze_file_type(path, "")
        return FileChange(path, status, "Empty file", file_type)
    if diff:
        file_type = analyze_file_type(path, diff)
        return FileChange(path, status, diff, file_type)
    return None


def create_file_change(status: STATUS_TYPE, file_path: str) -> Optional[FileChange]:
    """Create a FileChange object for a changed file.

    Gets the diff and determines the file type.
    Returns None if no diff is found, unless it's an empty file.
    """
    path = Path(file_path)
    diff = get_file_diff(file_path)

    # Handle empty files (they will have empty diffs but should still be included)
    if not diff and path.exists() and path.is_file() and path.stat().st_size == 0:
        file_type = analyze_file_type(path, "")
        return FileChange(path, status, "Empty file", file_type)
    if diff:
        file_type = analyze_file_type(path, diff)
        return FileChange(path, status, diff, file_type)
    return None


def exit_with_no_changes() -> NoReturn:
    """Exit the program when no changes are found.

    Displays a message and exits with status code 0.
    """
    console.print("[yellow]⚠ No changes to commit[/yellow]")
    sys.exit(0)


def process_change_group(
    group: list[FileChange], config: Config, accept_all: bool = False
) -> bool:
    """Process a group of related file changes.

    Args:
        group: List of file changes to process.
        config: Configuration object with settings for the commit message generator.
        accept_all: Whether to accept all future commits without prompting.

    Returns:
        bool: True if the user chose to accept all future commits.
    """
    message = generate_commit_message(group, config)

    # Style Message
    md = Markdown(message)

    # Capture the rendered Markdown output
    with console.capture() as capture:
        console.print(md, end="")  # Ensure no extra newline
    rendered_message = capture.get()

    display_commit_preview(rendered_message)  # Pass the properly rendered string

    if accept_all:
        return do_group_commit(group, message, True)

    response = get_valid_user_response()
    return handle_user_response(response, group, message)


def get_valid_user_response() -> str:
    """Get a valid response from the user for commit actions.

    Prompts the user until a valid response is provided.
    """
    prompt = "Proceed with commit? ([Y/n] [/e] to edit [all/a] for accept all): "
    while True:
        response = input(prompt).lower().strip()
        if response in ["y", "n", "e", "a", "all", ""]:
            return response
        prompt = "Invalid response. " + prompt


def handle_user_response(response: str, group: list[FileChange], message: str) -> bool:
    """Handle the user's response for a commit action.

    Performs the appropriate action based on the user's response:
    - y/empty: commit the changes
    - n: skip the changes
    - e: edit the commit message
    - a/all: accept all future commits

    Returns True if the user chose to accept all future commits.
    """
    actions = {
        "a": lambda: do_group_commit(group, message, True),
        "all": lambda: do_group_commit(group, message, True),
        "y": lambda: do_group_commit(group, message),
        "": lambda: do_group_commit(group, message),
        "n": lambda: console.print("[yellow]Skipping these changes...[/yellow]"),
        "e": lambda: do_group_commit(group, input("Enter new commit message: ")),
    }

    if response not in actions:
        console.print("[red]Invalid response. Exiting...[/red]")
        sys.exit(1)

    actions[response]()
    return response in ["a", "all"]


def do_group_commit(
    group: list[FileChange], message: str, accept_all: bool = False
) -> bool:
    """Commit a group of changes and return whether to accept all future commits.

    Commits the files in the group with the given message.
    Returns the accept_all flag to indicate whether to accept all future commits.
    """
    files = [str(change.path) for change in group]
    commit_changes(files, message)
    return accept_all


def display_commit_preview(message: str) -> None:
    """Display a preview of the commit message.

    Shows the commit message in a formatted panel.
    """
    console.print(
        Panel(
            f"Proposed commit message:\n[bold cyan]{message}[/bold cyan]",
            title="Commit Preview",
            border_style="blue",
        )
    )


if __name__ == "__main__":
    from c4f.config import default_config

    main(default_config)
