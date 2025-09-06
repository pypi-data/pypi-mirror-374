"""
from django.db import transaction

from huscy.bookings.services import book_timeslot
from huscy.pseudonyms.services import get_or_create_pseudonym
from huscy.participations.models import Participation  # Attendance,
from huscy.recruitment.models import ParticipationRequest
from huscy.recruitment.services import create_or_update_participation_request


@transaction.atomic
def create_participation(subject_group, subject, timeslots=[]):
   pseudonym = get_or_create_pseudonym(subject, 'participations.participation',
                                       object_id=subject_group.id).code
   if timeslots:
       participation = _create_pending_participation(pseudonym, subject_group, subject, timeslots)
   else:
       participation = _create_declined_participation(pseudonym, subject_group)

   attribute_filterset = subject_group.attribute_filtersets.latest('id')
   create_or_update_participation_request(subject, attribute_filterset,
                                          ParticipationRequest.STATUS.get_value('invited'))

   return participation


def _create_declined_participation(pseudonym, experiment):
    return Participation.objects.create(pseudonym=pseudonym, experiment=experiment)


def _create_pending_participation(pseudonym, experiment, subject, timeslots):
    participation = Participation.objects.create(pseudonym=pseudonym, experiment=experiment,
                                                 status=Participation.STATUS.pending)
    for timeslot in timeslots:
        booking = book_timeslot(timeslot, subject)
        Attendance.objects.create(participation=participation, booking=booking,
                                  start=timeslot.start, end=timeslot.end)
    return participation


def get_participations(experiment):
    participations = Participation.objects.filter(experiment=experiment)
    # if subject_group:
    #    participations = participations.filter(subject_group=subject_group)
    return participations
"""
