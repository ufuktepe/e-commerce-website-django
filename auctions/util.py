from decimal import Decimal
from .models import Watchlist, Listing, Comment


def get_listing_data(request, listing):
    """
    Returns the following listing attributes.
    in_watchlist: boolean value to indicate whether the listing is in the user's watchlist
    is_creator: boolean value to indicate whether the user is the creator of the listing
    is_winner: boolean value to indicate whether the user is the winner of the auction
    comments: set of Comment objects of the listing
    min_required_bid: equal to current bid + 0.01 if other users have placed bids. If no bids have been placed yet this
    will be equal to the initial bid.
    """
    # Initialize variables
    in_watchlist = False
    is_creator = False
    is_winner = False
    comments = None
    min_required_bid = listing.init_bid

    # Check if the user is logged in
    if request.user.is_authenticated:

        # Check if there exists a Watchlist object that has the user and this listing
        if Watchlist.objects.filter(user=request.user, listings=listing).exists():
            in_watchlist = True
        # Check if the user is the creator of the listing
        if request.user == listing.creator:
            is_creator = True
        # Check if the user is the winner of the auction
        if request.user == listing.winner:
            is_winner = True

    # Check if there is a Comment object associated with this listing
    if Comment.objects.filter(listing=listing).exists():
        # Get all comment objects associated with this listing
        comments = Comment.objects.filter(listing=listing)

    # If any bid exists other than the initial bid, set the min_required_bid to current_bid + 0.01
    if len(listing.bids.all()) > 1:
        min_required_bid = listing.current_bid + Decimal(0.01)

    return in_watchlist, is_creator, is_winner, comments, round(min_required_bid, 2)
