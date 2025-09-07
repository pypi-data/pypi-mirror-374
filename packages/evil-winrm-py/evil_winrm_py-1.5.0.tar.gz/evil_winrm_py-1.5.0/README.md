<div align=center>
  <img height="150" alt="ewp-logo" src="https://raw.githubusercontent.com/adityatelange/evil-winrm-py/refs/heads/main/assets/logo.svg" />
  <h1>evil-winrm-py</h1>

[![PyPI version](https://img.shields.io/pypi/v/evil-winrm-py)](https://pypi.org/project/evil-winrm-py/)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/github/license/adityatelange/evil-winrm-py)

</div>

`evil-winrm-py` is a python-based tool for executing commands on remote Windows machines using the WinRM (Windows Remote Management) protocol. It provides an interactive shell with enhanced features like file upload/download, command history, and colorized output. It supports various authentication methods including NTLM, Pass-the-Hash, Certificate, and Kerberos.

![](https://raw.githubusercontent.com/adityatelange/evil-winrm-py/refs/tags/v1.5.0/assets/terminal.png)

> [!NOTE]
> This tool is designed strictly for educational, ethical use, and authorized penetration testing. Always ensure you have explicit authorization before accessing any system. Unauthorized access or misuse of this tool is both illegal and unethical.

## Motivation

The original evil-winrm is written in Ruby, which can be a hurdle for some users. Rewriting it in Python makes it more accessible and easier to use, while also allowing us to leverage Python’s rich ecosystem for added features and flexibility.

I also wanted to learn more about winrm and its internals, so this project will also serve as a learning experience for me.

## Features

- Execute commands on remote Windows machines via an interactive shell.
- Download files from the remote host to the local machine.
- Upload files from the local machine to the remote host.
- Progress bar for file transfers with speed and time estimation.
- Stable and reliable file transfer including support for large files with MD5 checksum verification.
- Auto-complete local and remote file paths (also the ones which have spaces) with `Tab` completion.
- Load PowerShell functions from local scripts into the interactive shell. 🆕
- Run local PowerShell scripts on the remote host. 🆕
- Enable logging and debugging for better traceability.
- Navigate command history using `up`/`down` arrow keys.
- Display colorized output for improved readability.
- Lightweight and Python-based for ease of use.
- Keyboard Interrupt (Ctrl+C / Ctrl+D) support to terminate long-running commands gracefully.

Includes support for:

- NTLM authentication.
- Pass-the-Hash authentication.
- Certificate authentication.
- Kerberos authentication with custom SPN prefix and hostname options.
- SSL to secure communication with the remote host.
- custom WSMan URIs.
- custom user agent for the WinRM client.

Detailed documentation can be found in the [docs](https://github.com/adityatelange/evil-winrm-py/blob/main/docs) directory.

## Installation (Windows/Linux)

#### Installation of Kerberos prerequisites on Linux

```bash
sudo apt install gcc python3-dev libkrb5-dev krb5-pkinit
# Optional: krb5-user
```

### Install `evil-winrm-py`

> You may use [pipx](https://pipx.pypa.io/stable/) or [uv](https://docs.astral.sh/uv/) instead of pip to install evil-winrm-py. `pipx`/`uv` is a tool to install and run Python applications in isolated environments, which helps prevent dependency conflicts by keeping the tool's dependencies separate from your system's Python packages.

```bash
pip install evil-winrm-py
pip install evil-winrm-py[kerberos] # for kerberos support on Linux

# Note: building gssapi and krb5 packages may take some time, so be patient.
```

or if you want to install with latest commit from the main branch you can do so by cloning the repository and installing it with `pip`/`pipx`/`uv`:

```bash
git clone https://github.com/adityatelange/evil-winrm-py
cd evil-winrm-py
pip install .
```

### Update

```bash
pip install --upgrade evil-winrm-py
```

### Uninstall

```bash
pip uninstall evil-winrm-py
```

Check [Installation Guide](https://github.com/adityatelange/evil-winrm-py/blob/main/docs/install.md) for more details.

## Usage

Details on how to use `evil-winrm-py` can be found in the [Usage Guide](https://github.com/adityatelange/evil-winrm-py/blob/main/docs/usage.md).

```bash
usage: evil-winrm-py [-h] -i IP [-u USER] [-p PASSWORD] [-H HASH]
                     [--priv-key-pem PRIV_KEY_PEM] [--cert-pem CERT_PEM] [--uri URI]
                     [--ua UA] [--port PORT] [--spn-prefix SPN_PREFIX]
                     [--spn-hostname SPN_HOSTNAME] [-k] [--no-pass] [--ssl] [--log]
                     [--debug] [--no-colors] [--version]

options:
  -h, --help            show this help message and exit
  -i, --ip IP           remote host IP or hostname
  -u, --user USER       username
  -p, --password PASSWORD
                        password
  -H, --hash HASH       nthash
  --priv-key-pem PRIV_KEY_PEM
                        local path to private key PEM file
  --cert-pem CERT_PEM   local path to certificate PEM file
  --uri URI             wsman URI (default: /wsman)
  --ua UA               user agent for the WinRM client (default: "Microsoft WinRM Client")
  --port PORT           remote host port (default 5985)
  --spn-prefix SPN_PREFIX
                        specify spn prefix
  --spn-hostname SPN_HOSTNAME
                        specify spn hostname
  -k, --kerberos        use kerberos authentication
  --no-pass             do not prompt for password
  --ssl                 use ssl
  --log                 log session to file
  --debug               enable debug logging
  --no-colors           disable colors
  --version             show version

For more information about this project, visit https://github.com/adityatelange/evil-winrm-py
For user guide, visit https://github.com/adityatelange/evil-winrm-py/blob/main/docs/usage.md
```

Example:

```bash
evil-winrm-py -i 192.168.1.100 -u Administrator -p P@ssw0rd --ssl
```

## Menu Commands (inside evil-winrm-py shell)

```bash
Menu:
[+] upload <local_path> <remote_path>                       - Upload a file
[+] download <remote_path> <local_path>                     - Download a file
[+] loadps <local_path>.ps1                                 - Load PowerShell functions from a local script
[+] runps <local_path>.ps1                                  - Run a local PowerShell script on the remote host
[+] menu                                                    - Show this menu
[+] clear, cls                                              - Clear the screen
[+] exit                                                    - Exit the shell
Note: Use absolute paths for upload/download for reliability.
```

## Credits

- Original evil-winrm project - https://github.com/Hackplayers/evil-winrm
- PowerShell Remoting Protocol for Python - https://github.com/jborean93/pypsrp
- Prompt Toolkit - https://github.com/prompt-toolkit/python-prompt-toolkit
- tqdm - https://github.com/tqdm/tqdm
- Thanks to [Github Coplilot](https://github.com/features/copilot) and [Google Gemini](https://gemini.google.com/app) for code suggestions and improvements.

## Stargazers over time

[![Stargazers over time](https://starchart.cc/adityatelange/evil-winrm-py.svg?background=%23ffffff00&axis=%23858585&line=%236b63ff)](https://starchart.cc/adityatelange/evil-winrm-py)
