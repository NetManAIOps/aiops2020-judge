'''
Test utilities
'''
import tempfile

import pytest


@pytest.fixture
def storage():
    '''Tempory folder to store history data'''
    yield tempfile.gettempdir()
