# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import serializers


class UserAnswerSerializer(serializers.Serializer):
    exercise_id = serializers.IntegerField()
    user_answer = serializers.CharField(max_length=None)
