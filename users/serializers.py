import datetime

from rest_framework import serializers

from .models import (CustomUser, Shepherd, SubShepherd, Catalog, Permission,
                     WeekOne, WeekTwo, WeekThree, WeekFour,
                     FamilyMemberWeeklySchedule)


class UserSerializer(serializers.ModelSerializer):
    callings = serializers.CharField(read_only=True)
    shepherd = serializers.HyperlinkedRelatedField('shepherd-detail', read_only=True)
    sub_shepherd = serializers.HyperlinkedRelatedField('subshepherd-detail', read_only=True)
    age = serializers.SerializerMethodField(method_name='get_user_age')

    class Meta:
        model = CustomUser
        fields = [
            'url', 'first_name', 'last_name', 'username', 'gender', 'date_of_birth', 'age',
            'about', 'phone_number', 'occupation', 'address', 'skills', 'blood_group',
            'genotype', 'chronic_illness', 'lga', 'state', 'country', 'course_of_study',
            'years_of_study', 'current_year_of_study', 'final_year_status',
            'next_of_kin_full_name', 'next_of_kin_relationship',
            'next_of_kin_phone_number', 'next_of_kin_address', 'gift_graces', 'callings',
            'reveal_calling_by_shepherd', 'unit_of_work', 'shepherd', 'sub_shepherd',
            'shoe_size', 'cloth_size',
        ]

    def get_user_age(self, user: CustomUser):
        if user.date_of_birth:
            now = datetime.datetime.now()
            current_age = now.year - user.date_of_birth.year
            return current_age
        return None


class ShepherdSerializer(serializers.ModelSerializer):
    service_duration = serializers.SerializerMethodField(method_name='get_service_duration')
    name_url = serializers.HyperlinkedIdentityField(view_name='shepherd-user', source='name')

    class Meta:
        model = Shepherd
        fields = ['url', 'name', 'name_url', 'no_of_sheep', 'date_of_appointment',
                  'calling', 'service_duration']

    def get_service_duration(self, shepherd: Shepherd):
        return shepherd.get_service_duration()


class SubShepherdSerializer(serializers.ModelSerializer):
    service_duration = serializers.SerializerMethodField(method_name='get_service_duration')
    name_url = serializers.HyperlinkedIdentityField(view_name='subshepherd-user', source='name')

    class Meta:
        model = SubShepherd
        fields = ['url', 'name', 'name_url', 'no_of_sheep', 'date_of_appointment', 'calling', 'service_duration']

    def get_service_duration(self, sub_shepherd: SubShepherd):
        return sub_shepherd.get_service_duration()


class PermissionSerializer(serializers.ModelSerializer):
    name_url = serializers.HyperlinkedIdentityField(view_name='permission-user', source='name')

    class Meta:
        model = Permission
        fields = ['url', 'name', 'name_url', 'is_shepherd', 'is_subshepherd', 'can_edit_catalog',
                  'head_of_department']


class CatalogSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Catalog
        fields = "__all__"


class WeekOneSerializer(serializers.ModelSerializer):
    family_schedule = serializers.HyperlinkedRelatedField('familymemberweeklyschedule-detail', read_only=True)


    class Meta:
        model = WeekOne
        fields = ['url', 'In', 'out', 'wednesday', 'exception', 'family_schedule']


class WeekTwoSerializer(serializers.ModelSerializer):
    family_schedule = serializers.HyperlinkedRelatedField('familymemberweeklyschedule-detail', read_only=True)

    class Meta:
        model = WeekTwo
        fields = ['url', 'In', 'out', 'wednesday', 'exception', 'family_schedule']


class WeekThreeSerializer(serializers.ModelSerializer):
    family_schedule = serializers.HyperlinkedRelatedField('familymemberweeklyschedule-detail', read_only=True)

    class Meta:
        model = WeekThree
        fields = ['url', 'In', 'out', 'wednesday', 'exception', 'family_schedule']


class WeekFourSerializer(serializers.ModelSerializer):
    family_schedule = serializers.HyperlinkedRelatedField('familymemberweeklyschedule-detail', read_only=True)

    class Meta:
        model = WeekFour
        fields = ['url', 'In', 'out', 'wednesday', 'exception', 'family_schedule']


class FamilyMemberWeeklyScheduleSerializer(serializers.ModelSerializer):
    username = serializers.HyperlinkedIdentityField('familymemberweeklyschedule-user', read_only=True)
    week_one = serializers.HyperlinkedIdentityField('familymemberweeklyschedule-week-one', read_only=True)
    week_two = serializers.HyperlinkedIdentityField('familymemberweeklyschedule-week-two', read_only=True)
    week_three = serializers.HyperlinkedIdentityField('familymemberweeklyschedule-week-three', read_only=True)
    week_four = serializers.HyperlinkedIdentityField('familymemberweeklyschedule-week-four', read_only=True)

    class Meta:
        model = FamilyMemberWeeklySchedule
        fields = ['url', 'username', 'week_one', 'week_two', 'week_three', 'week_four']

    def get_week_one(self, obj: FamilyMemberWeeklySchedule):
        week_one = obj.weekone
        serialized_item = WeekOneSerializer(week_one, context=self.context)

        return serialized_item.data

    def get_week_two(self, obj: FamilyMemberWeeklySchedule):
        week_two = obj.weektwo
        serialized_item = WeekTwoSerializer(week_two, context=self.context)

        return serialized_item.data

    def get_week_three(self, obj: FamilyMemberWeeklySchedule):
        week_three = obj.weekthree
        serialized_item = WeekThreeSerializer(week_three, context=self.context)

        return serialized_item.data

    def get_week_four(self, obj: FamilyMemberWeeklySchedule):
        week_four = obj.weekfour
        serialized_item = WeekFourSerializer(week_four, context=self.context)

        return serialized_item.data



