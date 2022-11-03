from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from . import util
from .models import User, Watchlist, Listing, Bid, Comment, Category


class NewListingForm(ModelForm):
    """
    ModelForm for creating a new listing.
    """
    class Meta:
        model = Listing
        fields = ["title", "description", "init_bid", "url", "category"]
        # Rename "url" label as "Image URL"
        labels = {"url": "Image URL"}

    def __init__(self, *args, **kwargs):
        # Call super() to extend the functionality of the superclass
        super().__init__(*args, **kwargs)
        # Populate the "category" queryset with Category objects to display the categories in a select field in HTML
        self.fields["category"].queryset = Category.objects.all()
        # self.fields["url"].required = False


class NewBidForm(ModelForm):
    """
    ModelForm for creating a new bidding form.
    """
    class Meta:
        model = Bid
        fields = ["amount"]
        # Remove the "amount" label
        labels = {"amount": ""}


class NewCommentForm(ModelForm):
    """
    ModelForm for creating a new comment.
    """
    class Meta:
        model = Comment
        fields = ["content"]
        # Remove the "content" label
        labels = {"content": ""}

        widgets = {
            'content': forms.Textarea(attrs={
                'style': 'width:100%'}),
        }


def index(request):
    """
    Default route that returns active listings.
    """
    return render(request, "auctions/index.html", {"header": "Active Listings", "listings": Listing.objects.filter(active=True)})


def login_view(request):
    """
    Verifies user credentials and logs in the user.
    """
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    """
    Logs out the user.
    """
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    """
    Creates a new user and logs in the user.
    """
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/register.html")


def create_listing(request):
    """
    Creates Listing and Bid objects. Then redirects to the index page.
    """
    if request.method == "POST":
        # Fetch the form
        form = NewListingForm(request.POST)

        # Check if form is valid
        if form.is_valid():
            # Get the form data
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            init_bid = form.cleaned_data["init_bid"]
            url = form.cleaned_data["url"]
            category = form.cleaned_data["category"]

            # Create a new Listing object
            new_listing = Listing(title=title, description=description, init_bid=init_bid, current_bid=init_bid,
                                  url=url, creator=request.user, category=category)
            new_listing.save()

            # Create a new Bid object
            bid = Bid(listing=new_listing, amount=init_bid, bidder=request.user)
            bid.save()

            # Redirect to the index page
            return HttpResponseRedirect(reverse("index"))

        # If form is invalid, return the create page with the current form
        else:
            return render(request, "auctions/create.html", {"form": form})

    # If request is not a post request, return the create page with a new form
    return render(request, "auctions/create.html", {"form": NewListingForm()})


def display_listing(request, listing_id):
    """
    Displays listing based on the listing_id.
    """
    # Get the listing object
    listing = Listing.objects.get(pk=listing_id)
    # Get the listing data
    in_watchlist, is_creator, is_winner, comments, min_required_bid = util.get_listing_data(request, listing)

    # Render the listing page using the listing data
    return render(request, "auctions/listing.html",
                  {"listing": listing,
                   "in_watchlist": in_watchlist,
                   "bidding_form": NewBidForm(),
                   "error": False,
                   "min_required_bid": min_required_bid,
                   "is_creator": is_creator,
                   "is_winner": is_winner,
                   "active": listing.active,
                   "comment_form": NewCommentForm(),
                   "comments": comments})


@login_required(login_url="login")
def update_price(request, listing_id):
    """
    Updates the listing price based on the bid. The price is updated only if the bid is at least as large as the initial
    bid, and greater than any other bids that have been placed. If the bid does not meet those criteria, the user is
    presented with an error.
    """
    if request.method == "POST":
        # Get the listing object
        listing = Listing.objects.get(pk=listing_id)

        # Fetch the bidding form
        bidding_form = NewBidForm(request.POST)

        # Get the listing data
        in_watchlist, is_creator, is_winner, comments, min_required_bid = util.get_listing_data(request, listing)

        # Check if the bidding form is valid
        if bidding_form.is_valid():
            # Get the bidding amount
            new_bid = bidding_form.cleaned_data["amount"]

            # Check if new bid is greater than or equal to the minimum required bid
            if min_required_bid <= new_bid:
                # Create a Bid object
                bid = Bid(listing=listing, amount=new_bid, bidder=request.user)
                bid.save()
                # Update the current bid of the listing
                listing.current_bid = new_bid
                listing.save()
            else:
                # Render the listing page with an error saying the bid must be greater than the minimum required bid
                return render(request, "auctions/listing.html",
                              {"listing": listing,
                               "in_watchlist": in_watchlist,
                               "bidding_form": bidding_form,
                               "error": True,
                               "min_required_bid": min_required_bid,
                               "is_creator": is_creator,
                               "is_winner": is_winner,
                               "active": listing.active,
                               "comment_form": NewCommentForm(),
                               "comments": comments})
        else:
            # If the bidding form is invalid then get the listing data and render the listing page
            return render(request, "auctions/listing.html",
                          {"listing": listing,
                           "in_watchlist": in_watchlist,
                           "bidding_form": bidding_form,
                           "error": False,
                           "min_required_bid": min_required_bid,
                           "is_creator": is_creator,
                           "is_winner": is_winner,
                           "active": listing.active,
                           "comment_form": NewCommentForm(),
                           "comments": comments})

    # If request is not a post request, redirect to the listing page
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


@login_required(login_url="login")
def edit_watchlist(request, listing_id):
    """
    Adds/Removes the Listing to/from the Watchlist.
    If the Listing is in the user's Watchlist, removes the Listing from the Watchlist.
    Otherwise adds the Listing to the user's Watchlist.
    """
    # Get the listing object
    listing = Listing.objects.get(pk=listing_id)
    # Check if there exists a Watchlist object for the user
    if Watchlist.objects.filter(user=request.user).exists():
        if Watchlist.objects.filter(user=request.user, listings=listing).exists():
            # Remove the listing if it exists
            Watchlist.objects.get(user=request.user).listings.remove(listing)
        else:
            # Add the listing if it does not exist
            Watchlist.objects.get(user=request.user).listings.add(listing)
    else:
        # Create a new Watchlist object for the user
        new_watchlist = Watchlist(user=request.user)
        new_watchlist.save()
        # Add the listing to the Watchlist object's "listings" ManyToManyField
        new_watchlist.listings.add(listing)

    # Redirect to the listing page
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


def display_watchlist(request):
    """
    Displays the Watchlist of the user.
    """
    # Try to get the listings from the Watchlist of the user. If Watchlist does not exist, assign None to listings
    try:
        listings = Watchlist.objects.get(user=request.user).listings.all()
    except Watchlist.DoesNotExist:
        listings = None

    # Render the watchlist page
    return render(request, "auctions/watchlist.html", {"listings": listings})


def close_listing(request, listing_id):
    """
    Deactivates the listing and makes the last (highest) bidder the winner of the auction.
    """
    # Get the listing object
    listing = Listing.objects.get(pk=listing_id)
    # Deactivate the listing
    listing.active = False
    # Get the last Bid
    last_bid = listing.bids.last()
    # Make the last bidder the winner
    listing.winner = last_bid.bidder
    listing.save()

    # Redirect to the listing page
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


@login_required(login_url="login")
def create_comment(request, listing_id):
    """
    Creates a new Comment object and redirects to the listing page.
    """
    if request.method == "POST":
        # Get the listing object
        listing = Listing.objects.get(pk=listing_id)

        # Fetch the comment form
        comment_form = NewCommentForm(request.POST)

        # Check if the comment form is valid
        if comment_form.is_valid():
            # Get the content and create a new Comment object
            content = comment_form.cleaned_data["content"]
            new_comment = Comment(user=request.user, listing=listing, content=content)
            new_comment.save()

            # Redirect to the listing page
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

        else:
            # If the comment form is invalid then get the listing data and render the listing page
            in_watchlist, is_creator, is_winner, comments, min_required_bid = util.get_listing_data(request, listing)
            return render(request, "auctions/listing.html", {"listing": listing,
                                                             "in_watchlist": in_watchlist,
                                                             "bidding_form": NewBidForm(),
                                                             "error": False,
                                                             "min_required_bid": min_required_bid,
                                                             "is_creator": is_creator,
                                                             "is_winner": is_winner,
                                                             "active": listing.active,
                                                             "comment_form": comment_form,
                                                             "comments": comments})

    # If request is not a post request, redirect to the listing page
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


def display_all_categories(request):
    """
    Displays a list of all listing categories. Clicking on the name of any category takes the user to a page that
    displays all of the active listings in that category.
    """
    # Try to get all Category objects. If no Category object exists, assign None to categories
    try:
        categories = Category.objects.all()
    except Category.DoesNotExist:
        categories = None

    # Render the categories page
    return render(request, "auctions/all_categories.html", {"categories": categories})


def display_single_category(request, category_id):
    """
    Displays all of the active listings in the category with pk=category_id.
    """
    # Get the Category object
    category = Category.objects.get(pk=category_id)
    # Get all active listings in this category
    listings = Listing.objects.filter(category=category, active=True)

    # Render the category page
    return render(request, "auctions/index.html", {"header": category.name, "listings": listings})
