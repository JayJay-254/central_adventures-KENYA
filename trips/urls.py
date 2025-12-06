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
    # path('api/gallery/<int:image_id>/comment/', views.edit_comment, name='edit_comment'),
    path('api/gallery/<int:image_id>/add-comment/', views.add_comment, name='add-comment'),
    path('api/gallery/<int:image_id>/comments/', views.get_comments, name='get_comments'),
    path('api/gallery/<int:image_id>/download/', views.download_media, name='download_media'),
    
    path('gallery/<int:image_id>/comments/', views.get_comments, name='get_comments'), 
    path('gallery/<int:image_id>/comment/', views.add_comment, name='add_comment'),
    # Comment management
    path('api/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('api/comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('api/comment/<int:comment_id>/reply/', views.reply_comment, name='reply_comment'),
    path('api/comment/<int:comment_id>/like/', views.toggle_comment_like, name='toggle_comment_like'),
]