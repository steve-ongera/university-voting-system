# voting/context_processors.py
from .models import Election

def election_context(request):
    """Add current election to context"""
    current_election = Election.objects.filter(is_active=True).first()
    return {
        'current_election': current_election
    }