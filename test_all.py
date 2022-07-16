import pytest
import sys
import os


if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('UTF-8')

if __name__ == '__main__':
    pytest.main()