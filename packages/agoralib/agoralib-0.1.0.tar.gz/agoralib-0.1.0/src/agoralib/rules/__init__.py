from .position import PositionRule
from .shape import ShapeRule
from .proximity import ProximityRule
from .merge import MergeRule
from .delete import DeleteRule

RULE_CLASSES = {
    'position': PositionRule,
    'shape': ShapeRule,
    'proximity': ProximityRule,
    'merge': MergeRule,
    'delete': DeleteRule,
}