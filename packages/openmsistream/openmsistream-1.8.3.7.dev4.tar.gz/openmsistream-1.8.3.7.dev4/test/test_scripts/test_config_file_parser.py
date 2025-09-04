# imports
import os, configparser, string
from random import choices
from openmsistream.utilities.config_file_parser import ConfigFileParser

try:
    from .config import TEST_CONST  # pylint: disable=import-error,wrong-import-order

    # pylint: disable=import-error,wrong-import-order
    from .base_classes import TestWithLogger, TestWithEnvVars
except ImportError:
    from config import TEST_CONST  # pylint: disable=import-error,wrong-import-order

    # pylint: disable=import-error,wrong-import-order
    from base_classes import TestWithLogger, TestWithEnvVars


class TestConfigFileParser(TestWithLogger, TestWithEnvVars):
    """
    Class for testing ConfigFileParser functions
    """

    def setUp(self):  # pylint: disable=invalid-name
        """
        Create the config file parsers to use in tests
        """
        super().setUp()
        self.cfp = ConfigFileParser(TEST_CONST.TEST_CFG_FILE_PATH, logger=self.logger)
        self.testconfigparser = configparser.ConfigParser()
        self.testconfigparser.read(TEST_CONST.TEST_CFG_FILE_PATH)

    def test_available_group_names(self):
        """
        Make sure group names match
        """
        self.assertEqual(self.cfp.available_group_names, self.testconfigparser.sections())

    def test_get_config_dict_for_groups(self):
        """
        test getting the dictionary of configs for given groups
        """
        if len(self.testconfigparser.sections()) < 2:
            errmsg = (
                f"ERROR: config file used for testing ({TEST_CONST.TEST_CFG_FILE_PATH}) "
                "does not contain enough sections to test with!"
            )
            raise RuntimeError(errmsg)
        for group_name in self.testconfigparser.sections():
            group_ref_dict = dict(self.testconfigparser[group_name])
            for k, v in group_ref_dict.items():
                if v.startswith("$"):
                    group_ref_dict[k] = os.path.expandvars(v)
            self.assertEqual(
                self.cfp.get_config_dict_for_groups(group_name), group_ref_dict
            )
        all_sections_dict = {}
        for group_name in self.testconfigparser.sections():
            all_sections_dict = {
                **all_sections_dict,
                **(dict(self.testconfigparser[group_name])),
            }
            for k, v in all_sections_dict.items():
                if v.startswith("$"):
                    all_sections_dict[k] = os.path.expandvars(v)
        self.assertEqual(
            self.cfp.get_config_dict_for_groups(self.testconfigparser.sections()),
            all_sections_dict,
        )
        random_section_name = "".join(choices(string.ascii_letters, k=10))
        while random_section_name in self.cfp.available_group_names:
            random_section_name = string.ascii_letters
        self.log_at_info("\nExpecting two errors below:")
        with self.assertRaises(ValueError):
            _ = self.cfp.get_config_dict_for_groups(random_section_name)
        with self.assertRaises(ValueError):
            _ = self.cfp.get_config_dict_for_groups(
                [self.testconfigparser.sections()[0], random_section_name]
            )
        if (
            os.path.expandvars("$KAFKA_PROD_CLUSTER_USERNAME")
            == "$KAFKA_PROD_CLUSTER_USERNAME"
        ):
            other_cfp = ConfigFileParser(
                TEST_CONST.PROD_CONFIG_FILE_PATH,
                logger=self.logger,
            )
        else:
            other_cfp = ConfigFileParser(
                TEST_CONST.FAKE_PROD_CONFIG_FILE_PATH, logger=self.logger
            )
        self.assertTrue("broker" in other_cfp.available_group_names)
        self.log_at_info("\nExpecting one error below:")
        with self.assertRaises(ValueError):
            _ = other_cfp.get_config_dict_for_groups("broker")
