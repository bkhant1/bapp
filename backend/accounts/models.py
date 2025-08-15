from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)

    # Privacy settings
    is_profile_public = models.BooleanField(default=True)
    allow_friend_requests = models.BooleanField(default=True)
    show_location = models.BooleanField(default=True)

    # Geographic coordinates for location-based search
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_active = models.DateTimeField(auto_now=True)

    # Use email as the unique identifier for login
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        db_table = "accounts_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def display_name(self):
        return self.full_name or self.username

    def get_friends(self):
        """Get all friends for this user"""
        from friendships.models import Friendship

        friendships = Friendship.objects.filter(
            models.Q(user1=self, status="accepted")
            | models.Q(user2=self, status="accepted")
        )
        friends = []
        for friendship in friendships:
            if friendship.user1 == self:
                friends.append(friendship.user2)
            else:
                friends.append(friendship.user1)
        return friends

    def get_friends_of_friends(self):
        """Get friends of friends (excluding direct friends and self)"""
        friends = self.get_friends()
        friends_of_friends = set()

        for friend in friends:
            for fof in friend.get_friends():
                if fof != self and fof not in friends:
                    friends_of_friends.add(fof)

        return list(friends_of_friends)


class UserProfile(models.Model):
    """
    Extended profile information for users
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    reading_preferences = models.JSONField(default=dict, blank=True)
    favorite_genres = models.JSONField(default=list, blank=True)
    reading_goals = models.JSONField(default=dict, blank=True)

    # Social media links
    website = models.URLField(blank=True)
    twitter = models.CharField(max_length=50, blank=True)
    instagram = models.CharField(max_length=50, blank=True)
    goodreads = models.URLField(blank=True)

    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    weekly_digest = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "accounts_user_profile"

    def __str__(self):
        return f"Profile for {self.user.display_name}"
