import pytest
import json

@pytest.fixture(params=['admin', 'description', 'contenu', 'exercice'])
def role(request):
    from MookAPI.services import roles
    role_name = request.param
    role = roles.create(name=role_name, description='')
    return role


visible_views = {
     '/admin/staticpage/': ('admin',),
     '/admin/protectedfileadmin/': ('admin', 'contenu'),
     '/admin/exerciseresource/': ('admin', 'exercice'),
     '/admin/trackvalidationresource/': ('admin', 'exercice'),
     '/admin/richtextresource/': ('admin',  'contenu'),
     '/admin/audioresource/': ('admin',  'contenu'),
     '/admin/videoresource/': ('admin',  'contenu'),
     '/admin/downloadablefileresource/': ('admin',  'contenu'),
     '/admin/track/': ('admin', 'description'),
     '/admin/skill/': ('admin', 'description'),
     '/admin/lesson/': ('admin', 'description'),
     '/admin/user/': ('admin', ),
     '/admin/role/': ('admin', ),
     '/admin/localserver/': ('admin', ),
     '/admin/upload_local_servers/': ('admin',),
     '/admin/admin_analytics/': ('admin', 'description'),
}

def test_views_access(admin_conn_client, role):
    admin_conn_client.user.roles.append(role)
    admin_conn_client.user.save()
    for view, roles in visible_views.items():
        rv = admin_conn_client.get(view)
        if role.name in roles:
            assert rv.status_code == 200
        else:
            assert rv.status_code == 403        
    
    
