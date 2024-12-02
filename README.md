# coincap

A simple tracker of your cryptocurrency portfolio.

```bash
$ python coincap.py
bitcoin
        $6,705.80
bitcoin-cash
        $43.77
dogecoin
        $0.14
ethereum
        $351.65
Total coin value in USD: $7,101.36
```

To run with `uv`:
```bash
uv run coincap.py
```
## Installation

Download script and install dependencies. This project uses [uv](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) to manage dependencies and packaging.

```shell
git clone https://github.com/beachwood23/coincap.git
uv sync
```



### Caveats

This has only been used on a Mac so far. It probably doesn't work on Windows or Linux yet,
mainly because of [GNU readline differences](https://docs.python.org/3/library/readline.html).
