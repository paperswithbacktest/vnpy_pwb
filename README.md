# EdArchimbaud Data Service Interface for the VeighNa Framework

<p align="center">
  <img src ="https://vnpy.oss-cn-shanghai.aliyuncs.com/vnpy-logo.png"/>
</p>

<p align="center">
    <img src ="https://img.shields.io/badge/version-2.10.15.3-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/platform-windows|linux|macos-yellow.svg"/>
    <img src ="https://img.shields.io/badge/python-3.7|3.8|3.9|3.10-blue.svg" />
    <img src ="https://img.shields.io/github/license/vnpy/vnpy.svg?color=orange"/>
</p>

## Description

It supports the following US financial market bar data:

* Stock and ETF options:
  * NASDAQ: Nasdaq Stock Exchange


## Installation

The installation environment is recommended to be based on [[**VeighNa Studio**](https://edarchimbaud.com/veighna-website)] above version 3.6.0.

Use pip command directly:

```bash
pip install vnpy_edarchimbaud
```

Or download the source code, unzip it and run it in cmd:

```bash
pip install .
```

## Use

You need to fill in the following field information in the global configuration:

| Name              | Meaning  | Required | Examples     |
|-------------------|----------|----------|--------------|
| datafeed.name     | Name     | Yes      | edarchimbaud |
| datafeed.username | Username | No       |              |
| datafeed.password | Password | No       |              |
