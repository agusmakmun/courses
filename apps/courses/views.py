# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.db.models import (Q, F, Count)
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import (get_object_or_404, redirect)
from django.views.generic import (ListView, DetailView)

from rest_framework import (status, permissions)
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.courses.models.course import (Course, Exercise, ExpectedAnswer)
from apps.courses.serializers import UserExpectedAnswerSerializer
from apps.tools.python.cleaner import clean_code
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

    def get_resume_exercise_data(self):
        """ function to setup the resume for exercise """
        session = self.request.session
        resume_exercise_data = {'resume_exercise_id': None, 'resume_exercise_order': 1}

        if 'resume_exercise_id' in session:
            resume_exercise_data['resume_exercise_id'] = session.get('resume_exercise_id')

        if 'resume_exercise_order' in session:
            resume_exercise_data['resume_exercise_order'] = session.get('resume_exercise_order')

        # setup newest session
        if 'resume_exercise_id' not in session:
            exercise = self.object.get_exercises().first()
            if exercise is not None:
                session['resume_exercise_id'] = exercise.id
                session['resume_exercise_order'] = exercise.order

                resume_exercise_data['resume_exercise_id'] = session['resume_exercise_id']
                resume_exercise_data['resume_exercise_order'] = session['resume_exercise_order']

        return resume_exercise_data

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data.update(**self.get_resume_exercise_data())
        return context_data


class ExerciseDetailView(DetailView):
    template_name = 'apps/courses/exercise.html'
    context_object_name = 'exercise'
    model = Exercise

    def get_object(self):
        queries = {'course__slug': self.kwargs['slug'],
                   'id': self.kwargs['id'],
                   'deleted_at__isnull': True}
        exercise = get_object_or_404(self.model, **queries)

        # makesure the user following the rules (by session)
        # and not injecting into url only. for example:
        # /courses/learn-python/exercise/1/console/ (not finished yet)
        # /courses/learn-python/exercise/2/console/ (raise 404)
        resume_exercise_order = self.request.session.get('resume_exercise_order', 1)
        if resume_exercise_order >= exercise.order:
            return exercise
        raise Http404

    def get_initial_script(self):
        """ function to get the inital script """
        # issue: https://stackoverflow.com/q/64056744/6396981
        initial_script = self.object.initial_script.replace('`', '\`')
        return mark_safe(initial_script)

    def get_session_initial_script(self):
        # check the session answer for current exercise
        # when doesn't exist, setup into `initial_script`
        session_key = 'user_answer_script_exercise_%d' % self.object.id
        session_user_answer_script = self.request.session.get(session_key)
        if session_user_answer_script:
            # issue: https://stackoverflow.com/q/64056744/6396981
            user_answer_script = str(session_user_answer_script).replace('`', '\`')
            return mark_safe(user_answer_script)
        return self.get_initial_script()

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['session_initial_script'] = self.get_session_initial_script()
        context_data['initial_script'] = self.get_initial_script()
        return context_data


class UserExpectedAnswerView(APIView):
    allowed_methods = ('post',)
    permission_classes = (permissions.AllowAny,)  # just for test
    serializer_class = UserExpectedAnswerSerializer

    def validate_script(self, exercise_id, user_answer_script, response_sandbox):
        """
        function to makesure that `user_answer_script` is correct.
        :param `exercise_id` is integer id of exercise.
        :param `user_answer_script` is string user answer (script).
        :param `response_sandbox` is dict of response sandbox.
        :return bool <True/False>
        """
        exercise = Exercise.objects.get_or_none(id=exercise_id)
        if exercise and user_answer_script:
            if isinstance(user_answer_script, str):

                expected_answers = exercise.expectedanswer_set.published()
                user_answer_script_clean = clean_code(user_answer_script.replace('\r', ''))

                answer_is_valid = False
                output_is_valid = False

                # [1. script validation]
                if exercise.validate_script:
                    for answer in expected_answers:
                        expected_answer = answer.expected_script.replace('\r', '')
                        expected_answer_clean = clean_code(expected_answer)

                        if expected_answer_clean == user_answer_script_clean:
                            answer_is_valid = True
                            break  # stop the loop when correct
                else:
                    # this mean, if the `exercise.validate_script` not checked
                    # the validation of `valid_answer`, it assigned as valid.
                    answer_is_valid = True

                # [2. output validation]
                if exercise.validate_output:
                    user_answer_script_output = response_sandbox.get('result')
                    run_expected_script = exercise.run_expected_script

                    for answer in expected_answers:
                        expected_output = answer.expected_output
                        expected_script = answer.expected_script

                        # get output from expected_script
                        if run_expected_script:
                            result_sandbox_expected = sandbox(expected_script).get('result')
                            if user_answer_script_output == result_sandbox_expected:
                                output_is_valid = True
                                break  # stop the loop when correct
                        else:
                            if expected_output and (user_answer_script_output == expected_output):
                                output_is_valid = True
                                break  # stop the loop when correct

                else:
                    # this mean, if the `exercise.validate_output` not checked
                    # the validation of `valid_answer`, it assigned as valid.
                    output_is_valid = True

                # setup newest session when all is valids.
                if all([answer_is_valid, output_is_valid]):
                    # assign into newest session
                    # setup next exercise (to enable the button "Next")
                    next_exercise = exercise.get_next_exercise()
                    next_exercise_url = None
                    resume_exercise_id = exercise.id
                    resume_exercise_order = exercise.order

                    if next_exercise is not None:
                        resume_exercise_id = next_exercise.id
                        resume_exercise_order = next_exercise.order
                        args = [exercise.course.slug, next_exercise.id]
                        next_exercise_url = reverse('apps.courses:exercise_detail', args=args)

                    self.request.session['resume_exercise_id'] = resume_exercise_id
                    self.request.session['resume_exercise_order'] = resume_exercise_order
                    self.request.session['resume_next_exercise_url'] = next_exercise_url

                    return True

        return False

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        exercise_id = serializer.data.get('exercise_id')
        user_answer_script = serializer.data.get('user_answer_script')

        # assign the `user_answer_script` into new session.
        request.session['user_answer_script_exercise_%d' % exercise_id] = user_answer_script

        response_sandbox = sandbox(user_answer_script)  # {'success': <bool>, 'result': None}
        valid_answer = self.validate_script(exercise_id, user_answer_script, response_sandbox)
        is_correct = all([response_sandbox.get('success'), valid_answer])
        message = _('Success') if is_correct else _('Failed')

        result = {
            'console': response_sandbox.get('result'),
            'resume_next_exercise_url': request.session.get('resume_next_exercise_url')
        }

        response = {
            'status': status.HTTP_200_OK,
            'result': result,
            'message': message,
            'success': is_correct
        }
        return Response(response, status=response.get('status'))
