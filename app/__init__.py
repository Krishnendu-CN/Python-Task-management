import os
from flask import Flask
from .extensions import db, migrate, login_manager, jwt
from .config import Config
from .models import User

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_object(Config())

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)

    from .auth.routes import auth_bp
    from .tasks.routes import tasks_bp
    from .api.routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # CLI: create admin
    @app.cli.command("create-admin")
    def create_admin():
        import click
        from werkzeug.security import generate_password_hash
        email = click.prompt("Admin email")
        password = click.prompt("Admin password", hide_input=True, confirmation_prompt=True)
        name = click.prompt("Name", default="Admin")
        if User.query.filter_by(email=email).first():
            click.echo("User already exists.")
            return
        u = User(email=email, name=name, role="admin", password_hash=generate_password_hash(password))
        db.session.add(u)
        db.session.commit()
        click.echo("Admin created.")
    return app