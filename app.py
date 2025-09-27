
from flask import Flask, render_template
from models.db_models import db, User
from controllers.admin_routes import admin_bp
from controllers.user_routes import user_bp
import os

app = Flask(__name__)

# Basic Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.getenv("SECRET_KEY", "my_own_secret_key")  # fallback

# Initialize DB
db.init_app(app)


def setup_database(app):
    """
    Creates the database tables and ensures a default admin user exists.
    """
    with app.app_context():
        db.create_all()
        
        if not User.query.filter_by(email="admin@admin.com").first():
            admin = User(
                name="Admin",
                email="admin@admin.com",
                password="admin123",  # WARNING: In production, hash this
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()
        print("Database setup completed.")


# Register blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)


# Home route
@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    setup_database(app)
    app.run(debug=os.getenv("FLASK_DEBUG", "True") == "True")
