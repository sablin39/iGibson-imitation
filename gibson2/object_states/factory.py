from gibson2.object_states.pose import Pose
from gibson2.object_states.aabb import AABB
from gibson2.object_states.contact_bodies import ContactBodies
from gibson2.object_states.dummy_state import DummyState


def get_object_state_instance(state_name, obj, online=True):
    if state_name == 'pose':
        return Pose(obj, online) if online else DummyState(obj, online)
    elif state_name == 'aabb':
        return AABB(obj, online) if online else DummyState(obj, online)
    elif state_name == 'contact_bodies':
        return ContactBodies(obj, online) if online else DummyState(obj, online)
    else:
        assert False, 'unknown state name: {}'.format(state_name)
