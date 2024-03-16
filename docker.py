import re

DOCKER_PORT = 8888
HOST_PORT = 60000 # 60000-61000 are available (used by mosh, but we don't use mosh)
WORKDIR = '/home/jovyan/'
# IMAGE = 'quay.io/jupyter/pytorch-notebook'
IMAGE = 'jupyter-tinygrad'
LOCALDIR = '/home/mark/python/'
CIDFILE = '/tmp/docker_cid'

def run(HOST_PORT=60000, 
        notebook_name='notebook', 
        IMAGE=IMAGE
    ):
    cmd = [
        'docker',
        'run',
        '-p', f'{HOST_PORT}:{DOCKER_PORT}',
        f'--cidfile={CIDFILE}',
        '-e', 'CHOWN_HOME=yes',
        '-e', "CHOWN_HOME_OPTS='-R'",
        # necessary for initializing new host folder
        # can be omitted for further accesses to LOCALDIR
        '--user', 'root', 
        '-v', f'{LOCALDIR}/{IMAGE}/{notebook_name}:{WORKDIR}',
        '-w', f'{WORKDIR}',
        f'{IMAGE}'
    ]
    return cmd

def docker_kill_command(pid):
    cmd = [
        'docker',
        'kill',
        f'{pid}'
    ]
    return cmd

def get_token(url):
    pattern = '^.*token=([0-9a-f]*)$'
    m = re.match(pattern, url)
    return m.group(1)

if __name__ == "__main__":
    print('The docker command is:')
    print(' '.join(run()))
