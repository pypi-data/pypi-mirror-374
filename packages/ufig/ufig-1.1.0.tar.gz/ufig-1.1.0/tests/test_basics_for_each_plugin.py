# Copyright (C) 2024 ETH Zurich
# Institute for Particle Physics and Astrophysics
# Author: Silvan Fischbacher
# created: Tue Sep 17 2024

import importlib
import inspect
import pkgutil

import ivy
import pytest
from ivy.exceptions.exceptions import NotImplementedException

import ufig.plugins


def test_if_plugins_are_properly_written():
    ctx = ivy.context.create_ctx()
    # Get all modules in ufig.plugins
    plugin_modules = [
        importlib.import_module(f"{ufig.plugins.__name__}.{name}")
        for finder, name, ispkg in pkgutil.iter_modules(ufig.plugins.__path__)
    ]

    # Find all Plugin classes in these modules
    plugin_classes = []
    for module in plugin_modules:
        for _, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__name__ == "Plugin":
                plugin_classes.append(obj)

    # Check if each Plugin class has a __str__ method that returns a string and
    # a call method that can be called
    for plugin_class in plugin_classes:
        isinstance(str(plugin_class(ctx)), str)
        try:
            plugin_class(ctx)()
        except NotImplementedException:
            pytest.fail(
                f"__call__ in {plugin_class.__name__} from {plugin_class.__module__}"
                " raises NotImplementedException"
            )
        except AttributeError:
            pass
