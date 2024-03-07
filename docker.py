DOCKER_PORT = 8888
HOST_PORT   = 8888
WORKDIR = '/usr/src/jupyter'
IMAGE = 'quay.io/jupyter/pytorch-notebook'
LOCALDIR = '~/python'
CIDFILE = '/tmp/running_jupyters'

docker_command = [
    'docker',
    'run',
    f'--cidfile={CIDFILE}',
    f'-p {HOST_PORT}:{DOCKER_PORT}',
    f'-v {LOCALDIR}/{IMAGE}:{WORKDIR}/{IMAGE}',
    f'-w {WORKDIR}/{IMAGE} {IMAGE}'
]

if __name__ == "__main__":
    print('The docker command is:')
    print(docker_command)
