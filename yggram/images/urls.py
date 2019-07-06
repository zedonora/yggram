from django.urls import path
from . import views

app_name = "images"
urlpatterns = [
    path("", view=views.Feed.as_view(), name="feed"),
    path("<int:id>/likes/", view=views.LikeImage.as_view(), name="like_image"),
    path("<int:id>/unlikes/", view=views.UnLikeImage.as_view(), name="unlike_image"),
    path("<int:id>/comments/", view=views.CommentOnImage.as_view(), name="comment_image"),
    path("comments/<int:id>/", view=views.Comment.as_view(), name="comment"),
    path("search/", view=views.Search.as_view(), name="search"),
]

# /images/3/like/

# create the url and the view
# 1 take the id from the url
# 2 we want to find and image with this id
# 3 we want to create a like for that image

# /search/?terms=hello,search,for,this
