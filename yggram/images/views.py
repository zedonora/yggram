from rest_framework.views import APIView
from rest_framework.response import Response
from . import models, serializers
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

        # 가져온 값들을 원하는 형태로 sorting.(ex A의 1 - B의 1 - A의 2 - B의 2)
        sorted_list = sorted(image_list, key=lambda image: image.created_at, reverse=True)

        serializer = serializers.ImageSerializer(sorted_list, many=True)

        return Response(serializer.data)
