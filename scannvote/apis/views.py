# Create your views here.

import base.models as base
import cgeassembly.models as cge
import cgeassembly.views as cgeviews
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets, generics, status
from rest_framework import permissions
import apis.serializers as serializer
from django.db.models.query import QuerySet
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.http import QueryDict
from .serializers import AssemblySerializer

from django.contrib.auth.models import User

import base.forms as baseforms


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = serializer.UserSerializer
    # permission_classes = [permissions.IsAuthenticated]


# TODO add event date as a passable value
class AssemblyList(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = cge.Assembly.objects.all().order_by('-date')
    serializer_class = serializer.AssemblySerializer

# @api_view(['GET'])
# @permission_classes((permissions.AllowAny,))
# def AssemblyList(request):
#     if request.method == 'GET':
#         assemblies = cge.Assembly.objects.all().order_by('-date')
#         serializer = AssemblySerializer(assemblies, many=True)
#         return Response(serializer.data)


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


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def MotionDetailVote(request, pk):
    """
    API endpoint that allows users to be viewed or edited.
    """
    if request.user.id is None:
        return Response(data={'error_message': "User is not logged in", 'code': '5'}, status=status.HTTP_403_FORBIDDEN)

    motion = get_object_or_404(cge.Motion, pk=pk)
    student = base.Student.get_student_by_user(request.user)

    # case where a staff member has not open the motion to votes or is a past motion already voted on (archived)
    if motion.archived or not motion.voteable:
        return Response(data={'error_message': "Voting is not open at the moment", 'code': '0'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # case where a student is not attending the assembly but the motion is voteable and not archived
    if not student.attending:
        return Response(data={'error_message': "You are not attending the assembly", 'code': '1'}, status=status.HTTP_403_FORBIDDEN)

    try:
        if request.data.__contains__('choice'):
            selected_choice = request.data['choice']
        else:
            selected_choice = request.POST['choice']
    except:
        return Response(data={'error_message': "You didn't select a choice.", 'code': '2'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        # case where the student successfully votes on the motion
        if cge.create_vote(motion=motion, student=student):
            if selected_choice == '0':
                motion.a_favor += 1
            elif selected_choice == '1':
                motion.en_contra += 1
            else:
                motion.abstenido += 1
            motion.save()
        else:
            # case where create_vote returns None and the vote is not processed
            # because the student has already cast their vote
            return Response(data={'error_message': "You have already cast your vote.", 'code': '3'}, status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_200_OK)


class AmendmentList(viewsets.ModelViewSet):
    queryset = cge.Amendment.objects.all().order_by('-date')
    serializer_class = serializer.AmendmentSerializer

    # TODO llamar super() y aplicar filtro al final
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


def AmendmentDetailVote(request, pk):
    return MotionDetailVote(request, pk)


# TODO return if student id is already registered and if username is already taken
@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def signup(request):
    """
    :param request: http request with form attached to it
    :return: if successful, home page showing student details; if not, signup page to try again
    """
    if request.method == 'POST':
        form = baseforms.SignUpForm(request.data)
        if form.is_valid():
            student_id = form.clean_student_id()
            user = form.save()

            # load the profile instance created by the signal
            user.refresh_from_db()

            # assign student id to user's student one to one relation and save to db
            user.student.student_id = student_id
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return Response(data={'user': user.username}, status=status.HTTP_200_OK)
        else:
            return Response(data={'error_msg': 'error with a parameter'}, status=status.HTTP_409_CONFLICT)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def login_student(request):
    """
    :param request: http request with login form
    :return: if successful, home page showing student details; if not, login page to try again
    """
    if request.method == 'POST':
        if request.data.__contains__('username') and request.data.__contains__('password'):
            user = authenticate(username=request.data['username'], password=request.data['password'])
        else:
            return Response(data={'error_msg': 'Missing information.'}, status=status.HTTP_204_NO_CONTENT)
        if user:
            login(request, user)
            return Response(data={'user': user.username}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def logout_student(request):
    """
    method to remove student from active session
    :param request: http request
    :return: home page with no user session active which in turn returns to the login page
    """
    logout(request)
    return Response(status=status.HTTP_200_OK)