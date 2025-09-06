from django.db import models
from django.utils.translation import gettext_lazy as _

from huscy.bookings.models import Booking
from huscy.project_design.models import Experiment


class Participation(models.Model):
    class STATUS(models.IntegerChoices):
        declined = 0, _('Declined')
        pending = 1, _('Pending')
        canceled = 2, _('Canceled')
        finished = 3, _('Finished')

    pseudonym = models.CharField(_('Pseudonym'), max_length=64)
    experiment = models.ForeignKey(Experiment, on_delete=models.PROTECT,
                                   verbose_name=_('Experiment'))
    status = models.IntegerField(choices=STATUS.choices, default=0)

    class Meta:
        ordering = 'experiment', 'status'
        verbose_name = _('Participation')
        verbose_name_plural = _('Participations')


class Attendance(models.Model):
    class STATUS(models.IntegerChoices):
        scheduled = 0, _('Scheduled')
        canceled = 1, _('Canceled')
        finished = 2, _('Finished')

    participation = models.ForeignKey(Participation, on_delete=models.PROTECT,
                                      verbose_name=_('Participation'))
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, verbose_name=_('Booking'))

    start = models.DateTimeField(_('Start'))
    end = models.DateTimeField(_('End'))

    status = models.IntegerField(choices=STATUS.choices, default=0)

    class Meta:
        ordering = 'participation', 'status'
        verbose_name = _('Attendance')
        verbose_name_plural = _('Attendances')
