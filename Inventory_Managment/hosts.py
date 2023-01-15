from django.conf import settings
from django_hosts import patterns, host
host_patterns = patterns(
    '',
    host(r'', 'Inventory_Managment.urls', name='www'),
)