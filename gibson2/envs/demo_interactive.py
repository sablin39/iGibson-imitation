import yaml
from gibson2.core.physics.robot_locomotors import Turtlebot
from gibson2.core.simulator import Simulator
from gibson2.core.physics.scene import BuildingScene, StadiumScene, InteractiveBuildingScene
from gibson2.utils.utils import parse_config
import pytest
import pybullet as p
import numpy as np
import os
import gibson2
from gibson2.utils.assets_utils import download_data

class DemoInteractive(object):
    def __init__(self):
        download_data()
        self.download_interactive_assets()

    def download_interactive_assets(self):
        if not os.path.exists(gibson2.dataset_path):
            os.makedirs(gibson2.dataset_path)
        if not os.path.exists(os.path.join(gibson2.dataset_path, 'Rs_interactive')):
            os.system('wget https://storage.googleapis.com/gibson_scenes/Rs_interactive.tar.gz -O /tmp/Rs_interactive.tar.gz')
            os.system('tar -zxf /tmp/Rs_interactive.tar.gz --directory {}'.format(gibson2.dataset_path))

    def run_demo(self):
        config = parse_config(os.path.join(gibson2.assets_path, '../../examples/configs/turtlebot_p2p_nav.yaml'))
        s = Simulator(mode='gui', image_width=700, image_height=700)
        model_path = os.path.join(gibson2.dataset_path, 'Rs_interactive', 'rs_interactive.urdf')
        scene = InteractiveBuildingScene(model_path)
        s.import_scene(scene)
        turtlebot = Turtlebot(config)
        s.import_robot(turtlebot)

        for i in range(1000):
            turtlebot.apply_action([0.1,0.5])
            s.step()

        s.disconnect()


if __name__ == "__main__":
    DemoInteractive().run_demo()
