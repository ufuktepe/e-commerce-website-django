from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createlisting", views.create_listing, name="create_listing"),
    path("item/<int:listing_id>", views.display_listing, name="listing"),
    path("updateprice/<int:listing_id>", views.update_price, name="update_price"),
    path("editwatchlist/<int:listing_id>", views.edit_watchlist, name="edit_watchlist"),
    path("watchlist", views.display_watchlist, name="display_watchlist"),
    path("close/<int:listing_id>", views.close_listing, name="close_listing"),
    path("comment/<int:listing_id>", views.create_comment, name="create_comment"),
    path("categories", views.display_all_categories, name="display_all_categories"),
    path("category/<int:category_id>", views.display_single_category, name="display_single_category"),
]
