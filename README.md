# pyencrypt-pye 

---
[![Python package](https://github.com/ZhaoQi99/pyencrypt-pye/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/ZhaoQi99/pyencrypt-pye/actions/workflows/main.yml)
[![Python version](https://img.shields.io/pypi/pyversions/pyencrypt-pye.svg?logo=python)](https://pypi.python.org/pypi/pyencrypt-pye)
[![PyPI package](https://img.shields.io/pypi/v/pyencrypt-pye.svg)](https://pypi.python.org/pypi/pyencrypt-pye) 
[![PyPI download](https://img.shields.io/pypi/dm/pyencrypt-pye.svg)](https://pypi.python.org/pypi/pyencrypt-pye)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FZhaoQi99%2Fpyencrypt-pye&count_bg=%2379C83D&title_bg=%23555555&icon=github.svg&icon_color=%23E7E7E7&title=visitors&edge_flat=false)](https://hits.seeyoufarm.com)
[![GitHub](https://img.shields.io/github/license/ZhaoQi99/pyencrypt-pye)](https://github.com/ZhaoQi99/pyencrypt-pye/blob/main/LICENSE) 
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/ZhaoQi99/pyencrypt-pye) 


encrypt python source code and import module dynamically.

```
                                                      _
         _ __  _   _  ___ _ __   ___ _ __ _   _ _ __ | |_
        | '_ \| | | |/ _ \ '_ \ / __| '__| | | | '_ \| __|
        | |_) | |_| |  __/ | | | (__| |  | |_| | |_) | |_
        | .__/ \__, |\___|_| |_|\___|_|   \__, | .__/ \__|
        |_|    |___/                      |___/|_|

        encrypt python source code and import dynamically.

                    VERSION 0.3.0
```
## How to do
https://github.com/ZhaoQi99/pyencrypt-pye/wiki#how-to-do

## Install

```bash
pip install pyencrypt-pye
✨🍰✨
```
Or you can use `pip install git+https://github.com/ZhaoQi99/pyencrypt-pye.git` install latest version.

## Examples
View examples in the [examples](./examples) directory.

## Usage

```shell
Usage: pyencrypt [OPTIONS] COMMAND [ARGS]...

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  decrypt   Decrypt encrypted pye file
  encrypt   Encrypt your python code
  generate  Generate loader file using specified key
  license   Generate license file using specified key
```

### Encrypt

```shell
~$ pyencrypt encrypt -h
Usage: pyencrypt encrypt [OPTIONS] PATHNAME

  Encrypt your python code

Options:
  -i, --in-place                  make changes to files in place
  -k, --key 🔑                     Your encryption key.If you don‘t specify
                                  key, pyencrypt will generate encryption key
                                  randomly.  [env var: PYE_ENCRYPT_KEY]
  --with-license                  Add license to encrypted file
  -m, --bind-mac 01:23:45:67:89:AB
                                  Bind mac address to encrypted file
  -4, --bind-ipv4 192.168.0.1     Bind ipv4 address to encrypted file
  -b, --before [%Y-%m-%dT%H:%M:%S %z|%Y-%m-%d %H:%M:%S|%Y-%m-%d]
                                  License is invalid before this date.
  -a, --after [%Y-%m-%dT%H:%M:%S %z|%Y-%m-%d %H:%M:%S|%Y-%m-%d]
                                  License is invalid after this date.
  -y, --yes                       Automatically answer yes for confirm
                                  questions.
  -h, --help                      Show this message and exit.
```

### Entry File

In your entry file, you must import `loader` firstly, and then you can import encrypted modules as usual.

```python
import loader
from test import *
```

### Decrypt

```shell
~$ pyencrypt decrypt -h
Usage: pyencrypt decrypt [OPTIONS] PATHNAME

  Decrypt encrypted pye file

Options:
  -i, --in-place  make changes to files in place
  -k, --key 🔑     Your encryption key.  [required]
  -h, --help      Show this message and exit.
```

### Generate

```shell
~$ pyencrypt generate -h
Usage: pyencrypt generate [OPTIONS]

  Generate loader file using specified key

Options:
  -k, --key 🔑  Your encryption key.  [required]
  -h, --help   Show this message and exit.
```

### License

pyencrypt's loader will search for the license file in the following manner:

1. `~/.licenses/license.lic` file in your home directory.

2. `licenses/license.lic` file in `loader` file's directory.

3. `licenses/license.lic` file in the current working directory.

```shell
~$ pyencrypt license -h
   Usage: pyencrypt license [OPTIONS]

   Generate license file  using specified key

Options:
  -h, --help                      Show this message and exit.
  -k, --key 🔑     Your encryption key.  [required]
  -m, --bind-mac 01:23:45:67:89:AB
                                  Bind mac address to encrypted file
  -4, --bind-ipv4 192.168.0.1     Bind ipv4 address to encrypted file
  -b, --before [%Y-%m-%dT%H:%M:%S %z|%Y-%m-%d %H:%M:%S|%Y-%m-%d]
                                  License is invalid before this date.
  -a, --after [%Y-%m-%dT%H:%M:%S %z|%Y-%m-%d %H:%M:%S|%Y-%m-%d]
                                  License is invalid after this date.
```

### Shell Completion

<details open>
<summary>Bash</summary>
Add this to ~/.bashrc:

```shell
eval "$(_PYENCRYPT_COMPLETE=bash_source pyencrypt)"
```
</details>

<details>
<summary>Zsh</summary>
Add this to ~/.zshrc:

```shell
eval "$(_PYENCRYPT_COMPLETE=zsh_source pyencrypt)"
```
</details>

<details>
<summary>Fish</summary>
Add this to ~/.config/fish/completions/foo-bar.fish:

```shell
eval (env _PYENCRYPT_COMPLETE=fish_source pyencrypt)
```
</details>

## Example

### Encrypt

```shell
~$ pyencrypt encrypt --in-place  -y test.py
~$ pyencrypt encrypt test/
~$ pyencrypt encrypt test.py -y --with-license\
    --before="2000-01-01T00:00:00 +0800" --after="2030-01-01T00:00:00 +0800"\
    --bind-mac="AC:DE:48:00:11:22" --bind-ipv4="192.168.0.1"
```

### Decrypt

```shell
~$ pyencrypt decrypt -k xxx test.pye
```

### Generate

```shell
~$ pyencrypt generate -k xxx
```

### License

```shell
~$ pyencrypt license -k xxx\
    --before="2000-01-01T00:00:00 +0800" --after="2030-01-01T00:00:00 +0800"\
    --bind-mac="AC:DE:48:00:11:22" --bind-ipv4="192.168.0.1"
```
## FAQ

See [FAQ](FAQ.md) for frequently asked questions.

## Development

### Format Code

```shell
black pyencrypt 
isort pyencrypt
```

## License

[GNU General Public License v3.0](https://github.com/ZhaoQi99/pyencrypt-pye/blob/main/LICENSE)

## Author

* Qi Zhao([zhaoqi99@outlook.com](mailto:zhaoqi99@outlook.com))
