from .AdminDashboard import Name as AdminDashboard
from .extras import login
from .mini import *
from .ModManager_tests import run_mod_manager_tests
from .module import Tools
from .types import User
from .UI.widget import get_widget
from .UserAccountManager import Name as UserAccountManagerName
from .UserDashboard import Name as UserDashboardName
from .UserInstances import UserInstances

tools = Tools
Name = 'CloudM'
version = Tools.version
__all__ = ["mini"]
