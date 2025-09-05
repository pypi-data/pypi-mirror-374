from dataclasses import dataclass
from pathlib import Path
from subprocess import run


from config import Config, ConfigBuild, ConfigServer

IMAGE_NAME = "typeslide-server:latest"
REMOTE_USER = "root"
REMOTE_HOST = "5.161.248.115"
SOCKET_NAME = "tunnel"

BASE_DIR = Path(__file__).resolve().parent

#####################################################################
# Docker
#####################################################################


def build_docker_image(stack_name: str, service: str, entry: ConfigBuild):
    print("Building docker image", service)

    tags = []
    for tag in entry.tags:
        tags.extend(["-t", tag])

    args = [
        "docker",
        "build",
        "-t",
        f"localhost:5000/{stack_name}_{service}",
        *tags,
        str(entry.root),
    ]

    res = shell(args)
    if res.returncode != 0:
        print("Failed to build docker image", service)
        return False

    return True


def push_docker_image():
    p("push Docker image to host")
    run(["docker", "push", f"localhost:5000/{IMAGE_NAME}"], check=True)


def copy_compose_to_host():
    p("copy docker-compose.yml, postgres.conf, .env to host")
    ssh("mkdir -p /stack")
    run(
        [
            "scp",
            str(BASE_DIR / "server" / "docker-compose.yml"),
            str(BASE_DIR / "server" / "postgres.conf"),
            str(BASE_DIR / "server" / ".env"),
            f"{REMOTE_USER}@{REMOTE_HOST}:/stack",
        ]
    )


def pull_and_start_stack():
    p("pull and start stack on host")
    ssh("cd /stack;docker compose -f docker-compose.yml up -d --pull always")
    ssh("docker image prune -f")


#####################################################################
# Registry
#####################################################################


def start_registry_on_host(config: Config) -> bool:
    stop_registry_on_host(config, check=False)
    print("start registry on remote host", config.server.ip)
    res = ssh(
        config.server,
        "docker run -d -p 5000:5000 --name registry -v /mnt/docker_registry:/var/lib/registry registry:2",
    )
    if res.returncode != 0:
        print("Failed to start registry", res.stderr)
        return False
    return True


def stop_registry_on_host(config: Config, *, check=True) -> bool:
    print("stop registry on remote host", config.server.ip)
    res = ssh(config.server, "docker stop registry; docker rm registry")
    if check and res.returncode != 0:
        print("Failed to stop registry", res.stderr)
        return False
    return True


#####################################################################
# SSH
#####################################################################


def create_ssh_tunnel():
    p("create SSH tunnel")
    run(
        [
            "ssh",
            "-M",
            "-S",
            SOCKET_NAME,
            "-fnNT",
            "-L",
            f"5000:{REMOTE_HOST}:5000",
            f"{REMOTE_USER}@{REMOTE_HOST}",
        ],
        check=True,
    )


def stop_ssh_tunnel(check=True):
    p("stop SSH tunnel")
    run(
        ["ssh", "-S", SOCKET_NAME, "-O", "exit", f"{REMOTE_USER}@{REMOTE_HOST}"],
        check=check,
    )


#####################################################################
# apt
#####################################################################


def install_apt_packages(server: ConfigServer) -> bool:
    apt_updated_executed = False
    for package in server.apt:
        print("Checking apt package", package, "...")
        res = ssh(server, f"dpkg -s {package}")
        if res.returncode != 0:
            print("Installing apt package", package, "...")
            if not apt_updated_executed:
                print("Updating apt...")
                res = ssh(server, "apt-get update")
                if res.returncode != 0:
                    print("Failed to update apt", res.stderr)
                    return False
                apt_updated_executed = True
            res = ssh(server, f"apt-get install -y {package}")
            if res.returncode != 0:
                print("Failed to install apt package", package, res.stderr)
                return False

    return True


#####################################################################
# utils
#####################################################################


def p(msg: str):
    print("*" * 80)
    print(str(msg))
    print("*" * 80)


@dataclass
class RunHostResult:
    stdout: str
    stderr: str
    returncode: int


def ssh(server: ConfigServer, cmd: str, check=True, *args, **kwargs):
    run_args = ["ssh", f"{server.user}@{server.ip}", cmd]
    return shell(run_args)


def shell(command: list[str], *args, **kwargs):
    cp = run(command, check=False, capture_output=True, text=True, *args, **kwargs)
    return RunHostResult(cp.stdout, cp.stderr, cp.returncode)


def process(config: Config):
    return_code = 0

    for service, entry in config.build.items():
        if not build_docker_image(config.stack.name, service, entry):
            return -1

    if not install_apt_packages(config.server):
        return -1

    try:
        if not start_registry_on_host(config):
            return -1
        # create_ssh_tunnel(config)
        # push_docker_image(config)
        #     copy_compose_to_host()
        #     pull_and_start_stack()
        pass
    finally:
        if not stop_registry_on_host(config):
            return_code = -1
        # stop_ssh_tunnel(config)

    return return_code
