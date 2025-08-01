from flask import Blueprint, render_template, request, redirect, url_for, session
from app import db
from app.models.dish import Dish
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.category import Category  # import Category to filter dishes by category name
from flask import request

client_bp = Blueprint('client', __name__)

@client_bp.route('/')
def index():
    """Render the home page with a list of available dishes.

    An optional `category` query parameter filters the dishes by the
    category name.  Categories are retrieved by joining the Category
    model to Dish and returning a list of category names only.  This
    avoids confusing the template with Category objects when it expects
    plain strings.
    """
    selected_category = request.args.get('category')
    if selected_category:
        # Filter dishes by availability and selected category name
        dishes = (
            Dish.query
            .filter_by(is_available=True)
            .join(Category)
            .filter(Category.name == selected_category)
            .all()
        )
    else:
        dishes = Dish.query.filter_by(is_available=True).all()

    # Retrieve distinct categories associated with available dishes.  We
    # return only the category names for simplicity in the template.
    categories_query = (
        Category.query
        .join(Dish)
        .filter(Dish.is_available == True)
        .distinct()
        .all()
    )
    categories = [cat.name for cat in categories_query]

    return render_template('index.html', dishes=dishes, categories=categories, selected_category=selected_category)

@client_bp.route('/add_to_cart/<int:dish_id>', methods=['POST'])
def add_to_cart(dish_id):
    cart = session.get('cart', {})
    quantity = int(request.form.get('quantity', 1))
    cart[str(dish_id)] = cart.get(str(dish_id), 0) + quantity
    session['cart'] = cart
    return redirect(url_for('client.index'))

@client_bp.route('/cart')
def cart():
    cart = session.get('cart', {})
    dish_ids = [int(id) for id in cart.keys()]
    dishes = Dish.query.filter(Dish.id.in_(dish_ids)).all()
    return render_template('cart.html', dishes=dishes, cart=cart)

@client_bp.route('/submit_order', methods=['POST'])
def submit_order():
    # Получаем данные из формы
    table_id = request.form.get('table_id')
    comment = request.form.get('comment', '')
    remove_ids = request.form.getlist('remove[]')  # блюда, отмеченные на удаление

    # Получаем количество каждого блюда (формат name="quantities[1]")
    quantities = {
        int(key.split('[')[1].split(']')[0]): int(value)
        for key, value in request.form.items()
        if key.startswith('quantities[') and value.isdigit()
    }

    # Удаляем блюда, отмеченные для удаления
    for remove_id in remove_ids:
        dish_id = int(remove_id)
        if dish_id in quantities:
            del quantities[dish_id]

    # Если не осталось блюд или не указан стол — вернуться на главную
    if not quantities or not table_id:
        return redirect(url_for('client.index'))

    # Создаём новый заказ
    order = Order(table_id=table_id, comment=comment, status='новый')
    db.session.add(order)
    db.session.flush()  # получаем order.id без коммита

    # Добавляем позиции заказа
    for dish_id, qty in quantities.items():
        db.session.add(OrderItem(order_id=order.id, dish_id=dish_id, quantity=qty))

    db.session.commit()  # сохраняем заказ и его позиции в базе
    session['cart'] = {}  # очищаем корзину

    # Перенаправляем пользователя на экран отслеживания заказа
    return redirect(url_for('client.order_status', table_id=table_id))


@client_bp.route('/order_status/<int:table_id>')
def order_status(table_id):
    order = Order.query.filter_by(table_id=table_id).order_by(Order.created_at.desc()).first()
    return render_template('order_status.html', order=order)

# ---------------------------------------------------------------------------
# QR code endpoint
#
# This endpoint renders a small page that displays a QR code linking back
# to the client-facing menu.  The QR code is generated client-side using
# a lightweight JavaScript library loaded from a CDN.  The URL passed to
# the QR generator uses the application's root URL so that scanning the
# code always returns to the correct host and port.
@client_bp.route('/qr')
def qr_page():
    """Render a page showing a QR code for the client menu."""
    # Build the absolute URL for the menu.  request.url_root already
    # contains the scheme, host and trailing slash.  url_for with
    # _external=True would normally be used, but since the menu is at
    # the root URL we can reuse url_root directly.
    menu_url = request.url_root.rstrip('/') + url_for('client.index')
    return render_template('qr.html', menu_url=menu_url)