from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from ..extensions import db
from ..models import User, Task

api_bp = Blueprint("api", __name__)

@api_bp.post("/login")
def api_login():
    data = request.get_json() or {}
    email = data.get("email", "")
    password = data.get("password", "")
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_access_token(identity=user.id)
    return jsonify({"access_token": token})

@api_bp.get("/tasks")
@jwt_required()
def api_tasks_list():
    items = Task.query.order_by(Task.created_at.desc()).limit(100).all()
    return jsonify([{
        "id": t.id, "title": t.title, "description": t.description,
        "priority": t.priority, "due_date": t.due_date.isoformat() if t.due_date else None,
        "completed": t.completed
    } for t in items])

@api_bp.post("/tasks")
@jwt_required()
def api_tasks_create():
    data = request.get_json() or {}
    t = Task(
        title=data.get("title", ""),
        description=data.get("description", ""),
        priority=data.get("priority", "medium"),
    )
    db.session.add(t)
    db.session.commit()
    return jsonify({"id": t.id}), 201

@api_bp.patch("/tasks/<int:task_id>")
@jwt_required()
def api_tasks_update(task_id):
    t = Task.query.get_or_404(task_id)
    data = request.get_json() or {}
    for key in ["title", "description", "priority", "completed"]:
        if key in data:
            setattr(t, key, data[key])
    db.session.commit()
    return jsonify({"ok": True})

@api_bp.delete("/tasks/<int:task_id>")
@jwt_required()
def api_tasks_delete(task_id):
    t = Task.query.get_or_404(task_id)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"ok": True})