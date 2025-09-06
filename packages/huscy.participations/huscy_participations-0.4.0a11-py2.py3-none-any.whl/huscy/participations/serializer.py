# from django.shortcuts import get_object_or_404
from rest_framework import serializers

# from huscy.bookings.models import Timeslot
from huscy.participations.models import Attendance, Participation
# from huscy.participations.services import create_participation
from huscy.pseudonyms.services import get_subject
# from huscy.subjects.models import Subject


class AttendanceSerializer(serializers.ModelSerializer):
    # planned_end = serializers.DateTimeField(source='booking.timeslot.end', read_only=True)
    planned_start = serializers.DateTimeField(source='booking.timeslot.start', read_only=True)
    session = serializers.IntegerField(source='booking.timeslot.session.id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Attendance
        fields = (
            'end',
            # 'planned_end',
            'planned_start',
            'session',
            'start',
            'status',
            'status_display',
        )


class ParticipationSerializer(serializers.ModelSerializer):
    attendances = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    subject = serializers.CharField(write_only=True)
    experiment_title = serializers.CharField(source='experiment.title', read_only=True)
    timeslots = serializers.ListField(required=False)

    class Meta:
        model = Participation
        fields = (
            'attendances',
            'status',
            'status_display',
            'subject',
            'experiment',
            'experiment_title',
            'timeslots',
        )
        read_only_fields = 'experiment',
        write_only_fields = 'timeslots',

    def get_attendances(self, participation):
        attendances = participation.attendance_set.all()
        return AttendanceSerializer(attendances, many=True).data

    def to_representation(self, participation):
        representation = super().to_representation(participation)
        subject = get_subject(participation.pseudonym)
        representation['subject'] = subject.id
        representation['subject_display_name'] = subject.contact.display_name
        return representation


"""
    def create(self, validated_data):
        subject = get_object_or_404(Subject, pk=validated_data.pop('subject'))
        experiment = self.context.get('experiment')
        timeslots = []
        if 'timeslots' in validated_data:
            timeslots = Timeslot.objects.filter(id__in=validated_data.pop('timeslots'),
                                               session__experiment=subject_group.experiment)
        return create_participation(experiment=experiment, subject=subject,
                                    timeslots=timeslots, **validated_data)
"""
