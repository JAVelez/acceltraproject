# Create your views here.

import base.models as base
import cgeassembly.models as cge
from rest_framework import viewsets, generics
from rest_framework import permissions
import apis.serializers as serializer
from django.db.models.query import QuerySet


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = base.Student.objects.all()
    serializer_class = serializer.UserSerializer
    # permission_classes = [permissions.IsAuthenticated]


# TODO add event date as a passable value
class AssemblyList(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = cge.Assembly.objects.all().order_by('-date')
    serializer_class = serializer.AssemblySerializer


class AssemblyDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = cge.Assembly.objects.all().order_by('-date')
    serializer_class = serializer.AssemblySerializer


class MotionList(viewsets.ModelViewSet):
    queryset = cge.Motion.objects.filter(amendment=None).order_by('-date')
    serializer_class = serializer.MotionSerializer

    def get_queryset(self):
        """
        """
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        if self.request.query_params.__contains__('assembly_id'):
            queryset = queryset.filter(assembly_id=self.request.query_params['assembly_id'])
        return queryset


class MotionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = cge.Motion.objects.all().order_by('-date')
    serializer_class = serializer.MotionSerializer


class MotionDetailVote(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = cge.Motion.objects.all().order_by('-date')
    serializer_class = serializer.MotionSerializer


class AmendmentList(viewsets.ModelViewSet):
    queryset = cge.Amendment.objects.all().order_by('-date')
    serializer_class = serializer.AmendmentSerializer

    def get_queryset(self):
        """
        """
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        if self.request.query_params.__contains__('motion_amended_id'):
            queryset = queryset.filter(motion_amended_id=self.request.query_params['motion_amended_id'])
        return queryset


class AmendmentDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = cge.Amendment.objects.all().order_by('-date')
    serializer_class = serializer.AmendmentSerializer

