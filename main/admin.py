from django.contrib import admin
from .models import Users, User_level, projects, project_components_list, components
admin.site.register(Users)
admin.site.register(User_level)
admin.site.register(projects)
admin.site.register(project_components_list)
admin.site.register(components)