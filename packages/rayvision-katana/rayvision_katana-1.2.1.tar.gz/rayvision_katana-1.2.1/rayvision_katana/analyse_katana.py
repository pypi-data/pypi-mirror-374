#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import hashlib
import logging
import os
import sys
import time
import traceback
import threading

from rayvision_utils import constants
from rayvision_utils import utils
from rayvision_utils.cmd import Cmd
from rayvision_utils.exception import tips_code
from rayvision_utils.exception.error_msg import ERROR9899_CGEXE_NOTEXIST
from rayvision_utils.exception.exception import CGFileNotExistsError, AnalyseFailError, CGExeNotExistError
from rayvision_katana.constants import PACKAGE_NAME

class AnalyzeKatana(object):
    def __init__(self,
                 cg_file,
                 software_version,
                 project_name,
                 plugin_config,
                 render_software="Katana",
                 input_project_path=None,
                 local_os=None,
                 workspace=None,
                 custom_exe_path=None,
                 platform="2",
                 logger=None,
                 log_folder=None,
                 log_name=None,
                 log_level="DEBUG"
                 ):
        """Initialize and examine the analysis information.

        Args:
            cg_file (str): Scene file path.
            software_version (str): Software version.
            project_name (str): The project name.
            plugin_config (dict): Plugin information.
            render_software (str): Software name, Katana by default.
            input_project_path (str): The working path of the scenario.
            local_os (str): System name, linux or windows.
            workspace (str): Analysis out of the result file storage path.
            custom_exe_path (str): Customize the exe path for the analysis.
            platform (str): Platform no.
            logger (object, optional): Custom log object.
            log_folder (str, optional): Custom log save location.
            log_name (str, optional): Custom log file name.
            log_level (string):  Set log level, example: "DEBUG","INFO","WARNING","ERROR".
        """
        self.logger = logger
        if not self.logger:
            from rayvision_log.core import init_logger
            init_logger(PACKAGE_NAME, log_folder, log_name)
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(level=log_level.upper())

        self.check_path(cg_file)
        self.cg_file = cg_file

        self.render_software = render_software
        self.input_project_path = input_project_path or ""
        self.software_version = software_version
        self.project_name = project_name
        self.plugin_config = plugin_config

        local_os = self.check_local_os(local_os)
        self.local_os = local_os
        self.tmp_mark = str(int(time.time())) + str(self.get_current_id())
        workspace = os.path.join(self.check_workspace(workspace),
                                 self.tmp_mark)
        if not os.path.exists(workspace):
            os.makedirs(workspace)
        self.workspace = workspace

        if custom_exe_path:
            self.check_path(custom_exe_path)
        self.custom_exe_path = custom_exe_path

        self.platform = platform

        self.task_json = os.path.join(workspace, "task.json")
        self.tips_json = os.path.join(workspace, "tips.json")
        self.asset_json = os.path.join(workspace, "asset.json")
        self.upload_json = os.path.join(workspace, "upload.json")
        self.tips_info = {}
        self.task_info = {}
        self.asset_info = {}
        self.upload_info = {}

    @staticmethod
    def get_current_id():
        if isinstance(threading.current_thread(), threading._MainThread):
            return os.getpid()
        else:
            return threading.get_ident()

    @staticmethod
    def check_path(tmp_path):
        """Check if the path exists."""
        if not os.path.exists(tmp_path):
            raise CGFileNotExistsError("{} is not found".format(tmp_path))

    @staticmethod
    def check_local_os(local_os):
        """Check the system name.

        Args:
            local_os (str): System name.

        Returns:
            str

        """
        if not local_os:
            if "win" in sys.platform.lower():
                local_os = "windows"
            else:
                local_os = "linux"
        return local_os

    def check_workspace(self, workspace):
        """Check the working environment.

        Args:
            workspace (str):  Workspace path.

        Returns:
            str: Workspace path.

        """
        if not workspace:
            if self.local_os == "windows":
                workspace = os.path.join(os.environ["USERPROFILE"], "renderfarm_sdk")
            else:
                workspace = os.path.join(os.environ["HOME"], "renderfarm_sdk")
        else:
            self.check_path(workspace)

        return workspace

    def location_from_reg(self, version):
        """Get the path in the registry of the local CG.

        When the system environment is Windows or linux, get the path where the
        local Katana startup file is located in the registry.

        Args:
            version (str): Katana version.
                e.g.:
                    "3.2v1".

        Returns:
            str: The path where katana's startup files are located.
                e.g.:
                    "C:/Program Files/Katana3.2v1/".

        """
        temp = 2
        try:
            import _winreg
        except ImportError:
            import winreg as _winreg
            temp = 3

        location = None
        string = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Katana {}_is1'.format(version)
        self.logger.debug(string)
        try:
            if temp == 2:
                handle = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                                         string)
            else:
                handle = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                                         string, 0,
                                         (_winreg.KEY_WOW64_64KEY
                                          + _winreg.KEY_READ))
            location, _type = _winreg.QueryValueEx(
                handle, "InstallLocation")
            self.logger.debug('localtion: %s, type: %s', location, _type)
        except WindowsError:
            self.logger.debug(traceback.format_exc())

        return location

    def find_location(self):
        """Get the path where the local Houdini startup file is located.

        Raises:
            CGExeNotExistError: The path to the startup file does not exist.

        """
        exe_path = None
        if self.local_os == "linux":
            exe_path = "/opt/Foundry/Katana{}/katana".format(self.software_version)
            if not os.path.isfile(exe_path):
                self.logger.info("The linux software address is not found, please specify the software path directly")
                exe_path = None
        else:
            location = self.location_from_reg(self.software_version)
            tmp_exe_path = os.path.join(location, "bin", "katanaBin.exe")
            if os.path.exists(tmp_exe_path):
                exe_path = tmp_exe_path

        if exe_path is None:
            error_msg = "Software of scene has not been found"
            self.add_tip(tips_code.CG_NOTEXISTS, error_msg)
            self.save_tips()
            raise CGExeNotExistError(ERROR9899_CGEXE_NOTEXIST.format(
                self.render_software))

        self.logger.info("exe_path: %s", exe_path)
        return exe_path

    def analyse_cg_file(self):
        """Analyse cg file.

        Analyze the scene file to get the path to the startup file of the CG
        software.

        """
        if self.custom_exe_path is not None:
            exe_path = self.custom_exe_path
        else:
            exe_path = self.find_location()

        return exe_path

    def write_task_json(self):
        """The initialization task.json."""
        constants.TASK_INFO["task_info"]["input_cg_file"] = self.cg_file.replace("\\", "/")
        constants.TASK_INFO["task_info"]["project_name"] = self.project_name
        constants.TASK_INFO["task_info"]["cg_id"] = constants.CG_SETTING.get(self.render_software.capitalize())
        constants.TASK_INFO["task_info"]["os_name"] = "1" if self.local_os == "windows" else "0"
        constants.TASK_INFO["task_info"]["platform"] = self.platform
        constants.TASK_INFO["software_config"] = {
            "plugins": self.plugin_config,
            "cg_version": self.software_version,
            "cg_name": self.render_software
        }
        utils.json_save(self.task_json, constants.TASK_INFO)

    def add_tip(self, code, info):
        """Add error message.

        Args:
            code (str): error code.
            info (str or list): Error message description.

        """
        if isinstance(info, list):
            self.tips_info[code] = info
        else:
            self.tips_info[code] = [info]

    def save_tips(self):
        """Write the error message to tips.json."""
        utils.json_save(self.tips_json, self.tips_info, ensure_ascii=False)

    def get_file_md5(self, file_path):
        """Generate the md5 values for the scenario."""
        hash_md5 = hashlib.md5()
        if os.path.exists(file_path):
            with open(file_path, 'rb') as file_path_f:
                while True:
                    data_flow = file_path_f.read(8096)
                    if not data_flow:
                        break
                    hash_md5.update(data_flow)
        return hash_md5.hexdigest()

    def write_upload_json(self):
        """handle analyse result.

        Save the analyzed scene file information and texture information to
        the upload.json file.

        """
        upload_asset = []
        self.upload_info["scene"] = [
            {
                "local": self.cg_file.replace("\\", "/"),
                "server": utils.convert_path(self.cg_file),
                "hash": self.get_file_md5(self.cg_file)
            }
        ]

        upload_asset.append({
            "local": self.cg_file.replace("\\", "/"),
            "server": utils.convert_path(self.cg_file)
        })

        self.upload_info["asset"] = upload_asset

        utils.json_save(self.upload_json, self.upload_info)

    def analyse(self, exe_path="", no_upload=False):
        """Build a cmd command to perform an analysis scenario.

        Args:
            no_upload (bool): Do you not generate an upload,json file.

        Raises:
            AnalyseFailError: Analysis scenario failed.

        """
        if not os.path.exists(exe_path):
            exe_path = self.analyse_cg_file()
        self.write_task_json()
        analyse_script_name = "Analyse.py"
        analyze_script_path = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                           analyse_script_name))
        task_path = os.path.dirname(self.task_json).replace("\\", "/")

        cmd = '"{exe_path}" --script "{script_full_path}" -task "{task_path}" -file "{cg_file}"'
        if exe_path and (str(exe_path).endswith(('.sh', '.bat'))):
            cmd = '"{exe_path}" "{script_full_path}" "{task_path}" "{cg_file}"'
        cmd = cmd.format(
            exe_path=exe_path,
            script_full_path=analyze_script_path,
            cg_file=self.cg_file,
            task_path=task_path
        )
        self.logger.debug(cmd)
        code, _, _ = Cmd.run(cmd, shell=True)
        if code != 0:
            self.add_tip(tips_code.UNKNOW_ERR, "")
            self.save_tips()
            raise AnalyseFailError
        
        self.tips_info = utils.json_load(self.tips_json)
        self.asset_info = utils.json_load(self.asset_json)
        self.task_info = utils.json_load(self.task_json)
        # if not no_upload:
        #     self.write_upload_json()
        return self
