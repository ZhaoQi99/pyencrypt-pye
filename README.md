# pyencrypt-pye
---
encrypt python source code and import module dynamically.

```
                                                      _
         _ __  _   _  ___ _ __   ___ _ __ _   _ _ __ | |_
        | '_ \| | | |/ _ \ '_ \ / __| '__| | | | '_ \| __|
        | |_) | |_| |  __/ | | | (__| |  | |_| | |_) | |_
        | .__/ \__, |\___|_| |_|\___|_|   \__, | .__/ \__|
        |_|    |___/                      |___/|_|

        encrypt python source code and import dynamically.

                    VERSION 0.1.0
```

## Install
```bash
pip install git+https://github.com/ZhaoQi99/pyencrypt-pye.git
✨🍰✨
```
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
```

### Encrypt
```shell
~$ pyencrypt encrypt -h
Usage: pyencrypt encrypt [OPTIONS] PATHNAME

  Encrypt your python code

Options:
  -i, --in-place  make changes to files in place
  -k, --key TEXT  Your encryption key.If you don‘t specify key, pyencrypt will
                  generate encryption key randomly.
  --yes           Automatically answer yes for confirm questions.
  -h, --help      Show this message and exit.
```
### Decrypt
```shell
~$ pyencrypt decrypt -h
Usage: pyencrypt decrypt [OPTIONS] PATHNAME

  Decrypt encrypted pye file

Options:
  -i, --in-place  make changes to files in place
  -k, --key TEXT  Your encryption key.  [required]
  -h, --help      Show this message and exit.
```
### Generate

```shell
~$ pyencrypt generate -h
Usage: pyencrypt generate [OPTIONS]

  Generate loader file using specified key

Options:
  -k, --key TEXT  Your encryption key.  [required]
  -h, --help      Show this message and exit.
```

## Example
### Encrypt
```shell
~$ pyencrypt encrypt --in-place  -y test.py
~$ pyencrypt encrypt test/
```

### Decrypt
```shell
~$ pyencrypt decrypt -k xxx test.pye
```
### Generate
```shell
~$ pyencrypt generate -k xxx
```

### Entry File
```python
import loader
from test import *
```

## Development

### Format Code

```shell
yapf --recursive -i pyencrypt 
isort pyencrypt
```
## License
[GNU General Public License v3.0](https://github.com/ZhaoQi99/pyencrypt-pye/blob/main/LICENSE)
## Author
* Qi Zhao([zhaoqi99@outlook.com](mailto:zhaoqi99@outlook.com))
