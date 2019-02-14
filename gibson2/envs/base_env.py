from gibson2.core.physics.robot_locomotors import *
from gibson2.core.simulator import Simulator
from gibson2.core.physics.scene import *
import gibson2
from gibson2.utils.utils import parse_config


class BaseEnv(gym.Env):
    '''
    a basic environment, step, observation and reward not implemented
    '''
    def __init__(self, config_file, mode='headless'):
        self.simulator = Simulator(mode=mode)
        self.config = parse_config(config_file)
        if self.config['scene'] == 'stadium':
            scene = StadiumScene()
        elif self.config['scene'] == 'building':
            scene = BuildingScene(self.config['model_id'])

        self.simulator.import_scene(scene)
        if self.config['robot'] == 'Turtlebot':
            robot = Turtlebot(self.config)
        elif self.config['robot'] == 'Husky':
            robot = Husky(self.config)
        elif self.config['robot'] == 'Ant':
            robot = Ant(self.config)
        elif self.config['robot'] == 'Humanoid':
            robot = Humanoid(self.config)
        elif self.config['robot'] == 'JR2':
            robot = JR2(self.config)

        self.scene = scene
        self.robots = [robot]
        for robot in self.robots:
            self.simulator.import_robot(robot)

    def __del__(self):
        if not self.simulator is None:
            self.simulator.disconnect()

    def simulator_step(self):
        self.simulator.step()

    def step(self, action):
        return NotImplementedError

    def reset(self):
        return NotImplementedError

    def set_mode(self, mode):
        self.simulator.mode = mode

if __name__ == "__main__":
    config_filename = os.path.join(os.path.dirname(gibson2.__file__), '../test/test.yaml')
    env = BaseEnv(config_file=config_filename, mode='gui')
    for i in range(100):
        env.simulator_step()