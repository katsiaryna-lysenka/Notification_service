from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_ses_client():
    return Mock()


@pytest.fixture
def mocker():
    return mocker
