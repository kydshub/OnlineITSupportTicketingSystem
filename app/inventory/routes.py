from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from .forms import EquipmentForm, AssignEquipmentForm
from app.models import Equipment, User
from app import db
from . import bp
from app.decorators import it_support_required # Use the decorator
from datetime import datetime, timezone

@bp.route('/')
@login_required
@it_support_required # Only IT support and admins can access inventory
def list_equipment():
    equipment_list = Equipment.query.order_by(Equipment.name).all()
    return render_template('inventory/list_equipment.html',
                           equipment_list=equipment_list,
                           title="Equipment Inventory")

@bp.route('/new', methods=['GET', 'POST'])
@login_required
@it_support_required
def add_equipment():
    form = EquipmentForm()
    if form.validate_on_submit():
        # Check for unique serial number if provided
        if form.serial_number.data:
            existing_serial = Equipment.query.filter_by(serial_number=form.serial_number.data).first()
            if existing_serial:
                flash('Serial number already exists. Please use a unique serial number.', 'danger')
                return render_template('inventory/add_equipment.html', title='Add Equipment', form=form)

        equipment = Equipment(
            name=form.name.data,
            type=form.type.data,
            manufacturer=form.manufacturer.data,
            model_number=form.model_number.data,
            serial_number=form.serial_number.data,
            purchase_date=form.purchase_date.data,
            warranty_expiry_date=form.warranty_expiry_date.data,
            status=form.status.data,
            notes=form.notes.data
        )
        db.session.add(equipment)
        db.session.commit()
        flash('Equipment added successfully!', 'success')
        return redirect(url_for('inventory.view_equipment', equipment_id=equipment.id))
    return render_template('inventory/add_equipment.html', title='Add New Equipment', form=form)

@bp.route('/<int:equipment_id>', methods=['GET'])
@login_required
@it_support_required # Viewing specific equipment might be IT only, or broader if needed
def view_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    form = EquipmentForm(obj=equipment) # For the edit form part of the page
    assign_form = AssignEquipmentForm(obj=equipment) # For the assignment part
    if equipment.assigned_to_user_id:
        assign_form.assigned_to_user_id.data = equipment.assigned_to_user_id
    else:
        assign_form.assigned_to_user_id.data = 0 # 'Unassign / In Stock'

    return render_template('inventory/view_equipment.html',
                           equipment=equipment, form=form, assign_form=assign_form,
                           title=f"View {equipment.name}")

@bp.route('/<int:equipment_id>/edit', methods=['POST']) # POST only from view_equipment page
@login_required
@it_support_required
def edit_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    form = EquipmentForm() # Process submitted data, not obj=equipment here for POST

    if form.validate_on_submit():
        # Check for unique serial number if provided and changed
        if form.serial_number.data and form.serial_number.data != equipment.serial_number:
            existing_serial = Equipment.query.filter(Equipment.id != equipment.id, Equipment.serial_number == form.serial_number.data).first()
            if existing_serial:
                flash('Serial number already exists for another item. Please use a unique serial number.', 'danger')
                # Need to pass assign_form as well to re-render view_equipment correctly
                assign_form = AssignEquipmentForm(obj=equipment)
                if equipment.assigned_to_user_id:
                    assign_form.assigned_to_user_id.data = equipment.assigned_to_user_id
                else:
                    assign_form.assigned_to_user_id.data = 0
                return render_template('inventory/view_equipment.html', title=f"View {equipment.name}", equipment=equipment, form=form, assign_form=assign_form)

        equipment.name = form.name.data
        equipment.type = form.type.data
        equipment.manufacturer = form.manufacturer.data
        equipment.model_number = form.model_number.data
        equipment.serial_number = form.serial_number.data
        equipment.purchase_date = form.purchase_date.data
        equipment.warranty_expiry_date = form.warranty_expiry_date.data
        # Status and assignment are handled by assign_equipment route for clarity
        # equipment.status = form.status.data
        equipment.notes = form.notes.data
        equipment.updated_at = datetime.now(timezone.utc)

        db.session.commit()
        flash('Equipment details updated successfully!', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error updating details in {getattr(form, field).label.text}: {error}", 'danger')

    return redirect(url_for('inventory.view_equipment', equipment_id=equipment.id))


@bp.route('/<int:equipment_id>/assign', methods=['POST'])
@login_required
@it_support_required
def assign_equipment(equipment_id):
    equipment = Equipment.query.get_or_404(equipment_id)
    assign_form = AssignEquipmentForm() # Process submitted data

    if assign_form.validate_on_submit():
        user_id = assign_form.assigned_to_user_id.data
        if user_id == 0: # Unassign selected
            equipment.assigned_to_user_id = None
            if equipment.status == 'Assigned': # If unassigning, change status from 'Assigned'
                equipment.status = 'In Stock'
            flash('Equipment unassigned and marked as In Stock.', 'success')
        else:
            user = User.query.get(user_id)
            if user:
                equipment.assigned_to_user_id = user.id
                equipment.status = 'Assigned' # Explicitly set status when assigning
                flash(f'Equipment assigned to {user.username}.', 'success')
            else:
                flash('Selected user not found.', 'danger')

        equipment.updated_at = datetime.now(timezone.utc)
        db.session.commit()
    else:
        for field, errors in assign_form.errors.items():
            for error in errors:
                flash(f"Error in assignment: {error}", 'danger')

    return redirect(url_for('inventory.view_equipment', equipment_id=equipment.id))

# Optional: Delete route (use with caution)
# @bp.route('/<int:equipment_id>/delete', methods=['POST'])
# @login_required
# @it_support_required
# def delete_equipment(equipment_id):
#     equipment = Equipment.query.get_or_404(equipment_id)
#     # Add checks: e.g., cannot delete if associated with open tickets or currently assigned?
#     if equipment.tickets: # Basic check
#         flash('Cannot delete equipment with associated tickets. Please resolve or reassign tickets first.', 'warning')
#         return redirect(url_for('inventory.view_equipment', equipment_id=equipment.id))
#
#     db.session.delete(equipment)
#     db.session.commit()
#     flash('Equipment deleted successfully.', 'success')
#     return redirect(url_for('inventory.list_equipment'))
