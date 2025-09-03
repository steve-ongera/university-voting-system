from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.core.cache import cache
from django.conf import settings
import logging
import json
from datetime import datetime, timedelta

from .models import (
    Student, Election, Party, Delegate, Candidate, Position,
    DelegateVote, MainVote, VoteAuditLog, ElectionResult
)
from .forms import LoginForm, DelegateVoteForm, MainVoteForm
from .utils import get_client_ip, create_audit_log, check_voting_eligibility

# Set up logging
logger = logging.getLogger('voting')
security_logger = logging.getLogger('security')

def get_current_election():
    """Get the currently active election"""
    return Election.objects.filter(is_active=True).first()

class LoginView(TemplateView):
    template_name = 'voting/login.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = LoginForm()
        return context
    
    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        ip_address = get_client_ip(request)
        
        # Check for too many failed attempts
        cache_key = f"login_attempts_{ip_address}"
        attempts = cache.get(cache_key, 0)
        
        if attempts >= settings.VOTING_SETTINGS['MAX_LOGIN_ATTEMPTS']:
            security_logger.warning(f"Too many login attempts from {ip_address}")
            messages.error(request, "Too many failed login attempts. Please try again later.")
            return render(request, self.template_name, {'form': form})
        
        if form.is_valid():
            registration_number = form.cleaned_data['registration_number']
            birth_certificate_number = form.cleaned_data['birth_certificate_number']
            
            # Authenticate user
            user = authenticate(
                request,
                username=registration_number,
                password=birth_certificate_number
            )
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # Clear failed attempts
                    cache.delete(cache_key)
                    
                    # Update last login IP
                    user.last_login_ip = ip_address
                    user.save(update_fields=['last_login_ip'])
                    
                    # Create audit log
                    create_audit_log(
                        student=user,
                        action_type='login_attempt',
                        description=f"Successful login from {ip_address}",
                        ip_address=ip_address,
                        user_agent=request.META.get('HTTP_USER_AGENT', ''),
                        success=True
                    )
                    
                    logger.info(f"Student {registration_number} logged in successfully")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Your account has been deactivated.")
            else:
                # Increment failed attempts
                cache.set(
                    cache_key, 
                    attempts + 1, 
                    settings.VOTING_SETTINGS['LOGIN_LOCKOUT_TIME']
                )
                
                create_audit_log(
                    action_type='login_attempt',
                    description=f"Failed login attempt for {registration_number} from {ip_address}",
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    success=False
                )
                
                security_logger.warning(f"Failed login attempt for {registration_number} from {ip_address}")
                messages.error(request, "Invalid registration number or birth certificate number.")
        
        return render(request, self.template_name, {'form': form})

@login_required
def logout_view(request):
    student_reg = request.user.registration_number
    ip_address = get_client_ip(request)
    
    create_audit_log(
        student=request.user,
        action_type='logout',
        description=f"User logged out from {ip_address}",
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        success=True
    )
    
    logout(request)
    logger.info(f"Student {student_reg} logged out")
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

@login_required
def dashboard_view(request):
    """Main dashboard showing current election status and user's voting status"""
    current_election = get_current_election()
    
    if not current_election:
        messages.warning(request, "No active election at the moment.")
        return render(request, 'voting/no_election.html')
    
    context = {
        'election': current_election,
        'student': request.user,
        'department': request.user.department,
        'faculty': request.user.faculty,
    }
    
    # Check if student has voted for delegates
    delegate_vote = DelegateVote.objects.filter(
        election=current_election,
        voter=request.user
    ).first()
    
    context['has_voted_for_delegate'] = delegate_vote is not None
    context['delegate_vote'] = delegate_vote
    
    # Get available delegates in student's department
    available_delegates = Delegate.objects.filter(
        department=request.user.department,
        is_approved=True
    ).select_related('student', 'party')
    
    context['available_delegates'] = available_delegates
    
    # Check if student is a delegate
    try:
        delegate_profile = request.user.delegate_profile
        context['is_delegate'] = True
        context['delegate_profile'] = delegate_profile
        
        # If delegate, show voting options for main positions
        if current_election.is_main_voting_active:
            positions = Position.objects.all().order_by('order')
            candidates = Candidate.objects.filter(is_approved=True).select_related('student', 'party', 'position')
            
            # Get delegate's votes for each position
            delegate_votes = MainVote.objects.filter(
                election=current_election,
                delegate=delegate_profile
            ).select_related('candidate__position')
            
            voted_positions = {vote.candidate.position.id for vote in delegate_votes}
            
            context.update({
                'positions': positions,
                'candidates': candidates,
                'voted_positions': voted_positions,
                'delegate_votes': {vote.candidate.position.id: vote for vote in delegate_votes}
            })
    
    except Student.delegate_profile.RelatedObjectDoesNotExist:
        context['is_delegate'] = False
    
    return render(request, 'voting/dashboard.html', context)

@login_required
@require_POST
@csrf_protect
def vote_for_delegate(request):
    """Students vote for delegates in their department"""
    current_election = get_current_election()
    
    if not current_election or not current_election.is_delegate_voting_active:
        return JsonResponse({
            'success': False,
            'error': 'Delegate voting is not currently active.'
        }, status=400)
    
    # Check if student has already voted
    existing_vote = DelegateVote.objects.filter(
        election=current_election,
        voter=request.user
    ).exists()
    
    if existing_vote:
        return JsonResponse({
            'success': False,
            'error': 'You have already voted for a delegate.'
        }, status=400)
    
    try:
        data = json.loads(request.body)
        delegate_id = data.get('delegate_id')
        
        if not delegate_id:
            return JsonResponse({
                'success': False,
                'error': 'Delegate ID is required.'
            }, status=400)
        
        delegate = get_object_or_404(
            Delegate.objects.select_related('student', 'party', 'department'),
            id=delegate_id,
            is_approved=True
        )
        
        # Verify delegate is in voter's department
        if delegate.department != request.user.department:
            security_logger.warning(
                f"Student {request.user.registration_number} attempted to vote for delegate "
                f"outside their department: {delegate.department.name}"
            )
            return JsonResponse({
                'success': False,
                'error': 'You can only vote for delegates in your own department.'
            }, status=403)
        
        ip_address = get_client_ip(request)
        
        with transaction.atomic():
            # Create the vote
            vote = DelegateVote.objects.create(
                election=current_election,
                voter=request.user,
                delegate=delegate,
                voter_ip=ip_address
            )
            
            # Create audit log
            create_audit_log(
                student=request.user,
                action_type='delegate_vote',
                description=f"Voted for delegate {delegate.student.full_name} ({delegate.party.acronym})",
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=True
            )
        
        logger.info(
            f"Student {request.user.registration_number} voted for delegate "
            f"{delegate.student.registration_number} ({delegate.party.acronym})"
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully voted for {delegate.student.full_name} ({delegate.party.acronym})'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data.'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in delegate voting: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while processing your vote.'
        }, status=500)

@login_required
@require_POST
@csrf_protect
def vote_for_candidate(request):
    """Delegates vote for candidates in main positions"""
    current_election = get_current_election()
    
    if not current_election or not current_election.is_main_voting_active:
        return JsonResponse({
            'success': False,
            'error': 'Main voting is not currently active.'
        }, status=400)
    
    # Check if user is a delegate
    try:
        delegate = request.user.delegate_profile
        if not delegate.is_approved:
            return JsonResponse({
                'success': False,
                'error': 'You are not an approved delegate.'
            }, status=403)
    except Student.delegate_profile.RelatedObjectDoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'You are not registered as a delegate.'
        }, status=403)
    
    try:
        data = json.loads(request.body)
        candidate_id = data.get('candidate_id')
        
        if not candidate_id:
            return JsonResponse({
                'success': False,
                'error': 'Candidate ID is required.'
            }, status=400)
        
        candidate = get_object_or_404(
            Candidate.objects.select_related('student', 'party', 'position'),
            id=candidate_id,
            is_approved=True
        )
        
        # Check if delegate has already voted for this position
        existing_vote = MainVote.objects.filter(
            election=current_election,
            delegate=delegate,
            candidate__position=candidate.position
        ).exists()
        
        if existing_vote:
            return JsonResponse({
                'success': False,
                'error': f'You have already voted for {candidate.position.get_name_display()}.'
            }, status=400)
        
        ip_address = get_client_ip(request)
        
        with transaction.atomic():
            # Create the vote
            vote = MainVote.objects.create(
                election=current_election,
                delegate=delegate,
                candidate=candidate,
                voter_ip=ip_address
            )
            
            # Create audit log
            create_audit_log(
                student=request.user,
                action_type='main_vote',
                description=f"Voted for {candidate.student.full_name} for {candidate.position.get_name_display()} ({candidate.party.acronym})",
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=True
            )
        
        logger.info(
            f"Delegate {request.user.registration_number} voted for candidate "
            f"{candidate.student.registration_number} for {candidate.position.name}"
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Successfully voted for {candidate.student.full_name} for {candidate.position.get_name_display()}'
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data.'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in candidate voting: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while processing your vote.'
        }, status=500)

@login_required
def election_results_view(request):
    """Show election results"""
    current_election = get_current_election()
    
    if not current_election:
        messages.warning(request, "No active election found.")
        return redirect('dashboard')
    
    if current_election.current_phase not in ['results', 'closed']:
        messages.warning(request, "Election results are not yet available.")
        return redirect('dashboard')
    
    # Get results grouped by position
    positions = Position.objects.all().order_by('order')
    results = {}
    
    for position in positions:
        candidates = Candidate.objects.filter(
            position=position,
            is_approved=True
        ).select_related('student', 'party').annotate(
            vote_count=Count('votes_received', filter=Q(votes_received__election=current_election))
        ).order_by('-vote_count')
        
        total_votes = sum(candidate.vote_count for candidate in candidates)
        
        for candidate in candidates:
            if total_votes > 0:
                candidate.percentage = (candidate.vote_count / total_votes) * 100
            else:
                candidate.percentage = 0
        
        results[position] = {
            'candidates': candidates,
            'total_votes': total_votes
        }
    
    # Get delegate voting results
    delegate_results = {}
    departments = request.user.faculty.departments.all()
    
    for department in departments:
        delegates = Delegate.objects.filter(
            department=department,
            is_approved=True
        ).select_related('student', 'party').annotate(
            vote_count=Count('votes_received', filter=Q(votes_received__election=current_election))
        ).order_by('-vote_count')
        
        total_votes = sum(delegate.vote_count for delegate in delegates)
        
        for delegate in delegates:
            if total_votes > 0:
                delegate.percentage = (delegate.vote_count / total_votes) * 100
            else:
                delegate.percentage = 0
        
        delegate_results[department] = {
            'delegates': delegates,
            'total_votes': total_votes
        }
    
    context = {
        'election': current_election,
        'results': results,
        'delegate_results': delegate_results,
        'positions': positions,
    }
    
    return render(request, 'voting/results.html', context)

@login_required
def voting_status_api(request):
    """API endpoint to get current voting status"""
    current_election = get_current_election()
    
    if not current_election:
        return JsonResponse({'error': 'No active election'}, status=404)
    
    # Get user's voting status
    delegate_vote_exists = DelegateVote.objects.filter(
        election=current_election,
        voter=request.user
    ).exists()
    
    # Check if user is delegate and their main voting status
    main_votes_cast = 0
    total_positions = Position.objects.count()
    is_delegate = False
    
    try:
        delegate = request.user.delegate_profile
        if delegate.is_approved:
            is_delegate = True
            main_votes_cast = MainVote.objects.filter(
                election=current_election,
                delegate=delegate
            ).count()
    except Student.delegate_profile.RelatedObjectDoesNotExist:
        pass
    
    return JsonResponse({
        'election': {
            'name': current_election.name,
            'current_phase': current_election.current_phase,
            'delegate_voting_active': current_election.is_delegate_voting_active,
            'main_voting_active': current_election.is_main_voting_active,
        },
        'user_status': {
            'has_voted_for_delegate': delegate_vote_exists,
            'is_delegate': is_delegate,
            'main_votes_cast': main_votes_cast,
            'total_positions': total_positions,
            'department': request.user.department.name,
            'faculty': request.user.faculty.name,
        }
    })

@login_required
def candidates_api(request):
    """API endpoint to get candidates for a specific position"""
    position_id = request.GET.get('position_id')
    
    if not position_id:
        return JsonResponse({'error': 'Position ID required'}, status=400)
    
    candidates = Candidate.objects.filter(
        position_id=position_id,
        is_approved=True
    ).select_related('student', 'party').values(
        'id',
        'student__first_name',
        'student__last_name',
        'student__registration_number',
        'party__name',
        'party__acronym',
        'party__color_code',
        'manifesto'
    )
    
    return JsonResponse({'candidates': list(candidates)})

@login_required
def delegates_api(request):
    """API endpoint to get delegates in user's department"""
    delegates = Delegate.objects.filter(
        department=request.user.department,
        is_approved=True
    ).select_related('student', 'party').values(
        'id',
        'student__first_name',
        'student__last_name',
        'student__registration_number',
        'party__name',
        'party__acronym',
        'party__color_code'
    )
    
    return JsonResponse({'delegates': list(delegates)})

def health_check(request):
    """Health check endpoint for monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'database': 'connected'
    })