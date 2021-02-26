from gibson2.external.pybullet_tools.utils import get_link_position_from_name
from gibson2.object_states.object_state_base import AbsoluteObjectState
from gibson2.objects.particles import WaterStreamPhysicsBased

_WATER_SOURCE_LINK_NAME = "water_source"


class WaterSource(AbsoluteObjectState):

    def __init__(self, obj):
        super(WaterSource, self).__init__(obj)

        # Reduced to a single water stream for now since annotations don't support more.
        self.water_stream = None

    def update(self, simulator):
        water_source_position = get_link_position_from_name(self.obj.get_body_id(), _WATER_SOURCE_LINK_NAME)
        if water_source_position is None:
            return

        if self.water_stream is None:
            self.water_stream = WaterStreamPhysicsBased(self.obj, pos=water_source_position, num=10)
            simulator.import_particle_system(self.water_stream)
        else:
            self.water_stream.water_source_pos = water_source_position

        if "toggled_on" in self.obj.states:
            # sync water source state with toggleable
            self.water_stream.set_value(self.obj.states["toggled_on"].get_value())
        else:
            self.water_stream.set_value(True)  # turn on the water by default

        self.water_stream.step()

        # water reusing logic
        contacted_water_body_ids = set(item[1] for item in list(self.obj.states["contact_bodies"].get_value()))
        for particle in self.water_stream.particles:
            if particle.body_id in contacted_water_body_ids:
                self.water_stream.stash_particle(particle)

        # soaking logic
        soaked = simulator.scene.get_objects_with_state("soaked")
        for soakable_object in soaked:
            contacted_water_body_ids = set(
                item[1] for item in list(soakable_object.states["contact_bodies"].get_value()))
            for particle in self.water_stream.particles:
                if particle.body_id in contacted_water_body_ids:
                    soakable_object.states["soaked"].set_value(True)

    def set_value(self, new_value):
        pass

    def get_value(self):
        pass

    @staticmethod
    def get_optional_dependencies():
        return ["toggled_on"]

    @staticmethod
    def get_dependencies():
        return ["contact_bodies"]
