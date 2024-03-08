DOCKER_PORT = 8888
HOST_PORT = 8888
WORKDIR = '/usr/src/jupyter'
IMAGE = 'quay.io/jupyter/pytorch-notebook'
LOCALDIR = '/home/mark/python'
CIDFILE = '/tmp/running_jupyters'

docker_command = [
    'docker',
    'run',
    f'--cidfile={CIDFILE}',
    '-p', f'{HOST_PORT}:{DOCKER_PORT}',
    '-v', f'{LOCALDIR}/{IMAGE}:{WORKDIR}/{IMAGE}',
    '--user', 'root',
    '-w', f'{WORKDIR}/{IMAGE}', f'{IMAGE}'
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
    print(docker_command)
