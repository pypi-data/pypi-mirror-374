"""
from django.urls import include, path
# from rest_framework.viewsets import GenericViewSet
from rest_framework_nested.routers import NestedDefaultRouter

from huscy.participations.views import ListParticipationsViewSet, ParticipationViewSet
from huscy.project_design.urls import experiment_router


# experiment_router.register('experiments', GenericViewSet,
#                            basename='experiment')


experiment_router.register('participations', ListParticipationsViewSet,
                           basename='experiment-participation')

participation_router = NestedDefaultRouter(experiment_router, 'participations',
                                           lookup='participation')
participation_router.register('participations', ParticipationViewSet,
                              basename='experiment-participation')

urlpatterns = [
    path('api/', include(experiment_router.urls + participation_router.urls)),
]
"""
urlpatterns = []
