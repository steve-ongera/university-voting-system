# voting/utils.py
import logging
from django.conf import settings
from .models import VoteAuditLog

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def create_audit_log(action_type, description, ip_address, user_agent='', student=None, success=True):
    """Create an audit log entry"""
    try:
        VoteAuditLog.objects.create(
            student=student,
            action_type=action_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )
    except Exception as e:
        logging.getLogger('voting').error(f"Failed to create audit log: {str(e)}")

def check_voting_eligibility(student, election_type='delegate'):
    """Check if student is eligible to vote"""
    if not student.is_active:
        return False, "Your account is inactive"
    
    # Add additional eligibility checks here
    # e.g., check if student is in good academic standing, has paid fees, etc.
    
    return True, "Eligible to vote"