from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class VisitedSkillJsonSerializer(ActivityJsonSerializer):
    pass


class VisitedSkill(VisitedSkillJsonSerializer, Activity):
    """
    Records when a skill is visited by a user
    """

    skill = db.ReferenceField('Skill')

    def __init__(self, *args, **kwargs):
        super(VisitedSkill, self).__init__(*args, **kwargs)
        self.type = "visited_skill"
        self.skill = kwargs.pop('skill', None)

    def clean(self):
        super(VisitedSkill, self).clean()
        if self.skill:
            self.activity_id = self.skill.id
            self.activity_title = self.skill.title
