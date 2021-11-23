# pyencrypt-pye
---
encrypt python source code and import dynamically.

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
### Encrypt
```shell
~$ pyencrypt encrypt -h
Usage: pyencrypt encrypt [OPTIONS] PATHNAME

  Encrypt your python code

Options:
  -i, --in-place  make changes to files in place
  -k, --key TEXT  Your encryption key.If you don‘t specify key, pyencrypt will
                  generate encryption key randomly.
  -y, --yes       yes
  -h, --help      Show this message and exit.
```
### Decrypt
```shell
~$ pyencrypt decrypt -h
Usage: pyencrypt decrypt [OPTIONS] PATHNAME

  Decrypt encrypted pye file

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

