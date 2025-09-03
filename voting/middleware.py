# voting/middleware.py
from django.http import HttpResponseForbidden
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from .utils import get_client_ip, create_audit_log

class VotingSecurityMiddleware(MiddlewareMixin):
    """Custom middleware for additional security checks"""
    
    def process_request(self, request):
        ip_address = get_client_ip(request)
        
        # If IP restrictions are enabled, check allowed IPs
        allowed_ips = settings.VOTING_SETTINGS.get('ALLOWED_VOTING_IPS', [])
        if allowed_ips and ip_address not in allowed_ips:
            create_audit_log(
                action_type='security_violation',
                description=f"Access attempt from unauthorized IP: {ip_address}",
                ip_address=ip_address,
                success=False
            )
            return HttpResponseForbidden("Access denied from this IP address")
        
        # Add request info to request object for easy access
        request.client_ip = ip_address
        
        return None
