from django.urls import path
from .views import (DashboardView, SheepSummaryDetailView, ShepherdSheepListView,
                    ProfileDetailView, DetailView, ShepherdReportView)

#############  WORKSPACE  ###########
from .views import (CatalogView, AddCatalogView, FaultyCatalogView, TestimoniesView,
                    AddTestimonyView, PropheticWordsView, AddPropheticWordsView, 
                    BlogView, AddBlogView, SermonsView, AddSermonsView, GeneratedNewsView)


###########  END WORKSPACE  ###########
from .views import FetchView


app_name = 'pastoring'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('chief-shepherd/shepherd/<int:pk>/', ShepherdSheepListView.as_view(), name='shepherd-list'),
    path('<str:shepherd>/sheep-info/<str:sheep>/', SheepSummaryDetailView.as_view(), name='sheep-summary'),
    path('<str:shepherd>/sheep-info/<str:sheep>/profile/', ProfileDetailView.as_view(), name='sheep-profile'),
    path('<str:shepherd>/sheep-info/<str:sheep>/detail/<str:category>/<int:pk>/', DetailView.as_view(), name='sheep-detail'),

    path('shepherd-reports/', ShepherdReportView.as_view(), name='shepherd-reports'),

    #####################  WORKSPACE  ################################
    path('catalog/', CatalogView.as_view(), name='catalog'),
    # path('catalog/detail/, Catalo'),
    path('catalog/add/', AddCatalogView.as_view(), name='add-catalog'),

    path('catalog/faulty/', FaultyCatalogView.as_view(), name='faulty-catalog'),
    path('catalog/faulty/<str:action>/<int:pk>/', FaultyCatalogView.as_view(), name='faulty-catalog-action'),

    path('testimonies/', TestimoniesView.as_view(), name='testimonies'),
    path('testimonies/add/', AddTestimonyView.as_view(), name='add-testimonies'),

    path('prophetic-words/', PropheticWordsView.as_view(), name='prophetic_words'),
    path('prophetic-words/add/', AddPropheticWordsView.as_view(), name='add-prophetic_words'),
    path('prophetic-words/generated_news/', GeneratedNewsView.as_view(), name='generate_news'),

    path('blog/', BlogView.as_view(), name='blog'),
    path('blog/add/', AddBlogView.as_view(), name='add-blog'),

    path('sermons/', SermonsView.as_view(), name='sermons'),
    path('sermons/add/', AddSermonsView.as_view(), name='add-sermons'),

    path('fetch/<str:field>/<str:value>/', FetchView.as_view(), name='fetch'),

]
