from django.contrib.auth.models import User,AbstractUser
from django.db import models
class Users(AbstractUser):
    username = models.CharField(max_length=50,unique=True)
    password=models.CharField(max_length=128)
    sex = models.CharField(max_length=6)
    age = models.IntegerField()
    level_id=models.IntegerField(default=0)#0-бесплатная, 1 - платная
    def __str__(self):
        return self.first_name+" "+self.last_name
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
    unit_type = models.CharField(max_length=10)
    price_per_unit = models.IntegerField()
    url = models.TextField()
    status_id = models.IntegerField()
    def __str__(self):
        return self.name


