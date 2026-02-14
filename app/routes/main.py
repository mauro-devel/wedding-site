from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app import db
from app.models import Invitation, Guest

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@bp.route('/rsvp', methods=['GET', 'POST'])
def rsvp():
    """RSVP page - validate invitation code and show guest list."""
    if request.method == 'POST':
        invitation_code = request.form.get('invitation_code', '').strip().upper()
        
        # Validate invitation code
        invitation = Invitation.query.filter_by(invitation_code=invitation_code).first()
        
        if not invitation:
            flash('Invitation code not found. Please check and try again.', 'error')
            return render_template('rsvp.html')
        
        # Store invitation ID in session
        session['invitation_id'] = invitation.id
        
        # Redirect to guest selection page
        return redirect(url_for('main.rsvp_guests'))
    
    return render_template('rsvp.html')

@bp.route('/rsvp/guests', methods=['GET', 'POST'])
def rsvp_guests():
    """Show guests for the invitation and allow RSVP submission."""
    invitation_id = session.get('invitation_id')
    
    if not invitation_id:
        flash('Please enter your invitation code first.', 'error')
        return redirect(url_for('main.rsvp'))
    
    invitation = Invitation.query.get_or_404(invitation_id)
    
    if request.method == 'POST':
        # Handle RSVP submission (we'll implement this next)
        flash('RSVP submitted successfully!', 'success')
        return redirect(url_for('main.rsvp_confirmation'))
    
    return render_template('rsvp_guests.html', invitation=invitation)

@bp.route('/rsvp/confirmation')
def rsvp_confirmation():
    """Show RSVP confirmation page."""
    return render_template('rsvp_confirmation.html')

@bp.route('/language/<lang>')
def set_language(lang):
    """Set the user's language preference."""
    if lang in ['es', 'pt_PT']:
        session['language'] = lang
    return redirect(request.referrer or url_for('main.index'))