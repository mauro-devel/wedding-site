from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_babel import gettext as _
from app import db
from app.models import Invitation, Guest, RSVPStatus, GuestRSVP

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
            flash(_('Invitation code not found. Please check and try again.'), 'error')
            return render_template('rsvp.html')
        
        # Store invitation ID in session
        session['invitation_id'] = invitation.id

        # Check if any guests have already responded
        has_responses = any(guest.rsvp for guest in invitation.guests)

        if has_responses:
            flash(_('You have already submitted a confirmation. You can update your response below.'), 'info')
        
        
        # Redirect to guest selection page
        return redirect(url_for('main.rsvp_guests'))
    
    return render_template('rsvp.html')

@bp.route('/rsvp/guests', methods=['GET', 'POST'])
def rsvp_guests():
    """Show guests for the invitation and allow RSVP submission."""
    invitation_id = session.get('invitation_id')
    
    if not invitation_id:
        flash(_('Please enter your invitation code first.'), 'error')
        return redirect(url_for('main.rsvp'))
    
    invitation = Invitation.query.get_or_404(invitation_id)
    
    if request.method == 'POST':
        # Get RSVP statuses
        status_accepted = RSVPStatus.query.filter_by(status_key='ACCEPTED').first()
        status_declined = RSVPStatus.query.filter_by(status_key='DECLINED').first()
        
        # Process each guest's RSVP
        for guest in invitation.guests:
            rsvp_value = request.form.get(f'rsvp_{guest.id}')
            
            if rsvp_value:
                # Determine which status to use
                if rsvp_value == 'ACCEPTED':
                    status = status_accepted
                elif rsvp_value == 'DECLINED':
                    status = status_declined
                else:
                    continue
                
                # Check if guest already has an RSVP
                existing_rsvp = GuestRSVP.query.filter_by(guest_id=guest.id).first()
                
                if existing_rsvp:
                    # Update existing RSVP
                    existing_rsvp.rsvp_status_id = status.id
                    from datetime import datetime
                    existing_rsvp.responded_at = datetime.utcnow().isoformat()
                else:
                    # Create new RSVP
                    from datetime import datetime
                    new_rsvp = GuestRSVP(
                        guest_id=guest.id,
                        rsvp_status_id=status.id,
                        responded_at=datetime.utcnow().isoformat()
                    )
                    db.session.add(new_rsvp)
        
        db.session.commit()
        flash(_('RSVP submitted successfully!'), 'success')
        return redirect(url_for('main.rsvp_confirmation'))
    
    return render_template('rsvp_guests.html', invitation=invitation)

@bp.route('/rsvp/confirmation')
def rsvp_confirmation():
    """Show RSVP confirmation page."""
    invitation_id = session.get('invitation_id')
    invitation = None
    
    if invitation_id:
        invitation = Invitation.query.get(invitation_id)
    
    return render_template('rsvp_confirmation.html', invitation=invitation)

@bp.route('/language/<lang>')
def set_language(lang):
    """Set the user's language preference."""
    print(f"Setting language to {lang}")
    if lang in ['es', 'pt_PT']:
        session['language'] = lang
        print(f"Session language set to {session.get('language')}")
    else:
        print(f"Invalid language {lang}")
    return redirect(request.referrer or url_for('main.index'))
