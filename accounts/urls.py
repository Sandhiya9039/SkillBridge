from django.urls import path
from . import views

urlpatterns = [

    # ---------------- HOME ----------------
    path("", views.home, name="home"),

    # ---------------- AUTHENTICATION ----------------
    path("register/", views.register, name="register"),
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),

    # ---------------- DASHBOARD ----------------
    path("dashboard/", views.dashboard, name="dashboard"),

    # ---------------- PROFILE ----------------
    path("profile/", views.create_profile, name="create_profile"),

    # ---------------- FIND MATCHES ----------------
    path("matches/", views.find_matches, name="matches"),

    # ---------------- SEARCH USERS ----------------
    path("search/", views.search_users, name="search_users"),

    # ---------------- SKILL EXCHANGE REQUESTS ----------------
    path(
        "send-request/<int:profile_id>/",
        views.send_request,
        name="send_request"
    ),

    path(
        "received-requests/",
        views.received_requests,
        name="received_requests"
    ),

    path(
        "accept-request/<int:request_id>/",
        views.accept_request,
        name="accept_request"
    ),

    path(
        "reject-request/<int:request_id>/",
        views.reject_request,
        name="reject_request"
    ),

    # ---------------- CHAT ----------------
    path(
        "chat/<int:profile_id>/",
        views.chat,
        name="chat"
    ),
    path(
    "profile/<int:profile_id>/",
    views.user_profile,
    name="user_profile"
),

    # ---------------- REVIEWS ----------------
    path(
        "review/<int:profile_id>/",
        views.leave_review,
        name="leave_review"
    ),

    path(
        "reviews/<int:profile_id>/",
        views.view_reviews,
        name="view_reviews"
    ),
]