# ausankey

Uses matplotlib to create simple <a href="https://en.wikipedia.org/wiki/Sankey_diagram">
Sankey diagrams</a> flowing only from left to right.

[![PyPI version](https://badge.fury.io/py/auSankey.svg)](https://badge.fury.io/py/auSankey)
[![Coverage Status](https://coveralls.io/repos/github/AUMAG/auSankey/badge.svg?branch=main)](https://coveralls.io/github/AUMAG/auSankey?branch=main)

[![Python package](https://github.com/AUMAG/auSankey/actions/workflows/check.yml/badge.svg)](https://github.com/AUMAG/auSankey/actions/workflows/check.yml)
[![Jekyll Pages](https://github.com/AUMAG/auSankey/actions/workflows/doc.yml/badge.svg)](https://github.com/AUMAG/auSankey/actions/workflows/doc.yml)
[![Publish release](https://github.com/AUMAG/ausankey/actions/workflows/release.yml/badge.svg)](https://github.com/AUMAG/ausankey/actions/workflows/release.yml)

This package is [available on PyPi](https://pypi.org/project/ausankey/) and can be installed via:

    pip install ausankey

User documentation for the repository is published via GitHub Pages: https://aumag.github.io/ausankey/

Code documentation by Mkdocs is available here:
https://aumag.github.io/ausankey/reference/

## Minimal example

![example](https://aumag.github.io/ausankey/iface_frame3_pretty.png)

``` python
import ausankey as sky
import matplotlib.pyplot as plt
import pandas as pd

data = pd.DataFrame([
  ("a",1.0,"ab",2.0,"a",1.0),
  ("a",1.0,"ba",0.8,"ba",0.4),
  ("c",1.5,"cd",0.5,"d",2.0),
  ("b",0.5,"ba",0.8,"ba",0.4),
  ("b",0.5,"ab",0.8,"a",1.0),
  ("d",2.0,"cd",0.4,"d",1.0),
  ("e",1.0,"e",1.0,"e",3.0),
])

plt.figure()
sky.sankey(
  data,
  sort      = “top”,
  titles    = ["Stage 1","Stage 2","Stage 3"],
  valign    = "center",
)
plt.show()
```

## Requirements

* Python 3.x
* matplotlib
* numpy
* pandas

