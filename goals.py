from flask import Blueprint, request, jsonify
from db import supabase
from datetime import datetime, timezone

goals_bp = Blueprint("goals", __name__)


# ── Set a goal (start a session) ────────────────────────────────
# POST /goals/set
# Body: { "user_id": "...", "group_id": "...", "description": "Finish essay intro" }
@goals_bp.route("/set", methods=["POST"])
def set_goal():
    data = request.get_json()
    user_id = data.get("user_id")
    group_id = data.get("group_id")
    description = data.get("description")

    if not user_id or not group_id or not description:
        return jsonify({"error": "user_id, group_id, and description are required"}), 400

    result = (
        supabase.table("goals")
        .insert({
            "user_id": user_id,
            "group_id": group_id,
            "description": description,
            "status": "active",   # active | done
            "started_at": datetime.now(timezone.utc).isoformat(),
        })
        .execute()
    )

    return jsonify({"message": "Goal set — you're in!", "goal": result.data[0]}), 201


# ── Mark a goal as done ─────────────────────────────────────────
# POST /goals/<goal_id>/complete
# Body: { "user_id": "..." }   (to verify ownership)
@goals_bp.route("/<goal_id>/complete", methods=["POST"])
def complete_goal(goal_id):
    data = request.get_json()
    user_id = data.get("user_id")

    # Verify the goal belongs to this user
    existing = (
        supabase.table("goals")
        .select("*")
        .eq("id", goal_id)
        .eq("user_id", user_id)
        .execute()
    )

    if not existing.data:
        return jsonify({"error": "Goal not found or not yours"}), 404

    result = (
        supabase.table("goals")
        .update({
            "status": "done",
            "completed_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("id", goal_id)
        .execute()
    )

    # Check if everyone in the group has completed their active goal
    group_id = existing.data[0]["group_id"]
    group_complete = check_group_complete(group_id)

    return jsonify({
        "message": "Goal complete! Nice work.",
        "goal": result.data[0],
        "group_all_done": group_complete,   # frontend uses this to unlock the reward
    }), 200


# ── Get all active goals in a group ────────────────────────────
# GET /goals/group/<group_id>
@goals_bp.route("/group/<group_id>", methods=["GET"])
def get_group_goals(group_id):
    result = (
        supabase.table("goals")
        .select("*")
        .eq("group_id", group_id)
        .order("started_at", desc=True)
        .execute()
    )
    return jsonify({"goals": result.data}), 200


# ── Helper: check if all group members finished their goals ─────
def check_group_complete(group_id):
    members = (
        supabase.table("group_members")
        .select("user_id")
        .eq("group_id", group_id)
        .execute()
    ).data

    if not members:
        return False

    member_ids = [m["user_id"] for m in members]

    # Count how many members have an active (incomplete) goal right now
    incomplete = (
        supabase.table("goals")
        .select("id")
        .eq("group_id", group_id)
        .eq("status", "active")
        .in_("user_id", member_ids)
        .execute()
    ).data

    return len(incomplete) == 0
