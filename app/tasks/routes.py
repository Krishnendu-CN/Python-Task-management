from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_
from ..extensions import db
from ..models import Task

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route("/")
@login_required
def dashboard():
    # stats for chart
    total = Task.query.count()
    completed = Task.query.filter_by(completed=True).count()
    pending = total - completed
    return render_template("dashboard.html", total=total, completed=completed, pending=pending)

@tasks_bp.route("/tasks")
@login_required
def list_tasks():
    q = request.args.get("q", "").strip()
    sort = request.args.get("sort", "created_at")
    direction = request.args.get("dir", "desc")
    page = int(request.args.get("page", 1))
    per_page = 10

    query = Task.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Task.title.ilike(like), Task.description.ilike(like)))

    sort_col = getattr(Task, sort, Task.created_at)
    if direction == "desc":
        sort_col = sort_col.desc()
    query = query.order_by(sort_col)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    if request.headers.get("HX-Request"):  # partial render for HTMX
        return render_template("partials/task_table.html", pagination=pagination)

    return render_template("tasks/list.html", pagination=pagination, q=q, sort=sort, direction=direction)

@tasks_bp.route("/tasks/new", methods=["GET", "POST"])
@login_required
def create_task():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "medium")
        due_date = request.form.get("due_date") or None
        if due_date:
            due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
        if title:
            t = Task(title=title, description=description, priority=priority, due_date=due_date, created_by=current_user)
            db.session.add(t)
            db.session.commit()
            flash("Task created", "success")
            return redirect(url_for("tasks.list_tasks"))
        flash("Title is required", "danger")
    return render_template("tasks/form.html", task=None)

@tasks_bp.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == "POST":
        task.title = request.form.get("title", "").strip()
        task.description = request.form.get("description", "").strip()
        task.priority = request.form.get("priority", "medium")
        due_date = request.form.get("due_date") or None
        task.due_date = datetime.strptime(due_date, "%Y-%m-%d").date() if due_date else None
        db.session.commit()
        flash("Task updated", "success")
        return redirect(url_for("tasks.list_tasks"))
    return render_template("tasks/form.html", task=task)

@tasks_bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_complete(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    # return updated row for HTMX swap
    return render_template("partials/task_row.html", t=task)

@tasks_bp.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    # return nothing; HTMX will remove the row
    return ("", 204)