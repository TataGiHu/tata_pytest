import paramiko
import os
import pytest
from common import common

@pytest.mark.run(order=1)
def test_init():
    print("Test for documents preparation")