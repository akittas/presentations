from rest_framework_extensions.routers import ExtendedDefaultRouter

from main.api import views

router = ExtendedDefaultRouter()
router.register(r'students', views.StudentViewSet)

nested_route = router.register(r'universities', views.UniversityViewSet, base_name='universities')
nested_route.register(r'students', views.StudentViewSet,
                      base_name='university-students', parents_query_lookups=['university'])
