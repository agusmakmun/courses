# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import path

from apps.courses.views import (
    CourseListView, CourseDetailView,
    ExerciseDetailView
)

app_name = 'apps.courses'

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('courses/<slug:slug>/', CourseDetailView.as_view(), name='course_detail'),
    path('courses/<slug:slug>/exercise/<int:id>/console/', ExerciseDetailView.as_view(), name='exercise_detail'),
]
