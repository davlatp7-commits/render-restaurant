import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from app import db
from app.models.dish import Dish
from app.models.category import Category

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

UPLOAD_FOLDER = 'app/static/img'

STATUSES = ['новый', 'принят', 'готовится', 'передаётся', 'завершён']

@admin_bp.route('/')
def admin_panel():
    dishes = Dish.query.all()
    categories = Category.query.all()
    return render_template('admin.html', dishes=dishes, categories=categories)

@admin_bp.route('/add', methods=['POST'])
def add_dish():
    name = request.form['name'].strip()
    description = request.form['description'].strip()
    weight = request.form['weight'].strip()
    try:
        price = float(request.form['price'])
    except (KeyError, ValueError):
        price = 0.0
    image = request.files.get('image')
    filename = None
    if image and image.filename:
        cleaned = secure_filename(image.filename)
        unique_prefix = uuid.uuid4().hex
        filename = f"{unique_prefix}_{cleaned}"
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        image.save(os.path.join(UPLOAD_FOLDER, filename))

    category_id_str = request.form.get('category_id', '').strip()
    category_id = int(category_id_str) if category_id_str else None

    dish = Dish(
        name=name,
        description=description,
        weight=weight,
        price=price,
        image_filename=filename,
        category_id=category_id
    )
    db.session.add(dish)
    db.session.commit()
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/delete/<int:dish_id>')
def delete_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    db.session.delete(dish)
    db.session.commit()
    return redirect(url_for('admin.admin_panel'))

@admin_bp.route('/toggle/<int:dish_id>')
def toggle_availability(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    dish.is_available = not dish.is_available
    db.session.commit()
    return redirect(url_for('admin.admin_panel'))

from app.models.order import Order
from app.models.order_item import OrderItem

@admin_bp.route('/orders')
def admin_orders():
    status_filter = request.args.get('status')
    if status_filter:
        status_filter = status_filter.lower()
        orders = Order.query.filter_by(status=status_filter).order_by(Order.created_at.desc()).all()
    else:
        completed_status = STATUSES[-1]
        orders = (
            Order.query
            .filter(Order.status != completed_status)
            .order_by(Order.created_at.desc())
            .all()
        )
    return render_template('admin_orders.html', orders=orders, statuses=STATUSES)

@admin_bp.route('/update_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    new_status = request.form.get('status', '').lower()
    order = Order.query.get_or_404(order_id)
    if new_status in STATUSES:
        order.status = new_status
        db.session.commit()
    return redirect(url_for('admin.admin_orders'))

@admin_bp.route('/edit/<int:dish_id>', methods=['GET', 'POST'])
def edit_dish(dish_id):
    dish = Dish.query.get_or_404(dish_id)
    if request.method == 'POST':
        dish.name = request.form.get('name', dish.name).strip()
        dish.description = request.form.get('description', dish.description).strip()
        dish.weight = request.form.get('weight', dish.weight).strip()
        try:
            dish.price = float(request.form.get('price', dish.price))
        except (TypeError, ValueError):
            pass

        category_id_str = request.form.get('category_id', '').strip()
        dish.category_id = int(category_id_str) if category_id_str else None

        image = request.files.get('image')
        if image and image.filename:
            cleaned = secure_filename(image.filename)
            unique_prefix = uuid.uuid4().hex
            filename = f"{unique_prefix}_{cleaned}"
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            dish.image_filename = filename

        db.session.commit()
        return redirect(url_for('admin.admin_panel'))

    categories = Category.query.all()
    return render_template('edit_dish.html', dish=dish, categories=categories)

@admin_bp.route('/orders/history')
def orders_history():
    completed_status = STATUSES[-1]
    orders = Order.query.filter_by(status=completed_status).order_by(Order.created_at.desc()).all()
    return render_template('admin_orders_history.html', orders=orders)

@admin_bp.route('/categories')
def manage_categories():
    categories = Category.query.all()
    return render_template('admin_categories.html', categories=categories)

@admin_bp.route('/categories/add', methods=['POST'])
def add_category():
    name = request.form['name'].strip()
    if name and not Category.query.filter_by(name=name).first():
        db.session.add(Category(name=name))
        db.session.commit()
    return redirect(url_for('admin.manage_categories'))

@admin_bp.route('/categories/edit/<int:category_id>', methods=['POST'])
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    new_name = request.form['name'].strip()
    if new_name and new_name != category.name:
        category.name = new_name
        db.session.commit()
    return redirect(url_for('admin.manage_categories'))

@admin_bp.route('/categories/delete/<int:category_id>')
def delete_category(category_id):
    """Delete a category and unlink it from any dishes."""
    category = Category.query.get_or_404(category_id)
    for dish in Dish.query.filter_by(category_id=category.id).all():
        dish.category_id = None
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for('admin.manage_categories'))
