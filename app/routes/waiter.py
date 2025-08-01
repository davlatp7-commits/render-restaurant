from flask import Blueprint, render_template, redirect, url_for, jsonify
from app import db
from app.models.order import Order
from app.models.order_item import OrderItem

waiter_bp = Blueprint('waiter', __name__, url_prefix='/waiter')

@waiter_bp.route('/')
def waiter_panel():
    """Display active orders for the waiter.

    Only orders that have not yet been completed (status ``'завершён'``)
    are shown in the active list.  Completed orders are available via
    the history page.
    """
    orders = (Order.query
              .filter(Order.status != 'завершён')
              .order_by(Order.created_at.desc())
              .all())
    return render_template('waiter.html', orders=orders)

@waiter_bp.route('/update_status/<int:order_id>/<string:new_status>')
def update_status(order_id, new_status):
    order = Order.query.get_or_404(order_id)
    order.status = new_status
    db.session.commit()
    return redirect(url_for('waiter.waiter_panel'))

@waiter_bp.route('/check_new')
def check_new():
    """Return the ID of the most recently created order and whether there are
    any unprocessed (new) orders.

    The waiter dashboard periodically polls this endpoint to determine if a
    new order has arrived.  In addition to the latest order ID, we return a
    flag indicating the presence of any orders whose status is still
    'новый'.  When the client submits an order the default status on the
    Order model is 'новый'.  The waiter should acknowledge the order by
    setting it to another status (e.g., 'принят').  Until then the front‑end
    will continue to play a notification sound to draw the waiter's
    attention.
    """
    latest_order = Order.query.order_by(Order.id.desc()).first()
    latest_id = latest_order.id if latest_order else 0
    # Determine if there are any orders that have not yet been assigned a
    # status other than the default.  We consider an order 'unassigned'
    # when its status string matches exactly 'новый'.  Using an `exists` query
    # avoids fetching all rows unnecessarily.
    has_unassigned = db.session.query(Order.query.filter_by(status='новый').exists()).scalar()
    return jsonify({"latest_id": latest_id, "unassigned": has_unassigned})

@waiter_bp.route('/delete/<int:order_id>')
def delete_order(order_id):
    """Mark an order as completed instead of permanently deleting it.

    When the waiter clicks “Удалить”, the order is moved to the
    history by assigning it the completed status.  The actual rows
    remain in the database so that the administrator and waiter can
    review them later.  Completed orders are omitted from the active
    list but appear in the history view.
    """
    order = Order.query.get_or_404(order_id)
    # Assign the final status to indicate completion.  Do not delete
    # the associated items so they remain part of the order history.
    order.status = 'завершён'
    db.session.commit()
    return redirect(url_for('waiter.waiter_panel'))

@waiter_bp.route('/history')
def waiter_history():
    """Show the history of completed orders.

    Only orders with the final status ("завершён") are shown.  Orders
    are sorted from newest to oldest.
    """
    orders = Order.query.filter_by(status='завершён').order_by(Order.created_at.desc()).all()
    return render_template('waiter_history.html', orders=orders)

@waiter_bp.route('/clear')
def clear_history():
    """Delete all completed orders and their associated items.

    This operation irreversibly removes all orders with status
    "завершён" from the database along with their related
    OrderItem rows.
    """
    completed_orders = Order.query.filter_by(status='завершён').all()
    for order in completed_orders:
        # Remove each associated order item.  SQLAlchemy will cascade
        # deletes if configured, but we do this explicitly for clarity.
        for item in order.items:
            db.session.delete(item)
        db.session.delete(order)
    db.session.commit()
    return redirect(url_for('waiter.waiter_panel'))
