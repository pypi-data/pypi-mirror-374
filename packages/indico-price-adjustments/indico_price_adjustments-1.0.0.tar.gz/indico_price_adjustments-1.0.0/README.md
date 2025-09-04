# indico-price-adjustments

This plugin provides registration price adjustment options for non-logged-in users.

## Installation

Install the plugin [package](https://pypi.org/project/indico-price-adjustments/) from PyPI
```bash
pip install indico-price-adjustments
```

Open `indico.conf` of your indico installation then add `price_adjustments` on `PLUGIN`.
```python
PLUGINS = { ... , 'price_adjustments'}
```

## Install for development for contributing to this plugin

Clone this repository on `~/dev/indico/plugins`
```bash
git clone https://github.com/RobotHanzo/IndicoPriceAdjustments.git
```

With python virtual environment of Indico development installation enabled, enter the cloned directory then run following command to install the plugin.
```bash
pip install -e .
```

Open `indico.conf` which should be located in `~/dev/indico/src/indico` then add `price_adjustments` on `PLUGIN`.
```python
PLUGINS = { ... , 'price_adjustments'}
```

You can now test you modification on your development indico environment.