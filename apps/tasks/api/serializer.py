from rest_framework import serializers
from apps.tasks.models import Task, Status
from apps.accounts.api.serializer import UserSerializer
from django.contrib.auth.models import User
from datetime import date

class TaskSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset = User.objects.all(), required=False, allow_null=True
    )
    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.assigned_to:
            data["assigned_to"] = UserSerializer(instance.assigned_to).data
        return data

    def validate(self, data):
        if self.context.get("update_type") == "details":
            if "status" in data:
                raise serializers.ValidationError("Status can only be changed by task doer. So update others but not status")
        if data.get("due_date"):
            if data.get("due_date") < date.today():
                raise serializers.ValidationError("Due date cannot be before today.") 
        return data

class TaskApiSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Status.choices)

class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ["id", "created_by", "status", "created_at", "updated_at"]

class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ["id", "created_by", "status", "created_at", "updated_at"]

class TaskResponseSeerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = "__all__"

class TaskEmptyResponseSerializer(serializers.Serializer):
    message = serializers.CharField()