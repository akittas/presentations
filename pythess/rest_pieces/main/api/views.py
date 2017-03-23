from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin

from ..models import University, Student
from .permissions import IsAuthenticatedOrReadOnly
from .serializers import UniversitySerializer, StudentSerializer


class StudentViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class UniversityViewSet(NestedViewSetMixin, ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    # or we could re-implement all the methods below
    # def list(self, request, *args, **kwargs):
    #     pass
    #
    # def create(self, request, *args, **kwargs):
    #     pass
    #
    # def update(self, request, *args, **kwargs):
    #     pass
    #
    # def partial_update(self, request, *args, **kwargs):
    #     pass
    #
    # def destroy(self, request, *args, **kwargs):
    #     pass
