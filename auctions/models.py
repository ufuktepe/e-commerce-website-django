from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """
    User model that inherits from AbstractUser
    """
    pass


class Category(models.Model):
    """
    Category model that stores a name for a single category
    """
    name = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        # Correct the plural name of the model
        verbose_name_plural = "categories"


class Listing(models.Model):
    """
    Listing model that stores various attributes of a single listing item
    """
    # Title of the listing
    title = models.CharField(max_length=128)
    # Description of the item
    description = models.TextField()
    # Initial bid
    init_bid = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    # Last (highest) bid. Equal to initial bid when the listing is first created
    current_bid = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    # URL for the image
    url = models.URLField(blank=True)
    # Boolean field to identify whether the listing is active or closed
    active = models.BooleanField(default=True)
    # Creator of the listing
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_listings")
    # Winner of the auction
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="won_listings", default=None, null=True)
    # Category of the listing
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listings", blank=True, null=True)
    # Creation time of the listing
    created_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        # Sort listings by created_on when queried so that listings created recently will appear first. The minus sign
        # is used to sort the listings in descending order.
        ordering = ["-created_on"]


class Bid(models.Model):
    """
    Bid model that stores the amount of a single bid related to a listing and a bidder
    """
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")

    def __str__(self):
        return f"Listing: {self.listing.title}, Bid: {self.amount}, Bidder: {self.bidder.username}"


class Watchlist(models.Model):
    """
    Watchlist model that stores listings for a single user
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist", default=None)
    listings = models.ManyToManyField(Listing, related_name="watchlists")

    def __str__(self):
        return f"Watchlist of {self.user.username}"


class Comment(models.Model):
    """
    Comment model that stores various attributes of a single comment
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment", default=None)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)

    class Meta:
        # Sort comments by date_posted when queried so that comments made recently will appear first. The minus sign
        # is used to sort the comments in descending order.
        ordering = ["-date_posted"]

    def __str__(self):
        return f"User: {self.user.username}, Listing: {self.listing.title}, Date: {self.date_posted}"
