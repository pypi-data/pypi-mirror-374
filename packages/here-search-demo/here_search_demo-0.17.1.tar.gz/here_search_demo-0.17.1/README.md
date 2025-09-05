[![Python package][6]][7]
[![codecov][8]][9]
[![lite-badge][10]][3]


# HERE Search notebooks

A set of jupyter notebooks demonstrating the use of [HERE Geocoding & Search][4] endpoints `/autosuggest`,  `/discover`, `/browse`, and `/lookup`.

![searching for pizza][11]

Requirements: a [HERE API key][1] and a Python environment. Note that HERE Base Plan [Pricing][5] allows you to get started for free.

The notebooks can be [used in your browser][3] without further installation.

## Installation

If you need to install the notebooks or the underlying library on your workstation, run preferably in a virtual environment:

   ```shell
   pip install 'here-search-demo[lab]'
   ```

Or as a developer:

   ```shell
   pip install -r <(sort -u requirements/*) -e '.[lab]'
   ```

Link the virtual environment to a IPython kernel:

   ```shell
   python -m ipykernel install \
     --prefix $(python -c "import sys; print(sys.prefix)") \
     --name search_demo --display-name "search demo"
   ```

Copy `demo-config-example.json` to `demo-config.json` and add your [HERE API key][1] to it.

Start JupyterLab:

   ```shell
   python -m jupyterlab src/here_search/demo/notebooks
   ```

Or instead of JupyterLab, start JupyterLite
   ```shell
   bash src/here_search/demo/scripts/lite-run.sh
   ```


(Additional [notes][2])

## License

Copyright (C) 2022-2025 HERE Europe B.V.

This project is licensed under the MIT license - see the [LICENSE](./LICENSE) file in the root of this project for license details.

[1]: https://www.here.com/docs/bundle/geocoding-and-search-api-developer-guide/page/topics/quick-start.html#get-an-api-key
[2]: https://github.com/heremaps/here-search-demo/blob/main/docs/developers.md
[3]: https://heremaps.github.io/here-search-demo/lab/?path=demo.ipynb
[4]: https://www.here.com/docs/category/geocoding-search-v7
[5]: https://www.here.com/get-started/pricing

[6]: https://github.com/heremaps/here-search-demo/actions/workflows/test.yml/badge.svg
[7]: https://github.com/heremaps/here-search-demo/actions/workflows/test.yml
[8]: https://codecov.io/gh/heremaps/here-search-demo/branch/main/graph/badge.svg?token=MVFCS4BUFN
[9]: https://codecov.io/gh/heremaps/here-search-demo
[11]: https://github.com/heremaps/here-search-demo/raw/main/docs/screenshot.jpg
[10]: https://jupyterlite.rtfd.io/en/latest/_static/badge.svg
