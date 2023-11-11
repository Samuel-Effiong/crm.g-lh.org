import datetime

from rest_framework import serializers

from .models import (Testimony, PropheticWord, Sermon, Blog)


class TestimonySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Testimony
        fields = "__all__"


class PropheticWordSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = PropheticWord
        fields = "__all__"


class SermonSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Sermon
        fields = "__all__"


class BlogSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Blog
        fields = "__all__"
