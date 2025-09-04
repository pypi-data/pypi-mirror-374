# imports
import unittest, pathlib, importlib
from openmsistream.services.config import SERVICE_CONST
from openmsistream.services.linux_service_manager import LinuxServiceManager

try:
    from .config import TEST_CONST  # pylint: disable=import-error,wrong-import-order
except ImportError:
    from config import TEST_CONST  # pylint: disable=import-error,wrong-import-order

# constants
TEST_SERVICE_CLASS_NAME = "DataFileUploadDirectory"
TEST_SERVICE_NAME = "testing_service"
TEST_SERVICE_EXECUTABLE_ARGSLIST = ["test_upload"]


class TestServiceUtilities(unittest.TestCase):
    """
    Class for testing utilities used by the Service management code
    """

    def test_some_configs(self):
        """
        Make sure that some config variables can be created successfully
        """
        # self.assertFalse(SERVICE_CONST.NSSM_EXECUTABLE_PATH.is_file())
        for service_dict in SERVICE_CONST.available_services:
            _ = importlib.import_module(service_dict["filepath"])
        # the command below creates a file but that file should be ignored in the repo
        SERVICE_CONST.logger.info("testing")

    def test_write_executable_file(self):
        """
        Make sure an executable file is written to the expected location
        with the expected format
        """
        # the test below does create a file but that file should be ignored in the repo
        test_exec_fp = (
            pathlib.Path(__file__).parent.parent.parent
            / "openmsistream"
            / "services"
            / "working_dir"
        )
        test_exec_fp = (
            test_exec_fp
            / f"{TEST_SERVICE_NAME}{SERVICE_CONST.SERVICE_EXECUTABLE_NAME_STEM}"
        )
        manager = LinuxServiceManager(
            TEST_SERVICE_NAME,
            service_spec_string=TEST_SERVICE_CLASS_NAME,
            argslist=TEST_SERVICE_EXECUTABLE_ARGSLIST,
        )
        # pylint: disable=protected-access
        manager._write_executable_file(filepath=test_exec_fp)
        self.assertTrue(test_exec_fp.is_file())
        with open(test_exec_fp, "r") as test_fp:
            test_lines = test_fp.readlines()
        ref_exec_fp = TEST_CONST.TEST_DATA_DIR_PATH / test_exec_fp.name
        self.assertTrue(ref_exec_fp.is_file())
        with open(ref_exec_fp, "r") as ref_fp:
            ref_lines = ref_fp.readlines()
        real_ref_lines = [ref_line for ref_line in ref_lines if ref_line.strip() != ""]
        for test_line, ref_line in zip(test_lines, real_ref_lines):
            if ref_line.lstrip().startswith(
                "output_filepath = "
            ) or ref_line.lstrip().startswith("main(["):
                continue
            self.assertTrue(test_line == ref_line)
