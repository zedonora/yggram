from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import models, serializers
from yggram.users import models as user_models
from yggram.users import serializers as user_serializers
from notifications import views as notification_views

# Create your views here.


class Feed(APIView):

    # 유저를 팔로잉할때 해당 유저의 가장 최근 사진이 타임라인에 표시

    def get(self, request, format=None):
        # 처음 우리가 불러와야할 것은 우리 유저가 팔로잉하는 유저들 리스트.
        user = request.user

        # 팔로잉은 many - to - many 관계.
        following_users = user.following.all()

        # 이미지를 저장
        image_list = []

        for following_user in following_users:

            # [:2]로 리스트의 2번째 인자의 값까지만 받아옴.
            user_images = following_user.images.all()[:2]

            for image in user_images:

                image_list.append(image)

        # 나의 이미지 가져오기
        my_images = user.images.all()[:2]

        for image in my_images:

            image_list.append(image)

        # 가져온 값들을 원하는 형태로 sorting.(ex A의 1 - B의 1 - A의 2 - B의 2)
        sorted_list = sorted(image_list, key=lambda image: image.created_at, reverse=True)

        serializer = serializers.ImageSerializer(sorted_list, many=True)

        return Response(serializer.data)


class LikeImage(APIView):

    def get(self, request, image_id, format=None):
        # image__id => image 오브젝트 안에 있는 id
        # image에 있는 like 객체를 가져온다.
        likes = models.Like.objects.filter(image__id=image_id)

        # likes (likes 값) =>  [<Like: User:admin - Image Caption:Just Testing>, <>]
        # likes.values() (likes 안의 값) =>  [{'id': 8, 'created_at': datetime.datetime(2019, 7, 12, 23, 53, 6, 713417, tzinfo=<UTC>), 'updated_at': datetime.datetime(2019, 7, 12, 23, 53, 6, 713417, tzinfo=<UTC>)},{}]
        # likes 안의 특정 값 추출 ex) creator_id(image의 like를 누른 사람) => likes.values('creator_id')
        like_creators_ids = likes.values('creator_id')

        # array 안에 있는 유저 id를 검색
        users = user_models.User.objects.filter(id__in=like_creators_ids)

        serializer = user_serializers.ListUserSerializer(users, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, image_id, format=None):

        user = request.user

        try:
            found_image = models.Image.objects.get(id=image_id)
        except models.Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 이미지를 찾고, 이미지가 존재하면 이미 존재하는 좋아요를 찾는다.
        try:
            preexisiting_like = models.Like.objects.get(
                creator=user,
                image=found_image
            )
            return Response(status=status.HTTP_304_NOT_MODIFIED)

        # 이미 존재하는 좋아요가 없으면, 좋아요를 생성.
        except models.Like.DoesNotExist:

            new_like = models.Like.objects.create(
                creator=user,
                image=found_image
            )

            new_like.save()

            # create notification for user follow
            notification_views.create_notification(user, found_image.creator, 'like', found_image)

        return Response(status=status.HTTP_201_CREATED)


class UnLikeImage(APIView):

    def delete(self, request, image_id, format=None):

        user = request.user

        try:
            found_image = models.Image.objects.get(id=image_id)
        except models.Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 이미지를 찾고, 이미지가 존재하면 이미 존재하는 좋아요를 찾는다.
        try:
            preexisiting_like = models.Like.objects.get(
                creator=user,
                image=found_image
            )

            # 이미지가 존재하면 삭제한다.
            preexisiting_like.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        except models.Like.DoesNotExist:

            return Response(status=status.HTTP_201_CREATED)


class CommentOnImage(APIView):
    def post(self, request, image_id, format=None):

        # user는 요청한 유저ID를 가져가게 되어 있다.
        user = request.user

        try:
            # 해당 이미지는 이미지 ID와 같은 ID를 갖고 있다. 그 이미지 ID는 URL에서 왔다.
            found_image = models.Image.objects.get(id=image_id)

        except models.Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.CommentSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save(creator=user, image=found_image)

            # create notification for user follow
            notification_views.create_notification(
                user, found_image.creator, 'comment', found_image, serializer.data['message'])

            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Comment(APIView):

    def delete(self, request, image_id, format=None):

        user = request.user

        try:
            # 남의 댓글을 막 지울 수 없게 막는다.
            comment = models.Comment.objects.get(id=image_id, creator=user)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except models.Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class Search(APIView):

    def get(self, request, format=None):

        hashtags = request.query_params.get('hashtags', None)

        if hashtags is not None:
            hashtags = hashtags.split(",")

            # deep relationship을 검색하는 방법
            # title: 'hello',
            # location: 'bogota'
            # creator: (User:
            #     id:1,
            #     username:'nomadmin'
            # )

            # models.Image.objects.filter(location='bogota')
            # models.Image.objects.filter(creator__username='nomadmin')
            # models.Image.objects.filter(creator__username__exact='nomadmin')
            # models.Image.objects.filter(creator__username__contain='noma')
            # models.Image.objects.filter(creator__username__icontain='Noma')
            # [4,5,6]
            # filter(id__in=[4,5,6])
            images = models.Image.objects.filter(tags__name__in=hashtags).distinct()

            serializer = serializers.CountImageSerializer(images, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ModerateComments(APIView):

    def delete(self, request, image_id, comment_id, format=None):

        user = request.user

        try:
            # 삭제하고자 하는 댓글의 ID가 URL의 ID와 동일하고, image id체크, 그리고 유저에 의해 생성되었는지 찾으면 됨.
            # 예) 댓글 id 1번의 이미지 id를 체크하고, 생성자가 본인인지 확인.
            comment_to_delete = models.Comment.objects.get(id=comment_id, image__id=image_id, image__creator=user)
            comment_to_delete.delete()

        except models.Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ImageDetail(APIView):

    def find_own_image(self, image_id, user):
        try:
            image = models.Image.objects.get(id=image_id)
            return image
        except models.Image.DoesNotExist:
            return None

    def get(self, request, image_id, format=None):

        user = request.user

        image = self.find_own_image(image_id, user)

        if image is None:

            return Response(status=status.HTTP_401_UNAUTHORIZED)

        serializer = serializers.ImageSerializer(image)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, image_id, format=None):

        user = request.user

        image = self.find_own_image(image_id, user)

        if image is None:

            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # "file": ["파일이 제출되지 않았습니다."],"caption": ["이 필드는 필수 항목입니다."] 이와 같은 필수값 에러를 피하기 위한 방법 2
        # partial update를 사용하여 필수값 체크를 건너 뛴다.
        serializer = serializers.InputImageSerializer(image, data=request.data, partial=True)

        if serializer.is_valid():

            # Partial Updates (업데이트가 완성되지 않았을 때 시리얼라이저를 저장하는 방법)
            serializer.save(creator=user)

            return Response(data=serializer.data, status=status.HTTP_204_NO_CONTENT)

        else:

            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, image_id, format=None):

        user = request.user

        image = self.find_own_image(image_id, user)

        if image is None:

            return Response(status=status.HTTP_401_UNAUTHORIZED)

        image.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
