from django.conf import settings
from django.db import models


class Friendship(models.Model):
    """Friendship relationship between users"""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
        ("blocked", "Blocked"),
    ]

    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friendships_sent",
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friendships_received",
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    # Who initiated the friendship
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="initiated_friendships",
    )

    # Optional message when sending friend request
    message = models.TextField(max_length=500, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "friendships_friendship"
        unique_together = ["user1", "user2"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user1.display_name} -> {self.user2.display_name} ({self.status})"

    def save(self, *args, **kwargs):
        # Ensure user1 != user2
        if self.user1 == self.user2:
            raise ValueError("Users cannot be friends with themselves")

        # Set accepted_at when status changes to accepted
        if self.status == "accepted" and not self.accepted_at:
            from django.utils import timezone

            self.accepted_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def other_user(self):
        """Get the other user in the friendship from a given user's perspective"""
        # This would need to be called with context of which user is asking
        pass

    def get_other_user(self, user):
        """Get the other user in the friendship"""
        if user == self.user1:
            return self.user2
        elif user == self.user2:
            return self.user1
        else:
            return None


class FriendshipInvitation(models.Model):
    """Invitations sent to non-users to join the platform"""

    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_invitations",
    )
    email = models.EmailField()
    message = models.TextField(max_length=500, blank=True)
    invitation_code = models.CharField(max_length=50, unique=True)

    # Status tracking
    is_sent = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_invitations",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    accepted_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "friendships_invitation"
        unique_together = ["inviter", "email"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invitation from {self.inviter.display_name} to {self.email}"

    @property
    def is_expired(self):
        from django.utils import timezone

        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.is_expired and not self.is_accepted


class BlockedUser(models.Model):
    """Users blocked by other users"""

    blocker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blocked_users"
    )
    blocked = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blocked_by"
    )
    reason = models.CharField(
        max_length=50,
        choices=[
            ("spam", "Spam"),
            ("harassment", "Harassment"),
            ("inappropriate", "Inappropriate Content"),
            ("other", "Other"),
        ],
        blank=True,
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "friendships_blocked_user"
        unique_together = ["blocker", "blocked"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.blocker.display_name} blocked {self.blocked.display_name}"

    def save(self, *args, **kwargs):
        # Ensure blocker != blocked
        if self.blocker == self.blocked:
            raise ValueError("Users cannot block themselves")
        super().save(*args, **kwargs)
