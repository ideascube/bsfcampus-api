from exercise import ExerciseResourceJsonSerializer, ExerciseResource
from MookAPI.core import db


class TrackValidationResourceJsonSerializer(ExerciseResourceJsonSerializer):
    pass

class TrackValidationResource(TrackValidationResourceJsonSerializer, ExerciseResource):
    """An track validation test with a list of questions."""

    parent = db.ReferenceField('Track')
    """The parent Hierarchy object (here, it is a Track)."""

    @property
    def track(self):
        return self.parent

    @property
    def hierarchy(self):
        """
        Returns an array of the breadcrumbs up until the current object: [Track_, Skill_, Lesson_, Resource_]
        """

        return [
            self.track.to_json_dbref(),
            self.to_json_dbref()
        ]
