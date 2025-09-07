import asyncio
import logging
from typing import Dict, List, Any, Optional
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Button, Input, Label, Static, DataTable, LoadingIndicator, ProgressBar
from textual.widget import Widget
from textual.message import Message
from textual.reactive import reactive

from ..api.ollama import OllamaClient
from ..config import CONFIG

# Set up logging
logger = logging.getLogger(__name__)

class ModelBrowser(Container):
    """Widget for browsing and downloading Ollama models"""
    
    DEFAULT_CSS = """
    ModelBrowser {
        width: 100%;
        height: 100%;
        background: $surface;
        padding: 1;
    }
    
    #browser-header {
        width: 100%;
        height: 3;
        layout: horizontal;
        margin-bottom: 1;
    }
    
    #browser-title {
        width: 1fr;
        height: 3;
        content-align: center middle;
        text-align: center;
        color: $text;
        background: $primary-darken-2;
    }
    
    #close-button {
        width: 10;
        height: 3;
        margin-left: 1;
    }
    
    #search-container {
        width: 100%;
        height: 3;
        layout: horizontal;
        margin-bottom: 1;
    }
    
    #model-search {
        width: 1fr;
        height: 3;
    }
    
    #search-button {
        width: 10;
        height: 3;
        margin-left: 1;
    }
    
    #refresh-button {
        width: 10;
        height: 3;
        margin-left: 1;
    }
    
    #tabs-container {
        width: 100%;
        height: 3;
        layout: horizontal;
        margin-bottom: 1;
    }
    
    .tab-button {
        height: 3;
        min-width: 15;
        background: $primary-darken-3;
    }
    
    .tab-button.active {
        background: $primary;
    }
    
    #models-container {
        width: 100%;
        height: 1fr;
    }
    
    #local-models, #available-models {
        width: 100%;
        height: 100%;
        display: none;
    }
    
    #local-models.active, #available-models.active {
        display: block;
    }
    
    DataTable {
        width: 100%;
        height: 1fr;
        min-height: 10;
    }
    
    #model-actions {
        width: 100%;
        height: auto;
        margin-top: 1;
    }
    
    #model-details {
        width: 100%;
        height: auto;
        display: none;
        border: solid $primary;
        padding: 1;
        margin-top: 1;
    }
    
    #model-details.visible {
        display: block;
    }
    
    #progress-area {
        width: 100%;
        height: auto;
        display: none;
        margin-top: 1;
        border: solid $primary;
        padding: 1;
    }
    
    #progress-area.visible {
        display: block;
    }
    
    #progress-bar {
        width: 100%;
        height: 1;
    }
    
    #progress-label {
        width: 100%;
        height: 1;
        content-align: center middle;
        text-align: center;
    }
    
    #status-label {
        width: 100%;
        height: 2;
        content-align: center middle;
        text-align: center;
    }
    
    #action-buttons {
        layout: horizontal;
        width: 100%;
        height: auto;
        align: center middle;
    }
    
    #action-buttons Button {
        margin: 0 1;
    }
    
    LoadingIndicator {
        width: 100%;
        height: 1fr;
    }
    """
    
    # Reactive variables to track state
    selected_model_id = reactive("")
    current_tab = reactive("local")  # "local" or "available"
    is_loading = reactive(False)
    is_pulling = reactive(False)
    pull_progress = reactive(0.0)
    pull_status = reactive("")
    
    def __init__(
        self, 
        name: Optional[str] = None,
        id: Optional[str] = None
    ):
        super().__init__(name=name, id=id)
        self.ollama_client = OllamaClient()
        self.local_models = []
        self.available_models = []
    
    def compose(self) -> ComposeResult:
        """Set up the model browser"""
        # Title and close button
        with Container(id="browser-header"):
            yield Static("Ollama Model Browser", id="browser-title")
            yield Button("Close", id="close-button", variant="error")
        
        # Search bar
        with Container(id="search-container"):
            yield Input(placeholder="Search models...", id="model-search")
            yield Button("Search", id="search-button")
            yield Button("Refresh", id="refresh-button")
        
        # Tabs
        with Container(id="tabs-container"):
            yield Button("Local Models", id="local-tab", classes="tab-button active")
            yield Button("Available Models", id="available-tab", classes="tab-button")
        
        # Models container (will hold both tabs)
        with Container(id="models-container"):
            # Local models tab
            with ScrollableContainer(id="local-models", classes="active"):
                yield DataTable(id="local-models-table")
                with Container(id="model-actions"):
                    with Horizontal(id="action-buttons"):
                        yield Button("Run Model", id="run-button", variant="success")
                        yield Button("Delete Model", id="delete-button", variant="error")
                        yield Button("View Details", id="details-button", variant="default")
            
            # Available models tab
            with ScrollableContainer(id="available-models"):
                yield DataTable(id="available-models-table")
                with Container(id="model-actions"):
                    with Horizontal(id="action-buttons"):
                        yield Button("Pull Model", id="pull-available-button", variant="primary")
                        yield Button("View Details", id="details-available-button", variant="default")
        
        # Model details area (hidden by default)
        with ScrollableContainer(id="model-details"):
            yield Static("No model selected", id="details-content")
        
        # Progress area for model downloads (hidden by default)
        with Container(id="progress-area"):
            yield Static("Downloading model...", id="status-label")
            yield ProgressBar(id="progress-bar", total=100)
            yield Static("0%", id="progress-label")
    
    async def on_mount(self) -> None:
        """Initialize model tables after mount"""
        # Set up local models table
        local_table = self.query_one("#local-models-table", DataTable)
        local_table.add_columns("Model", "Size", "Family", "Modified")
        local_table.cursor_type = "row"
        
        # Set up available models table
        available_table = self.query_one("#available-models-table", DataTable)
        available_table.add_columns("Model", "Size", "Family", "Description")
        available_table.cursor_type = "row"
        
        # Show notification about model loading
        self.notify("Initializing model browser, this might take a moment on first run...", 
                   severity="information", timeout=5)
        
        # Load models
        await self.load_local_models()
        
        # Start loading available models in the background
        asyncio.create_task(self.preload_available_models())
        
        # Focus search input
        self.query_one("#model-search").focus()
        
    async def preload_available_models(self) -> None:
        """Preload available models in the background"""
        # Load the available models list in the background to make it faster when
        # the user switches to the Available Models tab
        try:
            # This will trigger cache creation if needed, making tab switching faster
            models = await self.ollama_client.list_available_models_from_registry()
            if models:
                logger.info(f"Preloaded {len(models)} available models")
        except Exception as e:
            logger.error(f"Error preloading available models: {str(e)}")
    
    async def load_local_models(self) -> None:
        """Load locally installed Ollama models"""
        self.is_loading = True
        
        try:
            self.local_models = await self.ollama_client.get_available_models()
            
            # Clear and populate table
            local_table = self.query_one("#local-models-table", DataTable)
            local_table.clear()
            
            for model in self.local_models:
                # Try to get additional details
                try:
                    details = await self.ollama_client.get_model_details(model["id"])
                    
                    # Extract parameter size info (in billions)
                    size = "Unknown"
                    
                    # First try to get parameter size from modelfile if available
                    if "modelfile" in details and details["modelfile"] is not None:
                        modelfile = details["modelfile"]
                        if "parameter_size" in modelfile and modelfile["parameter_size"]:
                            size = str(modelfile["parameter_size"])
                            # Make sure it ends with B for billions if it doesn't already
                            if not size.upper().endswith("B"):
                                size += "B"
                    
                    # If not found in modelfile, try to extract from name
                    if size == "Unknown":
                        name = model["name"].lower()
                        if "70b" in name:
                            size = "70B"
                        elif "405b" in name or "400b" in name:
                            size = "405B"
                        elif "34b" in name or "35b" in name:
                            size = "34B"
                        elif "27b" in name or "28b" in name:
                            size = "27B"
                        elif "13b" in name or "14b" in name:
                            size = "13B"
                        elif "8b" in name:
                            size = "8B"
                        elif "7b" in name:
                            size = "7B"
                        elif "6b" in name:
                            size = "6B"
                        elif "3b" in name:
                            size = "3B"
                        elif "2b" in name:
                            size = "2B"
                        elif "1b" in name:
                            size = "1B"
                        elif "mini" in name:
                            size = "3B"
                        elif "small" in name:
                            size = "7B"
                        elif "medium" in name:
                            size = "13B"
                        elif "large" in name:
                            size = "34B"
                        
                        # Special handling for base models with no size indicator
                        if size == "Unknown":
                            # Remove tag part if present to get base model
                            base_name = name.split(":")[0]
                            
                            # Check if we have default parameter sizes for known models
                            model_defaults = {
                                "llama3": "8B",
                                "llama2": "7B",
                                "mistral": "7B",
                                "gemma": "7B",
                                "gemma2": "9B",
                                "phi": "3B",
                                "phi2": "3B",
                                "phi3": "3B",
                                "orca-mini": "7B",
                                "llava": "7B",
                                "codellama": "7B",
                                "neural-chat": "7B",
                                "wizard-math": "7B",
                                "yi": "6B",
                                "deepseek": "7B",
                                "deepseek-coder": "7B",
                                "qwen": "7B",
                                "falcon": "7B",
                                "stable-code": "3B"
                            }
                            
                            # Try to find a match in default sizes
                            for model_name, default_size in model_defaults.items():
                                if model_name in base_name:
                                    size = default_size
                                    break
                    
                    # Extract family info - check multiple possible locations
                    family = "Unknown"
                    if "modelfile" in details and details["modelfile"] is not None:
                        # First check for family field
                        if "family" in details["modelfile"] and details["modelfile"]["family"]:
                            family = details["modelfile"]["family"]
                        # Try to infer from model name if not available
                        else:
                            name = model["name"].lower()
                            if "llama" in name:
                                family = "Llama"
                            elif "mistral" in name:
                                family = "Mistral"
                            elif "phi" in name:
                                family = "Phi"
                            elif "gemma" in name:
                                family = "Gemma"
                            elif "yi" in name:
                                family = "Yi"
                            elif "orca" in name:
                                family = "Orca"
                            elif "wizard" in name:
                                family = "Wizard"
                            elif "neural" in name:
                                family = "Neural Chat"
                            elif "qwen" in name:
                                family = "Qwen"
                            elif "deepseek" in name:
                                family = "DeepSeek"
                            elif "falcon" in name:
                                family = "Falcon"
                            elif "stable" in name:
                                family = "Stable"
                            elif "codellama" in name:
                                family = "CodeLlama"
                            elif "llava" in name:
                                family = "LLaVA"
                    
                    # Extract modified date
                    modified = details.get("modified_at", "Unknown")
                    if modified == "Unknown" and "created_at" in details:
                        modified = details["created_at"]
                        
                except Exception as detail_error:
                    self.notify(f"Error getting details for {model['name']}: {str(detail_error)}", severity="warning")
                    size = "Unknown"
                    family = "Unknown"
                    modified = "Unknown"
                
                local_table.add_row(model["name"], size, family, modified)
            
            self.notify(f"Loaded {len(self.local_models)} local models", severity="information")
            
        except Exception as e:
            self.notify(f"Error loading local models: {str(e)}", severity="error")
        finally:
            self.is_loading = False
    
    async def load_available_models(self, force_refresh: bool = False) -> None:
        """Load available models from Ollama registry"""
        self.is_loading = True
        
        try:
            # Get search query if any
            search_input = self.query_one("#model-search", Input)
            query = search_input.value.strip()
            
            # Debug to track model loading
            logger.info(f"Loading available models, query: '{query}', force_refresh: {force_refresh}")
            
            # Load models from registry - don't apply the query here, get ALL models
            try:
                # First try the API-based registry
                self.available_models = await self.ollama_client.list_available_models_from_registry("", force_refresh=force_refresh)
                logger.info(f"Got {len(self.available_models)} models from registry")
                
                # If no models found, use the curated list
                if not self.available_models:
                    self.available_models = await self.ollama_client.get_registry_models("")
                    logger.info(f"Got {len(self.available_models)} models from curated list")
            except Exception as e:
                logger.error(f"Error from registry API: {str(e)}")
                # Fallback to curated list
                self.available_models = await self.ollama_client.get_registry_models("")
                logger.info(f"Fallback: Got {len(self.available_models)} models from curated list")
            
            # Clear and populate table
            available_table = self.query_one("#available-models-table", DataTable)
            available_table.clear()
            
            # Get number of models loaded (but don't notify to avoid notification spam)
            model_count = len(self.available_models)
            logger.info(f"Found {model_count} models to display")
            
            # Filter models by search query if provided
            filtered_models = self.available_models
            if query:
                query = query.lower()
                filtered_models = []
                for model in self.available_models:
                    # Check if query matches name, description or family
                    name = str(model.get("name", "")).lower()
                    desc = str(model.get("description", "")).lower()
                    family = str(model.get("model_family", "")).lower()
                    
                    # Also check variants if available
                    variants_match = False
                    if "variants" in model and model["variants"]:
                        variants_text = " ".join([str(v).lower() for v in model["variants"]])
                        if query in variants_text:
                            variants_match = True
                    
                    if query in name or query in desc or query in family or variants_match:
                        filtered_models.append(model)
                
                logger.info(f"Filtered to {len(filtered_models)} models matching '{query}'")
            
            # Add all filtered models to the table - no pagination limit
            for model in filtered_models:
                name = model.get("name", "Unknown")
                
                # Extract parameter size info (in billions)
                size = "Unknown"
                
                # Check if parameter_size is available in the model metadata
                if "parameter_size" in model and model["parameter_size"]:
                    size = str(model["parameter_size"])
                    # Make sure it ends with B for billions if it doesn't already
                    if not size.upper().endswith("B"):
                        size += "B"
                # Check if we can extract from variants
                elif "variants" in model and model["variants"]:
                    for variant in model["variants"]:
                        if any(char.isdigit() for char in str(variant)):
                            # This looks like a size variant (e.g., "7b", "70b")
                            variant_str = str(variant).lower()
                            if variant_str.endswith('b'):
                                size = str(variant).upper()
                            else:
                                size = f"{variant}B"
                            break
                else:
                    # Extract from name if not available
                    model_name = str(name).lower()
                    if "70b" in model_name:
                        size = "70B"
                    elif "405b" in model_name or "400b" in model_name:
                        size = "405B"
                    elif "34b" in model_name or "35b" in model_name:
                        size = "34B"
                    elif "27b" in model_name or "28b" in model_name:
                        size = "27B"
                    elif "13b" in model_name or "14b" in model_name:
                        size = "13B"
                    elif "8b" in model_name:
                        size = "8B"
                    elif "7b" in model_name:
                        size = "7B"
                    elif "6b" in model_name:
                        size = "6B"
                    elif "3b" in model_name:
                        size = "3B"
                    elif "2b" in model_name:
                        size = "2B"
                    elif "1b" in model_name:
                        size = "1B"
                    elif "mini" in model_name:
                        size = "3B"
                    elif "small" in model_name:
                        size = "7B"
                    elif "medium" in model_name:
                        size = "13B"
                    elif "large" in model_name:
                        size = "34B"
                        
                    # Special handling for base models with no size indicator
                    if size == "Unknown":
                        # Remove tag part if present to get base model
                        base_name = model_name.split(":")[0]
                        
                        # Check if we have default parameter sizes for known models
                        model_defaults = {
                            "llama3": "8B",
                            "llama2": "7B",
                            "mistral": "7B",
                            "gemma": "7B",
                            "gemma2": "9B",
                            "phi": "3B",
                            "phi2": "3B",
                            "phi3": "3B",
                            "phi4": "7B",
                            "orca-mini": "7B",
                            "llava": "7B",
                            "codellama": "7B",
                            "neural-chat": "7B",
                            "wizard-math": "7B",
                            "yi": "6B",
                            "deepseek": "7B",
                            "deepseek-coder": "7B",
                            "qwen": "7B",
                            "falcon": "7B",
                            "stable-code": "3B"
                        }
                        
                        # Try to find a match in default sizes
                        for model_prefix, default_size in model_defaults.items():
                            if model_prefix in base_name:
                                size = default_size
                                break
                
                family = model.get("model_family", "Unknown")
                description = model.get("description", "No description available")
                
                # Keep this for debugging
                # logger.info(f"Adding model to table: {name} - {size} - {family}")
                
                available_table.add_row(name, size, family, description)
            
            actual_displayed = available_table.row_count
            logger.info(f"Loaded {actual_displayed} available models")
            
        except Exception as e:
            logger.error(f"Error loading available models: {str(e)}")
            self.notify(f"Error loading available models: {str(e)}", severity="error")
        finally:
            self.is_loading = False
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human-readable format"""
        if size_bytes == 0:
            return "Unknown"
        
        suffixes = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(suffixes) - 1:
            size_bytes /= 1024
            i += 1
        
        return f"{size_bytes:.2f} {suffixes[i]}"
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "close-button":
            # Close the model browser by popping the screen
            if hasattr(self.app, "pop_screen"):
                self.app.pop_screen()
            return
        elif button_id == "local-tab":
            self._switch_tab("local")
        elif button_id == "available-tab":
            self._switch_tab("available")
            # Load available models if they haven't been loaded yet
            if not self.available_models:
                self.app.call_later(self.load_available_models)
        elif button_id == "search-button":
            # Search in the current tab
            if self.current_tab == "local":
                self.app.call_later(self.load_local_models)
            else:
                self.app.call_later(self.load_available_models)
        elif button_id == "refresh-button":
            # Refresh current tab (force refresh for available models)
            if self.current_tab == "local":
                self.app.call_later(self.load_local_models)
            else:
                # Force refresh the cache when refresh button is clicked
                self.app.call_later(lambda: self.load_available_models(force_refresh=True))
        elif button_id == "run-button":
            # Set model in the main app
            self.app.call_later(self._run_selected_model)
        elif button_id == "pull-available-button":
            # Start model pull
            self.app.call_later(self._pull_selected_model)
        elif button_id == "delete-button":
            # Delete selected model
            self.app.call_later(self._delete_selected_model)
        elif button_id in ["details-button", "details-available-button"]:
            # Show model details
            self.app.call_later(self._show_model_details)
    
    def _switch_tab(self, tab: str) -> None:
        """Switch between local and available tabs"""
        self.current_tab = tab
        
        # Update tab buttons
        local_tab = self.query_one("#local-tab", Button)
        available_tab = self.query_one("#available-tab", Button)
        
        if tab == "local":
            local_tab.add_class("active")
            available_tab.remove_class("active")
        else:
            local_tab.remove_class("active")
            available_tab.add_class("active")
        
        # Update containers
        local_container = self.query_one("#local-models", ScrollableContainer)
        available_container = self.query_one("#available-models", ScrollableContainer)
        
        if tab == "local":
            local_container.add_class("active")
            available_container.remove_class("active")
        else:
            local_container.remove_class("active")
            available_container.add_class("active")
    
    async def _run_selected_model(self) -> None:
        """Set the selected model as the active model in the main app"""
        # Import debug_log function from main
        from app.main import debug_log
        
        debug_log(f"Entering _run_selected_model for tab {self.current_tab}")
        
        # Try several ways to get a valid model ID
        model_id = ""
        
        # First try the selected_model_id property
        if self.selected_model_id and self.selected_model_id.strip():
            debug_log(f"Using model_id from selected_model_id: {self.selected_model_id}")
            logger.info(f"Using model_id from selected_model_id: {self.selected_model_id}")
            model_id = self.selected_model_id
        
        # If that didn't work, try getting it through the getter method
        if not model_id:
            debug_log("Trying to get model_id from _get_selected_model_id method")
            logger.info("Trying to get model_id from _get_selected_model_id method")
            model_id = self._get_selected_model_id()
            debug_log(f"_get_selected_model_id returned: '{model_id}'")
            
        # As a last resort, if we're in local tab, try to just get the first model
        if not model_id and self.current_tab == "local":
            debug_log("Trying fallback to first local model")
            
            # Extra defensive check for local_models
            if not self.local_models:
                debug_log("local_models list is empty or None")
            else:
                debug_log(f"local_models has {len(self.local_models)} items")
                try:
                    # Check if the list is valid and not empty
                    if len(self.local_models) > 0:
                        first_model = self.local_models[0]
                        debug_log(f"First local model: {repr(first_model)}")
                        
                        # Very defensive checks
                        if first_model is None:
                            debug_log("First model is None")
                        elif not isinstance(first_model, dict):
                            debug_log(f"First model is not a dict: {type(first_model)}")
                        elif "id" not in first_model:
                            debug_log(f"First model has no 'id' key: {first_model}")
                        else:
                            model_id = first_model.get("id", "")
                            debug_log(f"Falling back to first model in list: {model_id}")
                            logger.info(f"Falling back to first model in list: {model_id}")
                    else:
                        debug_log("local_models list is empty")
                except Exception as e:
                    debug_log(f"Error getting first local model: {str(e)}")
                    logger.error(f"Error getting first local model: {str(e)}")
                
        # Or if we're in available tab, try to get name of first available model
        if not model_id and self.current_tab == "available":
            debug_log("Trying fallback to first available model")
            
            # Extra defensive check for available_models
            if not self.available_models:
                debug_log("available_models list is empty or None")
            else:
                debug_log(f"available_models has {len(self.available_models)} items")
                try:
                    # Check if the list is valid and not empty
                    if len(self.available_models) > 0:
                        first_model = self.available_models[0]
                        debug_log(f"First available model: {repr(first_model)}")
                        
                        # Very defensive checks
                        if first_model is None:
                            debug_log("First available model is None")
                        elif not isinstance(first_model, dict):
                            debug_log(f"First available model is not a dict: {type(first_model)}")
                        elif "name" not in first_model:
                            debug_log(f"First available model has no 'name' key: {first_model}")
                        else:
                            model_id = first_model.get("name", "")
                            debug_log(f"Falling back to first available model: {model_id}")
                            logger.info(f"Falling back to first available model: {model_id}")
                    else:
                        debug_log("available_models list is empty")
                except Exception as e:
                    debug_log(f"Error getting first available model: {str(e)}")
                    logger.error(f"Error getting first available model: {str(e)}")
        
        # Last resort - hardcoded fallback to a common model
        if not model_id:
            debug_log("All attempts to get model_id failed, checking if we should use default")
            # Only use default if we're in the available models tab, otherwise notify user
            if self.current_tab == "available":
                debug_log("Using 'llama3' as last-resort default")
                model_id = "llama3"
                self.notify("No model selected, using llama3 as default", severity="warning")
            else:
                debug_log("No model_id found and no default for local tab")
                self.notify("No model selected", severity="warning")
                return
            
        debug_log(f"Final model_id: {model_id}")
        logger.info(f"Setting model to: {model_id}")
        
        try:
            # Set the model in the app
            if hasattr(self.app, "selected_model"):
                debug_log("Setting model in the app")
                self.app.selected_model = model_id
                debug_log("Updating app info")
                self.app.update_app_info()  # Update app info to show new model
                debug_log("Model set successfully")
                self.notify(f"Model set to: {model_id}", severity="success")
                debug_log("Closing model browser screen")
                self.app.pop_screen()  # Close the model browser screen
            else:
                debug_log("app does not have selected_model attribute")
                self.notify("Cannot set model: app interface not available", severity="error")
        except Exception as e:
            debug_log(f"Error setting model: {str(e)}")
            logger.error(f"Error setting model: {str(e)}")
            self.notify(f"Error setting model: {str(e)}", severity="error")
            
    async def _pull_selected_model(self) -> None:
        """Pull the selected model from Ollama registry"""
        # Get selected model based on current tab
        model_id = self._get_selected_model_id()
        
        if not model_id:
            self.notify("No model selected", severity="warning")
            return
        
        # Show confirmation dialog - use a simple notification instead of modal
        msg = f"Downloading model '{model_id}'. This may take several minutes depending on model size."
        self.notify(msg, severity="information", timeout=5)
        
        # No confirmation needed now, since we're just proceeding with notification
        
        if self.is_pulling:
            self.notify("Already pulling a model", severity="warning")
            return
        
        self.is_pulling = True
        self.pull_progress = 0.0
        self.pull_status = f"Starting download of {model_id}..."
        
        # Show progress area
        progress_area = self.query_one("#progress-area")
        progress_area.add_class("visible")
        
        # Update progress UI
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        progress_bar.update(progress=0)
        status_label = self.query_one("#status-label", Static)
        status_label.update(f"Downloading {model_id}...")
        progress_label = self.query_one("#progress-label", Static)
        progress_label.update("0%")
        
        try:
            # Start pulling model with progress updates
            async for progress_data in self.ollama_client.pull_model(model_id):
                # Update progress
                if "status" in progress_data:
                    self.pull_status = progress_data["status"]
                    status_label.update(self.pull_status)
                
                if "completed" in progress_data and "total" in progress_data:
                    completed = progress_data["completed"]
                    total = progress_data["total"]
                    if total > 0:
                        percentage = (completed / total) * 100
                        self.pull_progress = percentage
                        progress_bar.update(progress=int(percentage))
                        progress_label.update(f"{percentage:.1f}%")
            
            # Download complete
            self.pull_status = f"Download of {model_id} complete!"
            status_label.update(self.pull_status)
            progress_bar.update(progress=100)
            progress_label.update("100%")
            
            # Refresh local models
            await self.load_local_models()
            
            # Show post-download options
            await self._show_post_download_options(model_id)
            
        except Exception as e:
            self.notify(f"Error pulling model: {str(e)}", severity="error")
            status_label.update(f"Error: {str(e)}")
        finally:
            self.is_pulling = False
            # Hide progress area after a delay
            async def hide_progress():
                # Use asyncio.sleep instead of app.sleep
                import asyncio
                await asyncio.sleep(3)
                progress_area.remove_class("visible")
            self.app.call_later(hide_progress)
    
    async def _show_post_download_options(self, model_id: str) -> None:
        """Show options after successful model download"""
        from textual.widgets import Button, Vertical
        from textual.containers import Center
        from textual.screen import ModalScreen
        
        class PostDownloadModal(ModalScreen):
            def __init__(self, model_id: str, parent: 'ModelBrowser'):
                super().__init__()
                self.model_id = model_id
                self.parent = parent
            
            def compose(self):
                with Center():
                    with Vertical(id="post-download-dialog"):
                        yield Button(f"✅ Model {self.model_id} downloaded successfully!", disabled=True, variant="success")
                        yield Button("🚀 Start chat with model", id="start-chat")
                        yield Button("🔍 Return to search results", id="return-search-results") 
                        yield Button("🔎 Return to search", id="return-search")
                        yield Button("📋 Return to model menu", id="return-menu")
            
            async def on_button_pressed(self, event: Button.Pressed) -> None:
                if event.button.id == "start-chat":
                    # Update config with selected model and start chat
                    await self.parent._start_chat_with_model(self.model_id)
                elif event.button.id == "return-search-results":
                    # Return to the last search results
                    self.parent._return_to_search_results()
                elif event.button.id == "return-search":
                    # Go back to search input
                    self.parent._return_to_search()
                elif event.button.id == "return-menu":
                    # Return to main model browser menu
                    self.parent._return_to_menu()
                
                self.dismiss()
        
        # Show the modal
        await self.app.push_screen(PostDownloadModal(model_id, self))
    
    async def _start_chat_with_model(self, model_id: str) -> None:
        """Start a chat with the downloaded model and update config"""
        try:
            # Update the configuration to use this model
            from app.config import load_config, save_config
            config = load_config()
            config["default_model"] = model_id
            save_config(config)
            
            # Close model browser and start chat
            self.app.pop_screen()  # Close model browser
            self.notify(f"Starting chat with {model_id}...", severity="success")
            
        except Exception as e:
            self.notify(f"Error starting chat: {str(e)}", severity="error")
    
    def _return_to_search_results(self) -> None:
        """Return to the last search results view"""
        # Switch to available tab if we're not already there
        if self.current_tab != "available":
            self.current_tab = "available"
            self.refresh_display()
    
    def _return_to_search(self) -> None:
        """Return to search input and clear results"""
        # Clear search and switch to available tab
        search_input = self.query_one("#search-input", Input)
        search_input.value = ""
        self.search_query = ""
        self.current_tab = "available"
        self.refresh_display()
    
    def _return_to_menu(self) -> None:
        """Return to the main model browser menu"""
        # Reset to local tab and clear any search
        search_input = self.query_one("#search-input", Input)
        search_input.value = ""
        self.search_query = ""
        self.current_tab = "local"
        self.refresh_display()
    
    async def _delete_selected_model(self) -> None:
        """Delete the selected model from local storage"""
        # Only works on local tab
        if self.current_tab != "local":
            self.notify("Can only delete local models", severity="warning")
            return
        
        model_id = self._get_selected_model_id()
        
        if not model_id:
            self.notify("No model selected", severity="warning")
            return
        
        # Confirm deletion
        if not await self.app.run_modal("confirm_dialog", f"Are you sure you want to delete {model_id}?"):
            return
        
        try:
            await self.ollama_client.delete_model(model_id)
            self.notify(f"Model {model_id} deleted successfully", severity="success")
            
            # Refresh local models
            await self.load_local_models()
            
        except Exception as e:
            self.notify(f"Error deleting model: {str(e)}", severity="error")
    
    async def _show_model_details(self) -> None:
        """Show details for the selected model"""
        model_id = self._get_selected_model_id()
        
        if not model_id:
            # Try to select the first model in the table
            if self.current_tab == "local" and self.local_models:
                model_id = self.local_models[0]["id"]
            elif self.current_tab == "available" and self.available_models:
                model_id = self.available_models[0]["name"]
                
            # If we still don't have a model ID, show warning and return
            if not model_id:
                self.notify("No model selected", severity="warning")
                return
        
        # Get model details container
        details_container = self.query_one("#model-details")
        details_content = self.query_one("#details-content", Static)
        
        # Check if we're in "available" tab or "local" tab
        if self.current_tab == "available":
            # For available models, use cached info instead of making API calls
            try:
                # Find the model in our available_models list
                model_info = None
                for model in self.available_models:
                    if model.get("name") == model_id:
                        model_info = model
                        break
                
                if not model_info:
                    details_content.update(f"No details found for model: {model_id}")
                    details_container.add_class("visible")
                    return
                
                # Format the details from the cached info
                formatted_details = f"Model: {model_id}\n"
                
                # Add parameters info
                param_size = model_info.get("parameter_size", "Unknown")
                if param_size and not str(param_size).upper().endswith("B"):
                    param_size = f"{param_size}B"
                formatted_details += f"Parameters: {param_size}\n"
                
                # Add family info
                family = model_info.get("model_family", "Unknown")
                formatted_details += f"Family: {family}\n"
                
                # Add description
                description = model_info.get("description", "No description available.")
                formatted_details += f"\nDescription:\n{description}\n"
                
                # Add variants if available
                if "variants" in model_info and model_info["variants"]:
                    formatted_details += f"\nVariants: {', '.join(model_info['variants'])}\n"
                
                # Add stats if available
                if "stats" in model_info and model_info["stats"]:
                    stats = model_info["stats"]
                    formatted_details += f"\nStats:\n"
                    if "pulls" in stats:
                        formatted_details += f"Pulls: {stats['pulls']}\n"
                    if "tags" in stats:
                        formatted_details += f"Tags: {stats['tags']}\n"
                    if "last_updated" in stats:
                        formatted_details += f"Last Updated: {stats['last_updated']}\n"
                
                # Update and show details
                details_content.update(formatted_details)
                details_container.add_class("visible")
            except Exception as e:
                logger.error(f"Error showing available model details: {str(e)}")
                details_content.update(f"Error loading details: {str(e)}")
                details_container.add_class("visible")
        else:
            # For local models, we still need to get details from API
            try:
                # Get model details from Ollama
                details = await self.ollama_client.get_model_details(model_id)
                
                # Check for error in response
                if "error" in details:
                    error_msg = f"Error: {details['error']}"
                    details_content.update(error_msg)
                    details_container.add_class("visible")
                    return
                
                formatted_details = f"Model: {model_id}\n"
                
                # Extract parameter size info
                param_size = "Unknown"
                
                # First try to get parameter size from modelfile if available
                if "modelfile" in details and details["modelfile"] is not None:
                    modelfile = details["modelfile"]
                    if "parameter_size" in modelfile and modelfile["parameter_size"]:
                        param_size = str(modelfile["parameter_size"])
                        # Make sure it ends with B for billions if it doesn't already
                        if not param_size.upper().endswith("B"):
                            param_size += "B"
                
                # If not found in modelfile, try to extract from name
                if param_size == "Unknown":
                    model_name = str(model_id).lower()
                    if "70b" in model_name:
                        param_size = "70B"
                    elif "405b" in model_name or "400b" in model_name:
                        param_size = "405B"
                    elif "34b" in model_name or "35b" in model_name:
                        param_size = "34B"
                    elif "27b" in model_name or "28b" in model_name:
                        param_size = "27B"
                    elif "13b" in model_name or "14b" in model_name:
                        param_size = "13B"
                    elif "8b" in model_name:
                        param_size = "8B"
                    elif "7b" in model_name:
                        param_size = "7B"
                    elif "6b" in model_name:
                        param_size = "6B"
                    elif "3b" in model_name:
                        param_size = "3B"
                    elif "2b" in model_name:
                        param_size = "2B"
                    elif "1b" in model_name:
                        param_size = "1B"
                    elif "mini" in model_name:
                        param_size = "3B"
                    elif "small" in model_name:
                        param_size = "7B"
                    elif "medium" in model_name:
                        param_size = "13B"
                    elif "large" in model_name:
                        param_size = "34B"
                    
                    # Special handling for base models with no size indicator
                    if param_size == "Unknown":
                        # Remove tag part if present to get base model
                        base_name = model_name.split(":")[0]
                        
                        # Check if we have default parameter sizes for known models
                        model_defaults = {
                            "llama3": "8B",
                            "llama2": "7B",
                            "mistral": "7B",
                            "gemma": "7B",
                            "gemma2": "9B",
                            "phi": "3B",
                            "phi2": "3B",
                            "phi3": "3B",
                            "phi4": "7B",
                            "orca-mini": "7B",
                            "llava": "7B",
                            "codellama": "7B",
                            "neural-chat": "7B",
                            "wizard-math": "7B",
                            "yi": "6B",
                            "deepseek": "7B",
                            "deepseek-coder": "7B",
                            "qwen": "7B",
                            "falcon": "7B",
                            "stable-code": "3B"
                        }
                        
                        # Try to find a match in default sizes
                        for model_name, default_size in model_defaults.items():
                            if model_name in base_name:
                                param_size = default_size
                                break
                    
                # Show both parameter size and disk size
                formatted_details += f"Parameters: {param_size}\n"
                formatted_details += f"Disk Size: {self._format_size(details.get('size', 0))}\n"
                
                # Extract family info - check multiple possible locations
                family = "Unknown"
                template = "Unknown"
                license_info = "Unknown"
                system_prompt = ""
                
                if "modelfile" in details and details["modelfile"] is not None:
                    modelfile = details["modelfile"]

                    # Ensure modelfile is a dictionary before accessing keys
                    if isinstance(modelfile, dict):
                        # Extract family/parameter size
                        if "parameter_size" in modelfile:
                            family = modelfile.get("parameter_size")
                        elif "family" in modelfile:
                            family = modelfile.get("family")
                        else:
                            # Try to infer from model name if not explicitly set
                            try:
                                name = str(model_id).lower() if model_id is not None else ""
                                if "llama" in name:
                                    family = "Llama"
                                elif "mistral" in name:
                                    family = "Mistral"
                                elif "phi" in name:
                                    family = "Phi"
                                elif "gemma" in name:
                                    family = "Gemma"
                                else:
                                    family = "Unknown"
                            except (TypeError, ValueError) as e:
                                logger.error(f"Error inferring model family: {str(e)}")
                                family = "Unknown"

                        # Get template
                        template = modelfile.get("template", "Unknown")

                        # Get license
                        license_info = modelfile.get("license", "Unknown")

                        # Get system prompt if available
                        if "system" in modelfile:
                            system_prompt = modelfile.get("system", "") # Use get for safety
                    else:
                        # If modelfile is not a dict (e.g., a string), set defaults
                        logger.warning(f"Modelfile for {model_id} is not a dictionary. Type: {type(modelfile)}")
                        # Keep existing defaults or try to infer family from name again
                        if family == "Unknown":
                             try:
                                name = str(model_id).lower() if model_id is not None else ""
                                if "llama" in name: family = "Llama"
                                elif "mistral" in name: family = "Mistral"
                                elif "phi" in name: family = "Phi"
                                elif "gemma" in name: family = "Gemma"
                             except (TypeError, ValueError): pass # Ignore errors here
                        # template, license_info, system_prompt remain "Unknown" or empty
                
                formatted_details += f"Family: {family}\n"
                formatted_details += f"Template: {template}\n"
                formatted_details += f"License: {license_info}\n"
                
                # Add timestamps if available
                if "modified_at" in details and details["modified_at"]:
                    formatted_details += f"Modified: {details['modified_at']}\n"
                elif "created_at" in details and details["created_at"]:
                    formatted_details += f"Created: {details['created_at']}\n"
                    
                # Add system prompt if available
                if system_prompt:
                    formatted_details += f"\nSystem Prompt:\n{system_prompt}\n"
                
                # Update and show details
                details_content.update(formatted_details)
                details_container.add_class("visible")
                
            except Exception as e:
                self.notify(f"Error getting model details: {str(e)}", severity="error")
                details_content.update(f"Error loading details: {str(e)}")
                details_container.add_class("visible")
    
    def _get_selected_model_id(self) -> str:
        """Get the ID of the currently selected model"""
        # Import debug_log function from main
        from app.main import debug_log
        
        debug_log(f"Entering _get_selected_model_id for tab {self.current_tab}")
        
        try:
            if self.current_tab == "local":
                debug_log("Processing local models tab")
                table = self.query_one("#local-models-table", DataTable)
                
                # Log table state
                debug_log(f"Table cursor_row: {table.cursor_row}, row_count: {table.row_count}")
                
                if table.cursor_row is not None and table.row_count > 0:
                    # Safety checks on cursor row
                    if table.cursor_row < 0 or table.cursor_row >= table.row_count:
                        debug_log(f"Invalid cursor row {table.cursor_row} for table with {table.row_count} rows")
                        logger.error(f"Invalid cursor row {table.cursor_row} for table with {table.row_count} rows")
                        return ""
                        
                    try:
                        debug_log(f"Getting row at cursor position {table.cursor_row}")
                        row = table.get_row_at(table.cursor_row)
                        debug_log(f"Row data: {repr(row)}")
                        
                        # Use a more permissive approach that works with any indexable type
                        if row and hasattr(row, '__getitem__') and len(row) > 0:
                            try:
                                row_value = row[0]
                                row_name = str(row_value) if row_value is not None else ""
                                debug_log(f"Row name extracted: '{row_name}'")
                                
                                # Check if local_models is valid
                                if not self.local_models:
                                    debug_log("local_models list is empty")
                                    return ""
                                    
                                debug_log(f"Searching through {len(self.local_models)} local models")
                                for i, model in enumerate(self.local_models):
                                    try:
                                        # Defensively check if model is a dict and has required keys
                                        if not isinstance(model, dict):
                                            debug_log(f"Model at index {i} is not a dict: {repr(model)}")
                                            continue
                                            
                                        model_name = model.get("name")
                                        model_id = model.get("id")
                                        
                                        if model_name is None:
                                            debug_log(f"Model at index {i} has no name: {repr(model)}")
                                            continue
                                            
                                        debug_log(f"Comparing '{model_name}' with '{row_name}'")
                                        if model_name == row_name:
                                            debug_log(f"Found matching model: {model_id}")
                                            return model_id
                                    except Exception as model_err:
                                        debug_log(f"Error processing model at index {i}: {str(model_err)}")
                                        logger.error(f"Error processing model: {model_err}")
                                        continue
                                        
                                # If we got here, no match was found
                                debug_log(f"No matching model found for '{row_name}'")
                            except Exception as extract_err:
                                debug_log(f"Error extracting row name: {str(extract_err)}")
                        else:
                            debug_log(f"Invalid row data: Row doesn't support indexing, is empty, or is None: {repr(row)}")
                            return ""
                                
                    except (IndexError, TypeError, AttributeError) as e:
                        debug_log(f"Error processing row data in _get_selected_model_id: {str(e)}")
                        logger.error(f"Error processing row data in _get_selected_model_id: {str(e)}")
            else:
                debug_log("Processing available models tab")
                table = self.query_one("#available-models-table", DataTable)
                
                # Log table state
                debug_log(f"Available table cursor_row: {table.cursor_row}, row_count: {table.row_count}")
                
                if table.cursor_row is not None and table.row_count > 0:
                    # Safety checks on cursor row
                    if table.cursor_row < 0 or table.cursor_row >= table.row_count:
                        debug_log(f"Invalid cursor row {table.cursor_row} for table with {table.row_count} rows")
                        logger.error(f"Invalid cursor row {table.cursor_row} for table with {table.row_count} rows")
                        # Try to select first row instead of returning empty
                        table.cursor_row = 0
                        debug_log("Reset cursor_row to 0")
                    
                    try:
                        debug_log(f"Getting row at cursor position {table.cursor_row}")
                        row = table.get_row_at(table.cursor_row)
                        debug_log(f"Row data: {repr(row)}")
                        
                        # Use a more permissive approach that works with any indexable type
                        if row and hasattr(row, '__getitem__') and len(row) > 0:
                            try:
                                row_value = row[0]
                                model_name = str(row_value) if row_value is not None else ""
                                debug_log(f"Available model selected: '{model_name}'")
                                logger.info(f"Selected available model: {model_name}")
                                return model_name
                            except Exception as extract_err:
                                debug_log(f"Error extracting row name: {str(extract_err)}")
                                return ""
                        else:
                            debug_log(f"Invalid row data: Row doesn't support indexing, is empty, or is None: {repr(row)}")
                            return ""
                                
                    except (IndexError, TypeError, AttributeError) as e:
                        debug_log(f"Error getting row at cursor: {str(e)}")
                        logger.error(f"Error getting row at cursor: {str(e)}")
                
                # If we couldn't get a valid row, check if there are any rows and select the first one
                debug_log("Trying fallback to first row")
                if hasattr(table, 'row_count') and table.row_count > 0:
                    try:
                        # Select the first row and get its ID
                        debug_log(f"Setting cursor_row to 0 and getting first row")
                        table.cursor_row = 0
                        row = table.get_row_at(0)
                        debug_log(f"First row data: {repr(row)}")
                        
                        # Use a more permissive approach that works with any indexable type
                        if row and hasattr(row, '__getitem__') and len(row) > 0:
                            try:
                                row_value = row[0]
                                model_name = str(row_value) if row_value is not None else ""
                                debug_log(f"First available model selected: '{model_name}'")
                                logger.info(f"Selected first available model: {model_name}")
                                return model_name
                            except Exception as extract_err:
                                debug_log(f"Error extracting first row name: {str(extract_err)}")
                                return ""
                        else:
                            debug_log(f"Invalid first row data: Row doesn't support indexing, is empty, or is None: {repr(row)}")
                            return ""
                                
                    except (IndexError, TypeError, AttributeError) as e:
                        debug_log(f"Error selecting first row: {str(e)}")
                        logger.error(f"Error selecting first row: {str(e)}")
                else:
                    debug_log("Table has no rows or row_count attribute missing")
        except Exception as e:
            debug_log(f"Unexpected error in _get_selected_model_id: {str(e)}")
            logger.error(f"Error in _get_selected_model_id: {str(e)}")
        
        debug_log("No model ID found, returning empty string")
        return ""
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in data tables"""
        # Import debug_log function from main
        from app.main import debug_log
        
        debug_log(f"Entering on_data_table_row_selected")
        
        # Set selected model ID based on the selected row
        try:
            # Check if event has valid structure
            if not hasattr(event, 'data_table') or not event.data_table:
                debug_log("Event has no data_table attribute or it is None")
                logger.error("Invalid event in on_data_table_row_selected")
                return
                
            if not hasattr(event, 'cursor_row'):
                debug_log("Event has no cursor_row attribute")
                logger.error("Event has no cursor_row attribute")
                return
                
            debug_log(f"Event cursor_row: {event.cursor_row}")
                
            if not hasattr(event.data_table, 'id') or not event.data_table.id:
                debug_log("Data table has no ID attribute or it is empty")
                logger.error("Data table has no ID in on_data_table_row_selected")
                return
            
            debug_log(f"Data table ID: {event.data_table.id}")
                
            if event.data_table.id == "local-models-table":
                debug_log("Processing local models table")
                try:
                    # Carefully get the row data
                    if event.cursor_row is None or event.cursor_row < 0:
                        debug_log(f"Invalid cursor row: {event.cursor_row}")
                        logger.error(f"Invalid cursor row: {event.cursor_row}")
                        return
                        
                    # Check row count to avoid index errors
                    if not hasattr(event.data_table, 'row_count'):
                        debug_log("Data table has no row_count attribute")
                        return
                        
                    debug_log(f"Table row_count: {event.data_table.row_count}")
                        
                    if event.data_table.row_count <= event.cursor_row:
                        debug_log(f"Cursor row {event.cursor_row} exceeds row count {event.data_table.row_count}")
                        logger.error(f"Cursor row {event.cursor_row} exceeds row count {event.data_table.row_count}")
                        return
                        
                    debug_log(f"Getting row at cursor position {event.cursor_row}")
                    row = event.data_table.get_row_at(event.cursor_row)
                    debug_log(f"Row data: {repr(row)}")
                    
                    # Find the model ID from the display name with more permissive checks
                    try:
                        # Check if row is valid and can be indexed
                        if row is None:
                            debug_log("Row is None")
                            return
                            
                        if not hasattr(row, '__getitem__') or not hasattr(row, '__len__'):
                            debug_log(f"Row doesn't support indexing or length: {type(row)}")
                            return
                            
                        if len(row) <= 0:
                            debug_log("Row has no items")
                            return
                            
                        # Extract the first item (model name)
                        try:
                            row_value = row[0]
                            row_name = str(row_value) if row_value is not None else ""
                            debug_log(f"DataTable row selected with name: '{row_name}'")
                            logger.info(f"DataTable row selected with name: {row_name}")
                        except Exception as idx_err:
                            debug_log(f"Error accessing row[0]: {str(idx_err)}")
                            return
                        
                        # Check if local_models is a valid list
                        if not self.local_models:
                            debug_log("local_models list is empty or None")
                            return
                            
                        debug_log(f"Searching through {len(self.local_models)} local models")
                        for i, model in enumerate(self.local_models):
                            try:
                                # Use .get() for safer dictionary access
                                model_name = model.get("name", None)
                                if model_name is None:
                                    debug_log(f"Model at index {i} has no name")
                                    continue
                                    
                                debug_log(f"Comparing '{model_name}' with '{row_name}'")
                                if model_name == row_name:
                                    model_id = model.get("id", "")
                                    debug_log(f"Found match. Setting selected_model_id to: '{model_id}'")
                                    logger.info(f"Setting selected_model_id to: {model_id}")
                                    self.selected_model_id = model_id
                                    break
                            except Exception as model_err:
                                debug_log(f"Error processing model at index {i}: {str(model_err)}")
                                logger.error(f"Error matching local model: {str(model_err)}")
                                continue
                    except (IndexError, TypeError) as idx_err:
                        debug_log(f"Error accessing row data: {str(idx_err)}")
                        logger.error(f"Error accessing row data: {str(idx_err)}")
                except (IndexError, TypeError, AttributeError) as e:
                    debug_log(f"Error processing local table row data: {str(e)}")
                    logger.error(f"Error processing local table row data: {str(e)}")
            elif event.data_table.id == "available-models-table":
                debug_log("Processing available models table")
                try:
                    # Similar safety checks for available models
                    if event.cursor_row is None or event.cursor_row < 0:
                        debug_log(f"Invalid cursor row: {event.cursor_row}")
                        logger.error(f"Invalid cursor row: {event.cursor_row}")
                        return
                        
                    # Check row count to avoid index errors
                    if not hasattr(event.data_table, 'row_count'):
                        debug_log("Data table has no row_count attribute")
                        return
                        
                    debug_log(f"Available table row_count: {event.data_table.row_count}")
                        
                    if event.data_table.row_count <= event.cursor_row:
                        debug_log(f"Cursor row {event.cursor_row} exceeds row count {event.data_table.row_count}")
                        logger.error(f"Cursor row {event.cursor_row} exceeds row count {event.data_table.row_count}")
                        return
                        
                    debug_log(f"Getting row at cursor position {event.cursor_row}")
                    row = event.data_table.get_row_at(event.cursor_row)
                    debug_log(f"Row data: {repr(row)}")
                    
                    # Model name is used as ID, with more permissive checks
                    try:
                        # Check if row is valid and can be indexed
                        if row is None:
                            debug_log("Row is None")
                            return
                            
                        if not hasattr(row, '__getitem__') or not hasattr(row, '__len__'):
                            debug_log(f"Row doesn't support indexing or length: {type(row)}")
                            return
                            
                        if len(row) <= 0:
                            debug_log("Row has no items")
                            return
                            
                        # Extract the first item (model name)
                        try:
                            row_value = row[0]
                            model_name = str(row_value) if row_value is not None else ""
                            debug_log(f"Available model selected: '{model_name}'")
                            logger.info(f"Selected available model: {model_name}")
                            self.selected_model_id = model_name
                        except Exception as access_err:
                            debug_log(f"Error accessing row[0]: {str(access_err)}")
                            logger.error(f"Error accessing row[0]: {str(access_err)}")
                            self.selected_model_id = ""
                    except (IndexError, TypeError) as idx_err:
                        debug_log(f"Error accessing available table row data: {str(idx_err)}")
                        logger.error(f"Error accessing available table row data: {str(idx_err)}")
                        self.selected_model_id = ""
                except (IndexError, TypeError, AttributeError) as e:
                    debug_log(f"Error getting model ID from available table row: {str(e)}")
                    logger.error(f"Error getting model ID from available table row: {str(e)}")
                    self.selected_model_id = ""
            else:
                debug_log(f"Unknown table ID: {event.data_table.id}")
        except Exception as e:
            # Catch-all for any other errors
            debug_log(f"Unexpected error in on_data_table_row_selected: {str(e)}")
            logger.error(f"Unexpected error in on_data_table_row_selected: {str(e)}")
            self.selected_model_id = ""
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key in search input)"""
        if event.input.id == "model-search":
            # Trigger search
            if self.current_tab == "local":
                self.app.call_later(self.load_local_models)
            else:
                self.app.call_later(self.load_available_models)
                
    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes for live search"""
        if event.input.id == "model-search" and self.current_tab == "available":
            # Auto-search as user types in the available models tab
            self.app.call_later(self.load_available_models)
