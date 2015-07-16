from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class CompletedSkillJsonSerializer(ActivityJsonSerializer):
    pass


class CompletedSkill(CompletedSkillJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    skill = db.ReferenceField('Skill')

    def __init__(self, **kwargs):
        super(CompletedSkill, self).__init__(**kwargs)
        self.type = "completed_skill"
        self.skill = kwargs.pop('skill', None)
