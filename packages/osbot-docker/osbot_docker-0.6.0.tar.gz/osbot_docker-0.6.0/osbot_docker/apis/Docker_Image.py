from docker.errors                          import APIError
from osbot_utils.type_safe.Type_Safe        import Type_Safe
from osbot_docker.apis.Docker_Container     import Docker_Container
from osbot_utils.decorators.methods.catch   import catch
from osbot_docker.apis.API_Docker           import API_Docker

class Docker_Image(Type_Safe):
    api_docker : API_Docker
    image_id   : str
    image_name : str = None
    image_tag  = str = None

    def __init__(self, image_name, image_tag='latest', image_id = None, **kwargs):                  # todo: refactor this to be more inline with how Type_Safe works
        self.image_id   = image_id or ''
        self.image_name = image_name
        self.image_tag  = image_tag
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.image_name}:{self.image_tag} {self.short_id()}"

    def architecture(self):
        return self.info().get('Architecture')

    def client_api(self):
        return self.api_docker.client_api()

    def client_docker(self):
        return self.api_docker.client_docker()

    def create_container(self, command='', volumes=None, tty=False, port_bindings=None, labels=None, name=None, **kwargs    ):
        """Creates a Docker container and returns its ID."""
        exposed_ports = None
        if port_bindings:
            exposed_ports = list(port_bindings.keys())
        image           = self.image_name_with_tag()
        host_config     = self.client_api().create_host_config(binds=volumes, port_bindings=port_bindings)
        create_result   = self.client_api().create_container(image=image, command=command, host_config=host_config, tty=tty, ports=exposed_ports, labels=labels, name=name, **kwargs)
        container_id    = create_result.get('Id')
        container       = Docker_Container(container_id=container_id, api_docker=self.api_docker)
        return container

    # todo: add solution that supports streaming of docker file creation, this version will only return when the docker build execute completes
    @catch
    def build(self, path):
        image_name = self.image_name_with_tag()
        (result,build_logs) = self.client_docker().images.build(path=path, tag=image_name)
        return {'status': 'ok', 'image': result.attrs, 'tags':result.tags, 'build_logs': build_logs }

    def delete(self):
        if self.exists():
            image = self.image_name_with_tag()
            self.client_docker().images.remove(image=image)
            return self.exists() is False
        return False

    def exists(self):
        return self.info() != {}

    def info(self):
        try:
            image  = self.image_name_with_tag()
            result = self.client_docker().images.get(image)
            return self.format_image(result)
        except APIError:
            return {}

    def image_name_with_tag(self):
        if self.image_tag:
            return f"{self.image_name}:{self.image_tag}"
        return self.image_name

    def format_image(self, target):
        data = target.attrs
        data['Labels' ] = target.labels
        data['ShortId'] = target.short_id
        data['Tags'   ] = target.tags
        return data

    def name(self):
        return self.image_name

    def pull(self):
        self.client_docker().images.pull(self.image_name, self.image_tag)
        return self.exists()

    def image_push(self):
        # note if the there is a ~/.docker/config.json file, any ecr login into client_docker will not be taken into account (at the moment looks like the solution is to delete this file)
        # see https://github.com/docker/docker-py/issues/2256#issuecomment-553496988
        client_docker = self.client_docker()
        return client_docker.images.push(self.image_name, self.image_tag)


    def short_id(self):
        return self.image_id[:12]




