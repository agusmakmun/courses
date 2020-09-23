# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from apps.courses.models.course import (Course, Exercise, Answer)


class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'deleted_at')
    list_filter = ('created_at', 'updated_at', 'deleted_at')
    prepopulated_fields = {'slug': ['title']}


class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('course', 'order', '__str__', 'created_at', 'updated_at', 'deleted_at')
    list_filter = ('created_at', 'updated_at', 'deleted_at')


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('exercise', '__str__', 'created_at', 'updated_at', 'deleted_at')
    list_filter = ('created_at', 'updated_at', 'deleted_at')


admin.site.register(Course, CourseAdmin)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(Answer, AnswerAdmin)
