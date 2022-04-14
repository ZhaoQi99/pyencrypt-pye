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
                                  randomly.
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
