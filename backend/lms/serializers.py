"""
DRF Serializers for LMS API
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Lesson, UserProgress, Exam


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class SignupSerializer(serializers.ModelSerializer):
    """Serializer for user signup"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    email = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        """Create user and auth token"""
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
                email=validated_data.get('email', '')
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        """Validate credentials"""
        from django.contrib.auth import authenticate

        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            data['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password')

        return data


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model"""
    class Meta:
        model = Lesson
        fields = ['id', 'lesson_id', 'title', 'subtitle', 'content', 'module_number', 'order_index', 'quiz_data', 'created_at']


class UserProgressSerializer(serializers.ModelSerializer):
    """Serializer for UserProgress model"""
    lesson_id = serializers.CharField(source='lesson.lesson_id', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = UserProgress
        fields = ['id', 'lesson_id', 'lesson_title', 'completed', 'completed_at']


class ExamSerializer(serializers.ModelSerializer):
    """Serializer for Exam model (list view - no instructions)"""
    class Meta:
        model = Exam
        fields = ['exam_id', 'title', 'time_limit_minutes']
