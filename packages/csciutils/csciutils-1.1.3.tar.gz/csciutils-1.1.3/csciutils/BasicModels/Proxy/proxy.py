def set_proxies(server_ip:str = None,
                server_port:int = None):
    if server_ip is not None and server_port is not None:
        proxies = {
            'http': f'{server_ip}:{server_port}',
            'https': f'{server_ip}:{server_port}',
        }
    else:
        proxies = {}
    return proxies