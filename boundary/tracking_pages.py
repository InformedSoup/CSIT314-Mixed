"""Boundary: Interior Designer insight pages - track IDP views (#38) and shortlists (#39)."""
from flask import Blueprint, render_template, request, session

from boundary.access_control import roles_required
from control.track_idp_shortlists_controller import TrackIDPShortlistsController
from control.track_idp_views_controller import TrackIDPViewsController
from entity.user_profile import INTERIOR_DESIGNER

tracking_bp = Blueprint("tracking", __name__, url_prefix="/designer/insights")


@tracking_bp.route("/")
@roles_required(INTERIOR_DESIGNER)
def displayInsights():
    sort = request.args.get("sort", "views")
    me = session["account_id"]
    views, shortlists = TrackIDPViewsController(), TrackIDPShortlistsController()
    idps = shortlists.getShortlistCounts(me) if sort == "shortlists" else views.getViewCounts(me)
    return render_template("designer/insights_page.html", idps=idps, sort=sort,
                           totalViews=views.getTotalViews(me),
                           totalShortlists=shortlists.getTotalShortlists(me))
