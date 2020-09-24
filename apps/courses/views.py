# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.db.models import (Q, F, Count)
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import (get_object_or_404, redirect)
from django.views.generic import (ListView, DetailView)

from rest_framework import (status, permissions)
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models.course import (Course, Exercise, Answer)
from apps.courses.serializers import UserAnswerSerializer


class CourseListView(ListView):
    paginate_by = getattr(settings, 'DEFAULT_PAGINATION_NUMBER', 10)
    template_name = 'apps/courses/list.html'
    queryset = Course.objects.published()
    context_object_name = 'courses'


class CourseDetailView(DetailView):
    template_name = 'apps/courses/detail.html'
    context_object_name = 'course'
    model = Course

    def get_object(self):
        queries = {'slug': self.kwargs['slug'], 'deleted_at__isnull': True}
        return get_object_or_404(self.model, **queries)


class ExerciseDetailView(DetailView):
    template_name = 'apps/courses/exercise.html'
    context_object_name = 'exercise'
    model = Exercise

    def get_object(self):
        queries = {'course__slug': self.kwargs['slug'],
                   'id': self.kwargs['id'],
                   'deleted_at__isnull': True}
        return get_object_or_404(self.model, **queries)


class UserAnswerView(APIView):
    allowed_methods = ('post',)
    permission_classes = (permissions.AllowAny,)  # just for test
    serializer_class = UserAnswerSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = {
            'status': status.HTTP_200_OK,
            'result': serializer.data,
            'message': _('Success'),
            'success': True
        }
        return Response(response, status=response.get('status'))
