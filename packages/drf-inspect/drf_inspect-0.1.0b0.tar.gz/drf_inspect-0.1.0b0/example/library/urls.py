from library import api
from rest_framework import routers


router = routers.DefaultRouter()
router.register('authors', api.AuthorModelViewSet)
router.register('books', api.BookModelViewSet)

urlpatterns = router.urls
