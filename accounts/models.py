from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):

    EXPERIENCE_CHOICES = [
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Expert", "Expert"),
    ]

    MODE_CHOICES = [
        ("Online", "Online"),
        ("Offline", "Offline"),
        ("Both", "Both"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(max_length=100)

    bio = models.TextField(
        blank=True
    )

    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    skills_offered = models.TextField(
        help_text="Comma-separated skills"
    )

    skills_wanted = models.TextField(
        help_text="Comma-separated skills"
    )

    experience = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES
    )

    language = models.CharField(max_length=50)

    availability = models.CharField(max_length=100)

    location = models.CharField(max_length=100)

    learning_mode = models.CharField(
        max_length=20,
        choices=MODE_CHOICES
    )

    # Average Rating
    def average_rating(self):
        reviews = self.reviews_received.all()

        if reviews.exists():
            total = sum(review.rating for review in reviews)
            return round(total / reviews.count(), 1)

        return 0

    def __str__(self):
        return self.full_name


class ExchangeRequest(models.Model):

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
    ]

    sender = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="sent_requests"
    )

    receiver = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="received_requests"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("sender", "receiver")

    def __str__(self):
        return f"{self.sender.full_name} → {self.receiver.full_name} ({self.status})"


class Message(models.Model):

    sender = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="messages_sent"
    )

    receiver = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="messages_received"
    )

    message = models.TextField()

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    # Notification
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.sender.full_name} → {self.receiver.full_name}"


class Review(models.Model):

    RATING_CHOICES = [
        (1, "⭐"),
        (2, "⭐⭐"),
        (3, "⭐⭐⭐"),
        (4, "⭐⭐⭐⭐"),
        (5, "⭐⭐⭐⭐⭐"),
    ]

    reviewer = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="reviews_given"
    )

    reviewed_user = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="reviews_received"
    )

    rating = models.IntegerField(
        choices=RATING_CHOICES
    )

    review = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("reviewer", "reviewed_user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reviewer.full_name} rated {self.reviewed_user.full_name} ({self.rating}⭐)"