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
    # FIXME this has to be set using the credentials provided

    dashboard_user_full_name = db.StringField()
    """ The full name of the dashboard_user """

    def clean(self):
        super(VisitedDashboard, self).clean()
        self.type = "visited_profile"
        if self.dashboard_user:
            self.dashboard_user_full_name = self.dashboard_user.full_name
