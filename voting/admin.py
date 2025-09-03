# voting/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    Student, Faculty, Department, Programme, Party, Position,
    Candidate, Delegate, Election, DelegateVote, MainVote,
    VoteAuditLog, ElectionResult
)

@admin.register(Student)
class StudentAdmin(UserAdmin):
    list_display = ('registration_number', 'full_name', 'programme', 'year_of_study', 'is_active')
    list_filter = ('is_active', 'year_of_study', 'programme__department__faculty')
    search_fields = ('registration_number', 'first_name', 'last_name', 'email')
    ordering = ('registration_number',)
    
    fieldsets = (
        (None, {'fields': ('registration_number', 'birth_certificate_number')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        ('Academic info', {'fields': ('programme', 'year_of_study')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('registration_number', 'birth_certificate_number', 'first_name', 'last_name', 'programme', 'year_of_study'),
        }),
    )

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'faculty', 'created_at')
    list_filter = ('faculty',)
    search_fields = ('name', 'code')

@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'created_at')
    list_filter = ('department__faculty', 'department')
    search_fields = ('name', 'code')

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'acronym', 'color_display', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'acronym')
    
    def color_display(self, obj):
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            obj.color_code,
            obj.color_code
        )
    color_display.short_description = 'Color'

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('get_name_display', 'order')
    ordering = ('order',)

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('student', 'party', 'position', 'is_approved', 'created_at')
    list_filter = ('party', 'position', 'is_approved')
    search_fields = ('student__first_name', 'student__last_name', 'student__registration_number')

@admin.register(Delegate)
class DelegateAdmin(admin.ModelAdmin):
    list_display = ('student', 'party', 'department', 'is_approved', 'created_at')
    list_filter = ('party', 'department', 'is_approved')
    search_fields = ('student__first_name', 'student__last_name', 'student__registration_number')

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'current_phase', 'is_active', 'created_at')
    list_filter = ('current_phase', 'is_active')
    date_hierarchy = 'created_at'

@admin.register(DelegateVote)
class DelegateVoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'delegate', 'election', 'vote_time')
    list_filter = ('election', 'delegate__party')
    search_fields = ('voter__registration_number', 'delegate__student__registration_number')
    readonly_fields = ('vote_time', 'voter_ip')

@admin.register(MainVote)
class MainVoteAdmin(admin.ModelAdmin):
    list_display = ('delegate', 'candidate', 'election', 'vote_time')
    list_filter = ('election', 'candidate__position', 'candidate__party')
    search_fields = ('delegate__student__registration_number', 'candidate__student__registration_number')
    readonly_fields = ('vote_time', 'voter_ip')

@admin.register(VoteAuditLog)
class VoteAuditLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'action_type', 'success', 'timestamp', 'ip_address')
    list_filter = ('action_type', 'success', 'timestamp')
    search_fields = ('student__registration_number', 'description', 'ip_address')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'

@admin.register(ElectionResult)
class ElectionResultAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'election', 'vote_count', 'percentage', 'is_winner')
    list_filter = ('election', 'candidate__position', 'is_winner')
    search_fields = ('candidate__student__registration_number',)