import sys
import os

# Sử dụng Python từ venv hoặc system
INTERP = "/usr/bin/python3"
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Thêm đường dẫn project
sys.path.insert(0, '/home/ipshield6949/domains/ipshield.vn/public_html')

# Set Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'ipshieldproject.settings'

# Import WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
