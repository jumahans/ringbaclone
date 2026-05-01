from django.contrib import admin
from django.utils.html import format_html
from .models import RespOrg, ScamReport, ReportLog

@admin.register(RespOrg)
class RespOrgAdmin(admin.ModelAdmin):
    list_display = ('code', 'carrier_name', 'abuse_email', 'website', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('code', 'carrier_name', 'abuse_email')
    readonly_fields = ('created_at',)
    ordering = ('code',)
    
    fieldsets = (
        (None, {
            'fields': ('code', 'carrier_name', 'abuse_email', 'website')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ScamReport)
class ScamReportAdmin(admin.ModelAdmin):
    list_display = (
        'id_short', 'brand', 'phone_number', 'campaign_id', 'status_colored', 
        'resporg_code', 'submitted_by_email', 'created_at_short'
    )
    list_filter = ('status', 'created_at', 'submitted_by', 'brand')
    search_fields = (
        'phone_number', 'landing_url', 'brand', 'campaign_id', 
        'notes', 'resporg_raw'
    )
    readonly_fields = ('id', 'created_at', 'updated_at', 'screenshot_preview')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Report Information', {
            'fields': ('id', 'brand', 'phone_number', 'landing_url', 'campaign_id')
        }),
        ('Status & RespOrg', {
            'fields': ('status', 'resporg', 'resporg_raw')
        }),
        ('Scam Details', {
            'fields': ('description', 'notes')
        }),
        ('Reporter Information', {
            'fields': (
                'reporter_first_name', 'reporter_last_name', 'reporter_email',
                'reporter_phone', 'reporter_address', 'reporter_address2',
                'reporter_city', 'reporter_state', 'reporter_zip'
            ),
            'classes': ('collapse',)
        }),
        ('Screenshots', {
            'fields': ('screenshot_path', 'screenshot_preview', 'ftc_screenshot', 'ic3_screenshot'),
            'classes': ('collapse',)
        }),
        ('Submission Info', {
            'fields': ('submitted_by', 'report_sent_at', 'created_at', 'updated_at')
        }),
    )
    
    def id_short(self, obj):
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def status_colored(self, obj):
        colors = {
            'pending': 'orange',
            'reported': 'blue',
            'killed': 'green',
            'failed': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(f'<span style="color: {color}; font-weight: bold;">{obj.get_status_display()}</span>')
    status_colored.short_description = 'Status'
    
    def resporg_code(self, obj):
        return obj.resporg.code if obj.resporg else obj.resporg_raw or '—'
    resporg_code.short_description = 'RespOrg'
    
    def submitted_by_email(self, obj):
        return obj.submitted_by.email if obj.submitted_by else 'Anonymous'
    submitted_by_email.short_description = 'Submitted By'
    
    def created_at_short(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_short.short_description = 'Created'
    
    def screenshot_preview(self, obj):
        if obj.screenshot_path:
            return format_html(f'<a href="{obj.screenshot_path}" target="_blank">View Screenshot</a>')
        return '—'
    screenshot_preview.short_description = 'Preview'
    
    actions = ['mark_as_reported', 'mark_as_killed', 'mark_as_failed']
    
    def mark_as_reported(self, request, queryset):
        updated = queryset.update(status='reported')
        self.message_user(request, f'{updated} reports marked as reported.')
    mark_as_reported.short_description = 'Mark selected as Reported'
    
    def mark_as_killed(self, request, queryset):
        updated = queryset.update(status='killed')
        self.message_user(request, f'{updated} reports marked as killed.')
    mark_as_killed.short_description = 'Mark selected as Killed'
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} reports marked as failed.')
    mark_as_failed.short_description = 'Mark selected as Failed'


@admin.register(ReportLog)
class ReportLogAdmin(admin.ModelAdmin):
    list_display = ('report_id_short', 'action_colored', 'success_icon', 'detail_preview', 'created_at')
    list_filter = ('action', 'success', 'created_at')
    search_fields = ('detail', 'report__phone_number', 'report__brand')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def report_id_short(self, obj):
        return str(obj.report.id)[:8]
    report_id_short.short_description = 'Report ID'
    
    def action_colored(self, obj):
        colors = {
            'created': 'green',
            'resporg_lookup': 'blue',
            'email_sent': 'purple',
            'status_changed': 'orange',
            'screenshot_saved': 'cyan',
        }
        color = colors.get(obj.action, 'gray')
        return format_html(f'<span style="color: {color};">{obj.get_action_display()}</span>')
    action_colored.short_description = 'Action'
    
    def success_icon(self, obj):
        if obj.success:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    success_icon.short_description = 'Success'
    
    def detail_preview(self, obj):
        return obj.detail[:100] + '...' if len(obj.detail) > 100 else obj.detail
    detail_preview.short_description = 'Details'