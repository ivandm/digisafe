from rest_framework import serializers
from users.models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'email']
        # fields = ['username', 'last_name', 'first_name', 'email']