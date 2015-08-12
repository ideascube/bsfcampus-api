from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class VisitedSkillJsonSerializer(ActivityJsonSerializer):
    pass


class VisitedSkill(VisitedSkillJsonSerializer, Activity):
    """
    Records when a skill is visited by a user
    """

    skill = db.ReferenceField('Skill')

    @property
    def object(self):
        return self.skill

    def clean(self):
        super(VisitedSkill, self).clean()
        self.type = "visited_skill"
