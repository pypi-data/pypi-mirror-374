# stooqpy

[![PyPI version](https://img.shields.io/pypi/v/stooqpy.svg)](https://pypi.org/project/stooqpy/)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)


> ⚠️ **UWAGA – Projekt w budowie!**
> Pakiet jest w fazie **aktywnego rozwoju**.
> Nie realizuje jeszcze wszystkich obiecanych funkcji.


Pakiet **stooqpy** umożliwia wygodne korzystanie z danych finansowych serwisu [stooq.pl](https://stooq.pl).

| Section  | Badges |
|----------|--------|
| **Testing** | [![CI](https://github.com/neon-symeon/stooqpy/actions/workflows/stooqpy_pkg_workflow.yml/badge.svg)](https://github.com/neon-symeon/stooqpy/actions) [![Coverage Status](https://coveralls.io/repos/github/neon-symeon/stooqpy/badge.svg?branch=main)](https://coveralls.io/github/neon-symeon/stooqpy?branch=main) |
| **Package** | [![PyPI version](https://img.shields.io/pypi/v/stooqpy.svg)](https://pypi.org/project/stooqpy/) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/stooqpy) |
| **Meta** | ![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg) |



## Główna idea
- ułatwia **pobieranie i przechowywanie** wysokiej jakości danych giełdowych z serwisu stooq.pl,
- dane gromadzone są w lekkiej i wydajnej bazie danych opartej na SQLite,
- stooqpy oferuje także możliwość pobierania danych przez API stooq.pl, ale preferowanym podejściem pozostaje półautomatyczne, bo daje wyższą jakość i dokładność danych.

---

## Instalacja

```bash
pip install stooqpy
