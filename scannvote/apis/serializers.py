import base.models as base
import cgeassembly.models as cge
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField()
    class Meta:
        model = User
        fields = ['username']


class AssemblySerializer(serializers.ModelSerializer):
    class Meta:
        model = cge.Assembly
        fields = ['pk', 'assembly_name', 'quorum', 'agenda', 'archived']


class AmendmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = cge.Amendment
        fields = ['pk', 'motion_text', 'archived', 'voteable', 'a_favor', 'en_contra', 'abstenido', 'assembly_id']


class MotionSerializer(serializers.ModelSerializer):
    original_motion = AmendmentSerializer(many=True)
    class Meta:
        model = cge.Motion
        fields = ['pk', 'motion_text', 'archived', 'voteable', 'a_favor', 'en_contra', 'abstenido', 'assembly_id', 'original_motion']


