import numpy as np
from scipy.spatial.transform import Rotation as R
import os
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('--scene', type=str, required=True)
args = parser.parse_args()
scene = args.scene

root = "/localhome/dya78/code/rui-indoorinv-data/data/indoor_synthetic"
scene_path = os.path.join(root, scene)


cam_info_path = os.path.join(scene_path,"train" ,"transforms.json")
cam_info = json.load(open(cam_info_path))

original_frame = cam_info["frames"][0]

cam_info["frames"] = [original_frame]

original_path = original_frame["file_path"]
original_transform = original_frame["transform_matrix"]


transform = np.array(original_transform)



rot = transform[0:3,0:3]
translation = transform[0:3,3]

d_xs = [5, -5]
d_ys = [5, -5]
counter = 0
for i in range(2):
    for j in range(2):
        new_frame = {}
        new_transform = np.eye(4)
        dx = d_xs[i]
        dy = d_ys[j]
        new_transform = np.eye(4)
        new_rot = R.from_euler('zyx', [0, dy, dx], degrees=True).as_matrix()
        new_transform[:3,:3] = np.dot(rot, new_rot)
        new_transform[:3,3] = translation

        new_frame["file_path"] = original_path + f"_{counter}"
        counter +=1

        new_frame["transform_matrix"] = new_transform.tolist()
        cam_info["frames"].append(new_frame)

json.dump(cam_info, open(cam_info_path, "w"), indent=4)
