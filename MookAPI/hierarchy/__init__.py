from MookAPI.core import Service
from .documents.track import Track
from .documents.skill import Skill
from .documents.lesson import Lesson


class TracksService(Service):
    __model__ = Track

class SkillsService(Service):
    __model__ = Skill

class LessonsService(Service):
    __model__ = Lesson
