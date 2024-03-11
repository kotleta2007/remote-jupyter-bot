DOCKER_PORT = 8888
HOST_PORT = 8888
WORKDIR = '/home/jovyan/'
IMAGE = 'quay.io/jupyter/pytorch-notebook'
LOCALDIR = '/home/mark/python'
CIDFILE = '/tmp/running_jupyters'

docker_command = [
    'docker',
    'run',
    '--user', 'root',
    '-p', f'{HOST_PORT}:{DOCKER_PORT}',
    f'--cidfile={CIDFILE}',
    '-e', 'CHOWN_HOME=yes',
    '-e', "CHOWN_HOME_OPTS='-R'",
    '-v', f'{LOCALDIR}/{IMAGE}:{WORKDIR}',
    '-w', f'{WORKDIR}',
    f'{IMAGE}'
]

def docker_kill_command(pid):
    cmd = [
        'docker',
        'kill',
        f'{pid}'
    ]
    return cmd

if __name__ == "__main__":
    print('The docker command is:')
    print(' '.join(docker_command))
