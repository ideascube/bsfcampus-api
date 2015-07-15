from MookAPI.core import db

from . import ActivityJsonSerializer, Activity


class VisitedDashboardJsonSerializer(ActivityJsonSerializer):
    pass


class VisitedDashboard(VisitedDashboardJsonSerializer, Activity):
    """
    Records when user visits its profile page (requests his dashboard)
    """

    dashboard_user = db.ReferenceField('User')
    """ The user whose dashboard is currently looked at by the current_user"""

    dashboard_user_username = db.StringField()
    """ The username of the dashboard_user """

    dashboard_user_full_name = db.StringField()
    """ The full name of the dashboard_user """

    def __init__(self, **kwargs):
        super(VisitedDashboard, self).__init__(**kwargs)
        self.type = "visited_profile"
        self.dashboard_user = kwargs.pop('dashboard_user', None)

    def clean(self):
        super(VisitedDashboard, self).clean()
        if self.dashboard_user:
            self.dashboard_user_username = self.dashboard_user.username
            self.dashboard_user_full_name = self.dashboard_user.full_name
