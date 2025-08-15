from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Genre(models.Model):
    """Book genres"""

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "books_genre"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Author(models.Model):
    """Book authors"""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "books_author"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Publisher(models.Model):
    """Book publishers"""

    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    country = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "books_publisher"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Book(models.Model):
    """Book information"""

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("es", "Spanish"),
        ("fr", "French"),
        ("de", "German"),
        ("it", "Italian"),
        ("pt", "Portuguese"),
        ("ru", "Russian"),
        ("zh", "Chinese"),
        ("ja", "Japanese"),
        ("ar", "Arabic"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=300, blank=True)
    authors = models.ManyToManyField(Author, related_name="books")
    isbn_10 = models.CharField(max_length=10, blank=True, unique=True, null=True)
    isbn_13 = models.CharField(max_length=13, blank=True, unique=True, null=True)

    # Publication details
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, null=True, blank=True
    )
    publication_date = models.DateField(blank=True, null=True)
    edition = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default="en")

    # Physical details
    pages = models.PositiveIntegerField(blank=True, null=True)
    format = models.CharField(max_length=50, blank=True)  # Hardcover, Paperback, etc.

    # Content details
    description = models.TextField(blank=True)
    genres = models.ManyToManyField(Genre, related_name="books", blank=True)

    # Metadata
    cover_image = models.ImageField(upload_to="book_covers/", blank=True, null=True)
    goodreads_id = models.CharField(max_length=50, blank=True)
    google_books_id = models.CharField(max_length=50, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "books_book"
        ordering = ["title"]
        unique_together = [
            ["title", "publication_date", "publisher"],
        ]

    def __str__(self):
        return self.title

    @property
    def author_names(self):
        return ", ".join([author.full_name for author in self.authors.all()])

    @property
    def display_title(self):
        if self.subtitle:
            return f"{self.title}: {self.subtitle}"
        return self.title


class UserBook(models.Model):
    """User's personal book collection"""

    STATUS_CHOICES = [
        ("owned", "Owned"),
        ("reading", "Currently Reading"),
        ("read", "Read"),
        ("want_to_read", "Want to Read"),
        ("available", "Available for Exchange"),
        ("lent_out", "Lent Out"),
        ("exchanged", "Exchanged"),
    ]

    CONDITION_CHOICES = [
        ("new", "New"),
        ("like_new", "Like New"),
        ("very_good", "Very Good"),
        ("good", "Good"),
        ("acceptable", "Acceptable"),
        ("poor", "Poor"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="books"
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="user_books")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="owned")
    condition = models.CharField(
        max_length=20, choices=CONDITION_CHOICES, default="good"
    )

    # Personal notes and ratings
    notes = models.TextField(blank=True)
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True
    )
    review = models.TextField(blank=True)

    # Physical details specific to this copy
    purchase_date = models.DateField(blank=True, null=True)
    purchase_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    location = models.CharField(max_length=100, blank=True)  # Where it's stored

    # Exchange settings
    available_for_exchange = models.BooleanField(default=False)
    exchange_type = models.CharField(
        max_length=20,
        choices=[
            ("permanent", "Permanent Exchange"),
            ("temporary", "Temporary Loan"),
            ("both", "Both"),
        ],
        default="both",
    )

    # Reading progress
    current_page = models.PositiveIntegerField(default=0)
    date_started = models.DateField(blank=True, null=True)
    date_finished = models.DateField(blank=True, null=True)

    # Timestamps
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "books_user_book"
        unique_together = ["user", "book"]
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.display_name} - {self.book.title}"

    @property
    def reading_progress(self):
        if self.book.pages and self.current_page:
            return (self.current_page / self.book.pages) * 100
        return 0


class BookCollection(models.Model):
    """User-created book collections/lists"""

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="collections"
    )
    books = models.ManyToManyField(UserBook, related_name="collections", blank=True)

    is_public = models.BooleanField(default=False)
    is_collaborative = models.BooleanField(default=False)
    collaborators = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="collaborative_collections", blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "books_collection"
        unique_together = ["user", "name"]
        ordering = ["name"]

    def __str__(self):
        return f"{self.user.display_name} - {self.name}"


class BookReview(models.Model):
    """Public book reviews"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField()

    is_spoiler = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)

    # Engagement
    likes_count = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_reviews", blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "books_review"
        unique_together = ["user", "book"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review of {self.book.title} by {self.user.display_name}"
