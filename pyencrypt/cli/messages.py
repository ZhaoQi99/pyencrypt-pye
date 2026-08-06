import sys

import click

from pyencrypt import __description__, __version__

VERSION = rf"""
                                                      _
         _ __  _   _  ___ _ __   ___ _ __ _   _ _ __ | |_
        | '_ \| | | |/ _ \ '_ \ / __| '__| | | | '_ \| __|
        | |_) | |_| |  __/ | | | (__| |  | |_| | |_) | |_
        | .__/ \__, |\___|_| |_|\___|_|   \__, | .__/ \__|
        |_|    |___/                      |___/|_|

        {__description__}

                    VERSION {__version__}
"""  # noqa: E221,E222

KEY_OPTION_HELP = """
Your encryption key.If you don't specify key,
pyencrypt will generate encryption key randomly.
"""

PYTHON_MAJOR, PYTHON_MINOR = sys.version_info[:2]
LOADER_FILE_NAME = click.style("encrypted/{}", blink=True, fg="blue")
LICENSE_FILE_NAME = click.style("license.lic", blink=True, fg="blue")

SUCCESS_ANSI = click.style("successfully", fg="green")

INVALID_DATETIME_MSG = click.style(
    "Before date must be less than after date.", fg="red"
)

FINISH_ENCRYPT_MSG = f"""\
Encryption completed {SUCCESS_ANSI}.\
"""

ENCRYPT_SUMMARY_MSG = """\
🔐 Encrypted {count} files ({size}) in {elapsed}s.
""".format(
    count=click.style("{count}", fg="green", bold=True),
    size=click.style("{size}", fg="cyan"),
    elapsed=click.style("{elapsed:.2f}", fg="yellow"),
)

FINISH_ENCRYPT_WITH_LOADER_MSG = f"""\
{FINISH_ENCRYPT_MSG}\
Please copy {LOADER_FILE_NAME} into your encrypted directory.
And then remove `encrypted` directory.
Finally, add `import loader` at the top of your entry file.\
"""  # noqa: W604

FINISH_DECRYPT_MSG = f"""
Decryption completed {SUCCESS_ANSI}. Your origin source code has be put: {{work_dir}}
"""

FINISH_GENERATE_LOADER_MSG = f"""
Generate loader file {SUCCESS_ANSI}. Your loader file is located in {LOADER_FILE_NAME}
"""

FINISH_GENERATE_LICENSE_MSG = f"""
Generate license file {SUCCESS_ANSI}. Your license file is located in {LICENSE_FILE_NAME}
"""

DATETIME_FORMATS = ["%Y-%m-%dT%H:%M:%S %z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]

ENVVAR_PREFIX = "PYE_ENCRYPT"
