# README
#     @pytest.fixture decorator config
import pytest
import os
from common import common

@pytest.fixture(scope="module",autouse="True")
def setup_module(request):
    def teardown_module():
        common.allureDeploy()
        print("\nteardown_module called.")
    request.addfinalizer(teardown_module)
    print("\nsetup_module called.")

@pytest.fixture(scope="session",autouse="True")
def setup_documents(request):
    def teardown_documents():
        common.allureDeploy()
        print("\nteardown_documents called.")
    request.addfinalizer(teardown_documents)
    # clean up temp files
    common.cleanTemp()
    # download test package form ftp site
    common.downloadPackage()
    print("\n==== Downloading Complished ====")
    # check the MD5 value of the test package
    common.checkMD5()
    print("\n==== MD5 Check Complished ====")
    # upload the test files to test machine
    common.fileUpload("SOC")
    common.fileUpload("PCIE")
    print("\n==== Test Files Uploading Complished ====")
    # Unzip the test package
    common.unzipPackage("SOC")
    common.unzipPackage("PCIE")
    print("\nsetup_documents called.")

if __name__ == '__main__':
    print("")