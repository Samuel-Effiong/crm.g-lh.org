from .models import (
    Department, DepartmentMember, DepartmentCategory,
    DepartmentProject, ProjectTarget, DepartmentTable,
    CustomField, FieldValue, FieldValueIndex,

    Diaconate, Unit, SubUnit, Team
)

import json
from django.utils import timezone
from django.db.models import Count, Q


def super_user_details(context, user, today, **kwargs):
    context['member_departments'] = Department.objects.all()

    context['diaconates'] = Diaconate.objects.all()
    context['departments_count'] = Department.objects.count()
    project_totals = DepartmentProject.objects.aggregate(
        active_project=Count('pk', filter=Q(status='In Progress')),
        pending_project=Count('pk', filter=Q(status='Not Started')),
        completed_project=Count('pk', filter=Q(status='Completed')),
        critical_project=Count('pk', filter=Q(project_priority='High'))
    )
    context['active_projects_count'] = project_totals.get('active_project', 0)

    context['performance_score'] = Diaconate.objects.get_overall_performance_score()['performance_score']
    context['performance_score_for_each_diaconate'] = Diaconate.objects.get_performance_score_for_each_diaconate()
    context['top_lowest_member_performing_score'] = DepartmentMember.objects.get_top_and_lowest_performing_members(
        limit=10)

    context['department_members_count'] = DepartmentMember.objects.count()
    context['project_target_totals'] = ProjectTarget.objects.aggregate(
        completed_target=Count('pk', filter=Q(state='Completed')),
        pending_target=Count('pk', filter=Q(state='Pending Approval')),
        active_target=Count('pk', filter=Q(state='In Progress')),
        not_started_target=Count('pk', filter=Q(state="Not Started")),
    )

    # Chart based data

    diaconate_chart_data = Diaconate.objects.get_overview_statistics()

    categories = [data.name for data in diaconate_chart_data]
    members = [data.num_members for data in diaconate_chart_data]
    active_projects = [data.num_active_projects for data in diaconate_chart_data]
    overdue_project = [data.num_overdue_projects for data in diaconate_chart_data]

    pending_targets = [data.num_pending_targets for data in diaconate_chart_data]
    active_targets = [data.num_active_targets for data in diaconate_chart_data]
    not_started_targets = [data.num_not_started_targets for data in diaconate_chart_data]

    context['diaconate_chart_data'] = {
        'categories': json.dumps(categories),
        'members': json.dumps(members),
        'active_projects': json.dumps(active_projects),
        'overdue_projects': json.dumps(overdue_project),

        'pending_targets': json.dumps(pending_targets),
        'active_targets': json.dumps(active_targets),
        'not_started_targets': json.dumps(not_started_targets),
    }

    context['active_projects'] = DepartmentProject.objects.filter(status='In Progress').order_by('-due_date')[:5]
    context['all_overdue_projects'] = DepartmentProject.objects.get_overdue_projects()

    context['active_targets'] = ProjectTarget.objects.filter(state='In Progress').order_by('-date')[:5]


def diakonate_details(context, user, today, **kwargs):
    user_diaconates = Diaconate.objects.filter(Q(head=user) | Q(assistant=user))
    context['diaconates'] = user_diaconates

    department_queryset = Department.objects.filter(department_diaconate__in=user_diaconates)
    context['member_departments'] = department_queryset

    department_project_queryset = DepartmentProject.objects.filter(department__department_diaconate__in=user_diaconates)

    context['departments_count'] = department_queryset.count()

    project_totals = department_project_queryset.aggregate(
        active_project=Count('pk', filter=Q(status='In Progress')),
        pending_project=Count('pk', filter=Q(status='Not Started')),
        completed_project=Count('pk', filter=Q(status='Completed')),
        critical_project=Count('pk', filter=Q(project_priority='High'))
    )

    context['active_projects_count'] = project_totals.get('active_project', 0)

    # context['performance_score'] =


def department_details(context, user, today, **kwargs):
    user_departments = Department.objects.filter(Q(leader__member_name=user) | Q(sub_leader__member_name=user))

    user_diaconates = Diaconate.objects.filter(
        Q(department__leader__member_name=user) | Q(department__sub_leader__member_name=user)
    ).distinct()

    department_queryset = Department.objects.filter(department_diaconate__in=user_diaconates)
    department_project_queryset = DepartmentProject.objects.filter(department__department_diaconate__in=user_diaconates)

    context['member_departments'] = user_departments
    context['diaconates'] = user_diaconates
    context['departments_count'] = user_departments.count()


def unit_leader_details(context):
    pass


def handle_view_details_for_various_roles(context):
    user = context['user']
    today = timezone.now().date()

    department_queryset = Department.objects.all()
    diaconate_queryset = Diaconate.objects.all()
    department_project_queryset = DepartmentProject.objects.all()
    project_target_queryset = ProjectTarget.objects.all()
    department_member_queryset = DepartmentMember.objects.all()

    queryset = {
        'department_queryset': department_queryset,
        'diaconate_queryset': diaconate_queryset,
        'department_project_queryset': department_project_queryset,
        'project_target_queryset': project_target_queryset,
        'department_member_queryset': department_member_queryset,
    }

    if user.is_superuser:
        super_user_details(context, user, today)
    elif user.groups.filter(name='Diakonate Head').exists():
        diakonate_details(context, user, today)
    elif user.groups.filter(name='Department Head').exists():
        department_details(context, user, today)
    else:  # Belonged to a department
        user_departments = Department.objects.filter(Q(member_names__member_name=user))

        user_diaconates = Diaconate.objects.filter(
            Q(department__in=user_departments)
        )

        context['member_departments'] = user_departments
        context['diaconates'] = user_diaconates
        context['departments_count'] = user_departments.count()


def subunit_leader_details(context):
    pass