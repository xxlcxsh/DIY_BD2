from django.contrib.auth.models import User
from django import forms
from .models import projects, components, project_components_list

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
    components = forms.ModelMultipleChoiceField(
        queryset=components.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    component_amounts = forms.CharField(
        required=False,
        help_text="Введите количество для каждого выбранного компонента через запятую",
        widget=forms.TextInput(attrs={'placeholder': '1, 2, 3,...'})
    )

    class Meta:
        model = projects
        fields = ['name', 'description', 'due_date', 'customer_name', 'price', 'amount', 'components']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['components'].queryset = components.objects.filter(user_id=user)


