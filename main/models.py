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
    price = models.IntegerField(null=True, blank=True)  # Изменено: теперь может быть null
    amount = models.IntegerField(null=False,default=1)
    completed = models.BooleanField(default=False)  # Флаг завершения проекта
    for_sale = models.BooleanField("На продажу?", default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Сначала сохраняем сам проект
        self.update_component_amounts()  # Затем обновляем остатки компонентов

    def update_component_amounts(self):
        components_in_project = project_components_list.objects.filter(project_id=self)
        for relation in components_in_project:
            component = relation.component_id
            # Обновляем количество оставшихся в таблице Components
            component.left_amount -= relation.amount  # Предполагается, что в relation есть поле amount
            component.save()

    @staticmethod
    def can_add_projects(user):
        if user.level_id == 1:  # Если платная подписка
            return True
        # Проверка для бесплатной версии
        return projects.objects.filter(user=user).count() < 5
    

class components(models.Model):
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

    # Метод для вычисления оставшихся компонентов
    def remaining_amount(self):
        total_used = project_components_list.objects.filter(component_id=self).aggregate(total=models.Sum('amount'))['total'] or 0
        return self.left_amount - total_used

    @staticmethod
    def can_add_components(user):
        if user.level_id == 1:  # Если платная подписка
            return True
        # Проверка для бесплатной версии
        return components.objects.filter(user=user).count() < 20
    

class project_components_list(models.Model):
    project_id = models.ForeignKey(projects, on_delete=models.CASCADE)
    component_id = models.ForeignKey(components, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.IntegerField(default=1)
