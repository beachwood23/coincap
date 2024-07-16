A simple tracker of your cryptocurrency portfolio.

```
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

## Installation
Download script and install dependencies:
```
git clone https://github.com/beachwood23/coincap.git
python3 -m pip install -r requirements.txt
```

### Caveats
This has only been used on a Mac so far. It probably doesn't work on Windows or Linux yet,
mainly because of [GNU readline differences](https://docs.python.org/3/library/readline.html).