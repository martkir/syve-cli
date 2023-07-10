# syve-cli

## Installation

```
pip install -e .
```

## Usage

```
syve <slug> --from-timestamp <timestamp> --until-timestamp <timestamp> --save-dir <path>
```

- Valid `slug` values: `blocks`, `erc20`, `prices_usd`.
- `from-timestamp` and `to-timestamp` are optional. If not provided, the last 30 days of data will be downloaded. 
- `save-dir` is optional. If not provided, the data will be saved in the current directory under `data`.

```syve --help``` for description of all options.

Example commands:

```
syve prices_usd
```

Will download the last 30 days of price data and save it in the current directory under `data`.
