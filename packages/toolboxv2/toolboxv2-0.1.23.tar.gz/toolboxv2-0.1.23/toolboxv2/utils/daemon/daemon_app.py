from ..singelton_class import Singleton
from ..toolbox import App
from .daemon_util import DaemonUtil


class DaemonApp(DaemonUtil, metaclass=Singleton):
    def __init__(self, app: App, host='0.0.0.0', port=6587, t=False):
        super().__init__(class_instance=app, host=host, port=port, t=t, app=app)
