from django.conf import settings
from rest_framework import serializers
from analytics_data_api.constants import enrollment_modes
from analytics_data_api.v0 import models


class CourseActivityByWeekSerializer(serializers.ModelSerializer):
    """
    Representation of CourseActivityByWeek that excludes the id field.

    This table is managed by the data pipeline, and records can be removed and added at any time. The id for a
    particular record is likely to change unexpectedly so we avoid exposing it.
    """

    activity_type = serializers.SerializerMethodField('get_activity_type')

    def get_activity_type(self, obj):
        """
        Lower-case activity type and change active to any.
        """

        activity_type = obj.activity_type.lower()
        if activity_type == 'active':
            activity_type = 'any'

        return activity_type

    class Meta(object):
        model = models.CourseActivityWeekly
        fields = ('interval_start', 'interval_end', 'activity_type', 'count', 'course_id')


class ProblemResponseAnswerDistributionSerializer(serializers.ModelSerializer):
    """
    Representation of the Answer Distribution table, without id.

    This table is managed by the data pipeline, and records can be removed and added at any time. The id for a
    particular record is likely to change unexpectedly so we avoid exposing it.
    """

    class Meta(object):
        model = models.ProblemResponseAnswerDistribution
        fields = (
            'course_id',
            'module_id',
            'part_id',
            'correct',
            'count',
            'value_id',
            'answer_value_text',
            'answer_value_numeric',
            'variant',
            'created'
        )


class GradeDistributionSerializer(serializers.ModelSerializer):
    """
    Representation of the grade_distribution table without id
    """

    class Meta(object):
        model = models.GradeDistribution
        fields = (
            'module_id',
            'course_id',
            'grade',
            'max_grade',
            'count',
            'created'
        )


class SequentialOpenDistributionSerializer(serializers.ModelSerializer):
    """
    Representation of the sequential_open_distribution table without id
    """

    class Meta(object):
        model = models.SequentialOpenDistribution
        fields = (
            'module_id',
            'course_id',
            'count',
            'created'
        )


class BaseCourseEnrollmentModelSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format=settings.DATE_FORMAT)
    created = serializers.DateTimeField(format=settings.DATETIME_FORMAT)


class CourseEnrollmentDailySerializer(BaseCourseEnrollmentModelSerializer):
    """ Representation of course enrollment for a single day and course. """

    class Meta(object):
        model = models.CourseEnrollmentDaily
        fields = ('course_id', 'date', 'count', 'created')


class CourseEnrollmentModeDailySerializer(BaseCourseEnrollmentModelSerializer):
    """ Representation of course enrollment, broken down by mode, for a single day and course. """

    def get_default_fields(self):
        # pylint: disable=super-on-old-class
        fields = super(CourseEnrollmentModeDailySerializer, self).get_default_fields()

        # Create a field for each enrollment mode
        for mode in enrollment_modes.ALL:
            fields[mode] = serializers.IntegerField(required=True)

        return fields

    class Meta(object):
        model = models.CourseEnrollmentDaily

        # Declare the dynamically-created fields here as well so that they will be picked up by Swagger.
        fields = ['course_id', 'date', 'count', 'created'] + enrollment_modes.ALL


class CountrySerializer(serializers.Serializer):
    """
    Serialize country to an object with fields for the complete country name
    and the ISO-3166 two- and three-digit codes.

    Some downstream consumers need two-digit codes, others need three. Both are provided to avoid the need
    for conversion.
    """
    alpha2 = serializers.CharField()
    alpha3 = serializers.CharField()
    name = serializers.CharField()


class CourseEnrollmentByCountrySerializer(BaseCourseEnrollmentModelSerializer):
    # pylint: disable=unexpected-keyword-arg, no-value-for-parameter
    country = CountrySerializer(many=False)

    class Meta(object):
        model = models.CourseEnrollmentByCountry
        fields = ('date', 'course_id', 'country', 'count', 'created')


class CourseEnrollmentByGenderSerializer(BaseCourseEnrollmentModelSerializer):
    female = serializers.IntegerField(required=False)
    male = serializers.IntegerField(required=False)
    other = serializers.IntegerField(required=False)
    unknown = serializers.IntegerField(required=False)

    class Meta(object):
        model = models.CourseEnrollmentByGender
        fields = ('course_id', 'date', 'female', 'male', 'other', 'unknown', 'created')


class CourseEnrollmentByEducationSerializer(BaseCourseEnrollmentModelSerializer):
    class Meta(object):
        model = models.CourseEnrollmentByEducation
        fields = ('course_id', 'date', 'education_level', 'count', 'created')


class CourseEnrollmentByBirthYearSerializer(BaseCourseEnrollmentModelSerializer):
    class Meta(object):
        model = models.CourseEnrollmentByBirthYear
        fields = ('course_id', 'date', 'birth_year', 'count', 'created')


class CourseActivityWeeklySerializer(serializers.ModelSerializer):
    interval_start = serializers.DateTimeField(format=settings.DATETIME_FORMAT)
    interval_end = serializers.DateTimeField(format=settings.DATETIME_FORMAT)
    any = serializers.IntegerField(required=False)
    attempted_problem = serializers.IntegerField(required=False)
    played_video = serializers.IntegerField(required=False)
    # posted_forum = serializers.IntegerField(required=False)
    created = serializers.DateTimeField(format=settings.DATETIME_FORMAT)

    class Meta(object):
        model = models.CourseActivityWeekly
        # TODO: Add 'posted_forum' here to restore forum data
        fields = ('interval_start', 'interval_end', 'course_id', 'any', 'attempted_problem', 'played_video', 'created')
