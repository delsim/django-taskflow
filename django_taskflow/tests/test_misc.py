import pytest

from django_taskflow.version import __version__


def test_version():
    assert __version__[0] == '0'
