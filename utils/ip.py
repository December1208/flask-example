def _get_client_ip(x_forwarded_for, remote_addr):
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = remote_addr
    if ip and ':' in ip:  # IPV6
        ip = '127.0.0.1'  
    return ip


def get_ip_by_req(request):
    headers = request.headers
    real_ip = headers.get('Ali-CDN-Real-IP') or headers.get('HTTP_X_REAL_IP')
    if real_ip:
        return real_ip
    x_forwarded_for = headers.get('X-Forwarded-For')
    remote_addr = headers.get('REMOTE_ADDR')
    return _get_client_ip(x_forwarded_for, remote_addr)