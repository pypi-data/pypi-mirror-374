"""Utility class holding constants and small calculations for working with Services/daemons"""

# imports
import os, pathlib, importlib
from inspect import isclass
import pkg_resources
from openmsitoolbox.logging import OpenMSILogger


class ServicesConstants:
    """
    Constants for working with services
    """

    WORKING_DIR = (
        os.environ["OPENMSISTREAM_SERVICES_WORKING_DIR"]
        if "OPENMSISTREAM_SERVICES_WORKING_DIR" in os.environ
        else (pathlib.Path(__file__).parent / "working_dir").resolve()
    )
    NSSM_PATH = WORKING_DIR / "nssm.exe"
    # The URL to use for downloading NSSM when needed
    NSSM_DOWNLOAD_URL = "https://nssm.cc/release/nssm-2.24.zip"
    ERROR_LOG_STEM = "_ERROR_LOG.txt"
    SERVICE_EXECUTABLE_NAME_STEM = "_service_executable.py"
    DAEMON_SERVICE_DIR = pathlib.Path("/etc/systemd/system/")

    @property
    def available_services(self):
        """
        A dictionary with details of the services that are available
        """
        return self.service_dicts

    def __init__(self):
        # make the Service dictionaries to use
        self.service_dicts = []
        for script in pkg_resources.iter_entry_points("console_scripts"):
            if script.dist.key == "openmsistream":
                if script.name in (
                    "InstallService",
                    "ManageService",
                    "ProvisionNode",
                    "ReproduceUndecryptableMessages",
                    "UploadDataFile",
                ):
                    continue
                scriptstr = str(script)
                cmd = (scriptstr.split())[0]
                path = ((scriptstr.split())[2].split(":"))[0]
                funcname = (((scriptstr.split())[2]).split(":"))[1]
                module = importlib.import_module(path)
                run_classes = [
                    getattr(module, x)
                    for x in dir(module)
                    if isclass(getattr(module, x))
                    and getattr(module, x).__name__ == script.name
                ]
                if len(run_classes) != 1:
                    errmsg = (
                        f"ERROR: could not determine class for script {cmd} in file {path}! "
                        f"Possibilities found: {run_classes}"
                    )
                    raise RuntimeError(errmsg)
                self.service_dicts.append(
                    {
                        "class_name": cmd,
                        "class": run_classes[0],
                        "filepath": path,
                        "func_name": funcname,
                    }
                )
        # make the logger to use
        self.logger = OpenMSILogger(
            "Services", logger_filepath=self.WORKING_DIR / "Services.log"
        )


SERVICE_CONST = ServicesConstants()
