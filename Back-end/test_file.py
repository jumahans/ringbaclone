import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from reports.services.resporg import extract_phone_from_url
result = extract_phone_from_url('https://learnbrainhub-b0h3ccg0bge0cbf3.z03.azurefd.net/winvrs.html')
print('RESULT:', repr(result))