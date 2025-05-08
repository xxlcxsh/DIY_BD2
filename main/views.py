from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
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
    cost_dict = (
        project_components_list.objects
        .filter(project_id__in=user_projects)
        .values('project_id')
        .annotate(cost_price=Sum('component_id__price_per_unit'))
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
            'cost_price': cost,
            'price_sale': p.price,
        })

    return render(request, 'main/projects_list.html', {'projects': projects_with_cost})


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, user=request.user)
        if form.is_valid():
            new_project = form.save(commit=False)
            new_project.user_id = request.user
            new_project.save()

            # Сохраняем связанные компоненты
            selected_components = form.cleaned_data['components']
            # Очистим старые связи, если есть (при создании их не должно быть)
            project_components_list.objects.filter(project_id=new_project).delete()
            for comp in selected_components:
                project_components_list.objects.create(project_id=new_project, component_id=comp)
            return redirect('project_detail', pk=new_project.pk)
    else:
        form = ProjectForm(user=request.user)  # при GET или другом методе создаём пустую форму

    # Возвращаем страницу с формой (и ошибками, если есть)
    return render(request, 'main/project_form.html', {'form': form, 'title': 'Добавить проект'})

@login_required
def project_edit(request, pk):
    project = get_object_or_404(projects, pk=pk, user_id=request.user.id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()

            selected_components = form.cleaned_data['components']
            # Удалим все старые связи
            project_components_list.objects.filter(project_id=project).delete()
            for comp in selected_components:
                project_components_list.objects.create(project_id=project, component_id=comp)

            return redirect('project_detail', pk=project.pk)
    else:
        # Получим компоненты, связанные с проектом
        linked_components_ids = project_components_list.objects.filter(
            project_id=project
        ).values_list('component_id', flat=True)

        initial_components = components.objects.filter(id__in=linked_components_ids)

        form = ProjectForm(instance=project)
        # Предварительно передать компоненты в форму, если нужно
        # (зависит, как ты реализовал поле components в форме)
        # Например:
        # form.fields['components'].initial = list(linked_components_ids)

    return render(request, 'main/project_form.html', {'form': form, 'title': 'Редактировать проект'})

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
    return render(request, 'main/components_list.html', {'components': user_components})

@login_required
def component_create(request):
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


