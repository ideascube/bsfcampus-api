from .users import \
    RolesService, \
    UsersService

roles = RolesService()
users = UsersService()

from .hierarchy import \
    TracksService, \
    SkillsService, \
    LessonsService

tracks = TracksService()
skills = SkillsService()
lessons = LessonsService()

from .resources import \
    ResourcesService, \
    AudioResourcesService, \
    DownloadableFileResourcesService, \
    ExerciseResourcesService, \
    ExternalVideoResourcesService, \
    RichTextResourcesService, \
    TrackValidationResourcesService, \
    VideoResourcesService

resources = ResourcesService()
audio_resources = AudioResourcesService()
downloadable_file_resources = DownloadableFileResourcesService()
exercise_resources = ExerciseResourcesService()
external_video_resources = ExternalVideoResourcesService()
rich_text_resources = RichTextResourcesService()
track_validation_resources = TrackValidationResourcesService()
video_resources = VideoResourcesService()

from .activity import \
    ActivitiesService, \
    ExerciseAttemptsService, \
    SkillValidationAttemptsService, \
    TrackValidationAttemptsService, \
    CompletedResourcesService, \
    CompletedSkillsService, \
    CompletedTracksService, \
    StartedTracksService, \
    UnlockedTrackTestsService, \
    VisitedTrackService, \
    VisitedSkillService, \
    VisitedResourceService, \
    VisitedDashboardService, \
    MiscActivityService

activities = ActivitiesService()
exercise_attempts = ExerciseAttemptsService()
skill_validation_attempts = SkillValidationAttemptsService()
track_validation_attempts = TrackValidationAttemptsService()
completed_resources = CompletedResourcesService()
completed_skills = CompletedSkillsService()
completed_tracks = CompletedTracksService()
started_tracks = StartedTracksService()
unlocked_track_tests = UnlockedTrackTestsService()
visited_tracks = VisitedTrackService()
visited_skills = VisitedSkillService()
visited_resources = VisitedResourceService()
visited_user_dashboards = VisitedDashboardService()
misc_activities = MiscActivityService()

from .local_servers import LocalServersService

local_servers = LocalServersService()
