from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from yggram.users import models as user_models
# Create your models here.


@python_2_unicode_compatible
class TimeStampedModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class Image(TimeStampedModel):

    """ Image Model """

    file = models.ImageField()
    location = models.CharField(max_length=140)
    caption = models.TextField()
    # 유저가 생성한 모든 이미지들은 이제 필드 이름 images 안에 있다.
    creator = models.ForeignKey(user_models.User, on_delete=models.PROTECT, null=True, related_name='images')

    # property는 function이면서 데이터베이스랑 연동되는 값이 아니라 기본적으로 가지고 있는 값
    @property
    def like_count(self):
        return self.likes.all().count()

    @property
    def comment_count(self):
        return self.comments.all().count()

    def __str__(self):
        return '{} - {}'.format(self.location, self.caption)

    # 보통 메타클래스는 모델의 설정을 위해 사용
    class Meta:
        # DB에서 얻은 리스트를 생성된 날짜로 정렬(최근순으로)
        ordering = ['-created_at']


@python_2_unicode_compatible
class Comment(TimeStampedModel):

    """ Comment Model """

    message = models.TextField()
    creator = models.ForeignKey(user_models.User, on_delete=models.PROTECT, null=True)
    image = models.ForeignKey(Image, on_delete=models.PROTECT, null=True, related_name='comments')

    def __str__(self):
        return self.message


@python_2_unicode_compatible
class Like(TimeStampedModel):

    """ Like Model """

    creator = models.ForeignKey(user_models.User, on_delete=models.PROTECT, null=True)
    image = models.ForeignKey(Image, on_delete=models.PROTECT, null=True, related_name='likes')

    def __str__(self):
        return 'User:{} - Image Caption:{}'.format(self.creator.username, self.image.caption)
