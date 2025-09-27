from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.db_models import db, User, ParkingLot, ParkingSpot, Booking
from datetime import datetime
from flask import jsonify
user_bp = Blueprint('user_bp', __name__)


@user_bp.route("/user")
def user_home():
    if 'user_id' not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("user_bp.login"))
    return render_template("dashboard_user.html")

    #return "<h2>Welcome, User!</h2><p><a href='/book'>Book Spot</a> | <a href='/release'>Release Spot</a> | <a href='/history'>Booking History</a></p>"

@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            flash("Login successful!", "success")
            return redirect(url_for("user_bp.user_home"))
        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for("user_bp.login"))

    return render_template("login.html")


@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Email already exists", "warning")
            return redirect(url_for("user_bp.register"))

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully!", "success")
        return redirect(url_for("user_bp.login"))

    return render_template("register.html")


@user_bp.route("/book", methods=["GET", "POST"])
def book_parking():
    if 'user_id' not in session:
        flash("Please login to continue", "warning")
        return redirect(url_for("user_bp.login"))

    parking_lots = ParkingLot.query.all()

    if request.method == "POST":
        selected_lot_id = request.form.get("lot_id")
        vehicle_no = request.form.get("vehicle_number")

        spot = ParkingSpot.query.filter_by(lot_id=selected_lot_id, status='A').first()

        if spot:
            spot.status = 'O'
            booking = Booking(
                spot_id=spot.id,
                user_id=session['user_id'],
                vehicle_number=vehicle_no,
                start_time=datetime.utcnow()
            )
            db.session.add(booking)
            db.session.commit()

            flash(f"Spot {spot.id} booked successfully in Lot {spot.lot_id}", "success")
            return redirect(url_for("user_bp.user_home"))
        else:
            flash("No available spots in that lot", "danger")

    return render_template("book_spot.html", parking_lots=parking_lots)

@user_bp.route("/history")
def booking_history():
    if 'user_id' not in session:
        flash("Login required to view booking history", "warning")
        return redirect(url_for("user_bp.login"))

    bookings = Booking.query.filter_by(user_id=session['user_id']).order_by(Booking.start_time.desc()).all()

    labels = [b.start_time.strftime('%d %b') for b in bookings]
    costs = [round(b.total_cost or 0, 2) for b in bookings]

    return render_template("booking_history.html", bookings=bookings, labels=labels, costs=costs)

@user_bp.route("/release", methods=["GET", "POST"])
def release_spot():
    if 'user_id' not in session:
        flash("Please login to release a spot", "warning")
        return redirect(url_for("user_bp.login"))

    booking = Booking.query.filter_by(user_id=session['user_id'], end_time=None).first()

    if not booking:
        flash("No active booking found", "info")
        return redirect(url_for("user_bp.user_home"))

    if request.method == "POST":
        booking.end_time = datetime.utcnow()
        duration = (booking.end_time - booking.start_time).total_seconds() / 3600

        spot = ParkingSpot.query.get(booking.spot_id)
        lot = ParkingLot.query.get(spot.lot_id)

        booking.total_cost = round(duration * lot.price_per_hour, 2)
        spot.status = 'A'

        db.session.commit()
        flash("Spot released successfully!", "success")
        return redirect(url_for("user_bp.user_home"))

    return render_template("release_form.html", booking=booking)
@user_bp.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("user_bp.login"))
