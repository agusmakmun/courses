# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

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
from apps.tools.python.exec import sandbox


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

    def get_resume_exercise_id(self):
        session = self.request.session
        if 'resume_exercise_id' in session:
            return session.get('resume_exercise_id')

        exercise = self.object.get_exercises().first()
        if exercise is not None:
            session['resume_exercise_id'] = exercise.id
            return session.get('resume_exercise_id')
        return None

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['resume_exercise_id'] = self.get_resume_exercise_id()
        return context_data


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

    def validate_answer(self, exercise_id, user_answer):
        """
        function to makesure that `user_answer` is correct.
        :param `exercise_id` is integer id of exercise.
        :param `user_answer` is string user answer.
        :return bool <True/False>
        """
        exercise = Exercise.objects.get_or_none(id=exercise_id)
        if exercise and user_answer:
            if isinstance(user_answer, str):
                correct_answers = exercise.answer_set.published()
                for canswer in correct_answers:
                    correct_answer = canswer.answer.replace('\r', '')
                    user_answer = user_answer.replace('\r', '')

                    if correct_answer == user_answer:
                        # assign into newest session
                        self.request.session['resume_exercise_id'] = exercise.id

                        return True
        return False

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        exercise_id = serializer.data.get('exercise_id')
        user_code = serializer.data.get('user_answer')

        response_sandbox = sandbox(user_code)  # {'success': <bool>, 'result': None}
        valid_answer = self.validate_answer(exercise_id, user_code)
        is_correct = all([response_sandbox.get('success'), valid_answer])
        message = _('Success') if is_correct else _('Failed')

        response = {
            'status': status.HTTP_200_OK,
            'result': response_sandbox.get('result'),
            'message': message,
            'success': is_correct
        }
        return Response(response, status=response.get('status'))
