from rest_framework import serializers
from . import models
from yggram.users import models as user_models


class SmallImageSerializer(serializers.ModelSerializer):

    """ Used fro the notifications """

    class Meta:
        model = models.Image
        fields = (
            'file',
        )


class CountImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = (
            'file',
            'like_count',
            'comment_count'
        )


class FeedUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = user_models.User
        fields = (
            'username',
            'profile_image'
        )


class CommentSerializer(serializers.ModelSerializer):

    creator = FeedUserSerializer(read_only=True)

    class Meta:
        model = models.Comment
        fields = (
            'id',
            'message',
            'creator'
        )


class LikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Like
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):

    comments = CommentSerializer(many=True)
    creator = FeedUserSerializer()

    class Meta:
        model = models.Image
        fields = ("id",
                  "file",
                  "location",
                  "caption",
                  "comments",
                  "like_count",
                  'creator',
                  'created_at')


class InputImageSerializer(serializers.ModelSerializer):

    class Meta:

        # "file": ["파일이 제출되지 않았습니다."],"caption": ["이 필드는 필수 항목입니다."] 이와 같은 필수값 에러를 피하기 위한 방법 1
        # file = serializers.FileField(required=False) => 이방법은 serializer를 변경하는 방법임.
        model = models.Image
        fields = (
            'file',
            'location',
            'caption',
        )
