from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class CompletedSkillJsonSerializer(ActivityJsonSerializer):
    pass


class CompletedSkill(CompletedSkillJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    skill = db.ReferenceField('Skill')

    def clean(self):
        super(CompletedSkill, self).clean()
        self.type = "completed_skill"
        if self.skill:
            self.activity_id = self.skill.id
            self.activity_title = self.skill.title
