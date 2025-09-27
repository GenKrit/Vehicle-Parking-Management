from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.db_models import db, User
from models.db_models import Booking, ParkingLot, ParkingSpot
admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route("/admin")
def admin_home():
    return "<h2>Welcome, Admin!</h2>"

from flask import session

@admin_bp.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        admin = User.query.filter_by(email=email, password=password, role='admin').first()
        if admin:
            session['admin_id'] = admin.id
            flash("Admin login successful", "success")
            return redirect(url_for("admin_bp.admin_dashboard"))
        else:
            flash("Invalid admin credentials", "danger")
            return redirect(url_for("admin_bp.admin_login"))

    return render_template("admin_login.html")

@admin_bp.route("/admin/dashboard")
def admin_dashboard():
    if 'admin_id' not in session:
        flash("You must be logged in as admin", "warning")
        return redirect(url_for("admin_bp.admin_login"))

    # Fetch data for dashboard
    user_count = User.query.filter_by(role='user').count()
    lot_count = ParkingLot.query.count()
    spot_count = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    available_spots = ParkingSpot.query.filter_by(status='A').count()

    return render_template("admin_dashboard.html",
                           user_count=user_count,
                           lot_count=lot_count,
                           spot_count=spot_count,
                           occupied_spots=occupied_spots,
                           available_spots=available_spots)
@admin_bp.route("/admin/view-lots")
def view_parking_lots():
    if 'admin_id' not in session:
        flash("Admin login required", "warning")
        return redirect(url_for("admin_bp.admin_login"))

    lots = ParkingLot.query.all()

    lot_data = []
    for lot in lots:
        total = len(lot.spots)
        occupied = sum(1 for s in lot.spots if s.status == 'O')
        available = total - occupied
        lot_data.append({
            'id': lot.id,
            'location': lot.prime_location,
            'address': lot.address,
            'pincode': lot.pincode,
            'price': lot.price_per_hour,
            'total': total,
            'available': available,
            'occupied': occupied
        })

    return render_template("view_parkinglots.html", lots=lot_data)
@admin_bp.route("/admin/logout")
def admin_logout():
    session.pop('admin_id', None)
    flash("Logged out successfully", "info")
    return redirect(url_for("admin_bp.admin_login"))
@admin_bp.route("/admin/add-lot", methods=["GET", "POST"])
def add_parkinglot():
    if 'admin_id' not in session:
        flash("Admin login required", "warning")
        return redirect(url_for("admin_bp.admin_login"))

    if request.method == "POST":
        prime_location = request.form.get("location")
        address = request.form.get("address")
        pincode = request.form.get("pincode")
        price = float(request.form.get("price_per_hour"))
        total_spots = int(request.form.get("total_spots"))

        # Create ParkingLot
        new_lot = ParkingLot(
            prime_location=prime_location,
            address=address,
            pincode=pincode,
            price_per_hour=price,
            max_spots=total_spots
        )
        db.session.add(new_lot)
        db.session.commit()

        # Create ParkingSpots
        for _ in range(total_spots):
            db.session.add(ParkingSpot(lot_id=new_lot.id, status='A'))
        db.session.commit()

        flash(f"Parking Lot '{prime_location}' created with {total_spots} spots!", "success")
        return redirect(url_for("admin_bp.admin_dashboard"))

    return render_template("add_parkinglot.html")
@admin_bp.route("/admin/view-users")
def view_users():
    if 'admin_id' not in session:
        flash("Admin access required", "warning")
        return redirect(url_for("admin_bp.admin_login"))

    users = User.query.filter_by(role='user').all()
    return render_template("view_users.html", users=users)
@admin_bp.route("/admin/view-bookings")
def view_bookings():
    if 'admin_id' not in session:
        flash("Admin access only", "warning")
        return redirect(url_for("admin_bp.admin_login"))

    bookings = Booking.query.order_by(Booking.start_time.desc()).all()
    return render_template("view_bookings.html", bookings=bookings)
@admin_bp.route("/admin/charts")
def admin_charts():
    if 'admin_id' not in session:
        flash("Admin access only", "warning")
        return redirect(url_for("admin_bp.admin_login"))

    # Earnings Over Time
    earnings_data = (
        db.session.query(
            db.func.date(Booking.start_time),
            db.func.sum(Booking.total_cost)
        )
        .group_by(db.func.date(Booking.start_time))
        .order_by(db.func.date(Booking.start_time))
        .all()
    )

    dates = [str(date) for date, _ in earnings_data]
    totals = [round(total or 0, 2) for _, total in earnings_data]

    # Pie chart – Occupancy
    total_spots = ParkingSpot.query.count()
    occupied_spots = ParkingSpot.query.filter_by(status='O').count()
    available_spots = total_spots - occupied_spots

    return render_template(
        "charts.html",
        dates=dates,
        totals=totals,
        occupied=occupied_spots,
        available=available_spots
    )
# EDIT Parking Lot
@admin_bp.route("/admin/edit-lot/<int:lot_id>", methods=["GET", "POST"])
def edit_lot(lot_id):
    if 'admin_id' not in session:
        flash("Admin access only", "warning")
        return redirect(url_for("admin_bp.admin_login"))

    lot = ParkingLot.query.get_or_404(lot_id)

    if request.method == "POST":
        lot.prime_location = request.form.get("prime_location")
        lot.address = request.form.get("address")
        lot.pincode = request.form.get("pincode")
        lot.price_per_hour = float(request.form.get("price_per_hour"))
        db.session.commit()
        flash("Lot updated successfully", "success")
        return redirect(url_for("admin_bp.view_parking_lots"))

    return render_template("edit_lot.html", lot=lot)

# DELETE Parking Lot
@admin_bp.route("/admin/delete-lot/<int:lot_id>")
def delete_lot(lot_id):
    if 'admin_id' not in session:
        flash("Admin access only", "warning")
        return redirect(url_for("admin_bp.admin_login"))

    lot = ParkingLot.query.get_or_404(lot_id)

    # Delete all its spots first (to prevent constraint errors)
    ParkingSpot.query.filter_by(lot_id=lot.id).delete()
    db.session.delete(lot)
    db.session.commit()
    flash("Parking lot and its spots deleted", "info")
    return redirect(url_for("admin_bp.view_parking_lots"))
