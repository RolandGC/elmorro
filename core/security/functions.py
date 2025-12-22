import socket
from core.security.models import Dashboard
from datetime import datetime


def system_information(request):
    try:
        hostname = socket.gethostname()
        localhost = socket.gethostbyname(hostname)
    except socket.gaierror:
        hostname = 'localhost'
        localhost = '127.0.0.1'

    data = {
        'dshboard': get_dashboard(),
        'hostname': hostname,
        'menu': get_layout(),
        'localhost': localhost,
        'date_joined': datetime.now(),
    }
    return data


def get_dashboard():
    try:
        items = Dashboard.objects.all()
        if items.exists():
            return items[0]
    except:
        pass
    return None


def get_layout():
    objs = Dashboard.objects.filter()
    if objs.exists():
        objs = objs[0]
        if objs.layout == 1:
            return 'vtcbody.html'
        return 'hztbody.html'
    return 'hztbody.html'
