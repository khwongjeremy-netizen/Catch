from flask import Blueprint, request, jsonify
from db import supabase
from datetime import datetime, timezone

nudges_bp = Blueprint("nudges", __name__)


# ── Send a nudge to a friend ────────────────────────────────────
# POST /nudges/send
# Body: {
#   "from_user_id": "...",
#   "to_user_id": "...",
#   "group_id": "...",
#   "image_url": "https://...",   # funny photo URL
#   "caption": "Get off TikTok!"  # optional message
# }
@nudges_bp.route("/send", methods=["POST"])
def send_nudge():
    data = request.get_json()
    from_user = data.get("from_user_id")
    to_user = data.get("to_user_id")
    group_id = data.get("group_id")
    image_url = data.get("image_url")
    caption = data.get("caption", "")

    if not from_user or not to_user or not group_id or not image_url:
        return jsonify({"error": "from_user_id, to_user_id, group_id, and image_url are required"}), 400

    if from_user == to_user:
        return jsonify({"error": "You can't nudge yourself"}), 400

    # Verify both users are in the same group
    members_result = (
        supabase.table("group_members")
        .select("user_id")
        .eq("group_id", group_id)
        .in_("user_id", [from_user, to_user])
        .execute()
    )

    found_ids = {m["user_id"] for m in members_result.data}
    if from_user not in found_ids or to_user not in found_ids:
        return jsonify({"error": "Both users must be in the same group"}), 403

    # Save the nudge to the database
    result = (
        supabase.table("nudges")
        .insert({
            "from_user_id": from_user,
            "to_user_id": to_user,
            "group_id": group_id,
            "image_url": image_url,
            "caption": caption,
            "seen": False,
            "sent_at": datetime.now(timezone.utc).isoformat(),
        })
        .execute()
    )

    nudge = result.data[0]

    # NOTE: Web Push notification goes here once you set up VAPID keys.
    # For now, the frontend polls /nudges/inbox/<user_id> to check for new nudges.
    # See README.md for instructions on adding Web Push later.

    return jsonify({"message": "Nudge sent!", "nudge": nudge}), 201


# ── Get unread nudges for a user (their inbox) ──────────────────
# GET /nudges/inbox/<user_id>
@nudges_bp.route("/inbox/<user_id>", methods=["GET"])
def get_inbox(user_id):
    result = (
        supabase.table("nudges")
        .select("*")
        .eq("to_user_id", user_id)
        .eq("seen", False)
        .order("sent_at", desc=True)
        .execute()
    )
    return jsonify({"nudges": result.data}), 200


# ── Mark a nudge as seen ────────────────────────────────────────
# POST /nudges/<nudge_id>/seen
# Body: { "user_id": "..." }
@nudges_bp.route("/<nudge_id>/seen", methods=["POST"])
def mark_seen(nudge_id):
    data = request.get_json()
    user_id = data.get("user_id")

    result = (
        supabase.table("nudges")
        .update({"seen": True})
        .eq("id", nudge_id)
        .eq("to_user_id", user_id)
        .execute()
    )

    if not result.data:
        return jsonify({"error": "Nudge not found"}), 404

    return jsonify({"message": "Marked as seen"}), 200


# ── Get nudge history for a group ───────────────────────────────
# GET /nudges/group/<group_id>?limit=20
@nudges_bp.route("/group/<group_id>", methods=["GET"])
def get_group_nudges(group_id):
    limit = request.args.get("limit", 20, type=int)
    result = (
        supabase.table("nudges")
        .select("*")
        .eq("group_id", group_id)
        .order("sent_at", desc=True)
        .limit(limit)
        .execute()
    )
    return jsonify({"nudges": result.data}), 200
