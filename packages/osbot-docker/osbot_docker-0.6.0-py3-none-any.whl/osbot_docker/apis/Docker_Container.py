from docker.errors                       import NotFound
from docker.models.containers import Container
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.type_safe.Type_Safe     import Type_Safe
from osbot_docker.apis.API_Docker        import API_Docker
from osbot_utils.utils.Misc              import date_time_from_to_str, wait_for


class Docker_Container(Type_Safe):
    api_docker    : API_Docker
    container_id  : str        = None
    #container_raw : Container  = None                              # todo: see if we shouldn't rename this var to just 'container'

    # def __init__(self, container_id, container_raw=None, **kwargs):                     # todo: refactor this to be more inline with how Type_Safe works
    #     self.container_id  = container_id
    #     self.container_raw = container_raw                                              # initial docker_api container_raw data
    #     super().__init__(**kwargs)

    def __repr__(self):
        return f"<Docker_Container: {self.short_id()}>"

    def client_api(self):
        return self.api_docker.client_api()

    def client_docker(self):
        return self.api_docker.client_docker()

    @cache_on_self
    def container(self):
        return self.client_docker().containers.get(self.container_id)

    def delete(self):
        if self.exists():
            if self.status() != 'running':
                self.client_api().remove_container(self.container_id)
                return True
        return False

    def exists(self):
        return self.info_raw() != {}

    def exec(self, command, workdir=None):
        """Executes a command inside a running Docker container."""
        exec_instance   = self.client_api().exec_create(self.container_id, cmd=command, workdir=workdir)
        result          = self.client_api().exec_start(exec_instance['Id'])
        return result.decode('utf-8')

    def image(self):                             # todo see what are the performance implications of using info here (which make a full rest call to get the data)
        return self.info().get('image')

    def info(self):
        info_raw = self.info_raw()
        return self.info_raw_parse(info_raw)

    def info_raw(self):
        try:
            return self.container().attrs
        except NotFound:
            return {}


    def info_raw_parse(self, info_raw):
        if info_raw is None or  info_raw == {}:
            return {}
        config      = info_raw.get('Config'         )
        created_raw = info_raw.get('Created'        )[:26] + 'Z'       # need to remove the micro seconds
        created     = date_time_from_to_str(created_raw, '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%d %H:%M', True)
        network     = info_raw.get('NetworkSettings')
        state       = info_raw.get('State'          )

        return dict(args        = info_raw.get('Args'         ),
                    created     = created                           ,
                    entrypoint  = config       .get('Entrypoint'   ),
                    env         = config       .get('Env'          ),
                    id          = info_raw.get('Id'           ),
                    id_short    = info_raw.get('Id'      )[:12],
                    image       = config       .get('Image'        ),
                    labels      = config       .get('Labels'       ),
                    name        = info_raw.get('Name'         ),
                    ports       = network      .get('Ports'        ),
                    status      = state        .get('Status'       ),
                    volumes     = config       .get('Volumes'      ),
                    working_dir = config       .get('WorkingDir'   ))

    def labels(self):
        return self.info().get('labels') or {}

    def logs(self):
        if self.exists():
            logs = self.client_api().logs(self.container_id)
            if logs:
                return logs.decode('utf-8')
        return ''

    def name(self):
        return self.container().name

    def start(self, wait_for_running=True):
        self.client_api().start(container=self.container_id)
        if wait_for_running:
            return self.wait_for_container_status('running')
        return True

    def short_id(self):
        return self.container_id[:12]

    def stop(self, wait_for_exit=True, timeout=0):
        if self.status() != 'running':
            return False
        self.client_api().stop(container=self.container_id, timeout=timeout)
        if wait_for_exit:
            self.wait_for_container_status('exited')
        return True

    def status(self):
        return self.info().get('status') or 'not found'

    def wait_for_container_status(self, desired_status, wait_delta=.2, wait_count=10):
        while wait_count > 0:
            container_status = self.status()
            #print(f'{wait_count}: {self.container_id} : {container_status}')
            if container_status is None:
                return False
            if container_status == desired_status:
                return True                                 # Container has reached the desired status
            wait_for(wait_delta)
            wait_count-=1
        return False

    def wait_for_logs(self, max_attempts=20, delay_interval=0.1):
        for i in range(0,max_attempts):
            if self.logs() != "":
                return True
            wait_for(delay_interval)
        return False