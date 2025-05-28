import json

from django import forms
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from DIY_BD import settings
from main.models import projects, components, project_components_list
from .forms import UserProfileForm,ComponentForm,ProjectForm
from django.db.models import Sum, F

def index(request):
    return render(request,'main/index.html')
@login_required
def projects_list(request):
    # Получаем проекты пользователя
    user_projects = projects.objects.filter(user_id=request.user)

    # Для каждого проекта посчитаем себестоимость - сумму цен всех компонентов
    # Компоненты связаны через project_components_list

    # Сперва получаем словарь с подсчитанной себестоимостью для всех проектов пользователя
    # Себестоимость = сумма price_per_unit компонентов, связанных с проектом
    # Измените расчет себестоимости компонентов, умножая price_per_unit на количество (amount)
    cost_dict = (
        project_components_list.objects
        .filter(project_id__in=user_projects)
        .values('project_id')
        .annotate(cost_price=Sum(F('component_id__price_per_unit') * F('amount')))
        .values_list('project_id', 'cost_price')
    )
    # Превратим в словарь для удобства
    cost_dict = dict(cost_dict)

    # Подготовим список данных для передачи в шаблон
    projects_with_cost = []
    for p in user_projects:
        cost = cost_dict.get(p.id) or 0
        projects_with_cost.append({
            'id': p.id,
            'name': p.name,
            'customer_name': p.customer_name,
            'cost': cost,
            'price': p.price,
            'amount': p.amount,
            'profit': p.amount * p.price if p.price is not None else 0,
            'due_date': p.due_date,
            'for_sale': p.for_sale,
        })

    return render(request, 'main/projects_list.html', {'projects': projects_with_cost})


@login_required
def project_create(request):
    """
    Создание нового проекта с динамическим добавлением компонентов
    """
    # Проверка лимита проектов
    if not projects.can_add_projects(request.user):
        messages.warning(request, "Для создания большего количества проектов требуется подписка")
        return redirect('purchase_subscription')

    if request.method == 'POST':
        form = ProjectForm(request.POST, user=request.user)

        if form.is_valid():
            try:
                with transaction.atomic():  # Транзакция для целостности данных
                    # Сохранение проекта
                    project = form.save(commit=False)
                    project.user_id = request.user
                    project.save()

                    # Обработка компонентов
                    components_data = json.loads(form.cleaned_data['components_data'])

                    # Проверка наличия компонентов
                    if not components_data:
                        raise forms.ValidationError("Не выбрано ни одного компонента")

                    # Создание связей с компонентами
                    for comp in components_data:
                        # Проверка существования компонента
                        if not components.objects.filter(id=comp['id'], user_id=request.user).exists():
                            raise forms.ValidationError(f"Компонент {comp.get('name', '')} не найден")

                        project_components_list.objects.create(
                            project_id=project,
                            component_id_id=comp['id'],
                            amount=comp['amount']
                        )

                    messages.success(request, "Проект успешно создан")
                    return redirect('projects_list')

            except json.JSONDecodeError:
                messages.error(request, "Ошибка обработки данных компонентов")
            except Exception as e:
                messages.error(request, f"Ошибка при создании проекта: {str(e)}")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме")
    else:
        form = ProjectForm(user=request.user)

    context = {
        'form': form,
        'title': 'Создать новый проект',
        'max_components': settings.MAX_COMPONENTS_PER_PROJECT  # Пример дополнительного параметра
    }

    return render(request, 'main/project_form.html', context)
@login_required
def project_edit(request, pk):
    project = get_object_or_404(projects, pk=pk, user_id=request.user.id)

    if request.method == 'POST':
        form = ProjectForm(request.POST, user=request.user, instance=project)
        if form.is_valid():
            project = form.save()

            # Обработка компонентов
            components_data = json.loads(form.cleaned_data['components_data'])
            project_components_list.objects.filter(project_id=project).delete()

            for comp in components_data:
                project_components_list.objects.create(
                    project_id=project,
                    component_id_id=comp['id'],
                    amount=comp['amount']
                )

            messages.success(request, "Проект успешно обновлен")
            return redirect('project_detail', pk=project.pk)
    else:
        # Загрузка связанных компонентов
        linked_components = project_components_list.objects.filter(
            project_id=project
        ).select_related('component_id')

        initial_components = [
            {
                'id': link.component_id.id,
                'name': link.component_id.name,
                'amount': link.amount,
                'unit': link.component_id.unit_type
            }
            for link in linked_components
        ]

        form = ProjectForm(user=request.user, instance=project)
        form.fields['components_data'].initial = json.dumps(initial_components)  # Исправленное имя поля

    return render(request, 'main/project_form.html', {
        'form': form,
        'title': 'Редактировать проект',
        'project': project
    })
@login_required
def project_detail(request, pk):
    project = get_object_or_404(projects, pk=pk, user_id=request.user.id)
    return render(request, 'main/project_detail.html', {'project': project})
@login_required
def project_delete(request, pk):
    project = get_object_or_404(projects, pk=pk, user_id=request.user.id)
    if request.method == 'POST':
        project.delete()
        return redirect('projects_list')
    return render(request, 'main/project_confirm_delete.html', {'project': project})


@login_required
def components_list(request):
    user = request.user
    user_components = components.objects.filter(user_id=user.id)

    # Создаем словарь для отображения остатков
    for component in user_components:
        component.remaining_amount = component.remaining_amount()  # Добавляем оставшееся количество

    return render(request, 'main/components_list.html', {'components': user_components})


@login_required
def component_create(request):
    if not components.can_add_components(request.user):
        return redirect('purchase_subscription')
    if request.method == 'POST':
        form = ComponentForm(request.POST)
        if form.is_valid():
            new_component = form.save(commit=False)
            new_component.user_id = request.user
            new_component.save()
            return redirect('components_list')
    else:
        form = ComponentForm()
    return render(request, 'main/component_form.html', {'form': form, 'title': 'Добавить компонент'})

@login_required
def component_edit(request, pk):
    component = get_object_or_404(components, pk=pk, user_id=request.user.id)
    if request.method == 'POST':
        form = ComponentForm(request.POST, instance=component)
        if form.is_valid():
            form.save()
            return redirect('components_list')
    else:
        form = ComponentForm(instance=component)
    return render(request, 'main/component_form.html', {'form': form, 'title': 'Редактировать компонент'})

@login_required
def component_delete(request, pk):
    component = get_object_or_404(components, pk=pk, user_id=request.user.id)
    if request.method == 'POST':
        component.delete()
        return redirect('components_list')
    return render(request, 'main/component_confirm_delete.html', {'component': component})
@login_required
def profile(request):
    user = request.user

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user)

    # Получаем количество проектов и компонентов пользователя:
    projects_count = projects.objects.filter(user_id=user.id).count()
    components_count = components.objects.filter(user_id=user.id).count()

    context = {
        'form': form,
        'projects_count': projects_count,
        'components_count': components_count,
        'user': user,
    }
    return render(request, 'main/profile.html', context)
@login_required
def custom_logout(request):
    logout(request)  # Это вызовет выход из учетной записи
    return redirect('/')
@login_required
def purchase_subscription(request):
    # Логика покупки подписки
    if request.method == 'POST':
        # Обработка оплаты (если необходимо)
        user = request.user
        user.level_id = 1  # Установим платный уровень
        user.save()

        return redirect('subscription_success')  # Перенаправление на страницу подтверждения

    return render(request, 'main/purchase_subscription.html', {'title': 'Купить подписку'})
# views.py
@login_required
def subscription_success(request):
    return render(request, 'main/subscription_success.html', {'title': 'Успех подписки'})

@login_required
def get_components_data(request):
    if not request.user.is_authenticated:
        return JsonResponse({}, status=401)

    user_components = components.objects.filter(user_id=request.user).values('id', 'unit_type')
    return JsonResponse({
        'components': list(user_components)
    })




