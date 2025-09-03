from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint, F

class CustomUserManager(BaseUserManager):
    def create_user(self, registration_number, birth_certificate_number, **extra_fields):
        if not registration_number:
            raise ValueError('Registration number is required')
        if not birth_certificate_number:
            raise ValueError('Birth certificate number is required')
        
        user = self.model(
            registration_number=registration_number,
            birth_certificate_number=birth_certificate_number,
            **extra_fields
        )
        user.set_password(birth_certificate_number)
        user.save(using=self._db)
        return user

    def create_superuser(self, registration_number, birth_certificate_number, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(registration_number, birth_certificate_number, **extra_fields)

class Faculty(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Faculties"
    
    def __str__(self):
        return self.name

class Department(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['name', 'faculty']
    
    def __str__(self):
        return f"{self.name} - {self.faculty.name}"

class Programme(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programmes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['name', 'department']
    
    def __str__(self):
        return f"{self.name} - {self.department.name}"

class Student(AbstractBaseUser, PermissionsMixin):
    registration_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[A-Z]{2}\d{3}/\d{4}/\d{4}$',
            message='Registration number must be in format: SC211/0530/2022'
        )]
    )
    birth_certificate_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100 , null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE, related_name='students',null=True, blank=True)
    year_of_study = models.IntegerField(choices=[(1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year'), (5, '5th Year')],null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'registration_number'
    REQUIRED_FIELDS = ['birth_certificate_number', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'voting_student'
    
    def __str__(self):
        return f"{self.registration_number} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def department(self):
        return self.programme.department
    
    @property
    def faculty(self):
        return self.programme.department.faculty

class Party(models.Model):
    name = models.CharField(max_length=200, unique=True)
    acronym = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='party_logos/', blank=True, null=True)
    color_code = models.CharField(max_length=7, default='#000000')  # Hex color code
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Parties"
    
    def __str__(self):
        return f"{self.name} ({self.acronym})"

class Position(models.Model):
    POSITION_TYPES = [
        ('president', 'President'),
        ('vice_president', 'Vice President'),
        ('secretary_general', 'Secretary General'),
        ('treasurer', 'Treasurer'),
        ('sports_minister', 'Sports Minister'),
        ('entertainment_minister', 'Entertainment Minister'),
        ('education_minister', 'Education Minister'),
        ('accommodation_minister', 'Accommodation Minister'),
    ]
    
    name = models.CharField(max_length=100, choices=POSITION_TYPES, unique=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)  # For ordering positions in UI
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.get_name_display()

class Candidate(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='candidacies')
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='candidates')
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidates')
    manifesto = models.TextField(blank=True)
    photo = models.ImageField(upload_to='candidate_photos/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['party', 'position']  # One candidate per position per party
    
    def __str__(self):
        return f"{self.student.full_name} - {self.position.name} ({self.party.acronym})"

class Delegate(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='delegate_profile')
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='delegates')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='delegates')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'department']  # Student can only be delegate in their department
    
    def clean(self):
        # Ensure delegate belongs to the correct department
        if self.student.department != self.department:
            raise ValidationError("Delegate must belong to their own department")
        
        # Check party delegate limit per department (max 2 per department)
        existing_delegates = Delegate.objects.filter(
            party=self.party, 
            department=self.department
        ).exclude(id=self.id if self.id else None)
        
        if existing_delegates.count() >= 2:
            raise ValidationError("Party can have maximum 2 delegates per department")
        
        # Check total party delegates limit (max 15)
        total_delegates = Delegate.objects.filter(party=self.party).exclude(id=self.id if self.id else None)
        if total_delegates.count() >= 15:
            raise ValidationError("Party can have maximum 15 delegates total")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.full_name} - Delegate ({self.party.acronym}) - {self.department.name}"

class Election(models.Model):
    ELECTION_PHASES = [
        ('registration', 'Registration Phase'),
        ('delegate_voting', 'Delegate Voting Phase'),
        ('main_voting', 'Main Voting Phase (Delegates vote for positions)'),
        ('results', 'Results Phase'),
        ('closed', 'Election Closed'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    current_phase = models.CharField(max_length=20, choices=ELECTION_PHASES, default='registration')
    delegate_voting_start = models.DateTimeField()
    delegate_voting_end = models.DateTimeField()
    main_voting_start = models.DateTimeField()
    main_voting_end = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.get_current_phase_display()}"
    
    @property
    def is_delegate_voting_active(self):
        now = timezone.now()
        return (self.current_phase == 'delegate_voting' and 
                self.delegate_voting_start <= now <= self.delegate_voting_end)
    
    @property
    def is_main_voting_active(self):
        now = timezone.now()
        return (self.current_phase == 'main_voting' and 
                self.main_voting_start <= now <= self.main_voting_end)

class DelegateVote(models.Model):
    """Students vote for delegates in their department"""
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='delegate_votes')
    voter = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='delegate_votes_cast')
    delegate = models.ForeignKey(Delegate, on_delete=models.CASCADE, related_name='votes_received')
    vote_time = models.DateTimeField(auto_now_add=True)
    voter_ip = models.GenericIPAddressField()
    
    class Meta:
        unique_together = ['election', 'voter']  # One vote per student per election
    
    def clean(self):
        # Ensure voter is from same department as delegate
        if self.voter.department != self.delegate.department:
            raise ValidationError("Can only vote for delegates in your own department")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.voter.registration_number} voted for {self.delegate.student.full_name}"

class MainVote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='main_votes')
    delegate = models.ForeignKey(Delegate, on_delete=models.CASCADE, related_name='main_votes_cast')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='votes_received')
    vote_time = models.DateTimeField(auto_now_add=True)
    voter_ip = models.GenericIPAddressField()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['election', 'delegate', 'candidate'],
                name='unique_vote_per_candidate'
            ),
            UniqueConstraint(
                fields=['election', 'delegate', 'candidate'],
                condition=models.Q(),  # Add condition if needed
                name='unique_vote_per_position'
            ),
        ]
class VoteAuditLog(models.Model):
    """Audit trail for all voting activities"""
    ACTION_TYPES = [
        ('delegate_vote', 'Delegate Vote Cast'),
        ('main_vote', 'Main Vote Cast'),
        ('login_attempt', 'Login Attempt'),
        ('vote_attempt', 'Vote Attempt'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='audit_logs', null=True, blank=True)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.timestamp}"

class ElectionResult(models.Model):
    """Cache election results for performance"""
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='cached_results')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='election_results')
    vote_count = models.IntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_winner = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['election', 'candidate']
        ordering = ['-vote_count']
    
    def __str__(self):
        return f"{self.candidate} - {self.vote_count} votes ({self.percentage}%)"