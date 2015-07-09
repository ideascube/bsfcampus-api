from MookAPI.core import Service
from documents import Activity
from documents.exercise_attempt import ExerciseAttempt
from documents.skill_validation_attempt import SkillValidationAttempt
from documents.track_validation_attempt import TrackValidationAttempt
from documents.completed_resource import CompletedResource
from documents.completed_skill import CompletedSkill
from documents.completed_track import CompletedTrack
from documents.started_track import StartedTrack
from documents.unlocked_track_test import UnlockedTrackTest

class ActivitiesService(Service):
    __model__ = Activity

class ExerciseAttemptsService(Service):
    __model__ = ExerciseAttempt

class SkillValidationAttemptsService(Service):
    __model__ = SkillValidationAttempt

class TrackValidationAttemptsService(Service):
    __model__ = TrackValidationAttempt

class CompletedResourcesService(Service):
    __model__ = CompletedResource

class CompletedSkillsService(Service):
    __model__ = CompletedSkill

class CompletedTracksService(Service):
    __model__ = CompletedTrack

class StartedTracksService(Service):
    __model__ = StartedTrack

class UnlockedTrackTestsService(Service):
    __model__ = UnlockedTrackTest
