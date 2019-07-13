from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from . import models, serializers


class Notifications(APIView):

    def get(self, request, format=None):

        user = request.user

        notifications = models.Notification.objects.filter(to=user)

        serializer = serializers.NotificationSerilaizer(notifications, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

# 알림은 아무나 볼 수 있는게 아니기 때문에 function으로 만든다.
# 알림에는 4가지 parameter가 있다.
# 누가 누구에게 어떤(like, unlike 등등), image, comment의 파라미터.


def create_notification(creator, to, notification_type, image=None, comment=None):

    print(creator, to, notification_type, image, comment)

    notification = models.Notification.objects.create(
        creator=creator,
        to=to,
        notification_type=notification_type,
        image=image,
        comment=comment
    )
    notification.save()
