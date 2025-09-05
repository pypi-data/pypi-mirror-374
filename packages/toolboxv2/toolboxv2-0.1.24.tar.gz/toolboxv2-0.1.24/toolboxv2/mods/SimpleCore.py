# toolboxv2/mods/SimpleCore.py

import json
import time
import uuid

from toolboxv2 import App, MainTool, RequestData, Result, get_app

# -- Constants ---
MOD_NAME = "SimpleCore"
VERSION = "1.0.0"

# -- Module Export ---
export = get_app(f"mods.{MOD_NAME}").tb

# --- Database Keys ---
DB_ELEMENTS_KEY = "sc_dw_elements"

# --- DataManager Class ---
class DataManager:
    def __init__(self, app: App):
        self.app = app
        self.db = app.get_mod("DB")
        if not self.db:
            self.app.logger.error("DB module not found!")
            raise ConnectionError("Database module 'DB' not found or failed to load.")

    def _initialize_storage_key(self, key: str):
        """Creates an empty list for a given key if it doesn't exist."""
        if not self.db.if_exist(key).get():
            # Storing as a JSON string of an empty list
            self.db.set(key, json.dumps([]))
            self.app.logger.info(f"Initialized empty storage for key: {key}")

    def on_start(self):
        self.app.logger.info("Initializing SimpleCore DataManager schema...")
        try:
            self._initialize_storage_key(DB_ELEMENTS_KEY)
            self.app.logger.info("SimpleCore DataManager schema check/initialization complete.")
        except Exception as e:
            self.app.logger.error(f"Failed to initialize SimpleCore DataManager schema: {e}", exc_info=True)

    def add_idea(self, user_id: str, content: str) -> Result:
        """Adds a new idea element to the database."""
        try:
            elements_json = self.db.get(DB_ELEMENTS_KEY).get()
            elements = json.loads(elements_json) if elements_json else []

            new_idea = {
                "element_id": str(uuid.uuid4()),
                "user_id": user_id,
                "content": content,
                "type": "idea",
                "created_at": time.time(),
                "updated_at": time.time(),
                "version": 1,
                "parent_id": None,
                "workspace_id": None # Or a default workspace
            }

            elements.append(new_idea)
            self.db.set(DB_ELEMENTS_KEY, json.dumps(elements))
            self.app.logger.info(f"New idea added for user {user_id}")
            return Result.ok(data=new_idea)
        except Exception as e:
            self.app.logger.error(f"Failed to add idea: {e}", exc_info=True)
            return Result.default_internal_error(f"Could not save idea: {e}")


# -- Main Logic Class (Recommended) ---
class Tools(MainTool):
    def __init__(self, app: App):
        self.name = MOD_NAME
        self.version = VERSION
        self.data_manager = DataManager(app)
        self.tools = {
            "all": [["show_version", "Displays the module version"]],
            "name": self.name,
            "show_version": self.show_version,
        }
        super().__init__(
            load=self.on_start,
            v=self.version,
            tool=self.tools,
            name=self.name,
            on_exit=self.on_exit
        )

    def on_start(self):
        """Called when the module is loaded."""
        self.app.logger.info(f"{self.name} v{self.version} initialized.")
        self.data_manager.on_start()
        self.app.run_any(("CloudM", "add_ui"),
                         name=self.name,
                         title=self.name,
                         path=f"/api/{self.name}/ui",
                         description="SimpleCore Idea Workbench.",
                         auth=True
                         )

    def on_exit(self):
        """Called when the application is shutting down."""
        self.app.logger.info(f"Closing {self.name}. Goodbye!")

    def show_version(self):
        return self.version

# -- API Endpoints & Functions ---

@export(mod_name=MOD_NAME, name="ui", api=True, api_methods=["GET"])
async def get_main_ui(self) -> Result:
    """Serves the main HTML UI for the module."""
    # 'self' is the Tools instance
    with open("toolboxv2/web/pages/simplecore/index.html") as f:
        return Result.html(data=f.read())

@export(mod_name=MOD_NAME, name="create_idea", api=True, api_methods=["POST"], request_as_kwarg=True)
async def create_idea(self, request: RequestData) -> Result:
    """Creates and saves a new idea."""
    # 'self' is the Tools instance
    form_data = request.form_data
    idea_content = form_data.get("content")

    if not idea_content:
        return Result.text("<span style='color: red;'>Idea content cannot be empty.</span>")

    # Get user from request
    user = await self.app.a_run_any(("WidgetsProvider", "get_user_from_request"), request=request)
    if not user:
        return Result.default_user_error("Authentication required.")

    # Save the idea using the DataManager
    result = self.data_manager.add_idea(user_id=user.id, content=idea_content)

    if result.is_ok():
        return Result.text("<span>Idea captured successfully!</span>")
    else:
        return Result.text(f"<span style='color: red;'>Error: {result.info}</span>")
