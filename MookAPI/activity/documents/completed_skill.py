from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class CompletedSkillJsonSerializer(ActivityJsonSerializer):
    pass


class CompletedSkill(CompletedSkillJsonSerializer, Activity):
    """
    Records when a resource is completed by a user
    """

    skill = db.ReferenceField('Skill')

    def all_syncable_items(self, local_server=None):
        top_level_syncable_document = self.skill.top_level_syncable_document()
        if local_server:
            if local_server.syncs_document(top_level_syncable_document):
                return super(CompletedSkill, self).all_syncable_items(local_server=local_server)
        return []
