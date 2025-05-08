from django import forms
from django.contrib.auth.models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
from django import forms
from .models import components, projects


class ComponentForm(forms.ModelForm):
    class Meta:
        model = components
        fields = ['name', 'description', 'left_amount', 'unit_type', 'price_per_unit', 'url', 'status_id']
class ProjectForm(forms.ModelForm):
    # Добавляем поле для выбора компонентов - множественный выбор
    components = forms.ModelMultipleChoiceField(
        queryset=components.objects.none(),  # изначально пусто, заполнится в __init__
        required=False,
        widget=forms.CheckboxSelectMultiple  # можно поменять на SelectMultiple или другое
    )

    class Meta:
        model = projects
        fields = ['name', 'description', 'due_date', 'customer_name', 'price']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['components'].queryset = components.objects.filter(user_id=user)
