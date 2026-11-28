"""Offline policy prototype. No network, payload storage, deletion or agent execution."""
from datetime import datetime, timedelta, timezone
from threading import Lock

ROLES = frozenset(f'AGI-{i:02}' for i in range(1, 56))
SOURCES = {'independent', 'cloud_customer', 'cloud_technical', 'workspace_user', 'workspace_technical'}
RESTRICTED = {'cloud_technical', 'workspace_user', 'workspace_technical'}
LEARNING = {'train', 'fine_tune', 'evaluation_dataset', 'distill', 'competing_service'}
PRODUCTS = {'gmail', 'calendar', 'drive', 'docs', 'sheets', 'slides', 'chat', 'tasks'}

def aware(t):
    return isinstance(t, datetime) and t.tzinfo is not None and t.utcoffset() is not None

def decide(role, sources, action, now, acquired, *, authorized=False, active=False,
           connected=False, rights=False, task_deadline=None):
    if role not in ROLES or not isinstance(sources, (set, frozenset)) or not sources or not sources <= SOURCES:
        return False, 'unknown_role_or_source'
    if not aware(now) or not aware(acquired) or acquired > now:
        return False, 'invalid_time'
    if action not in LEARNING | {'process', 'cache', 'durable_memory'}:
        return False, 'unknown_action'
    if authorized is not True or active is not True:
        return False, 'no_active_authorization'
    if sources & RESTRICTED:
        if connected is not True:
            return False, 'revoked_flag_for_removal'
        if not aware(task_deadline) or task_deadline <= acquired:
            return False, 'missing_task_deadline'
        if now >= min(acquired + timedelta(days=30), task_deadline):
            return False, 'expired_flag_for_removal'
        if action in LEARNING | {'durable_memory'}:
            return False, 'restricted_reuse'
        return True, 'temporary_task_only'
    if sources != {'independent'}:
        return False, 'customer_data_requires_separate_review'
    if rights is not True:
        return False, 'rights_unverified'
    return True, 'eligible_subject_to_other_policies'

class Quota:
    """In-memory synthetic reservation ledger; deliberately not a production meter."""
    def __init__(self, cap=4500):
        if type(cap) is not int or not 1 <= cap <= 5000:
            raise ValueError('invalid cap')
        self.cap, self.used, self.lock = cap, {}, Lock()
    def reserve(self, project, product, units, day, *, tier, route, verified=False, authorized=False):
        if tier != 'standard' or route != 'google_mcp' or verified is not True or authorized is not True:
            return False
        if not isinstance(project, str) or not project.strip() or product not in PRODUCTS:
            return False
        if type(units) is not int or units <= 0 or not aware(day):
            return False
        key = (project, product, day.astimezone(timezone.utc).date())
        with self.lock:
            total = self.used.get(key, 0) + units
            if total > self.cap:
                return False
            self.used[key] = total
            return True
