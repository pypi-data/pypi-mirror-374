"""
CLI interface for c4f (Commit For Free) - An Intelligent Git Commit Message Generator.

This module provides a command-line interface for the c4f tool, allowing users to configure
and customize the commit message generation process through various command-line arguments.

Arguments:
    -h, --help              Show this help message and exit
    -v, --version           Show program's version number and exit
    -r, --root PATH        Set the root directory [default: current project root]
    -m, --model MODEL      Set the AI model to use [default: gpt-4-mini]
    -a, --attempts NUM     Set the number of generation attempts [default: 3]
    -t, --timeout SEC      Set the fallback timeout in seconds [default: 10]
    --threads NUM          Set the number of concurrent threads for requests [default: 3]
    -f, --force-brackets   Force conventional commit type with brackets [default: False]
    -i, --icon             Add emoji icons to commit messages [default: False]
    -A, --ascii-only       Use ASCII alternatives instead of Unicode emojis [default: False]
    --models               Display all available models and exit
"""

import argparse
import contextlib
import locale
import os
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import g4f  # type: ignore
from rich.box import ASCII, ROUNDED, Box
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from c4f.utils import console
from c4f.config import Config

# Import main functionality here to avoid circular imports
from c4f.main import main as run_main

__all__ = ["parse_args", "run_main"]


# Define color codes for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def _create_patched_popen_init(original_init: Callable) -> Callable[..., None]:
    """
    Create a patched version of subprocess.Popen.__init__ that ensures UTF-8 encoding.

    Args:
        original_init: The original subprocess.Popen.__init__ function.

    Returns:
        A patched initialization function for subprocess.Popen.
    """

    def patched_init(self: subprocess.Popen, *args: List, **kwargs: Dict) -> None:
        kwargs = _ensure_utf8_encoding(kwargs)
        kwargs = _ensure_utf8_environment(kwargs)
        original_init(self, *args, **kwargs)

    return patched_init


def _ensure_utf8_encoding(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure UTF-8 encoding with error handling is set in kwargs when needed.

    Args:
        kwargs: The keyword arguments dictionary for subprocess.Popen.

    Returns:
        Updated kwargs dictionary with proper encoding settings.
    """
    if "encoding" not in kwargs and (
        kwargs.get("text", False) or kwargs.get("universal_newlines", False)
    ):
        kwargs["encoding"] = "utf-8"
        kwargs["errors"] = "replace"
    return kwargs


def _ensure_utf8_environment(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure the environment variables include UTF-8 encoding settings.

    Args:
        kwargs: The keyword arguments dictionary for subprocess.Popen.

    Returns:
        Updated kwargs dictionary with proper environment settings.
    """
    if "env" not in kwargs or kwargs["env"] is not None:
        env = os.environ.copy() if "env" not in kwargs else kwargs["env"].copy()
        env["PYTHONIOENCODING"] = "utf-8"
        kwargs["env"] = env
    return kwargs


# Fix for subprocess encoding issues on Windows
def patch_subprocess_for_windows() -> None:
    """
    Monkey patch subprocess.Popen to ensure all subprocess calls use UTF-8 encoding.
    This fixes common UnicodeDecodeError issues on Windows terminals.
    """
    original_init = subprocess.Popen.__init__
    subprocess.Popen.__init__ = _create_patched_popen_init(original_init)  # type: ignore


def fix_windows_encoding() -> None:
    """Fix encoding issues on Windows platforms to ensure proper UTF-8 handling."""
    if sys.platform == "win32":
        _configure_stdout_stderr_encoding()
        _set_environment_encoding()
        patch_subprocess_for_windows()
        _configure_locale_encoding()


def _configure_stdout_stderr_encoding() -> None:
    """Configure stdout and stderr to use UTF-8 encoding with appropriate error handling."""
    with contextlib.suppress(Exception):
        if hasattr(sys.stdout, "reconfigure"):
            _reconfigure_streams_python37_plus()
        else:
            _reconfigure_streams_python_legacy()


def _reconfigure_streams_python37_plus() -> None:
    """Reconfigure stdout and stderr using Python 3.7+ reconfigure method."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")  # type: ignore


def _reconfigure_streams_python_legacy() -> None:
    """Reconfigure stdout and stderr for Python versions before 3.7."""
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "backslashreplace")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "backslashreplace")


def _set_environment_encoding() -> None:
    """Set environment variables to prefer UTF-8 encoding."""
    os.environ["PYTHONIOENCODING"] = "utf-8"


def _configure_locale_encoding() -> None:
    """Configure locale settings to support UTF-8 where possible."""
    try:
        locale.setlocale(locale.LC_ALL, ".UTF-8")
    except locale.Error:
        with contextlib.suppress(locale.Error):
            locale.setlocale(locale.LC_ALL, "")


fix_windows_encoding()

# ASCII art banner for c4f
BANNER_ASCII = r"""
   _____ _  _     _____ 
  / ____| || |   |  ___|
 | |    | || |_  | |_   
 | |    |__   _| |  _|  
 | |____   | |   | |    
  \_____|  |_|   |_|    
                        
 Commit For Free - AI-Powered Git Commit Message Generator
"""


# Create formatted banner with Rich
def create_banner_text() -> Text:
    """Create the initial banner text with base styling."""
    banner_text = Text(BANNER_ASCII)
    banner_text.stylize("bold blue")
    return banner_text


def style_banner_lines(banner_text: Text) -> Text:
    """Style individual banner lines with different styles for title."""
    title_line = " Commit For Free - AI-Powered Git Commit Message Generator"
    banner_lines = banner_text.plain.split("\n")
    styled_banner = Text()

    for i, line in enumerate(banner_lines):
        if title_line.strip() in line:
            styled_banner.append(line.replace(title_line, ""), style="bold blue")
            styled_banner.append(title_line, style="bold green")
        else:
            styled_banner.append(line, style="bold blue")
        if i < len(banner_lines) - 1:
            styled_banner.append("\n")

    return styled_banner


def determine_box_style() -> Box:
    """Determine the appropriate box style based on platform."""
    # Use simple ASCII characters for the panel border on Windows
    # to avoid encoding issues
    return ASCII if sys.platform == "win32" else ROUNDED


def create_banner_panel(styled_banner: Text, box_style: Box) -> Panel:
    """Create a panel containing the styled banner."""
    return Panel(
        styled_banner,
        border_style="cyan",
        padding=(0, 1),
        title="C4F",
        title_align="left",
        box=box_style,
    )


def get_rich_banner() -> Panel:
    """Create and return a rich formatted banner for the application."""
    # Create banner_text and style it
    banner_text = create_banner_text()
    styled_banner = style_banner_lines(banner_text)
    box_style = determine_box_style()

    # Create the panel directly without any template substitution
    return Panel(
        styled_banner,
        border_style="cyan",
        padding=(0, 1),
        title="C4F",
        title_align="left",
        box=box_style,
    )


# For backward compatibility
BANNER = BANNER_ASCII


# noinspection PyProtectedMember
class ColoredHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """Custom help formatter that adds colors to the help text."""

    def __init__(
        self,
        prog: str,
        indent_increment: int = 2,
        max_help_position: int = 30,
        width: Optional[int] = None,
        color: bool = True,
    ) -> None:
        super().__init__(prog, indent_increment, max_help_position, width)
        self.color = color

    def _format_action(self, action: argparse.Action) -> str:
        # Get the original help text
        help_text = super()._format_action(action)

        if not self.color:
            return help_text

        # Add colors to different parts of the help text
        help_text = help_text.replace(
            "usage:", f"{Colors.BOLD}{Colors.GREEN}usage:{Colors.ENDC}"
        )
        help_text = help_text.replace(
            "options:", f"{Colors.BOLD}{Colors.BLUE}options:{Colors.ENDC}"
        )

        # Highlight option strings
        for opt in ["-h", "--help", "-v", "--version"]:
            if opt in help_text:
                help_text = help_text.replace(
                    f"{opt}", f"{Colors.BOLD}{Colors.YELLOW}{opt}{Colors.ENDC}"
                )

        return help_text

    def _format_usage(self, usage: Any, actions: Any, groups: Any, prefix: Any) -> str:  # noqa: ANN401
        usage_text = super()._format_usage(usage, actions, groups, prefix)

        if not self.color:
            return usage_text

        # Add colors to the usage text
        return usage_text.replace(
            "usage:", f"{Colors.BOLD}{Colors.GREEN}usage:{Colors.ENDC}"
        )

    def _format_action_invocation(self, action: argparse.Action) -> str:
        text = super()._format_action_invocation(action)

        if not self.color or not action.option_strings:
            return text

        # Add colors to option strings
        for opt in action.option_strings:
            text = text.replace(
                f"{opt}", f"{Colors.BOLD}{Colors.YELLOW}{opt}{Colors.ENDC}"
            )

        return text


def get_banner_description(color: bool = True) -> str:
    """Get the banner description for the CLI.

    Args:
        color (bool): Whether to use colored output.

    Returns:
        str: The banner description.
    """
    if not color:
        return f"{BANNER_ASCII}\nIntelligent Git Commit Message Generator"

    try:
        # Simply use color codes for terminal directly instead of Rich's capture mechanism
        # which can be problematic on some systems
        colored_ascii = "\n".join(
            [
                f"{Colors.BOLD}{Colors.BLUE}{line}{Colors.ENDC}"
                for line in BANNER_ASCII.splitlines()
            ]
        )

        # Add a colorful title
        colored_ascii = colored_ascii.replace(
            f"{Colors.BOLD}{Colors.BLUE} Commit For Free - AI-Powered Git Commit Message Generator{Colors.ENDC}",
            f"{Colors.BOLD}{Colors.GREEN} Commit For Free - AI-Powered Git Commit Message Generator{Colors.ENDC}",
        )

    except Exception as e:
        # Fallback to plain banner if coloring fails
        warnings.warn(
            f"Failed to create colored banner: {e}", stacklevel=2, category=UserWarning
        )
        return f"{BANNER_ASCII}\nIntelligent Git Commit Message Generator"
    else:
        return f"{colored_ascii}\n"


def get_epilog_text(color: bool = True) -> str:
    """Get the epilog text for the CLI.

    Args:
        color (bool): Whether to use colored output.

    Returns:
        str: The epilog text.
    """
    repo_url = "https://github.com/alaamer12/c4f"
    if color:
        return f"{Colors.GREEN}For more information, visit: {repo_url}{Colors.ENDC}"
    return f"For more information, visit: {repo_url}"


def create_argument_parser(color: bool = True) -> argparse.ArgumentParser:
    """Create and configure the argument parser for the CLI.

    Args:
        color (bool): Whether to use colored output.

    Returns:
        argparse.ArgumentParser: Configured argument parser with program metadata.
    """
    description = get_banner_description(color)
    epilog = get_epilog_text(color)

    return argparse.ArgumentParser(
        description=description,
        formatter_class=lambda prog: ColoredHelpFormatter(prog, color=color),
        epilog=epilog,
        prog="c4f",
        add_help=True,
        allow_abbrev=True,
    )


def add_version_argument(parser: argparse.ArgumentParser) -> None:
    """Add version argument to the parser.

    Args:
        parser (argparse.ArgumentParser): The argument parser to add the version argument to.
    """
    from c4f import __version__

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + __version__,
        help="Show program's version number and exit",
    )


def add_directory_argument(parser: argparse.ArgumentParser) -> None:
    """Add root directory argument to the parser.

    Args:
        parser (argparse.ArgumentParser): The argument parser to add the directory argument to.
    """
    parser.add_argument(
        "-r",
        "--root",
        type=Path,
        help="Set the root directory for git operations [default: current project root]",
        default=Path.cwd(),
        metavar="PATH",
        dest="root",
    )


def add_model_argument(parser: argparse.ArgumentParser) -> None:
    """Add AI model argument to the parser.

    Args:
        parser (argparse.ArgumentParser): The argument parser to add the model argument to.
    """
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        help="Set the AI model to use for commit message generation [default: default]",
        default="default",
        metavar="MODEL",
        choices=["default", "MetaAI", "gpt-4-mini", "gpt-4"],
        dest="model",
    )


def add_generation_arguments(parser: argparse.ArgumentParser) -> None:
    """Add arguments related to message generation.

    Args:
        parser (argparse.ArgumentParser): The argument parser to add the generation arguments to.
    """
    generation_group = parser.add_argument_group(
        "Generation Options", "Configure the commit message generation process"
    )

    generation_group.add_argument(
        "-a",
        "--attempts",
        type=int,
        help="Set the number of generation attempts before falling back [default: 3]",
        default=3,
        metavar="NUM",
        choices=range(1, 11),
        dest="attempts",
    )

    generation_group.add_argument(
        "-t",
        "--timeout",
        type=int,
        help="Set the fallback timeout in seconds for model response [default: 10]",
        default=10,
        metavar="SEC",
        choices=range(1, 61),
        dest="timeout",
    )
    
    generation_group.add_argument(
        "--threads",
        type=int,
        help="Set the number of concurrent threads for model requests [default: 3]",
        default=3,
        metavar="NUM",
        choices=range(1, 6),
        dest="thread_count",
    )


def add_formatting_arguments(parser: argparse.ArgumentParser) -> None:
    """Add formatting arguments to the parser.

    Args:
        parser (argparse.ArgumentParser): The argument parser to add the formatting arguments to.
    """
    formatting_group = parser.add_argument_group(
        "Formatting Options", "Configure the commit message format"
    )

    formatting_group.add_argument(
        "-f",
        "--force-brackets",
        action="store_true",
        help="Force conventional commit type with brackets (e.g., feat(scope): message)",
        dest="force_brackets",
    )

    formatting_group.add_argument(
        "-i",
        "--icon",
        action="store_true",
        help="Add emoji icons to commit messages (e.g., ✨ feat: new feature)",
        dest="icon",
    )

    formatting_group.add_argument(
        "-A",
        "--ascii-only",
        action="store_true",
        help="Use ASCII alternatives instead of Unicode emojis for better terminal compatibility",
        dest="ascii_only",
    )


def add_all_arguments(parser: argparse.ArgumentParser) -> None:
    """Add all arguments to the parser.

    Args:
        parser (argparse.ArgumentParser): The argument parser to add the arguments to.
    """
    add_version_argument(parser)
    add_directory_argument(parser)
    add_model_argument(parser)
    add_generation_arguments(parser)
    add_formatting_arguments(parser)
    add_show_models_argument(parser)


def add_show_models_argument(parser: argparse.ArgumentParser) -> None:
    """Add a flag to display available models."""
    # Add models command
    parser.add_argument(
        "--models",
        action="store_true",
        help="Display all available models and exit",
        dest="show_models",
    )



def parse_args() -> argparse.Namespace:
    """Create parser, add arguments, and parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    # First parse just the color argument to determine if we should use colors
    pre_parser = argparse.ArgumentParser(add_help=False)

    # Parse known args to get the color setting
    pre_args, _ = pre_parser.parse_known_args()

    # Now create the full parser with the correct color setting
    parser = create_argument_parser(color=True)

    # Add all arguments
    add_all_arguments(parser)

    args = parser.parse_args()

    # If root is specified, change to that directory
    if args.root:
        try:
            os.chdir(args.root)
        except (OSError, FileNotFoundError) as e:
            parser.error(f"Failed to change to directory {args.root}: {e!s}")

    return args


# noinspection PyBroadException
def display_banner() -> None:
    """Display the application banner with error handling."""
    try:
        # Use direct ANSI color codes for a more compatible approach
        colored_ascii = "\n".join(
            [
                f"{Colors.BOLD}{Colors.BLUE}{line}{Colors.ENDC}"
                for line in BANNER_ASCII.splitlines()
            ]
        )

        # Add a colorful title
        colored_ascii = colored_ascii.replace(
            f"{Colors.BOLD}{Colors.BLUE} Commit For Free - AI-Powered Git Commit Message Generator{Colors.ENDC}",
            f"{Colors.BOLD}{Colors.GREEN} Commit For Free - AI-Powered Git Commit Message Generator{Colors.ENDC}",
        )

        print(colored_ascii)  # noqa: T201
    except UnicodeEncodeError:
        # Fallback to plain banner if rich formatting fails
        print(BANNER_ASCII)  # noqa: T201
    except Exception:
        # Silently continue if any display errors occur - the banner is nice to have but not critical
        print("   C4F - Commit For Free")  # noqa: T201


def create_config_from_args(args: argparse.Namespace) -> Config:
    """Create a Config object from command line arguments.

    Args:
        args: Parsed command line arguments.

    Returns:
        Config: A configuration object with settings from the command line.
    """
    # Convert string model name to g4f model object
    model_mapping = {
        "default": g4f.models.default,
        "MetaAI": g4f.models.meta,
        "gpt-4-mini": g4f.models.gpt_4o_mini,
        "gpt-4": g4f.models.gpt_4o,
    }

    # Warn about login-required models
    login_required_models = ["gpt-4-mini", "gpt-4"]
    if args.model in login_required_models:
        console.print(
            f"[yellow]⚠️  Warning: Model '{args.model}' may require login and could show 'Login to continue using' messages.[/yellow]"
        )
        console.print(
            f"[cyan]💡 Recommended alternatives: --model default or --model MetaAI[/cyan]"
        )
        console.print(
            f"[dim]🔧 We're working on fixing login-required models in future updates.[/dim]\n"
        )

    model = model_mapping.get(args.model, g4f.models.default)

    return Config(
        force_brackets=args.force_brackets,
        icon=args.icon,
        ascii_only=args.ascii_only,
        fallback_timeout=args.timeout,
        attempt=args.attempts,
        model=model,
        thread_count=args.thread_count,
    )


def display_available_models() -> None:
    """Display all available models from g4f in a formatted table, highlighting recommended ones."""
    
    models = [
        'ARTA', 'Blackbox', 'ChatGLM', 'Chatai', 'DeepInfraChat', 'DocsBot', 
        'Free2GPT', 'FreeGpt', 'ImageLabs', 'LambdaChat', 'Liaobots', 'MetaAI', 
        'OIVSCodeSer0501', 'OIVSCodeSer2', 'OIVSCodeSer5', 'PollinationsAI', 
        'PollinationsImage', 'PuterJS', 'TeachAnything', 'WeWordle', 'Yqcloud', 
        'blackboxai', 'codestral', 'command', 'default', 'evil', 'flux', 
        'grok', 'midjourney', 'o1', 'o3', 'sonar'
    ]

    # Add officially supported model names for display purposes
    if 'gpt-4-mini' not in models:
        models.append('gpt-4-mini')
    if 'gpt-3.5-turbo' not in models:
        models.append('gpt-3-5-turbo')

    # Recommended models based on performance testing and availability
    recommended = {'default', 'MetaAI'}
    login_required = {'gpt-4-mini', 'gpt-3-5-turbo', 'gpt-4'}

    table = Table(title="Available G4F Models", box=determine_box_style())
    table.add_column("Model", style="cyan", header_style="bold magenta")
    table.add_column("Status", style="green")

    # Sort models with recommended ones first
    sorted_models = sorted(models, key=lambda m: (m.lower() not in [r.lower() for r in recommended], m.lower()))
    
    for model in sorted_models:
        if model.lower() in [r.lower() for r in recommended]:
            table.add_row(f"[bold green]{model}[/bold green]", "[green]✅ Working[/green]")
        elif model.lower() in [r.lower() for r in login_required]:
            table.add_row(f"[dim]{model}[/dim]", "[red]⚠️  Login Required[/red]")
        else:
            table.add_row(model, "")
    
    console.print("\n")
    console.print(table)
    console.print(
        f"\nTotal available models: {len(models)} "
        f"| [bold green]{len(recommended)} working without login[/bold green] "
        f"| [red]{len(login_required)} require login[/red]"
    )
    
    # Add usage recommendations
    console.print("\n[green]💡 Recommendations:[/green]")
    console.print("  • Use working models: [cyan]c4f --model default[/cyan] or [cyan]c4f --model MetaAI[/cyan]")
    console.print("  • If models timeout: [cyan]c4f --timeout 30[/cyan]")
    console.print("  • For large commits: break into smaller ones")
    console.print("\n[yellow]⚠️  Note:[/yellow] Models marked as 'Login Required' may show authentication errors.")
    console.print("[dim]🔧 We're working on fixing login-required models in future updates.[/dim]\n")


def main() -> None:
    """Main entry point for the CLI."""
    from c4f.utils import console

    # Check if we're displaying help or version info
    help_flags = ("-h", "--help", "-v", "--version")
    showing_help = any(flag in sys.argv for flag in help_flags)

    # Only display the banner directly if not showing help/version
    # (since help/version output already includes the banner)
    if not showing_help:
        display_banner()

    # Parse command line arguments
    args = parse_args()
    
    # Check if we should display models
    if hasattr(args, 'show_models') and args.show_models:
        display_available_models()
        return

    # Create configuration from arguments
    config = create_config_from_args(args)

    # Run the main program with the configuration
    try:
        run_main(config)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user. Exiting...[/yellow]")
        return


if __name__ == "__main__":
    main()
