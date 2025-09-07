#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
evil-winrm-py
https://github.com/adityatelange/evil-winrm-py
"""

import argparse
import base64
import hashlib
import json
import logging
import os
import re
import shutil
import signal
import sys
import tempfile
import time
import traceback
from importlib import resources
from pathlib import Path

from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import clear
from pypsrp.complex_objects import PSInvocationState
from pypsrp.exceptions import AuthenticationError, WinRMTransportError, WSManFaultError
from pypsrp.powershell import PowerShell, RunspacePool
from requests.exceptions import ConnectionError
from spnego.exceptions import NoCredentialError, OperationNotAvailableError, SpnegoError
from tqdm import tqdm

# check if kerberos is installed
try:
    from krb5._exceptions import Krb5Error
    from gssapi.creds import Credentials as GSSAPICredentials
    from gssapi.raw import Creds as RawCreds
    from gssapi.exceptions import MissingCredentialsError, ExpiredCredentialsError

    is_kerb_available = True
except ImportError:
    is_kerb_available = False

    # If kerberos is not available, define a dummy exception
    class Krb5Error(Exception):
        pass


from evil_winrm_py import __version__
from evil_winrm_py.pypsrp_ewp.wsman import WSManEWP

# --- Constants ---
LOG_PATH = Path.cwd().joinpath("evil_winrm_py.log")
HISTORY_FILE = Path.home().joinpath(".evil_winrm_py_history")
HISTORY_LENGTH = 1000
MENU_COMMANDS = [
    "upload",
    "download",
    "loadps",
    "runps",
    "menu",
    "clear",
    "exit",
]
COMMAND_SUGGESTIONS = []

# --- Colors ---
# ANSI escape codes for colored output
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
BOLD = "\033[1m"


# --- Logging Setup ---
log = logging.getLogger(__name__)


# --- Helper Functions ---
class DelayedKeyboardInterrupt:
    """
    A context manager to delay the handling of a SIGINT (Ctrl+C) signal until
    the enclosed block of code has completed execution.

    This is useful for ensuring that critical sections of code are not
    interrupted by a keyboard interrupt, while still allowing the signal
    to be handled after the block finishes.
    """

    def __enter__(self):
        self.signal_received = False
        self.old_handler = signal.getsignal(signal.SIGINT)

        def handler(sig, frame):
            print(RED + "\n[-] Caught Ctrl+C. Stopping current command..." + RESET)
            self.signal_received = (sig, frame)

        signal.signal(signal.SIGINT, handler)

    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            # raise the signal after the task is done
            self.old_handler(*self.signal_received)


def run_ps_cmd(r_pool: RunspacePool, command: str) -> tuple[str, list, bool]:
    """Runs a PowerShell command and returns the output, streams, and error status."""
    log.info("Executing command: {}".format(command))
    ps = PowerShell(r_pool)
    ps.add_cmdlet("Invoke-Expression").add_parameter("Command", command)
    ps.add_cmdlet("Out-String").add_parameter("Stream")
    ps.invoke()
    return "\n".join(ps.output), ps.streams, ps.had_errors


def get_prompt(r_pool: RunspacePool) -> str:
    """Returns the prompt string for the interactive shell."""
    output, streams, had_errors = run_ps_cmd(
        r_pool, "$pwd.Path"
    )  # Get current working directory
    if not had_errors:
        return f"{RED}evil-winrm-py{RESET} {YELLOW}{BOLD}PS{RESET} {output}> "
    return "PS ?> "  # Fallback prompt


def show_menu() -> None:
    """Displays the help menu for interactive commands."""
    print(BOLD + "\nMenu:" + RESET)
    commands = [
        # ("command", "description")
        ("upload <local_path> <remote_path>", "Upload a file"),
        ("download <remote_path> <local_path>", "Download a file"),
        ("loadps <local_path>.ps1", "Load PowerShell functions from a local script"),
        ("runps <local_path>.ps1", "Run a local PowerShell script on the remote host"),
        ("menu", "Show this menu"),
        ("clear, cls", "Clear the screen"),
        ("exit", "Exit the shell"),
    ]

    for command, description in commands:
        print(f"{CYAN}[+] {command:<55} - {description}{RESET}")
    print("Note: Use absolute paths for upload/download for reliability.\n")


def get_directory_and_partial_name(text: str, sep: str) -> tuple[str, str]:
    """
    Parses the input text to find the directory prefix and the partial name.
    """
    if sep not in ["\\", "/"]:
        raise ValueError("Separator must be either '\\' or '/'")
    # Find the last unquoted slash or backslash
    last_sep_index = text.rfind(sep)
    if last_sep_index == -1:
        # No separator found, the whole text is the partial name in the current directory
        directory_prefix = ""
        partial_name = text
    else:
        split_at = last_sep_index + 1
        directory_prefix = text[:split_at]
        partial_name = text[split_at:]
    return directory_prefix, partial_name


def get_remote_path_suggestions(
    r_pool: RunspacePool,
    directory_prefix: str,
    partial_name: str,
    dirs_only: bool = False,
) -> list[str]:
    """
    Returns a list of remote path suggestions based on the current directory
    and the partial name entered by the user.
    """

    exp = "FullName"
    attrs = ""
    if not re.match(r"^[a-zA-Z]:", directory_prefix):
        # If the path doesn't start with a drive letter, prepend the current directory
        pwd, streams, had_errors = run_ps_cmd(
            r_pool, "$pwd.Path"
        )  # Get current working directory
        directory_prefix = f"{pwd}\\{directory_prefix}"
        exp = "Name"

    if dirs_only:
        attrs = "-Attributes Directory"

    command = f'Get-ChildItem -LiteralPath "{directory_prefix}" -Filter "{partial_name}*" {attrs} -Fo | select -Exp {exp}'
    ps = PowerShell(r_pool)
    ps.add_cmdlet("Invoke-Expression").add_parameter("Command", command)
    ps.add_cmdlet("Out-String").add_parameter("Stream")
    ps.invoke()
    return ps.output


def get_local_path_suggestions(
    directory_prefix: str, partial_name: str, extension: str = None
) -> list[str]:
    """
    Returns a list of local path suggestions based on path entered by the user.
    Optionally filters files by extension (e.g., ".ps1").
    """
    suggestions = []

    # Expand the tilde to the user's home directory
    home = str(Path.home())

    try:
        entries = Path(directory_prefix).expanduser().iterdir()
        for entry in entries:
            if entry.match(f"{partial_name}*"):
                if entry.is_dir():
                    entry = (
                        f"{entry}{os.sep}"  # Append a trailing slash for directories
                    )
                    if directory_prefix.startswith("~"):
                        # If the directory prefix starts with ~, replace home with ~
                        entry = str(entry).replace(home, "~", 1)
                    suggestions.append(str(entry))
                else:
                    if (extension is None) or (
                        entry.suffix.lower() == extension.lower()
                    ):
                        if directory_prefix.startswith("~"):
                            # If the directory prefix starts with ~, replace home with ~
                            entry = str(entry).replace(home, "~", 1)
                        suggestions.append(str(entry))
    except (FileNotFoundError, NotADirectoryError, PermissionError):
        pass
    finally:
        if extension:
            # Sort suggestions alphabetically, prioritizing those that match the extension
            return sorted(suggestions, key=lambda x: not x.endswith(extension))
        return suggestions


class CommandPathCompleter(Completer):
    """
    Completer for command paths in the interactive shell.
    This completer suggests command names based on the user's input.
    """

    def __init__(self, r_pool: RunspacePool):
        self.r_pool = r_pool

    def get_completions(self, document: Document, complete_event):
        dirs_only = False  # Whether to suggest only directories
        text_before_cursor = document.text_before_cursor.lstrip()
        tokens = text_before_cursor.split(maxsplit=1)

        if not tokens:  # Empty input, suggest all commands
            for cmd_sugg in MENU_COMMANDS + COMMAND_SUGGESTIONS:
                yield Completion(cmd_sugg, start_position=0, display=cmd_sugg)
            return

        command_typed_part = tokens[0]

        # Handle .\name or ./name as first-token paths (run from current remote directory)
        if command_typed_part.startswith(".\\") or command_typed_part.startswith("./"):
            path_being_completed = command_typed_part
            # strip surrounding quotes if any
            if path_being_completed.startswith('"') and path_being_completed.endswith(
                '"'
            ):
                path_being_completed = path_being_completed.strip('"')
            directory_prefix, partial_name = get_directory_and_partial_name(
                path_being_completed, sep="\\"
            )
            suggestions = get_remote_path_suggestions(
                self.r_pool, directory_prefix, partial_name
            )
            for sugg_path in suggestions:
                text_to_insert_in_prompt = f".\\" + sugg_path
                if " " in sugg_path:
                    text_to_insert_in_prompt = f'& ".\\{sugg_path}"'
                yield Completion(
                    text_to_insert_in_prompt,
                    start_position=-len(command_typed_part),
                    display=sugg_path,
                )
            return

        # Case 1: Completing the command name itself
        # There's only one token and no trailing space.
        if len(tokens) == 1 and not text_before_cursor.endswith(" "):
            # User is typing the command, -> "downl"
            for cmd_sugg in MENU_COMMANDS + COMMAND_SUGGESTIONS:
                if cmd_sugg.startswith(command_typed_part):
                    yield Completion(
                        cmd_sugg + " ",  # Full suggested command
                        start_position=-len(
                            command_typed_part
                        ),  # Replace the typed part
                        display=cmd_sugg,
                    )
            return

        # Case 2: Completing a path argument
        path_typed_segment = ""  # What the user has typed for the current path argument
        if len(tokens) == 2:
            path_typed_segment = tokens[1]

        actual_command_name = command_typed_part.strip().lower()

        args = quoted_command_split(path_typed_segment.strip())

        suggestions = []
        current_arg_text_being_completed = ""
        directory_prefix = partial_name = ""

        if actual_command_name == "upload":
            # syntax: upload <local_path> <remote_path>
            num_args_present = len(args)

            if num_args_present == 0:
                # User typed "upload "
                # Completing the 1st argument (local_path), currently empty
                current_arg_text_being_completed = ""
                directory_prefix, partial_name = get_directory_and_partial_name(
                    current_arg_text_being_completed, sep=os.sep
                )
                suggestions = get_local_path_suggestions(directory_prefix, partial_name)
            elif num_args_present == 1:
                # We have one argument part, e.g., "upload arg1" or "upload local_path "
                if path_typed_segment.endswith(" "):
                    # 1st argument (local_path) is complete
                    # Completing the 2nd argument (remote_path), currently empty
                    current_arg_text_being_completed = ""
                    directory_prefix, partial_name = get_directory_and_partial_name(
                        current_arg_text_being_completed, sep="\\"
                    )
                    suggestions = get_remote_path_suggestions(
                        self.r_pool, directory_prefix, partial_name
                    )
                else:
                    # Still completing the 1st argument (local_path), e.g., "upload arg1"
                    current_arg_text_being_completed = path_being_completed = args[0]
                    if path_being_completed.startswith('"'):
                        path_being_completed = current_arg_text_being_completed.strip(
                            '"'
                        )
                    directory_prefix, partial_name = get_directory_and_partial_name(
                        path_being_completed, sep=os.sep
                    )
                    suggestions = get_local_path_suggestions(
                        directory_prefix, partial_name
                    )
            elif num_args_present == 2:
                #  We have two argument parts
                # e.g., "upload local_path arg2" or "upload local_path remote_path "
                if path_typed_segment.endswith(" "):
                    # 2nd argument (remote_path) is complete. No more suggestions for "upload".
                    pass
                else:
                    # Completing the 2nd argument (remote_path), e.g., "upload local_path arg2"
                    current_arg_text_being_completed = path_being_completed = args[1]
                    if path_being_completed.startswith('"'):
                        path_being_completed = current_arg_text_being_completed.strip(
                            '"'
                        )
                    directory_prefix, partial_name = get_directory_and_partial_name(
                        path_being_completed, sep="\\"
                    )
                    suggestions = get_remote_path_suggestions(
                        self.r_pool, directory_prefix, partial_name
                    )
            else:
                # More than 2 arguments, e.g., "upload local_path remote_path extra_arg"
                pass
        elif actual_command_name == "download":
            # syntax: download <remote_path> <local_path>
            num_args_present = len(args)

            if num_args_present == 0:
                # User typed "download "
                # Completing 1st arg (remote_path), empty
                current_arg_text_being_completed = ""
                directory_prefix, partial_name = get_directory_and_partial_name(
                    current_arg_text_being_completed, sep="\\"
                )
                suggestions = get_remote_path_suggestions(
                    self.r_pool, directory_prefix, partial_name
                )
            elif num_args_present == 1:
                # We have "download arg1" or "download local_path "
                if path_typed_segment.endswith(" "):
                    # First arg (remote_path) is complete. Completing 2nd arg (local_path), empty.
                    current_arg_text_being_completed = ""
                    directory_prefix, partial_name = get_directory_and_partial_name(
                        current_arg_text_being_completed, sep=os.sep
                    )
                    suggestions = get_local_path_suggestions(
                        directory_prefix, partial_name
                    )
                else:
                    # Still completing 1st arg (remote_path)
                    current_arg_text_being_completed = path_being_completed = args[0]
                    if path_being_completed.startswith('"'):
                        path_being_completed = current_arg_text_being_completed.strip(
                            '"'
                        )
                    directory_prefix, partial_name = get_directory_and_partial_name(
                        path_being_completed, sep="\\"
                    )
                    suggestions = get_remote_path_suggestions(
                        self.r_pool, directory_prefix, partial_name
                    )
            elif num_args_present == 2:
                # We have two argument parts
                # e.g., "download remote_path arg2" or "download remote_path local_path "
                if path_typed_segment.endswith(" "):
                    # 2nd argument (local_path) is complete. No more suggestions for "download".
                    pass
                else:
                    # Completing 2nd arg (local_path)
                    current_arg_text_being_completed = path_being_completed = args[1]
                    if path_being_completed.startswith('"'):
                        path_being_completed = current_arg_text_being_completed.strip(
                            '"'
                        )
                    directory_prefix, partial_name = get_directory_and_partial_name(
                        path_being_completed, sep=os.sep
                    )
                    suggestions = get_local_path_suggestions(
                        directory_prefix, partial_name
                    )
            else:
                # More than 2 arguments, e.g., "download remote_path local_path extra_arg"
                pass
        elif actual_command_name in ["loadps", "runps"]:
            # syntax: loadps <local_path>
            num_args_present = len(args)

            if num_args_present == 0:
                # User typed "loadps "
                # Completing the 1st argument (local_path), currently empty
                current_arg_text_being_completed = ""
                directory_prefix, partial_name = get_directory_and_partial_name(
                    current_arg_text_being_completed, sep=os.sep
                )
                suggestions = get_local_path_suggestions(
                    directory_prefix, partial_name, extension=".ps1"
                )
            elif num_args_present == 1:
                # We have "loadps arg1" or "loadps local_path "
                if path_typed_segment.endswith(" "):
                    # 1st argument (local_path) is complete, currently empty.
                    current_arg_text_being_completed = ""
                    directory_prefix, partial_name = get_directory_and_partial_name(
                        current_arg_text_being_completed, sep=os.sep
                    )
                    suggestions = get_local_path_suggestions(
                        directory_prefix, partial_name, extension=".ps1"
                    )
                else:
                    # Still completing the 1st argument (local_path)
                    current_arg_text_being_completed = path_being_completed = args[0]
                    if path_being_completed.startswith('"'):
                        path_being_completed = current_arg_text_being_completed.strip(
                            '"'
                        )
                    directory_prefix, partial_name = get_directory_and_partial_name(
                        path_being_completed, sep=os.sep
                    )
                    suggestions = get_local_path_suggestions(
                        directory_prefix, partial_name, extension=".ps1"
                    )
            else:
                # More than 1 argument, e.g., "loadps local_path extra_arg"
                pass
        else:
            if actual_command_name == "cd":
                dirs_only = True

            current_arg_text_being_completed = path_being_completed = path_typed_segment

            if path_being_completed.startswith('"'):
                path_being_completed = current_arg_text_being_completed.strip('"')

            directory_prefix, partial_name = get_directory_and_partial_name(
                path_being_completed, sep="\\"
            )
            suggestions = get_remote_path_suggestions(
                self.r_pool, directory_prefix, partial_name, dirs_only
            )

        for sugg_path in suggestions:

            # If the path doesn't start with a drive letter, prepend the directory_prefix
            if (
                not re.match(r"^[a-zA-Z]:", directory_prefix)
                and directory_prefix
                and directory_prefix.endswith("\\")
            ):
                sugg_path = f"{directory_prefix}{sugg_path}"

            text_to_insert_in_prompt = sugg_path

            if " " in sugg_path:
                # If the path contains spaces, quote it
                text_to_insert_in_prompt = f'"{sugg_path}"'

            yield Completion(
                text_to_insert_in_prompt,
                start_position=-len(
                    current_arg_text_being_completed
                ),  # Use the length of quoted part
                display=sugg_path,
            )


def get_ps_script(script_name: str) -> str:
    """
    Returns the content of a PowerShell script from the package resources.
    """
    try:
        with resources.path("evil_winrm_py._ps", script_name) as script_path:
            return script_path.read_text()
    except FileNotFoundError:
        print(RED + f"[-] Script {script_name} not found." + RESET)
        log.error(f"Script {script_name} not found.")
        return ""


def quoted_command_split(command: str) -> list[str]:
    """
    Splits a command string into parts, respecting quoted strings.
    This is useful for handling paths with spaces or special characters.
    """
    actual_command_parts = []
    continuation = False
    cursor = 0

    command_parts = command.split(" ")
    for part in command_parts:
        if not part:
            continue
        if continuation:
            actual_command_parts[cursor] = actual_command_parts[cursor] + " " + part
            if part.endswith('"'):
                continuation = False
                cursor += 1
        else:
            if part.startswith('"'):
                actual_command_parts += [part]
                continuation = True
            elif part.find('"') != -1:
                # #TODO: decide later how to handle this case
                pass
            else:
                actual_command_parts += [part]
                cursor += 1
    return actual_command_parts


def download_file(r_pool: RunspacePool, remote_path: str, local_path: str) -> None:
    ps = PowerShell(r_pool)
    script = get_ps_script("fetch.ps1")
    ps.add_script(script)
    ps.add_parameter("FilePath", remote_path)
    ps.begin_invoke()

    ts = int(time.time())
    tmp_file_path = Path(tempfile.gettempdir()) / f"evil-winrm-py.file_{ts}.tmp"

    try:
        # Create a temporary file to store the downloaded data
        with open(tmp_file_path, "ab+") as bin:
            cursor = 0
            metadata = {}
            while ps.state == PSInvocationState.RUNNING:
                with DelayedKeyboardInterrupt():
                    ps.poll_invoke()
                output = ps.output
                if cursor == 0:
                    line = json.loads(output[0])
                    if line["Type"] == "Error":
                        print(RED + f"[-] Error: {line['Message']}" + RESET)
                        log.error(f"Error: {line['Message']}")
                        return
                    elif line["Type"] == "Metadata":
                        metadata = line
                    pbar = tqdm(
                        total=metadata["FileSize"],
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=f"Downloading {remote_path}",
                        dynamic_ncols=True,
                        mininterval=0.1,
                    )
                for line in output[cursor:]:
                    line = json.loads(line)
                    if line["Type"] == "Chunk":
                        Base64Data = line["Base64Data"]
                        chunk = base64.b64decode(Base64Data)
                        bin.write(chunk)
                        pbar.update(metadata["ChunkSize"])
                    if line["Type"] == "Error":
                        print(RED + f"[-] Error: {line['Message']}" + RESET)
                        log.error(f"Error: {line['Message']}")
                        return
                cursor = len(output)
            pbar.close()
            bin.close()

        if ps.had_errors:
            if ps.streams.error:
                for error in ps.streams.error:
                    print(error)

    except KeyboardInterrupt:
        if "pbar" in locals() and pbar:
            pbar.leave = (
                False  # Make the progress bar disappear on close after interrupt
            )
            pbar.close()
        Path(tmp_file_path).unlink(missing_ok=True)
        if ps.state == PSInvocationState.RUNNING:
            log.info("Stopping command execution.")
            ps.stop()
        return

    # Verify the downloaded file's hash
    hexdigest = hashlib.md5(open(tmp_file_path, "rb").read()).hexdigest()
    if metadata["FileHash"].lower() == hexdigest:
        # If the hash matches, rename the temporary file to the final name
        tmp_file_path = Path(tmp_file_path)
        try:
            shutil.move(tmp_file_path, local_path)
        except Exception as e:
            print(RED + f"[-] Error saving file: {e}" + RESET)
            log.error(f"Error saving file: {e}")
            return
        print(
            GREEN
            + "[+] File downloaded successfully and saved as: "
            + local_path
            + RESET
        )
        log.info("File downloaded successfully and saved as: {}".format(local_path))
    else:
        print(RED + "[-] File hash mismatch. Downloaded file may be corrupted." + RESET)
        log.error("File hash mismatch. Downloaded file may be corrupted.")


def upload_file(r_pool: RunspacePool, local_path: str, remote_path: str) -> None:
    hexdigest = hashlib.md5(open(local_path, "rb").read()).hexdigest().upper()
    with open(local_path, "rb") as bin:
        file_size = Path(local_path).stat().st_size
        chunk_size_bytes = 65536  # 64 KB
        total_chunks = (file_size + chunk_size_bytes - 1) // chunk_size_bytes
        metadata = {"FileHash": ""}  # Declare a psuedo metadata

        pbar = tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=f"Uploading {local_path}",
            dynamic_ncols=True,
            mininterval=0.1,
        )
        try:
            temp_file_path = ""
            for i in range(total_chunks):
                start_offset = i * chunk_size_bytes
                bin.seek(start_offset)
                chunk = bin.read(chunk_size_bytes)

                if not chunk:  # End of file
                    break

                elif i == 0:
                    chunk_type = 0  # First chunk, tells PS script to create file
                    if len(chunk) < chunk_size_bytes:
                        chunk_type = 3
                elif i == total_chunks - 1:
                    chunk_type = 1  # Last chunk, tells PS script to calculate hash
                else:
                    chunk_type = 2  # Intermediate chunk

                base64_chunk = base64.b64encode(chunk).decode("utf-8")

                script = get_ps_script("send.ps1")
                with DelayedKeyboardInterrupt():
                    ps = PowerShell(r_pool)
                    ps.add_script(script)
                    ps.add_parameter("Base64Chunk", base64_chunk)
                    ps.add_parameter("ChunkType", chunk_type)

                    if chunk_type == 1:
                        # If it's the last chunk, we provide the file path and hash
                        ps.add_parameter("TempFilePath", temp_file_path)
                        ps.add_parameter("FilePath", remote_path)
                        ps.add_parameter("FileHash", hexdigest)
                    elif chunk_type == 2:
                        ps.add_parameter("TempFilePath", temp_file_path)
                    elif chunk_type == 3:
                        ps.add_parameter("FilePath", remote_path)
                        ps.add_parameter("FileHash", hexdigest)

                    ps.begin_invoke()

                    while ps.state == PSInvocationState.RUNNING:
                        ps.poll_invoke()
                output = ps.output

                for line in output:
                    line = json.loads(line)
                    if line["Type"] == "Metadata":
                        metadata = line
                        if "TempFilePath" in metadata:
                            temp_file_path = metadata["TempFilePath"]

                    if line["Type"] == "Error":
                        print(RED + f"[-] Error: {line['Message']}" + RESET)
                        log.error(f"Error: {line['Message']}")
                        pbar.leave = False  # Make the progress bar disappear on close
                        return
                if ps.had_errors:
                    if ps.streams.error:
                        for error in ps.streams.error:
                            print(error)
                if chunk_type == 3:
                    pbar.update(file_size)
                else:
                    pbar.update(chunk_size_bytes)
            pbar.close()

            # Verify the downloaded file's hash
            if metadata["FileHash"] == hexdigest:
                print(
                    GREEN
                    + "[+] File uploaded successfully as: "
                    + metadata["FilePath"]
                    + RESET
                )
                log.info(
                    "File uploaded successfully as: {}".format(metadata["FilePath"])
                )
            else:
                print(
                    RED
                    + "[-] File hash mismatch. Uploaded file may be corrupted."
                    + RESET
                )
                log.error("File hash mismatch. Uploaded file may be corrupted.")

        except KeyboardInterrupt:
            if "pbar" in locals() and pbar:
                pbar.leave = (
                    False  # Make the progress bar disappear on close after interrupt
                )
                pbar.close()
            if ps.state == PSInvocationState.RUNNING:
                log.info("Stopping command execution.")
                ps.stop()


def load_ps(r_pool: RunspacePool, local_path: str):
    ps = PowerShell(r_pool)
    try:
        with open(local_path, "r") as script_file:
            script = script_file.read()
            # Remove block comments (<#...#>) to avoid matching commented-out functions
            content = re.sub(r"<#.*?#>", "", script, flags=re.DOTALL)
            # Find all function names in the script
            pattern = r"function\s+([a-zA-Z0-9_-]+)\s*(?={|$)"
            function_names = re.findall(pattern, content, re.MULTILINE)

        ps.add_script(f". {{ {script} }}")  # Dot sourcing the script
        ps.begin_invoke()

        while ps.state == PSInvocationState.RUNNING:
            with DelayedKeyboardInterrupt():
                ps.poll_invoke()

        if ps.streams.error:
            print(RED + "[-] Failed to load PowerShell script." + RESET)
            log.error(f"Failed to load PowerShell script '{local_path}'.")
            for error in ps.streams.error:
                print(RED + error._to_string + RESET)
                log.error("Error: {}".format(error._to_string))
                log.error("\tCategoryInfo: {}".format(error.message))
                log.error("\tFullyQualifiedErrorId: {}".format(error.fq_error))
        else:
            print(GREEN + "[+] PowerShell script loaded successfully." + RESET)
            log.info(f"PowerShell script '{local_path}' loaded successfully.")
            global COMMAND_SUGGESTIONS
            # Update the command suggestions with the function names
            new_suggestions = []
            for func in function_names:
                if func not in COMMAND_SUGGESTIONS:
                    new_suggestions += [func]
            if new_suggestions:
                COMMAND_SUGGESTIONS += new_suggestions
                print(
                    CYAN
                    + "[*] New commands available (use TAB to autocomplete):"
                    + RESET
                )
                print(", ".join(new_suggestions))
    except KeyboardInterrupt:
        if ps.state == PSInvocationState.RUNNING:
            log.info("Stopping command execution.")
            ps.stop()


def run_ps(r_pool: RunspacePool, local_path: str) -> None:
    """Runs a local PowerShell script on the remote host."""
    ps = PowerShell(r_pool)
    try:
        with open(local_path, "r") as script_file:
            script = script_file.read()

        ps.add_script(script)
        ps.begin_invoke()

        cursor = 0
        while ps.state == PSInvocationState.RUNNING:
            with DelayedKeyboardInterrupt():
                ps.poll_invoke()
            output = ps.output
            for line in output[cursor:]:
                print(line)
            cursor = len(output)

        if ps.streams.error:
            print(RED + "[-] Failed to run PowerShell script." + RESET)
            log.error(f"Failed to run PowerShell script '{local_path}'.")
            for error in ps.streams.error:
                print(RED + error._to_string + RESET)
                log.error("Error: {}".format(error._to_string))
                log.error("\tCategoryInfo: {}".format(error.message))
                log.error("\tFullyQualifiedErrorId: {}".format(error.fq_error))
        else:
            print(GREEN + "[+] PowerShell script ran successfully." + RESET)
            log.info(f"PowerShell script '{local_path}' ran successfully.")
    except KeyboardInterrupt:
        if ps.state == PSInvocationState.RUNNING:
            log.info("Stopping command execution.")
            ps.stop()


def interactive_shell(r_pool: RunspacePool) -> None:
    """Runs the interactive pseudo-shell."""
    log.info("Starting interactive PowerShell session...")

    # Set up history file
    if not HISTORY_FILE.exists():
        Path(HISTORY_FILE).touch()
    prompt_history = FileHistory(HISTORY_FILE)
    prompt_session = PromptSession(history=prompt_history)

    # Set up command completer
    completer = CommandPathCompleter(r_pool)

    while True:
        try:
            try:
                prompt_text = ANSI(get_prompt(r_pool))
            except (KeyboardInterrupt, EOFError):
                return
            command = prompt_session.prompt(
                prompt_text,
                completer=completer,
                complete_while_typing=False,
            )

            if not command:
                continue

            # Normalize command input
            command_lower = str(command).strip().lower()

            # Check for exit command
            if command_lower == "exit":
                log.info("Exiting interactive shell.")
                return
            elif command_lower in ["clear", "cls"]:
                log.info("Clearing the screen.")
                clear()  # Clear the screen
                continue
            elif command_lower == "menu":
                log.info("Displaying menu.")
                show_menu()
                continue
            elif command_lower.startswith("download"):
                command_parts = quoted_command_split(command)
                if len(command_parts) < 3:
                    print(
                        RED + "[-] Usage: download <remote_path> <local_path>" + RESET
                    )
                    continue
                remote_path = command_parts[1].strip('"')
                local_path = command_parts[2].strip('"')

                remote_file, streams, had_errors = run_ps_cmd(
                    r_pool, f"(Resolve-Path -Path '{remote_path}').Path"
                )
                if not remote_file:
                    print(
                        RED
                        + f"[-] Remote file '{remote_path}' does not exist or you do not have permission to access it."
                        + RESET
                    )
                    continue

                file_name = remote_file.split("\\")[-1]

                if Path(local_path).expanduser().is_dir() or local_path.endswith(
                    os.sep
                ):
                    local_path = (
                        Path(local_path).expanduser().resolve().joinpath(file_name)
                    )
                else:
                    local_path = Path(local_path).expanduser().resolve()

                download_file(r_pool, remote_file, str(local_path))
                continue
            elif command_lower.startswith("upload"):
                command_parts = quoted_command_split(command)
                if len(command_parts) < 3:
                    print(RED + "[-] Usage: upload <local_path> <remote_path>" + RESET)
                    continue
                local_path = command_parts[1].strip('"')
                remote_path = command_parts[2].strip('"')

                if not Path(local_path).expanduser().exists():
                    print(
                        RED + f"[-] Local file '{local_path}' does not exist." + RESET
                    )
                    continue

                file_name = local_path.split(os.sep)[-1]

                if not re.match(r"^[a-zA-Z]:", remote_path):
                    # If the path doesn't start with a drive letter, prepend the current directory
                    pwd, streams, had_errors = run_ps_cmd(r_pool, "$pwd.Path")
                    if remote_path == ".":
                        remote_path = f"{pwd}\\{file_name}"
                    else:
                        remote_path = f"{pwd}\\{remote_path}"

                if remote_path.endswith("\\"):
                    remote_path = f"{remote_path}{file_name}"

                upload_file(
                    r_pool, str(Path(local_path).expanduser().resolve()), remote_path
                )
                continue
            elif command_lower.startswith("loadps"):
                command_parts = quoted_command_split(command)
                if len(command_parts) < 2:
                    print(RED + "[-] Usage: loadps <local_path>" + RESET)
                    continue
                local_path = command_parts[1].strip('"')
                local_path = Path(local_path).expanduser().resolve()

                if not local_path.exists():
                    print(
                        RED
                        + f"[-] Local PowerShell script '{local_path}' does not exist."
                        + RESET
                    )
                    continue
                elif local_path.suffix.lower() != ".ps1":
                    print(
                        RED
                        + "[-] Please provide a valid PowerShell script file with .ps1 extension."
                        + RESET
                    )
                    continue

                load_ps(r_pool, local_path)
                continue
            elif command_lower.startswith("runps"):
                command_parts = quoted_command_split(command)
                if len(command_parts) < 2:
                    print(RED + "[-] Usage: runps <local_path>" + RESET)
                    continue
                local_path = command_parts[1].strip('"')
                local_path = Path(local_path).expanduser().resolve()

                if not local_path.exists():
                    print(
                        RED
                        + f"[-] Local PowerShell script '{local_path}' does not exist."
                        + RESET
                    )
                    continue
                elif local_path.suffix.lower() != ".ps1":
                    print(
                        RED
                        + "[-] Please provide a valid PowerShell script file with .ps1 extension."
                        + RESET
                    )
                    continue

                run_ps(r_pool, local_path)
                continue
            else:
                try:
                    ps = PowerShell(r_pool)
                    ps.add_cmdlet("Invoke-Expression").add_parameter("Command", command)
                    ps.add_cmdlet("Out-String").add_parameter("Stream")
                    ps.begin_invoke()
                    log.info("Executing command: {}".format(command))

                    cursor = 0
                    while ps.state == PSInvocationState.RUNNING:
                        with DelayedKeyboardInterrupt():
                            ps.poll_invoke()
                        output = ps.output
                        for line in output[cursor:]:
                            print(line)
                        cursor = len(output)
                    log.info("Command execution completed.")
                    log.info("Output: {}".format("\n".join(output)))

                    if ps.streams.error:
                        for error in ps.streams.error:
                            print(RED + error._to_string + RESET)
                            log.error("Error: {}".format(error._to_string))
                            log.error("\tCategoryInfo: {}".format(error.message))
                            log.error(
                                "\tFullyQualifiedErrorId: {}".format(error.fq_error)
                            )
                except KeyboardInterrupt:
                    if ps.state == PSInvocationState.RUNNING:
                        log.info("Stopping command execution.")
                        ps.stop()
        except KeyboardInterrupt:
            print("\nCaught Ctrl+C. Type 'exit' or press Ctrl+D to exit.")
            continue  # Allow user to continue or type exit
        except EOFError:
            return  # Exit on Ctrl+D


# --- Main Function ---
def main():
    print(
        """          _ _            _                             
  _____ _(_| |_____ __ _(_)_ _  _ _ _ __ ___ _ __ _  _ 
 / -_\\ V | | |___\\ V  V | | ' \\| '_| '  |___| '_ | || |
 \\___|\\_/|_|_|    \\_/\\_/|_|_||_|_| |_|_|_|  | .__/\\_, |
                                            |_|   |__/  v{}\n""".format(
            __version__
        )
    )
    parser = argparse.ArgumentParser(
        epilog="For more information about this project, visit https://github.com/adityatelange/evil-winrm-py"
        "\nFor user guide, visit https://github.com/adityatelange/evil-winrm-py/blob/main/docs/usage.md",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-i",
        "--ip",
        required=True,
        help="remote host IP or hostname",
    )
    parser.add_argument("-u", "--user", help="username")
    parser.add_argument("-p", "--password", help="password")
    parser.add_argument("-H", "--hash", help="nthash")
    parser.add_argument(
        "--priv-key-pem",
        help="local path to private key PEM file",
    )
    parser.add_argument(
        "--cert-pem",
        help="local path to certificate PEM file",
    )
    parser.add_argument("--uri", default="wsman", help="wsman URI (default: /wsman)")
    parser.add_argument(
        "--ua",
        default="Microsoft WinRM Client",
        help='user agent for the WinRM client (default: "Microsoft WinRM Client")',
    )
    parser.add_argument(
        "--port", type=int, default=5985, help="remote host port (default 5985)"
    )
    if is_kerb_available:
        parser.add_argument(
            "--spn-prefix",
            help="specify spn prefix",
        )
        parser.add_argument(
            "--spn-hostname",
            help="specify spn hostname",
        )
        parser.add_argument(
            "-k", "--kerberos", action="store_true", help="use kerberos authentication"
        )
    parser.add_argument(
        "--no-pass", action="store_true", help="do not prompt for password"
    )
    parser.add_argument("--ssl", action="store_true", help="use ssl")
    parser.add_argument("--log", action="store_true", help="log session to file")
    parser.add_argument("--debug", action="store_true", help="enable debug logging")
    parser.add_argument("--no-colors", action="store_true", help="disable colors")
    parser.add_argument(
        "--version", action="version", version=__version__, help="show version"
    )

    args = parser.parse_args()

    # Set Default values
    auth = "ntlm"  # this can be 'negotiate'
    encryption = "auto"
    username = args.user

    # --- Run checks on provided arguments ---
    if args.no_colors:
        global RESET, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, BOLD
        RESET = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = BOLD = ""

    if args.cert_pem or args.priv_key_pem:
        auth = "certificate"
        encryption = "never"
        args.ssl = True
        args.no_pass = True
        if not args.cert_pem or not args.priv_key_pem:
            print(
                RED
                + "[-] Both cert.pem and priv-key.pem must be provided for certificate authentication."
                + RESET
            )
            sys.exit(1)

    if args.hash and args.password:
        print(RED + "[-] You cannot use both password and hash." + RESET)
        sys.exit(1)

    if args.hash:
        ntlm_hash_pattern = r"^[0-9a-fA-F]{32}$"
        if re.match(ntlm_hash_pattern, args.hash):
            args.password = "00000000000000000000000000000000:{}".format(args.hash)
        else:
            print(RED + "[-] Invalid NTLM hash format." + RESET)
            sys.exit(1)

    if args.uri:
        if args.uri.startswith("/"):
            args.uri = args.uri.lstrip("/")

    if args.ssl and (args.port == 5985):
        args.port = 5986

    if args.log or args.debug:
        level = logging.INFO
        # Disable all loggers except the root logger
        if args.debug:
            print(BLUE + "[*] Debug logging enabled." + RESET)
            level = logging.DEBUG
            os.environ["KRB5_TRACE"] = str(LOG_PATH)  # Enable Kerberos trace logging
        else:
            # Disable all loggers except the root logger
            for name in logging.root.manager.loggerDict:
                if not name.startswith("evil_winrm_py"):
                    logging.getLogger(name).disabled = True
        # Set up logging to a file
        try:
            logging.basicConfig(
                level=level,
                format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                filename=LOG_PATH,
            )
            print(BLUE + "[*] Logging session to {}".format(LOG_PATH) + RESET)
        except PermissionError as pe:
            print(
                RED + "[-] Permission denied to write to log file '{}'."
                " Please check the permissions or run with elevated privileges.".format(
                    LOG_PATH
                )
                + RESET
            )
            log.disabled = True
    else:
        log.disabled = True

    # --- Initialize WinRM Session ---
    log.info("--- Evil-WinRM-Py v{} started ---".format(__version__))
    try:
        if is_kerb_available:
            if args.kerberos:
                auth = "kerberos"
                args.spn_prefix = (
                    args.spn_prefix or "http"
                )  # can also be cifs, ldap, HOST
                if not args.user:
                    try:
                        cred = GSSAPICredentials(RawCreds())
                        username = cred.name
                    except MissingCredentialsError:
                        print(
                            MAGENTA
                            + "[%] No credentials cache found for Kerberos authentication."
                            + RESET
                        )
                        sys.exit(1)
                    except ExpiredCredentialsError as ece:
                        print(
                            RED + "[-] The Kerberos credentials have expired. " + RESET
                        )
                        log.error("Expired credentials error: {}".format(ece))
                        sys.exit(1)
                # User needs to set environment variables `KRB5CCNAME` and `KRB5_CONFIG` as per requirements
                # example: export KRB5CCNAME=/tmp/krb5cc_1000
                # example: export KRB5_CONFIG=/etc/krb5.conf
            elif args.spn_prefix or args.spn_hostname:
                args.spn_prefix = args.spn_hostname = None  # Reset to None
                print(
                    MAGENTA
                    + "[%] SPN prefix/hostname is only used with Kerberos authentication."
                    + RESET
                )
        else:
            args.spn_prefix = args.spn_hostname = None

        if args.no_pass:
            args.password = None
        elif args.user and not args.password:
            args.password = prompt("Password: ", is_password=True)
            if not args.password:
                args.password = None

        if username:
            log.info(
                "[*] Connecting to '{}:{}' as '{}'"
                "".format(args.ip, args.port, username, auth)
            )
            print(
                BLUE + "[*] Connecting to '{}:{}' as '{}'"
                "".format(args.ip, args.port, username) + RESET
            )
        else:
            log.info("[*] Connecting to '{}:{}'".format(args.ip, args.port))
            print(BLUE + "[*] Connecting to '{}:{}'".format(args.ip, args.port) + RESET)

        with WSManEWP(
            server=args.ip,
            port=args.port,
            auth=auth,
            encryption=encryption,
            username=args.user,
            password=args.password,
            ssl=args.ssl,
            cert_validation=False,
            path=args.uri,
            negotiate_service=args.spn_prefix,
            negotiate_hostname_override=args.spn_hostname,
            certificate_key_pem=args.priv_key_pem,
            certificate_pem=args.cert_pem,
            user_agent=args.ua,
        ) as wsman:
            with RunspacePool(wsman) as r_pool:
                interactive_shell(r_pool)
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
    except WinRMTransportError as wte:
        print(RED + "[-] {}".format(wte) + RESET)
        log.error("WinRM transport error: {}".format(wte))
        sys.exit(1)
    except ConnectionError as ce:
        print(
            RED + "[-] Failed to connect to the remote host: {}:{}"
            "".format(args.ip, args.port) + RESET
        )
        log.error("Connection error: {}".format(ce))
        sys.exit(1)
    except AuthenticationError as ae:
        print(RED + "[-] {}".format(ae) + RESET)
        log.error("Authentication failed: {}".format(ae))
        sys.exit(1)
    except WSManFaultError as wfe:
        print(RED + "[-] {}".format(wfe) + RESET)
        log.error("WSMan fault error: {}".format(wfe))
        sys.exit(1)
    except Krb5Error as ke:
        print(RED + "[-] {}".format(ke) + RESET)
        log.error("Kerberos error: {}".format(ke))
        sys.exit(1)
    except (OperationNotAvailableError, NoCredentialError) as se:
        print(RED + "[-] {}".format(se._context_message) + RESET)
        print(RED + "[-] {}".format(se._BASE_MESSAGE) + RESET)
        log.error("SpnegoError error: {}".format(se))
        sys.exit(1)
    except SpnegoError as se:
        print(RED + "[-] {}".format(se._context_message) + RESET)
        print(RED + "[-] {}".format(se.message) + RESET)
        log.error("SpnegoError error: {}".format(se))
        sys.exit(1)
    except Exception as e:
        traceback.print_exc()
        log.exception("An unexpected error occurred: {}".format(e), exc_info=True)
        sys.exit(1)
    finally:
        log.info("--- Evil-WinRM-Py v{} ended ---".format(__version__))
