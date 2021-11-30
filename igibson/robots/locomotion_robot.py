from abc import abstractmethod

import gym
import numpy as np
from transforms3d.euler import euler2quat
from transforms3d.quaternions import qmult, quat2mat

from igibson.controllers import LocomotionController
from igibson.robots.robot_base import BaseRobot
from igibson.utils.python_utils import assert_valid_key


class LocomotionRobot(BaseRobot):
    """
    Robot that is is equipped with locomotive (navigational) capabilities.
    Provides common interface for a wide variety of robots.

    NOTE: controller_config should, at the minimum, contain:
        base: controller specifications for the controller to control this robot's base (locomotion).
            Should include:

            - name: Controller to create
            - <other kwargs> relevant to the controller being created. Note that all values will have default
                values specified, but setting these individual kwargs will override them

    """

    def _validate_configuration(self):
        # We make sure that our base controller exists and is a locomotion controller
        assert (
            "base" in self._controllers
        ), "Controller 'base' must exist in controllers! Current controllers: {}".format(list(self._controllers.keys()))
        assert isinstance(
            self._controllers["base"], LocomotionController
        ), "Base controller must be a LocomotionController!"

        # run super
        super()._validate_configuration()

    @property
    def controller_order(self):
        # By default, only base is supported
        return ["base"]

    @property
    def _default_controllers(self):
        # Always call super first
        controllers = super()._default_controllers

        # For best generalizability use, joint controller as default
        controllers["base"] = "JointController"

        return controllers

    @property
    def _default_base_joint_controller_config(self):
        """
        :return: Dict[str, Any] Default base joint controller config to control this robot's base. Uses velocity
            control by default.
        """
        return {
            "name": "JointController",
            "control_freq": self.control_freq,
            "motor_type": "velocity",
            "control_limits": self.control_limits,
            "joint_idx": self.base_control_idx,
            "command_output_limits": "default",
            "use_delta_commands": False,
            "use_compliant_mode": True,
        }

    @property
    def _default_base_differential_drive_controller_config(self):
        """
        :return: Dict[str, Any] Default differential drive controller config to
            control this robot's base. Note: assumes self.wheel_radius and self.wheel_axle_length properties
            are specified!
        """
        # Make sure base only has two indices (i.e.: two wheels for differential drive)
        assert len(self.base_control_idx) == 2, "Differential drive can only be used with robot with two base joints!"
        assert hasattr(self, "wheel_radius"), "self.wheel_radius property must be specified to use differential drive!"
        assert hasattr(self, "wheel_axle_length"), (
            "self.wheel_axle_length property must be specified to use " "differential drive!"
        )

        # Calculate max linear, angular velocities -- make sure each wheel has same max values
        max_vels = [list(self._joints.values())[i].max_velocity for i in self.base_control_idx]
        assert max_vels[0] == max_vels[1], "Differential drive requires both wheel joints to have same max velocities!"
        max_lin_vel = max_vels[0] * self.wheel_radius
        max_ang_vel = max_lin_vel * 2.0 / self.wheel_axle_length

        return {
            "name": "DifferentialDriveController",
            "control_freq": self.control_freq,
            "wheel_radius": self.wheel_radius,
            "wheel_axle_length": self.wheel_axle_length,
            "control_limits": self.control_limits,
            "joint_idx": self.base_control_idx,
            "command_output_limits": ([-max_lin_vel, -max_ang_vel], [max_lin_vel, max_ang_vel]),  # (lin_vel, ang_vel)
        }

    @property
    def _default_controller_config(self):
        # Always run super method first
        cfg = super()._default_controller_config

        # Add supported base controllers
        cfg["base"] = {
            self._default_base_differential_drive_controller_config[
                "name"
            ]: self._default_base_differential_drive_controller_config,
            self._default_base_joint_controller_config["name"]: self._default_base_joint_controller_config,
        }

        return cfg

    def move_by(self, delta):
        """
        Move robot base without physics simulation

        :param delta: Array[float], (x,y,z) cartesian delta base position
        """
        new_pos = np.array(delta) + self.get_position()
        self.robot_body.reset_position(new_pos)

    def move_forward(self, delta=0.05):
        """
        Move robot base forward without physics simulation

        :param delta: float, delta base position forward
        """
        self.move_by(quat2mat(self.base_link.get_orientation()).dot(np.array([delta, 0, 0])))

    def move_backward(self, delta=0.05):
        """
        Move robot base backward without physics simulation

        :param delta: float, delta base position backward
        """
        self.move_by(quat2mat(self.base_link.get_orientation()).dot(np.array([-delta, 0, 0])))

    def move_left(self, delta=0.05):
        """
        Move robot base left without physics simulation

        :param delta: float, delta base position left
        """
        self.move_by(quat2mat(self.base_link.get_orientation()).dot(np.array([0, -delta, 0])))

    def move_right(self, delta=0.05):
        """
        Move robot base right without physics simulation

        :param delta: float, delta base position right
        """
        self.move_by(quat2mat(self.base_link.get_orientation()).dot(np.array([0, delta, 0])))

    def turn_left(self, delta=0.03):
        """
        Rotate robot base left without physics simulation

        :param delta: float, delta angle to rotate the base left
        """
        quat = self.base_link.get_orientation()
        quat = qmult((euler2quat(-delta, 0, 0)), quat)
        self.base_link.set_orientation(quat)

    def turn_right(self, delta=0.03):
        """
        Rotate robot base right without physics simulation

        :param delta: delta angle to rotate the base right
        """
        quat = self.base_link.get_orientation()
        quat = qmult((euler2quat(delta, 0, 0)), quat)
        self.base_link.set_orientation(quat)

    def keep_still(self):
        """
        Keep the robot still. Apply zero velocity to all joints.
        """
        for n, j in enumerate(self.joints.values()):
            j.set_vel(0.0)

    @property
    @abstractmethod
    def base_control_idx(self):
        """
        :return Array[int]: Indices in low-level control vector corresponding to base joints.
        """
        raise NotImplementedError
