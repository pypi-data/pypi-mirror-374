# -*- coding: utf-8 -*-
"""only analyze katana"""

from rayvision_katana.analyse_katana import AnalyzeKatana

analyze_info = {
    "cg_file": r"F:\cache\arnold_test.katana",
    "workspace": "c:/workspace",
    "software_version": "3.2v1",
    "project_name": "Project1",
    "plugin_config": {
        "KtoA": "2.4.0.3"
    }
}

# AnalyzeKatana(**analyze_info).analyse(exe_path=r"C:\Program Files\Katana3.2v1\bin\katanaBin.exe")
AnalyzeKatana(**analyze_info).analyse()
