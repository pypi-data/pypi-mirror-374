"""
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from huscy.participations.serializer import ParticipationSerializer
from huscy.participations.services import get_participations
from huscy.project_design.models import Experiment
from huscy.recruitment.models import SubjectGroup


class ListParticipationsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
   permission_classes = (IsAuthenticated, )
   serializer_class = ParticipationSerializer

   def initial(self, request, *args, **kwargs):
       super().initial(request, *args, **kwargs)
       self.experiment = get_object_or_404(Experiment, pk=self.kwargs['experiment_pk'])

   def get_queryset(self):
       return get_participations(self.experiment)


class ParticipationViewSet(mixins.CreateModelMixin, ListParticipationsViewSet):

   def initial(self, request, *args, **kwargs):
       super().initial(request, *args, **kwargs)
       self.experiment = get_object_or_404(Experiment, pk=self.kwargs['experiment_pk'])

   def get_queryset(self):
       return get_participations(self.experiment)

   def get_serializer_context(self):
       context = super().get_serializer_context()
       context['experiment'] = self.experiment
       return context
"""
