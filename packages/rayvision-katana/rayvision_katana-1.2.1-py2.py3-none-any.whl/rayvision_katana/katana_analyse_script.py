import argparse
import codecs
import json
import os
import re
import sys

import NodegraphAPI
from Katana import KatanaFile, FarmAPI, Nodes3DAPI

'''
katana cmd ::
"C:\Program Files\Katana2.6v3\bin\katanaBin.exe" --script "E:\PycharmProjects\newPlatform\CG\Katana\script\katana_analyse_script.py"  "E:\fang\katana_prm\001_005_test.katana"  "E:\fang\katana_prm\taks_info\task.json"  "E:\fang\katana_prm\taks_info\system.json"

in katana ::
import sys
sys.path.append(r"E:\PycharmProjects\newPlatform\CG\Katana\script")
import katana_analyse_script
task_json = r"E:\fang\katana_prm\taks_info\task.json"
kanana_analyse = katana_analyse_script.ray_Katana_rendernodes()
kanana_analyse.kanana_rendernodes(task_json)
#katana_asset = katana_analyse_script.ray_Katana_asset()
#katana_asset.get_Alembic_In()

'''


class ray_Katana(object):
    def __init__(self):

        pass

    def open_json(self, info_file):
        with open(info_file, 'r') as f:
            json_src = json.load(f)
            return json_src

    def write_json_info(self, json_file, key, dict):
        info_file_path = os.path.dirname(json_file)
        print("write info to %s" % json_file)
        if not os.path.exists(info_file_path):
            os.makedirs(info_file_path)
        if not os.path.exists(json_file):
            with open(json_file, "w") as t:
                t.write("{}")
                t.close()
                pass
        try:
            info_file = json_file
            with open(info_file, 'r') as f:
                json_src = json.load(f)
                f.close()
            json_src[key] = dict
            with codecs.open(info_file, 'w', 'utf-8') as f:
                json.dump(json_src, f, ensure_ascii=False, indent=4)
                f.close()

        except Exception as err:
            print  (err)
            pass


class ray_Katana_rendernodes(ray_Katana):

    def __init__(self):

        pass

    def kanana_rendernodes(self, task_json):

        katana_scene = FarmAPI.GetKatanaFileName()
        render_info_dict = {}
        render_node_info_dict = {}
        render_nodes = NodegraphAPI.GetAllNodesByType("Render")
        if len(render_nodes) != 0:
            for render_node in render_nodes:
                render_output_dict = {}
                render_frame_dict = {}
                render_names = render_node.getName()
                render_name = render_names
                scene_name = os.path.basename(os.path.basename(katana_scene))
                print ("the render node name is  %s" % render_name)
                num_re = re.compile(r"(\d+_\d+)[\D]*", re.I)

                try:
                    render_node.getParameter("lock").setValue(0, 0)
                    # render_node_info=Nodes3DAPI.RenderNodeUtil.GetRenderNodeInfo(render_node,graphState)
                    render_node_info = Nodes3DAPI.RenderNodeUtil.GetRenderNodeInfo(render_node)

                    for i in xrange(render_node_info.getNumberOfOutputs()):
                        outputInfo = render_node_info.getOutputInfoByIndex(i, forceLocal=False)

                        render_output_name = outputInfo['name']
                        render_output = outputInfo["outputFile"]
                        # print render_output_name,render_output
                        if render_output.find('Temp') > 0:

                            print ("the %s output is %s ,it is tmp ,dont copy" % (render_output_name, render_output))
                        else:
                            render_output_dict[render_output_name] = render_output

                    render_start = render_node.getParameter('farmSettings.activeFrameRange.start').getValue(0)
                    render_end = render_node.getParameter('farmSettings.activeFrameRange.end').getValue(0)

                    render_frame_dict["start"] = render_start
                    render_frame_dict["end"] = render_end
                    render_info_dict[render_name] = {}
                    render_info_dict[render_name]["aov"] = {}
                    render_info_dict[render_name]["aov"] = render_output_dict
                    try:
                        render_TimeRange = render_node.getParameter('farmSettings.TimeRange').getValue(0)
                        render_info_dict[render_name]["frames"] = "%s[%s]" % (render_TimeRange, 1)
                    except:
                        render_info_dict[render_name]["frames"] = "%s-%s[%s]" % (int(render_start), int(render_end), 1)
                    render_info_dict[render_name]["denoise"] = "0"
                    render_info_dict[render_name]["renderable"] = "1"

                except Exception as err:
                    print (err)
                    print ("the bad render node name is   %s" % render_name)
                    pass

            render_node_info_dict["rendernodes"] = render_info_dict
            self.write_json_info(task_json, "scene_info", render_node_info_dict)


class ray_Katana_asset(ray_Katana):
    # TODO get asset list from katana_scene
    def __init__(self):
        if task_json:
            asset_json = os.path.join(os.path.dirname(task_json), "asset.json")
            self.write_json_info(asset_json, "", {"aseet": {}})
            print (asset_json)
        pass

    def get_Alembic_In(self, node_name=None):
        nodes = []
        if node_name:
            nodes.append(NodegraphAPI.GetNode(node_name))
        else:
            nodes = NodegraphAPI.GetAllNodesByType("Alembic_In")
        print (nodes)
        for node in nodes:
            print (node.getName())
            print (node.getParameter("abcAsset").getValue(0))

    def get_PrmanShadingNode(self, node_name=None):
        nodes = []
        if node_name:
            nodes.append(NodegraphAPI.GetNode(node_name))
        else:

            nodes = NodegraphAPI.GetAllNodesByType("PrmanShadingNode")
        for node in nodes:
            if node.getParameter("nodeType").getValue(0) == "PxrTexture":
                print (node.getParameter("parameters.filename.value").getValue(0))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-task", help='task id', type=str)
    parser.add_argument('-file', help='file path', type=str)
    args = parser.parse_args()
    katana_scene = args.file
    json_path = args.task
    task_json = os.path.join(json_path, "task.json")
    KatanaFile.Load(katana_scene)
    print(katana_scene)
    print(task_json)
    print(os.path.basename(sys.executable.lower()))
    kanana_analyse = ray_Katana_rendernodes()
    kanana_analyse.kanana_rendernodes(task_json)
    katana_asset = ray_Katana_asset()
    task_dict = katana_asset.open_json(task_json)
    katana_asset.get_Alembic_In()
    katana_asset.get_PrmanShadingNode()
    analyze_flag_file = os.path.join(json_path, "analyze_sucess")
    with open(analyze_flag_file, "w"):
        pass

