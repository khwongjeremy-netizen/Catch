from flask import Blueprint, request, jsonify
from db import supabase
import uuid

groups_bp = Blueprint("groups", __name__)


# ── Create a group ──────────────────────────────────────────────
# POST /groups/create
# Body: { "name": "Study Squad", "created_by": "<user_id>" }
@groups_bp.route("/create", methods=["POST"])
def create_group():
    data = request.get_json()
    name = data.get("name")
    created_by = data.get("created_by")

    if not name or not created_by:
        return jsonify({"error": "name and created_by are required"}), 400

    # Generate a short invite code friends can use to join
    invite_code = str(uuid.uuid4())[:8].upper()

    result = (
        supabase.table("groups")
        .insert({
            "name": name,
            "created_by": created_by,
            "invite_code": invite_code,
        })
        .execute()
    )

    group = result.data[0]

    # Automatically add the creator as a member
    supabase.table("group_members").insert({
        "group_id": group["id"],
        "user_id": created_by,
    }).execute()

    return jsonify({
        "message": "Group created",
        "group": group,
        "invite_code": invite_code,
    }), 201


# ── Join a group via invite code ────────────────────────────────
# POST /groups/join
# Body: { "invite_code": "ABC12345", "user_id": "<user_id>" }
@groups_bp.route("/join", methods=["POST"])
def join_group():
    data = request.get_json()
    invite_code = data.get("invite_code", "").upper()
    user_id = data.get("user_id")

    if not invite_code or not user_id:
        return jsonify({"error": "invite_code and user_id are required"}), 400

    # Look up the group by invite code
    group_result = (
        supabase.table("groups")
        .select("*")
        .eq("invite_code", invite_code)
        .execute()
    )

    if not group_result.data:
        return jsonify({"error": "Invalid invite code"}), 404

    group = group_result.data[0]

    # Check they're not already a member
    existing = (
        supabase.table("group_members")
        .select("id")
        .eq("group_id", group["id"])
        .eq("user_id", user_id)
        .execute()
    )

    if existing.data:
        return jsonify({"message": "Already a member", "group": group}), 200

    supabase.table("group_members").insert({
        "group_id": group["id"],
        "user_id": user_id,
    }).execute()

    return jsonify({"message": "Joined group", "group": group}), 200


# ── Get all members of a group ──────────────────────────────────
# GET /groups/<group_id>/members
@groups_bp.route("/<group_id>/members", methods=["GET"])
def get_members(group_id):
    result = (
        supabase.table("group_members")
        .select("*")
        .eq("group_id", group_id)
        .execute()
    )
    return jsonify({"members": result.data}), 200


# ── Get all groups a user belongs to ───────────────────────────
# GET /groups/user/<user_id>
@groups_bp.route("/user/<user_id>", methods=["GET"])
def get_user_groups(user_id):
    result = (
        supabase.table("group_members")
        .select("group_id, groups(*)")
        .eq("user_id", user_id)
        .execute()
    )
    return jsonify({"groups": result.data}), 200
