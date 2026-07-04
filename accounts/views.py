from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import (
    Profile,
    ExchangeRequest,
    Message,
    Review,
)

from .forms import (
    ProfileForm,
    ReviewForm,
)

# ---------------- HOME ----------------
def home(request):
    return render(request, "home.html")


# ---------------- REGISTER ----------------
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Registration successful! Please login.")
        return redirect("login")

    return render(request, "register.html")


# ---------------- LOGIN ----------------
def login_user(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


# ---------------- DASHBOARD ----------------
@login_required
def dashboard(request):

    profile = Profile.objects.get(user=request.user)

    unread_count = Message.objects.filter(
        receiver=profile,
        is_read=False
    ).count()

    return render(request, "dashboard.html", {
        "profile": profile,
        "unread_count": unread_count,
    })

# ---------------- LOGOUT ----------------
@login_required
def logout_user(request):
    logout(request)
    return redirect("home")


# ---------------- PROFILE ----------------
@login_required
def create_profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            return redirect("dashboard")

    else:

        form = ProfileForm(instance=profile)

    return render(request, "create_profile.html", {
        "form": form
    })


# ---------------- MATCHES ----------------
@login_required
def find_matches(request):

    my_profile = Profile.objects.get(user=request.user)

    wanted = [
        x.strip().lower()
        for x in my_profile.skills_wanted.split(",")
        if x.strip()
    ]

    matches = []

    for person in Profile.objects.exclude(user=request.user):

        offered = [
            x.strip().lower()
            for x in person.skills_offered.split(",")
            if x.strip()
        ]

        if any(skill in offered for skill in wanted):
            matches.append(person)

    return render(request, "matches.html", {
        "matches": matches
    })


# ---------------- SEARCH ----------------
@login_required
def search_users(request):

    query = request.GET.get("q", "")

    users = Profile.objects.none()

    if query:
        users = Profile.objects.filter(
            skills_offered__icontains=query
        ).exclude(user=request.user)

    return render(request, "search_users.html", {
        "query": query,
        "users": users
    })


# ---------------- SEND REQUEST ----------------
@login_required
def send_request(request, profile_id):

    sender = Profile.objects.get(user=request.user)

    receiver = get_object_or_404(
        Profile,
        id=profile_id
    )

    if sender == receiver:
        return redirect("matches")

    exists = ExchangeRequest.objects.filter(
        sender=sender,
        receiver=receiver
    ).exists()

    if not exists:

        ExchangeRequest.objects.create(
            sender=sender,
            receiver=receiver
        )

    return redirect("matches")


# ---------------- RECEIVED REQUESTS ----------------
@login_required
def received_requests(request):

    profile = Profile.objects.get(user=request.user)

    requests = ExchangeRequest.objects.filter(
        receiver=profile
    )

    return render(request, "received_requests.html", {
        "requests": requests
    })


# ---------------- ACCEPT REQUEST ----------------
@login_required
def accept_request(request, request_id):

    req = get_object_or_404(
        ExchangeRequest,
        id=request_id
    )

    req.status = "Accepted"
    req.save()

    return redirect("received_requests")


# ---------------- REJECT REQUEST ----------------
@login_required
def reject_request(request, request_id):

    req = get_object_or_404(
        ExchangeRequest,
        id=request_id
    )

    req.status = "Rejected"
    req.save()

    return redirect("received_requests")


# ---------------- CHAT ----------------
@login_required
def chat(request, profile_id):

    sender = Profile.objects.get(user=request.user)

    receiver = get_object_or_404(
        Profile,
        id=profile_id
    )

    accepted = ExchangeRequest.objects.filter(
        sender=sender,
        receiver=receiver,
        status="Accepted"
    ).exists() or ExchangeRequest.objects.filter(
        sender=receiver,
        receiver=sender,
        status="Accepted"
    ).exists()

    if not accepted:
        messages.error(request, "Skill request not accepted.")
        return redirect("matches")

    if request.method == "POST":

        text = request.POST.get("message")

        if text:

            Message.objects.create(
                sender=sender,
                receiver=receiver,
                message=text
            )

            return redirect("chat", profile_id=profile_id)

    # Mark received messages as read
    Message.objects.filter(
        sender=receiver,
        receiver=sender,
        is_read=False
    ).update(is_read=True)

    chats = Message.objects.filter(
        sender=sender,
        receiver=receiver
    ) | Message.objects.filter(
        sender=receiver,
        receiver=sender
    )

    chats = chats.order_by("timestamp")

    unread_count = Message.objects.filter(
        receiver=sender,
        is_read=False
    ).count()

    return render(request, "chat.html", {
        "receiver": receiver,
        "messages": chats,
        "unread_count": unread_count
    })
@login_required
def leave_review(request, profile_id):

    reviewer = Profile.objects.get(user=request.user)

    reviewed_user = get_object_or_404(
        Profile,
        id=profile_id
    )

    # Cannot review yourself
    if reviewer == reviewed_user:

        messages.error(
            request,
            "You cannot review yourself."
        )

        return redirect("dashboard")

    # Must have accepted request
    accepted = ExchangeRequest.objects.filter(
        sender=reviewer,
        receiver=reviewed_user,
        status="Accepted"
    ).exists() or ExchangeRequest.objects.filter(
        sender=reviewed_user,
        receiver=reviewer,
        status="Accepted"
    ).exists()

    if not accepted:

        messages.error(
            request,
            "You can only review after an accepted skill exchange."
        )

        return redirect("dashboard")

    # Already reviewed?
    if Review.objects.filter(
        reviewer=reviewer,
        reviewed_user=reviewed_user
    ).exists():

        messages.warning(
            request,
            "You already reviewed this user."
        )

        return redirect("chat", profile_id=profile_id)

    if request.method == "POST":

        form = ReviewForm(request.POST)

        if form.is_valid():

            review = form.save(commit=False)

            review.reviewer = reviewer

            review.reviewed_user = reviewed_user

            review.save()

            messages.success(
                request,
                "Review submitted successfully."
            )

            return redirect(
                "chat",
                profile_id=profile_id
            )

    else:

        form = ReviewForm()

    return render(
        request,
        "leave_review.html",
        {
            "form": form,
            "receiver": reviewed_user
        }
    )
# ---------------- VIEW REVIEWS ----------------
@login_required
def view_reviews(request, profile_id):

    profile = get_object_or_404(
        Profile,
        id=profile_id
    )

    reviews = Review.objects.filter(
        reviewed_user=profile
    )

    average_rating = profile.average_rating()

    return render(
        request,
        "view_reviews.html",
        {
            "profile": profile,
            "reviews": reviews,
            "average_rating": average_rating,
        }
    )
# ---------------- VIEW REVIEWS ----------------
@login_required
def view_reviews(request, profile_id):

    profile = get_object_or_404(
        Profile,
        id=profile_id
    )

    reviews = Review.objects.filter(
        reviewed_user=profile
    ).order_by("-created_at")

    average_rating = reviews.aggregate(
        Avg("rating")
    )["rating__avg"]

    return render(
        request,
        "view_reviews.html",
        {
            "profile": profile,
            "reviews": reviews,
            "average_rating": average_rating
        }
    )
# ---------------- USER PROFILE ----------------
@login_required
def user_profile(request, profile_id):

    profile = get_object_or_404(
        Profile,
        id=profile_id
    )

    reviews = Review.objects.filter(
        reviewed_user=profile
    ).order_by("-created_at")

    average_rating = reviews.aggregate(
        Avg("rating")
    )["rating__avg"]

    if average_rating is None:
        average_rating = 0

    total_reviews = reviews.count()

    return render(
        request,
        "user_profile.html",
        {
            "profile": profile,
            "reviews": reviews,
            "average_rating": round(average_rating, 1),
            "total_reviews": total_reviews,
        }
    )