from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from .forms import TicketForm, UpdateTicketForm, CommentForm
from app.models import Ticket, User, Equipment, Comment
from app import db
from . import bp
from datetime import datetime, timezone

@bp.route('/')
@login_required
def list_tickets():
    list_title = "My Reported Tickets"
    if current_user.role in ['it_support', 'admin']:
        tickets = Ticket.query.order_by(Ticket.created_at.desc()).all()
        list_title = "All Tickets"
    else:
        tickets = Ticket.query.filter_by(reporter_id=current_user.id).order_by(Ticket.created_at.desc()).all()

    # A separate view for "Assigned to me" could be:
    # assigned_tickets = Ticket.query.filter_by(assignee_id=current_user.id).order_by(Ticket.created_at.desc()).all()

    return render_template('tickets/list_tickets.html', tickets=tickets, list_title=list_title, title="Tickets")

@bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_ticket():
    form = TicketForm()
    # TODO: Populate equipment choices if that field is added to form
    if form.validate_on_submit():
        ticket = Ticket(title=form.title.data,
                        description=form.description.data,
                        priority=form.priority.data,
                        reporter_id=current_user.id)
        if form.equipment_id.data and form.equipment_id.data != 0:
            ticket.equipment_id = form.equipment_id.data
        else:
            ticket.equipment_id = None # Ensure it's None if '--- None ---' was selected
        db.session.add(ticket)
        db.session.commit()
        flash('Ticket created successfully!', 'success')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))
    return render_template('tickets/create_ticket.html', title='New Ticket', form=form)

@bp.route('/<int:ticket_id>', methods=['GET'])
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    if not (current_user.role in ['it_support', 'admin'] or \
            ticket.reporter_id == current_user.id or \
            (ticket.assignee_id and ticket.assignee_id == current_user.id)):
        flash('You do not have permission to view this ticket.', 'danger')
        return redirect(url_for('tickets.list_tickets'))

    comment_form = CommentForm()
    update_form = None
    if current_user.role in ['it_support', 'admin']:
        update_form = UpdateTicketForm(obj=ticket)
        # Ensure assignee_id is correctly set if it's None from db
        if ticket.assignee_id is None and update_form.assignee_id.data is None:
             update_form.assignee_id.data = 0 # Represents "Unassign"

    # Comments are loaded via relationship, ordered by model definition
    return render_template('tickets/view_ticket.html', ticket=ticket,
                           comment_form=comment_form, update_form=update_form,
                           title=f"Ticket #{ticket.id}")

@bp.route('/<int:ticket_id>/update', methods=['POST']) # Should only be POST from view_ticket's embedded form
@login_required
def update_ticket(ticket_id):
    if not current_user.role in ['it_support', 'admin']:
        abort(403) # Forbidden

    ticket = Ticket.query.get_or_404(ticket_id)
    form = UpdateTicketForm() # Process submitted data

    if form.validate_on_submit():
        ticket.title = form.title.data
        ticket.description = form.description.data
        original_status = ticket.status
        ticket.status = form.status.data
        ticket.priority = form.priority.data

        assignee_id_data = form.assignee_id.data
        if assignee_id_data == 0: # 'Unassign' selected
            ticket.assignee_id = None
        else:
            ticket.assignee_id = assignee_id_data

        # Set resolved_at if status changes to 'Resolved' or 'Closed'
        if ticket.status in ['Resolved', 'Closed'] and original_status not in ['Resolved', 'Closed']:
            ticket.resolved_at = datetime.now(timezone.utc)
        elif ticket.status not in ['Resolved', 'Closed'] and original_status in ['Resolved', 'Closed']:
            # If reopened, clear resolved_at
            ticket.resolved_at = None

        if form.equipment_id.data and form.equipment_id.data != 0:
            ticket.equipment_id = form.equipment_id.data
        else:
            ticket.equipment_id = None # Ensure it's None if '--- None ---' was selected

        ticket.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        flash('Ticket updated successfully!', 'success')
    else:
        # Form validation failed, collect errors and flash them
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))


@bp.route('/<int:ticket_id>/comment', methods=['POST'])
@login_required
def add_comment(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    # Permission check similar to view_ticket might be good
    if not (current_user.role in ['it_support', 'admin'] or \
            ticket.reporter_id == current_user.id or \
            (ticket.assignee_id and ticket.assignee_id == current_user.id)):
        flash('You do not have permission to comment on this ticket.', 'danger')
        return redirect(url_for('tickets.list_tickets'))

    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          user_id=current_user.id,
                          ticket_id=ticket.id)
        db.session.add(comment)
        ticket.updated_at = datetime.now(timezone.utc) # Adding a comment updates the ticket
        db.session.commit()
        flash('Comment added.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in comment: {error}", 'danger')
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))
