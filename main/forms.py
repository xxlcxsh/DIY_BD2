import json
from django.contrib.auth.models import User
from django import forms
from django.utils import timezone

from .models import projects, components, project_components_list

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ComponentForm(forms.ModelForm):
    left_amount = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Остаток"
    )

    price_per_unit = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Остаток"
    )

    class Meta:
        model = components
        fields = ['name', 'description', 'left_amount', 'unit_type', 'price_per_unit', 'url', 'status_id']
class ProjectForm(forms.ModelForm):
    # Заменяем поле due_date на версию с HTML5 date input
    due_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'type': 'date',  # Ключевое изменение - тип date
                'class': 'form-control',
                'min': timezone.now().strftime('%Y-%m-%d')  # Минимальная дата - сегодня
            }
        ),
        input_formats=['%Y-%m-%d'],  # Стандартный формат для HTML5 date input
        label="Дедлайн"
    )

    customer_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя заказчика'
        }),
        label="Имя заказчика"
    )

    price = forms.IntegerField(
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Цена'
        }),
        label="Цена"
    )

    amount = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Количество'
        }),
        label="Количество проектов"
    )

    for_sale = forms.BooleanField(
        required=False,
        label="На продажу?",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    # Поля для работы с компонентами
    component_choice = forms.ModelChoiceField(
        queryset=components.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_component_choice'
        }),
        label="Выберите компонент"
    )

    components_data = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta:
        model = projects
        fields = ['name', 'description', 'due_date', 'customer_name',
                  'price', 'amount', 'for_sale']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
        labels = {
            'name': 'Название проекта',
            'description': 'Описание'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.set_component_queryset()

            if self.instance.pk:
                self.load_existing_components()

    def set_component_queryset(self):
        """Устанавливает queryset для компонентов текущего пользователя"""
        self.fields['component_choice'].queryset = (
            components.objects.filter(user_id=self.user)
            .only('id', 'name', 'unit_type', 'price_per_unit')
        )

    def load_existing_components(self):
        """Загружает компоненты существующего проекта"""
        try:
            linked_components = (
                project_components_list.objects
                .filter(project_id=self.instance)
                .select_related('component_id')
            )

            components_list = [
                {
                    'id': item.component_id.id,
                    'name': item.component_id.name,
                    'amount': item.amount,
                    'unit': item.component_id.unit_type,
                    'price': item.component_id.price_per_unit
                }
                for item in linked_components
            ]

            self.fields['components_data'].initial = json.dumps(components_list)
        except Exception as e:
            print(f"Error loading components: {e}")

    def clean(self):
        cleaned_data = super().clean()
        self.validate_components()
        return cleaned_data

    def validate_components(self):
        """Валидация выбранных компонентов"""
        components_data = self.cleaned_data.get('components_data', '[]')

        try:
            components_list = json.loads(components_data)
            if not components_list:
                raise forms.ValidationError("Добавьте хотя бы один компонент")

            for comp in components_list:
                if not components.objects.filter(
                        id=comp['id'],
                        user_id=self.user
                ).exists():
                    raise forms.ValidationError(
                        f"Компонент {comp['name']} недоступен"
                    )
        except json.JSONDecodeError:
            raise forms.ValidationError("Ошибка обработки компонентов")

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user_id = self.user

        if commit:
            instance.save()
            self.save_project_components(instance)

        return instance

    def save_project_components(self, project):
        """Сохранение связей проекта с компонентами"""
        project_components_list.objects.filter(project_id=project).delete()

        components_data = json.loads(self.cleaned_data.get('components_data', '[]'))

        for comp in components_data:
            project_components_list.objects.create(
                project_id=project,
                component_id_id=comp['id'],
                amount=comp['amount']
            )