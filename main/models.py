from django.contrib.auth.models import User
from django.db import models
class Users(models.Model):
    name = models.CharField(max_length=50)
    sex = models.CharField(max_length=1)
    age = models.IntegerField()
    level_id = models.ForeignKey(user_level, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
class user_level(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
class projects(models.Model):
    user_id=models.ForeignKey(Users, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateField()
    customer_name = models.CharField(max_length=100)
    price = models.IntegerField()
    def __str__(self):
        return self.name
class project_components_list(models.Model):
    project_id = models.ForeignKey(projects, on_delete=models.CASCADE)
class components(models.Model):
    component_id = models.ForeignKey(project_components_list, on_delete=models.CASCADE)
    user_id=models.ForeignKey(Users, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    left_amount = models.IntegerField()
    unit_type_id = models.IntegerField()
    price_per_unit = models.IntegerField()
    url = models.TextField()
    status_id = models.IntegerField()
    def __str__(self):
        return self.name
class unit_types(models.Model):
    unit_type_id = models.ForeignKey(components,to_field='unit_type_id', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
class component_status(models.Model):
    status_id = models.ForeignKey(components,to_field='status_id', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name


