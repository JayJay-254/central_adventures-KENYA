from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('trips/', views.trips, name='trips'),
    path('trip/<int:id>/', views.trip_details, name='trip_details'),
    path('book/<int:id>/', views.book_trip, name='book'),
    path('group-chat/', views.chat_room, name='group_chat'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('management/', views.management_page, name='management'),
    # Static/frontend templates routes
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_page, name='signup'),
    path('gallery/', views.gallery_page, name='gallery'),
    path('edit-profile/', views.edit_profile_page, name='edit_profile'),
    path('destinations/', views.destinations_page, name='destinations_page'),
    path('notification-demo/', views.notification_demo, name='notification_demo'),
    # Location API endpoints
    path('api/counties/', views.api_counties, name='api_counties'),
    path('api/constituencies/', views.api_constituencies, name='api_constituencies'),
    # Gallery interactions
    path('api/gallery/<int:image_id>/like/', views.toggle_like, name='toggle_like'),
    path('api/gallery/<int:image_id>/comment/', views.add_comment, name='add_comment'),
    path('api/gallery/<int:image_id>/comments/', views.get_comments, name='get_comments'),
    path('api/gallery/<int:image_id>/download/', views.download_media, name='download_media'),
]