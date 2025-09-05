"""Main module."""
from gradio_client import Client
import time
import re
import os
import requests
import json
import asyncio
import base64
import anthropic
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Union, Optional, Any
import urllib.parse
import urllib.request
# https://working-tuna-massive.ngrok-free.app
# https://upright-mantis-intensely.ngrok-free.app/
# https://working-tuna-massive.ngrok-free.app/

# Load environment variables from .env file
load_dotenv()

OS_URL = "https://fintor-cute-test-1.ngrok.app"
HF_FINTOR_GUI_ENDPOINT = "https://jtpozbeohnafofam.us-east-1.aws.endpoints.huggingface.cloud/v1/"
HF_TOKEN = os.environ.get("HF_TOKEN")

HITL_URL = "https://d5x1qrpuf7.execute-api.us-west-1.amazonaws.com/prod/"
SHARED_STATE_URL = "https://c16bgaz0i2.execute-api.us-west-1.amazonaws.com/prod"

HITL_TOKEN = os.environ.get("HITL_TOKEN")

class WindowsAgent:
	def __init__(self, variable_name="friend", os_url=OS_URL, cache_token=None):
		"""
		Initializes the WindowsAgent with a configurable variable name.

		Args:
			variable_name (str): The name to be used by hello_old_friend.
							  Defaults to "friend".
			os_url (str): The URL for OS operations.
					   Defaults to OS_URL.
			cache_token (str): The API token for element search operations.
							 Defaults to None.
		"""
		self.config_variable_name = variable_name
		self.os_url = os_url
		self.cache_token = cache_token

	def hello_world(self):
		"""Prints a hello world message."""
		print("Hello World from WindowsAgent!")

	def hello_old_friend(self):
		"""Prints a greeting to the configured variable name."""
		print(f"Hello, my old {self.config_variable_name}!")

	def add(self, a, b):
		"""Adds two numbers and returns the result."""
		return a + b

	def act(self, input_data):
		try:
			client = Client(self.os_url) 
			result = client.predict(
				user_input=str(input_data),
				api_name="/process_input1"
			)
			print(result)
		except Exception as e:
			print(f"Error in act operation: {e}")
			return None

	def click_element(self, x: int, y: int):
		"""Click at the specified coordinates.
		
		Args:
			x (int): X coordinate
			y (int): Y coordinate
		"""
		try:
			if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
				raise ValueError("Coordinates must be numbers")
				
			input_data = {
				"action": "CLICK",
				"coordinate": [int(x), int(y)],
				"value": "value",
				"model_selected": "claude"
			}
			
			client = Client(self.os_url)
			result = client.predict(
				user_input=str(input_data),
				api_name="/process_input1"
			)
			print(result)
			return result
		except Exception as e:
			print(f"Error in click operation: {e}")
			return None

	def screenshot(self):
		try:
			client = Client(self.os_url) 
			result = client.predict(
				api_name="/get_screenshot_url"
			)
			print(result)
			return result
		except Exception as e:
			print(f"Error in act operation: {e}")
			return result
		

	def screenshot_cropped(self, arr_input):
		try:
			client = Client(self.os_url) 
			result = client.predict(
				array_input=arr_input,
				api_name="/get_cropped_screenshot"
			)
			print(result)
			return result
		except Exception as e:
			print(f"Error in act operation: {e}")
			return result


	def click_cached_element(self, task_type: str, element_name: str):
		"""Click on an element using cached coordinates from the API.
		
		This method fetches cached element coordinates from the API based on the 
		element name and task type, then performs a click action at those coordinates.
		Instead of requiring direct coordinates, it uses the element name and task_type
		to retrieve cached coordinate data from the element search API.
		
		Args:
			task_type (str): The task type ID (e.g., 'approveITP')
			element_name (str): The name of the element to click
			
		Returns:
			Result from the click operation or None if failed
			
		Raises:
			ValueError: If cache_token is not provided during WindowsAgent initialization
		"""
		try:
			# Check if cache_token is defined
			if self.cache_token is None:
				raise ValueError("cache_token is required for click_cached_element operation but was not provided during WindowsAgent initialization")
			
			# API configuration
			api_url = "https://cega6bexzc.execute-api.us-west-1.amazonaws.com/prod/elements/search"
			
			# Prepare API request parameters
			params = {
				"name": element_name,
				"taskTypeID": task_type
			}
			
			headers = {
				"x-api-key": self.cache_token
			}
			
			# Make API call to get coordinates
			response = requests.get(api_url, params=params, headers=headers)
			
			if response.status_code != 200:
				print(f"API request failed with status code: {response.status_code}")
				print(f"Response: {response.text}")
				return None
			
			api_data = response.json()
			
			# Extract coordinates from API response
			if 'x' in api_data and 'y' in api_data:
				x = int(api_data['x'])
				y = int(api_data['y'])
			else:
				print(f"Could not find x/y coordinates in API response: {api_data}")
				return None
			
			print(f"Retrieved coordinates for '{element_name}': ({x}, {y})")
			
			# Validate coordinates
			if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
				raise ValueError("Retrieved coordinates must be numbers")
			
			# Prepare input data for the click action
			input_data = {
				"action": "CLICK",
				"coordinate": [x, y],
				"value": "value",
				"model_selected": "claude"
			}
			
			# Execute the click using the existing client
			client = Client(self.os_url)
			result = client.predict(
				user_input=str(input_data),
				api_name="/process_input1"
			)
			
			print(f"Click result: {result}")
			return result
			
		except requests.exceptions.RequestException as e:
			print(f"API request error: {e}")
			return None
		except KeyError as e:
			print(f"Missing key in API response: {e}")
			return None
		except ValueError as e:
			print(f"Value error: {e}")
			return None
		except Exception as e:
			print(f"Error in click_cached_element operation: {e}")
			return None

class VisionAgent:
	def __init__(self,screen_size=(1366, 768), model_selected="FINTOR_GUI", hf_fintor_gui_endpoint=HF_FINTOR_GUI_ENDPOINT, hf_token=HF_TOKEN, anthropic_api_key: Optional[str] = None):
		"""
		Initializes the Vision class with a configurable variable name and OS URL.

		Args:
			variable_name (str): The name to use for configuration.
								Defaults to "friend".
			os_url (str): The URL for OS operations.
						Defaults to OS_URL.
		"""
		self.hf_fintor_gui_endpoint = hf_fintor_gui_endpoint
		self.hf_token = hf_token
		self.model_selected = model_selected
		self.screen_size = screen_size
		self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
		
	def find_element(self, screenshot_url, element_name):
		try:
			if self.model_selected != "FINTOR_GUI":
				raise ValueError("We only support FINTOR_GUI for now!")
			
			print("Element name in find_element", element_name)
			
			print("Screenshot url in find_element", screenshot_url)
			client = OpenAI(
				base_url = self.hf_fintor_gui_endpoint,	 
				api_key = self.hf_token
			)
			_NAV_SYSTEM_GROUNDING = """
			You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task. 

			## Output Format
			```Action: ...```

			## Action Space
			click(start_box='<|box_start|>(x1,y1)<|box_end|>')
			hotkey(key='')
			type(content='') #If you want to submit your input, use \"\" at the end of `content`.
			scroll(start_box='<|box_start|>(x1,y1)<|box_end|>', direction='down or up or right or left')
			wait() #Sleep for 5s and take a screenshot to check for any changes.
			finished()
			call_user() # Submit the task and call the user when the task is unsolvable, or when you need the user's help.

			## Note
			- Do not generate any other text.
			"""

			chat_completion = client.chat.completions.create(
				model="tgi",
				messages=[
				{"role": "system", "content": _NAV_SYSTEM_GROUNDING},
				{
					"role": "user",
					"content": [
						{"type": "image_url", "image_url": {"url": screenshot_url}},
						{
							"type": "text",
							"text": element_name
						}
					]
				}
			],
				top_p=None,
				temperature=0,
				max_tokens=150,
				stream=True,
				seed=None,
				stop=None,
				frequency_penalty=None,
				presence_penalty=None
			)
			word_buffer = ""
			full_text = []

			for message in chat_completion:
				chunk = message.choices[0].delta.content
				if chunk:
					word_buffer += chunk
					words = word_buffer.split()
					full_text.extend(words[:-1])
					word_buffer = words[-1] if words else ""

			if word_buffer:
				full_text.append(word_buffer)

			final_text = " ".join(full_text)
			print("final_text", final_text)
			pattern = r"\(\d+,\d+\)"

			matches = re.findall(pattern, final_text)
			print("matches", matches)

			if matches:
				if len(matches) == 1:
					extracted_coordinates = matches[0]
				elif len(matches) == 2:
					# Parse the two coordinate pairs
					coord1 = matches[0].strip('()')
					coord2 = matches[1].strip('()')
					x1, y1 = map(int, coord1.split(','))
					x2, y2 = map(int, coord2.split(','))
					
					# Average the coordinates
					avg_x = (x1 + x2) // 2
					avg_y = (y1 + y2) // 2
					extracted_coordinates = f"({avg_x},{avg_y})"
				else:
					# If more than 2 matches, use the first one
					extracted_coordinates = matches[0]
				

				extracted_coordinates = self.convert_coordinates(extracted_coordinates)
				if extracted_coordinates:
					return extracted_coordinates
			else:
				return "NOT FOUND"
		except Exception as e:
			print(f"Error in ui_tars_coordinates: {e}")
			return None
		
	def convert_coordinates(self, coordinates_str):
		"""
		Convert coordinates based on screen size ratio (screen_size/1000).
		
		Args:
			coordinates_str (str): String in format "(x,y)"
			
		Returns:
			str: Converted coordinates in same format
		"""
		try:
			# Strip parentheses and split by comma
			coords = coordinates_str.strip('()')
			x, y = map(int, coords.split(','))
			
			# Convert coordinates based on screen ratio
			x_ratio = self.screen_size[0] / 1000
			y_ratio = self.screen_size[1] / 1000
			
			new_x = int(x * x_ratio)
			new_y = int(y * y_ratio)
			
			return f"({new_x},{new_y})"
		except Exception as e:
			print(f"Error converting coordinates: {e}")
			return coordinates_str

	def claude(self, original_image_url, element_description: Dict[str, Any], api_key: Optional[str] = None) -> Union[str, None]:
		"""
		Send a description and screenshot image to Claude and return grounded coordinates.

		Args:
			original_image_url (str): URL of the screenshot image to analyze
			element_description (dict): Detailed description fields of the target element
			api_key (str, optional): Anthropic API key override; falls back to env/initializer
		
		Returns:
			str | None: Coordinates in format "(x,y)" if found, "NOT FOUND" if not found, or None on error
		"""
		try:
			key = api_key or self.anthropic_api_key
			if not key:
				return "ERROR: ANTHROPIC_API_KEY is required. Set it in environment or pass api_key."
			
			print("📸 Encoding original image from URL...")
			resp = requests.get(original_image_url, timeout=45)
			resp.raise_for_status()
			original_base64 = base64.b64encode(resp.content).decode("utf-8")
			media_type = resp.headers.get("Content-Type", "") or ""
			allowed_media = {"image/png", "image/jpeg", "image/gif", "image/webp"}
			if media_type not in allowed_media:
				# Try to infer from URL extension; default to image/png
				lower_url = (original_image_url or "").lower()
				if lower_url.endswith(".png"):
					media_type = "image/png"
				elif lower_url.endswith(".jpg") or lower_url.endswith(".jpeg"):
					media_type = "image/jpeg"
				elif lower_url.endswith(".gif"):
					media_type = "image/gif"
				elif lower_url.endswith(".webp"):
					media_type = "image/webp"
				else:
					media_type = "image/png"
			
			# Extract description fields with safe defaults
			element_name = element_description.get('name', 'Unknown element') if isinstance(element_description, dict) else str(element_description)
			description = element_description.get('description', 'No description available') if isinstance(element_description, dict) else ''
			element_type = element_description.get('element_type', 'Unknown type') if isinstance(element_description, dict) else 'Unknown type'
			exact_text = element_description.get('exact_text', 'N/A') if isinstance(element_description, dict) else 'N/A'
			visual_cues = element_description.get('visual_cues', 'N/A') if isinstance(element_description, dict) else 'N/A'
			spatial_location = element_description.get('spatial_location', 'N/A') if isinstance(element_description, dict) else 'N/A'
			surrounding_elements = element_description.get('surrounding_elements', 'N/A') if isinstance(element_description, dict) else 'N/A'
			container_context = element_description.get('container_context', 'N/A') if isinstance(element_description, dict) else 'N/A'
			functional_context = element_description.get('functional_context', 'N/A') if isinstance(element_description, dict) else 'N/A'
			unique_identifiers = element_description.get('unique_identifiers', []) if isinstance(element_description, dict) else []
			search_strategy = element_description.get('search_strategy', 'N/A') if isinstance(element_description, dict) else 'N/A'
			
			width, height = self.screen_size
			grounding_prompt = f"""
You are an expert UI automation specialist. I will provide you with a detailed description of a UI element, and you need to locate it in the screenshot and provide the exact coordinates for clicking.

**ELEMENT TO LOCATE:**

**Element Name:** {element_name}
**Element Type:** {element_type}
**Description:** {description}

**Visual Characteristics:**
- Exact Text: {exact_text}
- Visual Cues: {visual_cues}

**Contextual Information:**
- Spatial Location: {spatial_location}
- Container Context: {container_context}
- Surrounding Elements: {surrounding_elements}
- Functional Context: {functional_context}

**Unique Identifiers:** {', '.join(unique_identifiers) if unique_identifiers else 'None specified'}

**Search Strategy:** {search_strategy}

**YOUR TASK:**
1. **LOCATE** the element in the provided screenshot using the description above
2. **IDENTIFY** the exact pixel coordinates where this element can be clicked
3. **PROVIDE** both the coordinates and detailed reasoning

**CRITICAL REQUIREMENTS:**
- Find the element based ONLY on the description provided
- Return the exact pixel coordinates (x, y) for clicking
- Provide reasoning for why you chose those coordinates
- If multiple similar elements exist, choose the one that best matches the description
- Be precise - the coordinates should be within the element boundaries

**IMAGE SPECIFICATIONS:**
- Image dimensions: {width} width × {height} height pixels
- Coordinate system: (0,0) is top-left corner
- X-axis: increases left to right (0 to {width})
- Y-axis: increases top to bottom (0 to {height})

**RESPONSE FORMAT:**
{{
    "thinking": "Step-by-step reasoning process for locating the element",
    "visual_match": "What visual cues confirmed this is the right element",
    "text_verification": "Confirmation of any text content found",
    "spatial_verification": "Confirmation you're in the correct UI area",
    "element_found": true/false,
    "coordinates": [x, y],
    "confidence": "high/medium/low",
    "reasoning": "Why you chose these specific coordinates",
    "element_bounds": "Description of the element's approximate size and bounds",
    "alternative_candidates": [
        {{
            "coordinates": [x, y],
            "reason_excluded": "Why this similar element was not chosen"
        }}
    ]
}}

**IMPORTANT NOTES:**
- This is a pure coordinate grounding test
- You must find the element based solely on the description
- Be as precise as possible with coordinates
- Explain your reasoning clearly
- If you cannot find the element, set "element_found" to false

Please analyze the screenshot and locate the element described above.
"""
			
			print("🤖 Sending screenshot to Claude for coordinate grounding...")
			client = anthropic.Anthropic(api_key=key)
			response = client.messages.create(
				model="claude-3-5-sonnet-20241022",
				max_tokens=1500,
				messages=[
					{
						"role": "user",
						"content": [
							{"type": "text", "text": grounding_prompt},
							{
								"type": "image",
								"source": {"type": "base64", "media_type": media_type, "data": original_base64}
							}
						]
					}
				]
			)
			
			if response.content and len(response.content) > 0:
				response_text = response.content[0].text
				print(f"Claude grounding response: {response_text}")
				
				# Try to extract JSON and coordinates
				if "{" in response_text and "}" in response_text:
					try:
						start = response_text.find("{")
						end = response_text.rfind("}") + 1
						json_str = response_text[start:end]
						data = json.loads(json_str)
						coords = data.get("coordinates") if isinstance(data, dict) else None
						if isinstance(coords, list) and len(coords) == 2:
							x, y = int(coords[0]), int(coords[1])
							# Clamp within screen bounds just in case
							x = max(0, min(x, width))
							y = max(0, min(y, height))
							return f"({x},{y})"
					except Exception:
						pass
				
				# Regex fallback for [x, y]
				match = re.search(r"coordinates\"?\s*:\s*\[\s*(\d+)\s*,\s*(\d+)\s*\]", response_text)
				if match:
					x = int(match.group(1))
					y = int(match.group(2))
					x = max(0, min(x, width))
					y = max(0, min(y, height))
					return f"({x},{y})"
				
				return "NOT FOUND"
			
			return "NOT FOUND"
		except Exception as e:
			print(f"Error in claude grounding: {e}")
			return f"ERROR: {e}"

class HumanAgent:
	def __init__(self, HITL_token=HITL_TOKEN, HITL_url=HITL_URL):
		"""
		Initializes the HumanAgent with token and URL.

		Args:
			HITL_token (str): Authentication token
			HITL_url (str): API endpoint URL
		"""
		self.HITL_token = HITL_token
		self.HITL_url = HITL_url

	def task(self,  image_urls, thread_id="1234567890", questions=None, task_type="NotSpecified", thread_state=None):
		"""
		Creates a human task with images, instructions, and questions.
		
		Args:
			image_urls (list): List of image URLs to display
			instruction_markdown (str, optional): Markdown formatted instructions
			instruction_url (str, optional): URL to instructions
			questions (list, optional): List of question dictionaries with format:
				{
					"Question": "Is this green?",
					"Choices": ["Yes", "No", "Maybe"],  # Optional
					"TypeIn": True  # Optional, defaults to True
				}
		
		Returns:
			Response from the human task API
		"""
		try:
			if not image_urls:
				raise ValueError("At least one image URL is required")

			# Default empty list if questions parameter is None
			if questions is None:
				questions = []


			# Prepare task data
			task_data = {
				"type": "task",
				"image_urls": image_urls,
				"questions": questions,
				"thread_id": thread_id,
				"task_type": task_type,
				"thread_state": thread_state,
			}

			# Set up headers for the API request
			headers = {
				"Content-Type": "application/json",
				"Authorization": f"Bearer {self.HITL_token}"
			}

			# Make the API call
			response = requests.post(
				self.HITL_url,
				headers=headers,
				data=json.dumps(task_data)
			)

			# Check if the request was successful
			response.raise_for_status()
			
			# Return the response from the API
			print(f"Task sent to {self.HITL_url} successfully")
			return response.json()
			
		except requests.exceptions.RequestException as e:
			print(f"API request error: {e}")
			return None
		except Exception as e:
			print(f"Error creating human task: {e}")
			return None

	def reporting(self, thread_id="1234567890", report_type="NotSpecified", thread_state=None):
			"""
			Creates a human task with images, instructions, and questions.
			
			Args:
				thread_id (str): ID for the thread. Defaults to "1234567890"
				thread_state (dict, optional): Dictionary containing thread state information
			
			Returns:
				Response from the reporting API containing thread status and any updates
			"""
			try:
				task_data = {
					"type": "reporting",
					"thread_id": thread_id,
					"thread_state": thread_state,
					"report_type": report_type
				}

				# Set up headers for the API request
				headers = {
					"Content-Type": "application/json",
					"Authorization": f"Bearer {self.HITL_token}"
				}

				# Make the API call
				response = requests.post(
					self.HITL_url,
					headers=headers,
					data=json.dumps(task_data)
				)

				# Check if the request was successful
				response.raise_for_status()
				
				# Return the response from the API
				print(f"Reporting sent to {self.HITL_url} successfully")
				return response.json()
				
			except requests.exceptions.RequestException as e:
				print(f"API request error: {e}")
				return None
			except Exception as e:
				print(f"Error creating human reporting: {e}")
				return None

class StationAgent:
	"""
	A class for managing shared state and server coordination between LangGraph workflows.
	
	This class integrates with a SharedState API to coordinate state and server management
	across different workflow instances in LangGraph.
	
	Server Status Constraint:
		The "server" variable can only have two values: "busy" or "idle"
		- "idle": Server is available for new tasks
		- "busy": Server is currently processing a task
		
	Reserved Variables:
		- "server": Server status (managed by server.load/unload methods only)
		- "serverThread": Current task type (managed by server.load/unload methods only)
	"""
	
	# Reserved variable names that cannot be set by users
	RESERVED_VARIABLES = {"server", "serverThread", "serverCheckpoint", "serverTaskType"}
	
	# Valid server status values
	VALID_SERVER_STATUS = {"busy", "idle"}
	
	def __init__(self, station_thread_id: str, graph_thread_id: str, token: str, initial_state: Optional[Dict[str, Any]] = None, langgraph_token: Optional[str] = None, current_graph_url: Optional[str] = None, current_graph_assistant_id: Optional[str] = None):
		"""
		Initialize the StationAgent with thread IDs and authentication tokens.
		
		Args:
			station_thread_id (str): Identifier for the station/workflow instance
			graph_thread_id (str): LangGraph thread identifier
			token (str): Authentication token for SharedState API access
			initial_state (dict, optional): Initial state object to push to SharedState API. Defaults to None.
			langgraph_token (str, optional): Authentication token for LangGraph API access. Required for pause/unpause functionality.
			current_graph_url (str, optional): Current graph URL for pause/unpause functionality
			current_graph_assistant_id (str, optional): Current graph assistant ID for pause/unpause functionality
		"""
		self.station_thread_id = station_thread_id
		self.graph_thread_id = graph_thread_id
		self.token = token
		self.langgraph_token = langgraph_token
		self.current_graph_url = current_graph_url
		self.current_graph_assistant_id = current_graph_assistant_id
		self.base_url = SHARED_STATE_URL
		
		# Set up HTTP session with authentication
		self.session = requests.Session()
		self.session.headers.update({
			"Content-Type": "application/json",
			"Authorization": f"Bearer {token}"
		})
		
		# Initialize nested classes
		self.state = self.State(self)
		self.server = self.Server(self)
		
		# Handle initial state and server variable initialization
		if initial_state is not None:
			# Ensure initial_state includes server variables
			self.initial_state = initial_state.copy()
			num_servers = 4  # Default number of servers
			if "server" not in self.initial_state:
				self.initial_state["server"] = ["idle"] * num_servers
			if "serverThread" not in self.initial_state:
				self.initial_state["serverThread"] = ["idle"] * num_servers
			if "serverCheckpoint" not in self.initial_state:
				self.initial_state["serverCheckpoint"] = ["setup"] * num_servers
			if "serverTaskType" not in self.initial_state:
				self.initial_state["serverTaskType"] = ["taskPlaceholder"] * num_servers
				
			# Use direct API call during initialization to bypass reserved variable protection
			data = {
				"stationThread": self.station_thread_id,
				"variables": self.initial_state
			}
			
			response = self._make_request("POST", "/shared-state/bulk-upsert", data=data)
			push_result = response is not None and response.get("success", False)
			
			if push_result:
				print(f"🚀 StationAgent initialized and pushed {len(self.initial_state)} variables to SharedState API")
			else:
				print(f"⚠️ StationAgent initialized but failed to push {len(self.initial_state)} variables to SharedState API")
		else:
			# No initial state provided - check if server variables exist, if not initialize them
			self.initial_state = None
			print("🆕 StationAgent initialized with no initial state to push")
			
			# Check if server variables exist as arrays, if not initialize them
			server_vars = self.state.get("server")
			if server_vars is None or not isinstance(server_vars, list):
				print("⚠️ Server variables not found or not arrays, initializing...")
				num_servers = 4  # Default number of servers
				server_initialization = {
					"server": ["idle"] * num_servers,
					"serverThread": ["idle"] * num_servers,
					"serverCheckpoint": ["setup"] * num_servers,
					"serverTaskType": ["taskPlaceholder"] * num_servers
				}
				
				# Use direct API call to initialize server variables
				data = {
					"stationThread": self.station_thread_id,
					"variables": server_initialization
				}
				
				response = self._make_request("POST", "/shared-state/bulk-upsert", data=data)
				if response and response.get("success", False):
					print("✅ Server variables initialized successfully")
				else:
					print("❌ Failed to initialize server variables")
			else:
				print("✅ Server variables already exist as arrays")
	
	def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
				  data: Optional[Dict] = None, max_retries: int = 3) -> Optional[Dict]:
		"""
		Make HTTP request with retry logic and error handling.
		
		Args:
			method (str): HTTP method (GET, POST, PUT, DELETE)
			endpoint (str): API endpoint
			params (dict, optional): Query parameters
			data (dict, optional): Request body data
			max_retries (int): Maximum number of retry attempts
			
		Returns:
			dict: Response JSON or None on failure
		"""
		url = f"{self.base_url}{endpoint}"
		
		for attempt in range(max_retries):
			try:
				response = self.session.request(
					method=method,
					url=url,
					params=params,
					json=data,
					timeout=30
				)
				
				if response.status_code == 401:
					raise ValueError("Authentication failed: Invalid token")
				
				if response.status_code == 404:
					return None
				
				response.raise_for_status()
				return response.json()
				
			except requests.exceptions.Timeout:
				if attempt < max_retries - 1:
					wait_time = (2 ** attempt) * 1  # Exponential backoff
					print(f"Request timeout, retrying in {wait_time} seconds...")
					time.sleep(wait_time)
					continue
				else:
					print("Request timeout after maximum retries")
					return None
					
			except requests.exceptions.RequestException as e:
				if attempt < max_retries - 1:
					wait_time = (2 ** attempt) * 1
					print(f"Request error: {e}, retrying in {wait_time} seconds...")
					time.sleep(wait_time)
					continue
				else:
					print(f"Request failed after maximum retries: {e}")
					return None
					
			except json.JSONDecodeError:
				print("Invalid JSON response received")
				return None
				
		return None
	
	def validate_server_status(self, status: str) -> bool:
		"""
		Validate that a server status value is allowed.
		
		Args:
			status (str): Server status to validate
			
		Returns:
			bool: True if status is "busy" or "idle", False otherwise
		"""
		return status in self.VALID_SERVER_STATUS
	
	def validate_connection(self) -> Dict:
		"""
		Validate the connection to the SharedState API.
		
		Returns:
			dict: Connection status and information
		"""
		try:
			# Try to list variables to test connection
			response = self._make_request("GET", f"/shared-state/list?stationThread={self.station_thread_id}")
			
			if response is not None:
				return {
					"connected": True,
					"api_url": self.base_url,
					"station_thread": self.station_thread_id,
					"variable_count": len(response.get("attributes", {}))
				}
			else:
				return {
					"connected": False,
					"error": "Failed to connect to API",
					"api_url": self.base_url
				}
		except Exception as e:
			return {
				"connected": False,
				"error": str(e),
				"api_url": self.base_url
			}
	
	class State:
		"""Nested class for state management operations."""
		
		def __init__(self, agent: 'StationAgent'):
			self.agent = agent
		
		def get(self, variable_name: str) -> Union[Dict, str, None]:
			"""
			Get single variable from SharedState API.
			
			Args:
				variable_name (str): Name of the variable to retrieve
				
			Returns:
				Union[Dict, str, None]: The attributeValue from response or None if not found
			"""
			params = {
				"stationThread": self.agent.station_thread_id,
				"attributeName": variable_name
			}
			
			response = self.agent._make_request("GET", "/shared-state", params=params)
			
			if response and response.get("success"):
				return response.get("data", {}).get("attributeValue")
			
			return None
		
		def set(self, variable_name: str, variable_value: Any) -> bool:
			"""
			Create/update single variable using PUT endpoint.
			
			Args:
				variable_name (str): Name of the variable to set
				variable_value (Any): Value to assign to the variable
				
			Returns:
				bool: True on success, False on failure
				
			Raises:
				ValueError: If variable_name is a reserved variable
			"""
			if variable_name in self.agent.RESERVED_VARIABLES:
				raise ValueError(f"Cannot set reserved variable '{variable_name}'. Reserved variables: {self.agent.RESERVED_VARIABLES}")
			
			return self._set_internal(variable_name, variable_value)
		
		def _set_internal(self, variable_name: str, variable_value: Any) -> bool:
			"""
			Internal method to set variables without reserved variable protection.
			Used by server management methods to update server variables.
			
			Args:
				variable_name (str): Name of the variable to set
				variable_value (Any): Value to assign to the variable
				
			Returns:
				bool: True on success, False on failure
			"""
			data = {
				"stationThread": self.agent.station_thread_id,
				"attributeName": variable_name,
				"attributeValue": variable_value
			}
			
			response = self.agent._make_request("PUT", "/shared-state", data=data)
			
			return response is not None and response.get("success", False)
		
		def pull(self) -> Dict:
			"""
			Get ALL variables from SharedState API using list endpoint.
			
			Returns:
				dict: The attributes dict from response
			"""
			params = {
				"stationThread": self.agent.station_thread_id
			}
			
			response = self.agent._make_request("GET", "/shared-state/list", params=params)
			
			if response and response.get("success"):
				return response.get("attributes", {})
			
			return {}
		
		def push(self, json_object: Dict) -> bool:
			"""
			Bulk create/update variables using bulk-upsert endpoint.
			
			Args:
				json_object (Dict): Dictionary of variables to create/update
				
			Returns:
				bool: True on success, False on failure
				
			Raises:
				ValueError: If any variable name is reserved
			"""
			# Check for reserved variables in the input
			reserved_found = set(json_object.keys()) & self.agent.RESERVED_VARIABLES
			if reserved_found:
				raise ValueError(f"Cannot set reserved variables: {reserved_found}. Reserved variables: {self.agent.RESERVED_VARIABLES}")
			
			# Don't automatically add server variables - they should be explicitly managed
			variables = json_object.copy()
				
			data = {
				"stationThread": self.agent.station_thread_id,
				"variables": variables
			}
			
			response = self.agent._make_request("POST", "/shared-state/bulk-upsert", data=data)
			
			return response is not None and response.get("success", False)
		
		def sync(self, variable_name: str, langgraph_state: Any = None) -> Any:
			"""
			Sync variable from SharedState API to LangGraph state.
			
			If langgraph_state is provided, this method will:
			1. Get the variable from SharedState API
			2. Create state.sharedState if it doesn't exist
			3. Set state.sharedState[variable_name] = retrieved_value
			4. Return the updated state object
			
			Args:
				variable_name (str): Name of the variable to sync
				langgraph_state (Any, optional): LangGraph state object to update
				
			Returns:
				Any: If langgraph_state provided, returns the updated state object.
				     If no langgraph_state provided, returns just the variable value.
			"""
			# Get the variable from SharedState API
			variable_value = self.get(variable_name)
			
			# If LangGraph state is provided, update it and return the state
			if langgraph_state is not None:
				# Check if sharedState exists, if not create it
				if not hasattr(langgraph_state, 'sharedState'):
					langgraph_state.sharedState = {}
				elif langgraph_state.sharedState is None:
					langgraph_state.sharedState = {}
				
				# Set the variable in sharedState
				langgraph_state.sharedState[variable_name] = variable_value
				
				print(f"✅ Synced '{variable_name}' to LangGraph state.sharedState['{variable_name}'] = {variable_value}")
				
				# Return the updated state object
				return langgraph_state
			
			# Backward compatibility: return just the variable value if no state provided
			return variable_value
		
		def sync_all(self, langgraph_state: Any) -> Any:
			"""
			Sync ALL variables from SharedState API to LangGraph state.
			
			This method will:
			1. Pull all variables from SharedState API
			2. Create state.sharedState if it doesn't exist
			3. Replace state.sharedState with all variables from API
			4. Return the updated LangGraph state object
			
			Args:
				langgraph_state (Any): LangGraph state object to update
				
			Returns:
				Any: The updated LangGraph state object
			"""
			# Get all variables from SharedState API
			all_variables = self.pull()
			
			# Update LangGraph state
			if not hasattr(langgraph_state, 'sharedState'):
				langgraph_state.sharedState = {}
			
			# Replace sharedState with all variables from API
			langgraph_state.sharedState = all_variables.copy()
			
			print(f"✅ Synced ALL variables to LangGraph state.sharedState: {len(all_variables)} variables")
			return langgraph_state
		
		def sync_multiple(self, variable_names: list, langgraph_state: Any = None) -> Any:
			"""
			Sync multiple variables from SharedState API to LangGraph state.
			
			Args:
				variable_names (list): List of variable names to sync
				langgraph_state (Any, optional): LangGraph state object to update
				
			Returns:
				Any: If langgraph_state provided, returns the updated state object.
				     If no langgraph_state provided, returns dict with variable_name -> value mappings.
			"""
			results = {}
			
			# Create sharedState if needed
			if langgraph_state is not None:
				if not hasattr(langgraph_state, 'sharedState'):
					langgraph_state.sharedState = {}
				elif langgraph_state.sharedState is None:
					langgraph_state.sharedState = {}
			
			# Sync each variable
			for variable_name in variable_names:
				variable_value = self.get(variable_name)
				results[variable_name] = variable_value
				
				# Update LangGraph state if provided
				if langgraph_state is not None:
					langgraph_state.sharedState[variable_name] = variable_value
			
			if langgraph_state is not None:
				print(f"✅ Synced {len(variable_names)} variables to LangGraph state.sharedState")
				# Return the updated state object
				return langgraph_state
			
			# Backward compatibility: return just the results dict if no state provided
			return results
		
		def delete(self, variable_name: str) -> bool:
			"""
			Delete a variable from SharedState API.
			
			Args:
				variable_name (str): Name of the variable to delete
				
			Returns:
				bool: True on success, False on failure
				
			Raises:
				ValueError: If variable_name is a reserved variable
			"""
			if variable_name in self.agent.RESERVED_VARIABLES:
				raise ValueError(f"Cannot delete reserved variable '{variable_name}'. Reserved variables: {self.agent.RESERVED_VARIABLES}")
			
			params = {
				"stationThread": self.agent.station_thread_id,
				"attributeName": variable_name
			}
			
			response = self.agent._make_request("DELETE", "/shared-state", params=params)
			
			return response is not None and response.get("success", False)
		
		def exists(self, variable_name: str) -> bool:
			"""
			Check if a variable exists in SharedState API.
			
			Args:
				variable_name (str): Name of the variable to check
				
			Returns:
				bool: True if variable exists, False otherwise
			"""
			return self.get(variable_name) is not None
		
		def list_variables(self) -> list:
			"""
			Get list of all variable names for the station thread.
			
			Returns:
				list: List of variable names
			"""
			all_vars = self.pull()
			return list(all_vars.keys())

	class Server:
		"""
		Nested class for server management operations.
		
		Note: Server management methods use direct API calls to manage reserved variables
		(server, serverThread, serverCheckpoint, serverTaskType) which are arrays to manage multiple servers.
		Server status can only be "busy" or "idle".
		"""
		
		def __init__(self, agent: 'StationAgent'):
			self.agent = agent
		
		def load(self, serverThreadId: str, serverCheckpoint: str = "setup", serverIndex: int = 0, serverTaskType: str = "taskPlaceholder") -> Dict:
			"""
			Load server for a specific task type.
		
			Args:
				serverThreadId (str): The thread ID to assign to the server.
				serverCheckpoint (str, optional): The checkpoint to check against. Defaults to "setup".
				serverIndex (int, optional): The index of the server to load. Defaults to 0.
				serverTaskType (str, optional): The task type to assign. Defaults to "taskPlaceholder".
		
			Returns:
				dict: Status information about the load operation
			"""
						# Get current server states
			servers = self.agent.state.get("server")
			checkpoints = self.agent.state.get("serverCheckpoint")

			if servers is None or checkpoints is None or not isinstance(servers, list) or not isinstance(checkpoints, list):
				return {"status": "error", "error": "Server state variables are not initialized as arrays."}

			if not (0 <= serverIndex < len(servers)):
				return {"status": "error", "error": f"serverIndex {serverIndex} is out of bounds."}

			if servers[serverIndex] == "busy":
				return {"status": "busy", "error": "Server is busy"}

			if checkpoints[serverIndex] != serverCheckpoint:
				return {"status": "wrongCheckpoint", "error": f"Incorrect checkpoint. Expected {checkpoints[serverIndex]}, got {serverCheckpoint}"}

			# Update server state arrays
			servers[serverIndex] = "busy"
			
			threads = self.agent.state.get("serverThread") or ["idle"] * len(servers)
			task_types = self.agent.state.get("serverTaskType") or ["taskPlaceholder"] * len(servers)

			threads[serverIndex] = serverThreadId
			task_types[serverIndex] = serverTaskType
			
			# Persist changes using internal method to bypass reserved variable protection
			self.agent.state._set_internal("server", servers)
			self.agent.state._set_internal("serverCheckpoint", checkpoints)
			self.agent.state._set_internal("serverThread", threads)
			self.agent.state._set_internal("serverTaskType", task_types)

			return {"status": "loaded", "serverThread": serverThreadId}

		def unload(self, checkpoint: str = "setup", index: int = 0) -> Dict:
			"""
			Unload the server and set it to idle.
		
			Args:
				checkpoint (str): The checkpoint to set after unloading.
				index (int, optional): The index of the server to unload. Defaults to 0.
		
			Returns:
				dict: Status information about the unload operation
			"""
			servers = self.agent.state.get("server")
			if servers is None or not isinstance(servers, list):
				return {"status": "error", "error": "Server state is not initialized correctly."}

			if not (0 <= index < len(servers)):
				return {"status": "error", "error": f"serverIndex {index} is out of bounds."}

			if servers[index] == "idle":
				return {"status": "idle", "error": "Server is already idle"}

			servers[index] = "idle"
			checkpoints = self.agent.state.get("serverCheckpoint") or ["setup"] * len(servers)
			checkpoints[index] = checkpoint

			self.agent.state._set_internal("server", servers)
			self.agent.state._set_internal("serverCheckpoint", checkpoints)

			return {"status": "unloaded"}

		def avail(self, index: int = 0) -> Dict:
			"""
			Get current server availability status for a specific server.
		
			Args:
				index (int, optional): The index of the server to check. Defaults to 0.
		
			Returns:
				dict: Current server and serverThread values for the specified index.
				      Server status will be "busy" or "idle" only
			"""
			servers = self.agent.state.get("server")
			threads = self.agent.state.get("serverThread")
			checkpoints = self.agent.state.get("serverCheckpoint")
			task_types = self.agent.state.get("serverTaskType")

			if any(v is None or not isinstance(v, list) for v in [servers, threads, checkpoints, task_types]):
				return {"status": "error", "error": "Server state is not initialized correctly as arrays."}

			if not (0 <= index < len(servers)):
				return {"status": "error", "error": f"serverIndex {index} is out of bounds."}

			server_status = servers[index]
			if server_status not in self.agent.VALID_SERVER_STATUS:
				return {
					"server": "idle",  # Default to safe state
					"serverThread": threads[index],
					"serverCheckpoint": checkpoints[index],
					"serverTaskType": task_types[index],
					"warning": f"Invalid server status '{server_status}' detected, defaulting to 'idle'"
				}

			return {
				"server": server_status,
				"serverThread": threads[index],
				"serverCheckpoint": checkpoints[index],
				"serverTaskType": task_types[index]
			}
	


	async def pause(self, pause_tag: str, interrupt_func=None) -> Dict:
		"""
		Complete pause method that handles everything internally.
		Uses asyncio.to_thread() internally for SharedState operations,
		but calls interrupt() in the main thread context.
		"""
		print(f"🔄 Pausing graph with tag: '{pause_tag}'")
		
		# PART 1: Check if this is a resume situation first
		try:
			resume_value = await asyncio.to_thread(self.state.get, f"{pause_tag}-resume-value")
			if resume_value is not None:
				# This is a resume - clean up and return (no preparation needed)
				await asyncio.to_thread(self._cleanup_resume, pause_tag)
				return {
					"success": True,
					"status": "resumed", 
					"human_response": resume_value,
					"message": f"Resumed from tag '{pause_tag}'"
				}
		except Exception as e:
			return {"success": False, "error": f"Failed to check resume status: {str(e)}"}
		
		# PART 2: Preparation (in thread) - only if not a resume
		try:
			# Use asyncio.to_thread() internally for sync SharedState operations
			await asyncio.to_thread(self._prepare_pause_context, pause_tag)
			print("✅ Pause context prepared")
		except Exception as e:
			return {"success": False, "error": f"Failed to prepare pause context: {str(e)}"}
		
		# PART 3: Call interrupt() directly (in main thread) - sync operation
		if interrupt_func is not None:
			try:
				interrupt_info = {
					"pause_tag": pause_tag,
					"question_text": f"Graph paused with tag: {pause_tag}",
					"expected_format": "Resume command or use unpause() method"
				}
				
				print(f"🔄 Calling interrupt() directly for tag: {pause_tag}")
				
				# CRITICAL: This runs in main thread - no asyncio.to_thread()
				human_response = interrupt_func(interrupt_info)
				
				# THIS CODE RUNS AFTER RESUME
				print(f"🎉 Graph resumed! Human provided: {human_response}")
				
				# PART 4: Cleanup (in thread) - async operation
				await asyncio.to_thread(self._finalize_pause, pause_tag, human_response)
				
				return {
					"success": True,
					"status": "completed",
					"pause_tag": pause_tag,
					"message": f"Successfully paused and resumed with tag '{pause_tag}'",
					"human_response": human_response
				}
				
			except Exception as e:
				exception_name = type(e).__name__
				if "Interrupt" in exception_name:
					print(f"✅ Graph interrupted - waiting for unpause()")
					# Re-raise so graph pauses
					raise e
				else:
					return {"success": False, "error": f"Unexpected error: {str(e)}"}
		else:
			return {"success": False, "error": "No interrupt function provided"}

	def _prepare_pause_context(self, pause_tag: str):
		"""Sync helper method for pause preparation (runs in thread)"""
		import time
		
		# Check if already in use
		waitpoint_var = f"{pause_tag}-waitpoint"
		if self.state.get(waitpoint_var) == "paused":
			raise Exception(f"Pause tag '{pause_tag}' already in use")
		
		# Prepare values with fallbacks to ensure they're never None
		graph_url = self.current_graph_url or "not_provided"
		graph_assistant = self.current_graph_assistant_id or "not_provided"
		thread_id = self.graph_thread_id or "not_provided"
		api_key = self.langgraph_token or "not_provided"
		timestamp = time.time()
		
		print(f"🔧 Debug - Saving pause context for '{pause_tag}':")
		print(f"  - URL: {graph_url}")
		print(f"  - Assistant: {graph_assistant}")
		print(f"  - Thread ID: {thread_id}")
		print(f"  - API Key: {'***masked***' if api_key != 'not_provided' else 'not_provided'}")
		print(f"  - Timestamp: {timestamp}")
		
		# Store context with guaranteed non-None values
		result1 = self.state.set(f"{pause_tag}-waitpoint-url", graph_url)
		result2 = self.state.set(f"{pause_tag}-waitpoint-assistant", graph_assistant)
		result3 = self.state.set(f"{pause_tag}-waitpoint-threadId", thread_id)
		result4 = self.state.set(f"{pause_tag}-waitpoint-apikey", api_key)
		result5 = self.state.set(f"{pause_tag}-waitpoint-timestamp", timestamp)
		result6 = self.state.set(waitpoint_var, "paused")
		
		print(f"🔧 Debug - Save results: url={result1}, assistant={result2}, threadId={result3}, apikey={result4}, timestamp={result5}, waitpoint={result6}")
		
		# Verify variables were actually saved by reading them back
		saved_url = self.state.get(f"{pause_tag}-waitpoint-url")
		saved_apikey = self.state.get(f"{pause_tag}-waitpoint-apikey")
		saved_timestamp = self.state.get(f"{pause_tag}-waitpoint-timestamp")
		
		print(f"🔧 Debug - Verification read back:")
		print(f"  - URL saved: {saved_url}")
		print(f"  - API Key saved: {'***masked***' if saved_apikey and saved_apikey != 'not_provided' else saved_apikey}")
		print(f"  - Timestamp saved: {saved_timestamp}")

	def _cleanup_resume(self, pause_tag: str):
		"""Sync helper method for resume cleanup (runs in thread)"""
		try:
			self.state.delete(f"{pause_tag}-resume-value")
			self.state.delete(f"{pause_tag}-waitpoint")
		except:
			pass  # Ignore cleanup errors

	def _finalize_pause(self, pause_tag: str, human_response: str):
		"""Sync helper method for pause finalization (runs in thread)"""
		self.state.set(f"{pause_tag}-waitpoint", "completed")
		self.state.set(f"{pause_tag}-human-response", str(human_response))

	def unpause(self, pause_tag: str, resume_payload: str = "nextstep: Proceed") -> Dict:
		"""
		Unpause a previously paused StationAgent by calling the LangGraph Thread Unpause API.
		
		Args:
			pause_tag (str): The pause tag identifier
			resume_payload (str, optional): Payload to send to resume thread. Defaults to "nextstep: Proceed"
			
		Returns:
			Dict: Status information about the unpause operation
		"""
		print(f"Attempting to unpause with tag: '{pause_tag}'")
		
		# Step 1: Check if pause_tag-waitpoint exists and is "paused"
		waitpoint_var = f"{pause_tag}-waitpoint"
		waitpoint_status = self.state.get(waitpoint_var)
		
		if waitpoint_status != "paused":
			return {"success": False, "status": "tagNotPaused", "error": f"Pause tag '{pause_tag}' is not in paused state"}
		
		# Step 2: Get waitpoint variables
		waitpoint_url_var = f"{pause_tag}-waitpoint-url"
		waitpoint_assistant_var = f"{pause_tag}-waitpoint-assistant"
		waitpoint_thread_var = f"{pause_tag}-waitpoint-threadId"
		waitpoint_apikey_var = f"{pause_tag}-waitpoint-apikey"
		
		graph_url = self.state.get(waitpoint_url_var)
		graph_assistant_id = self.state.get(waitpoint_assistant_var)
		thread_id = self.state.get(waitpoint_thread_var)
		api_key = self.state.get(waitpoint_apikey_var)
		
		if not all([graph_url, graph_assistant_id, thread_id, api_key]):
			missing = []
			if not graph_url: missing.append("url")
			if not graph_assistant_id: missing.append("assistant_id")
			if not thread_id: missing.append("thread_id")
			if not api_key: missing.append("api_key")
			
			return {"success": False, "error": f"Missing waitpoint variables: {', '.join(missing)}"}
		
		# Step 3: Call the LangGraph Thread Unpause API
		try:
			# Prepare API request payload
			unpause_payload = {
				"thread_id": thread_id,
				"assistant_id": graph_assistant_id,
				"langgraph_url": graph_url,
				"api_key": api_key,
				"resume_payload": resume_payload
			}
			
			# Make API call to unpause endpoint
			unpause_url = f"{self.base_url}/shared-state/unpause"
			headers = {
				"Content-Type": "application/json",
				"Authorization": f"Bearer {self.token}"
			}
			
			response = requests.post(unpause_url, headers=headers, json=unpause_payload, timeout=30)
			
			if response.status_code != 200:
				return {
					"success": False, 
					"error": f"Unpause API request failed with status {response.status_code}: {response.text}"
				}
			
			api_result = response.json()
			
			if not api_result.get("success", False):
				return {
					"success": False,
					"error": f"Unpause API returned error: {api_result.get('error', 'Unknown error')}"
				}
			
			# Step 4: If successful, set resume value for pause() to detect
			resume_var = f"{pause_tag}-resume-value"
			self.state.set(resume_var, resume_payload)
			self.state.set(waitpoint_var, "unPaused")
			
			# Optional: Clean up waitpoint variables after successful unpause
			try:
				# Clean up the main waitpoint variables
				self.state.delete(waitpoint_url_var)
				self.state.delete(waitpoint_assistant_var)
				self.state.delete(waitpoint_thread_var)
				self.state.delete(waitpoint_apikey_var)
				
				# Clean up the timestamp variable created by pause
				self.state.delete(f"{pause_tag}-waitpoint-timestamp")
			except Exception as cleanup_error:
				print(f"Warning: Could not clean up waitpoint variables: {cleanup_error}")
			
			print(f"Successfully unpaused graph with tag: {pause_tag}")
			return {
				"success": True,
				"status": "unPaused",
				"pause_tag": pause_tag,
				"thread_id": thread_id,
				"assistant_id": graph_assistant_id,
				"message": f"Graph successfully unpaused from tag '{pause_tag}' using API",
				"response_preview": api_result.get("response_preview", ""),
				"unpause_method": "shared_state_api"
			}
			
		except requests.exceptions.RequestException as e:
			error_message = f"Network error calling unpause API: {str(e)}"
			print(f"ERROR: {error_message}")
			return {"success": False, "error": error_message}
		
		except json.JSONDecodeError as e:
			error_message = f"Invalid JSON response from unpause API: {str(e)}"
			print(f"ERROR: {error_message}")
			return {"success": False, "error": error_message}
		
		except Exception as e:
			error_message = f"Unexpected error during unpause operation: {str(e)}"
			print(f"ERROR: {error_message}")
			return {"success": False, "error": error_message}

class DocumentAgent:
    # Required for get_task function calls:
    TASKDOC_ROOT_URL="https://tm.msd.uat.cybersoftbpo.com"
    TASKDOC_USER="pull.doc.system.user"
    
    def __init__(self):
        """Initialize DocumentAgent with nested ESFuse class."""
        self.ESFuse = self.ESFuse(self)  # Initialize the nested class

    def get_task(self, task_id: str, api_token: str, auth_token: str) -> dict:
        """Get task details using task ID.
        
        GET /api/tools/v0/tasks/{TASK_ID}.json?auth_token=...&api_token=...
        
        Args:
            task_id (str): The task ID to retrieve details for
            api_token (str): TASKDOC API token
            auth_token (str): TASKDOC authentication token
            
        Returns:
            dict: Task response dict compatible with downstream processing
        """
        try:
            url = f"{self.TASKDOC_ROOT_URL}/api/tools/v0/tasks/{task_id}.json"
            parsed = urllib.parse.urlparse(url)
            query = urllib.parse.parse_qs(parsed.query)
            query['auth_token'] = [auth_token]
            query['api_token'] = [api_token]
            final_query = urllib.parse.urlencode(query, doseq=True)
            final_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, final_query, parsed.fragment))
            
            req = urllib.request.Request(final_url)
            req.add_header('Accept', 'application/json')
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                return {
                    "task_id": task_id,
                    "status": response.status,
                    "response": data,
                    "fallback_used": "get_task"
                }
        except Exception as ge:
            return {
                "task_id": task_id,
                "status": 0,
                "error": str(ge),
                "fallback_used": "get_task"
            }
     
    def screenshot_upload(self, screenshot_url: str, client_id: str, put_api: str, custom_filename: str = None, loan_id: str = None, package_type: str = None, data_object: dict = None) -> dict:

        try:
            import time
            response = requests.post(screenshot_url, json=data_object)
            response.raise_for_status()
            content_base64 = base64.b64encode(response.content).decode('utf-8')

            body = {
                "clientId": client_id,
                "content_base64": content_base64,
                "dataObject": data_object or {
                    "source_url": screenshot_url,
                    "timestamp": time.time(),
                    "upload_method": "cuteagent_library"
                }
            }
            if custom_filename:
                body["screenId"] = custom_filename  # Use custom filename as screen_id
            if loan_id:
                body["loanId"] = loan_id
            if package_type:
                body["packageType"] = package_type
            
            upload_response = requests.post(
                f"{put_api}/put",
                headers={"Authorization": "Bearer esfuse-token", "Content-Type": "application/json"},
                json=body,
                timeout=30
            )
        
            if upload_response.status_code == 200:
                result = upload_response.json()
                return {
                    "success": True,
                    "screen_id": result["screenId"],  # Auto UUID or custom filename
                    "client_id": result["clientId"],
                    "loan_id": result.get("loanId"),
                    "package_type": result.get("PackageType") or result.get("packageType"),
                    "screen_id_generated": result.get("screenIdGenerated", False),
                    "data_object_stored": result.get("dataObjectStored", False)
                }
            else:
                return {"success": False, "error": f"Upload failed: {upload_response.text}"}
        except Exception as e:
            pass
    
    class ESFuse:
        """Nested class for ESFuse functionality with multiple sub-functions."""
        
        def __init__(self, agent: 'DocumentAgent'):
            self.agent = agent


        def pull_data(self, client_id: str, loan_id: str, esfuse_token: str, get_api_base: str):
            """
            Makes an API call to retrieve loan data using the loan endpoint and returns both raw and parsed data.
                
            Args:
                client_id (str): The client ID for the loan
                loan_id (str): The loan ID to retrieve
                esfuse_token (str): The ESFuse authentication token
                get_api_base (str): The base URL for the ESFuse API
                    
            Returns:
                dict: JSON object containing both raw and parsed data or error information
            """
            try:
                if not client_id or not loan_id or not esfuse_token or not get_api_base:
                    return {
                        "success": False,
                        "error": "client_id, loan_id, esfuse_token, and get_api_base are required"
                    }
                
                # Use loan endpoint instead of doc endpoint
                api_url = f"{get_api_base}/loan?clientId={client_id}&loanId={loan_id}"
                
                # Set up headers with the ESFuse token
                headers = {
                    "Authorization": f"Bearer {esfuse_token}"
                }
                
                # Make the API call
                response = requests.get(api_url, headers=headers, timeout=30)
                
                # Check if the request was successful
                if response.status_code == 200:
                    raw_data = response.json()
                    
                    # Parse important loan details
                    parsed_data = self._parse_loan_data(raw_data)
                    
                    return {
                        "success": True,
                        "raw": raw_data,
                        "parsed": parsed_data,
                        "api_url": api_url,
                        "client_id": client_id,
                        "loan_id": loan_id
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API call failed with status {response.status_code}: {response.text}",
                        "api_url": api_url
                    }
                
            except requests.exceptions.RequestException as e:
                return {
                    "success": False,
                    "error": f"API request failed: {str(e)}"
                }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse API response as JSON: {str(e)}"
                }
            except Exception as e:
                return {
                    "success": False, 
                    "error": f"Error extracting data: {str(e)}"
                }

        def _parse_loan_data(self, raw_data: dict) -> dict:
            """
            Parse important loan details from the raw API response.
            
            Args:
                raw_data (dict): Raw JSON response from the loan API
                
            Returns:
                dict: Parsed loan information with key details
            """
            try:
                parsed = {}
                
                # Extract top-level loan info
                parsed["client_id"] = raw_data.get("clientId")
                parsed["loan_id"] = raw_data.get("loanId")
                
                # Extract encompass GUID from pull_containers
                if "pull_containers" in raw_data:
                    pull_containers = raw_data["pull_containers"]
                    parsed["encompass_loan_guid"] = pull_containers.get("encompass_loan_guid")
                    parsed["workflow_state"] = pull_containers.get("workflow_state")
                
                # Extract main loan details from loaninfo.load_loan_by_guid.Loan
                loan_path = raw_data.get("loaninfo", {}).get("load_loan_by_guid", {}).get("Loan", {})
                
                if loan_path:
                    # Basic loan information
                    parsed["loan_number"] = loan_path.get("LoanNumber")
                    parsed["loan_amount"] = loan_path.get("LoanAmount")
                    parsed["interest_rate"] = loan_path.get("InterestRate")
                    parsed["loan_type"] = loan_path.get("LoanType")
                    parsed["loan_program"] = loan_path.get("LoanProgram")
                    parsed["loan_purpose"] = loan_path.get("LoanPurpose")
                    parsed["occupancy"] = loan_path.get("Occupancy")
                    parsed["lender"] = loan_path.get("Lender")
                    
                    # Property information
                    parsed["property_address"] = loan_path.get("Address")
                    parsed["property_city"] = loan_path.get("City")
                    parsed["property_state"] = loan_path.get("State")
                    parsed["property_zip"] = loan_path.get("ZipCode")
                    
                    # Extract Form1003Content (main application data)
                    form1003 = loan_path.get("Form1003Content", {})
                    if form1003:
                        # Borrower information
                        borrower = form1003.get("borrower", {})
                        parsed["borrower"] = {
                            "first_name": borrower.get("firstName"),
                            "last_name": borrower.get("lastName"),
                            "middle_name": borrower.get("middleName"),
                            "email": borrower.get("email"),
                            "ssn": form1003.get("SSN"),
                            "dob": form1003.get("DOB"),
                            "home_phone": form1003.get("homePhone"),
                            "business_phone": form1003.get("businessPhone"),
                            "marital_status": form1003.get("status"),
                            "gross_monthly_income": form1003.get("borrowerGrossMonthlyIncome")
                        }
                        
                        # Co-Borrower information
                        co_borrower = form1003.get("coBorrower", {})
                        if co_borrower:
                            parsed["co_borrower"] = {
                                "first_name": co_borrower.get("firstName"),
                                "last_name": co_borrower.get("lastName"),
                                "middle_name": co_borrower.get("middleName"),
                                "email": co_borrower.get("email"),
                                "ssn": form1003.get("coBorrowerSSN"),
                                "dob": form1003.get("coBorrowerDOB"),
                                "home_phone": form1003.get("coBorrowerHomePhone"),
                                "business_phone": form1003.get("coBorrowerBusinessPhone"),
                                "marital_status": form1003.get("coBorrowerStatus"),
                                "gross_monthly_income": form1003.get("coBorrowerGrossMonthlyIncome"),
                                "position": form1003.get("coBorrowerPosition")
                            }
                        
                        # Present Address
                        present_address = form1003.get("presentAddress", {})
                        if present_address:
                            parsed["borrower_current_address"] = {
                                "address1": present_address.get("address1"),
                                "address2": present_address.get("address2"),
                                "city": present_address.get("city"),
                                "state": present_address.get("state"),
                                "zip_code": present_address.get("zipCode"),
                                "own_or_rent": present_address.get("ownOrRent"),
                                "years": present_address.get("years"),
                                "months": present_address.get("months")
                            }
                        
                        # Subject Property Address
                        subject_property = form1003.get("subjectPropertyAddress", {})
                        if subject_property:
                            parsed["subject_property_address"] = {
                                "address1": subject_property.get("address1"),
                                "address2": subject_property.get("address2"),
                                "city": subject_property.get("city"),
                                "state": subject_property.get("state"),
                                "zip_code": subject_property.get("zipCode")
                            }
                        
                        # Employment Information
                        employer = form1003.get("nameOfEmployer", {})
                        if employer:
                            parsed["borrower_employment"] = {
                                "employer_name": employer.get("name"),
                                "position": form1003.get("position"),
                                "years_on_job": form1003.get("yrsOnThisJob", {}),
                                "years_in_line_of_work": form1003.get("yrsEmployedInThisLineOfWork", {}),
                                "self_employed": form1003.get("selfEmployed")
                            }
                            
                        # Employment Address
                        employer_address = form1003.get("addressOfEmployer", {})
                        if employer_address:
                            parsed["borrower_employment"]["employer_address"] = {
                                "address1": employer_address.get("address1"),
                                "address2": employer_address.get("address2"),
                                "city": employer_address.get("city"),
                                "state": employer_address.get("state"),
                                "zip_code": employer_address.get("zipCode")
                            }
                        
                        # Co-Borrower Employment
                        co_employer = form1003.get("coBorrowerNameOfEmployer", {})
                        if co_employer:
                            parsed["co_borrower_employment"] = {
                                "employer_name": co_employer.get("name"),
                                "position": form1003.get("coBorrowerPosition"),
                                "years_on_job": form1003.get("coBorrowerYrsOnThisJob", {}),
                                "years_in_line_of_work": form1003.get("coBorrowerYrsEmployedInThisLineOfWork", {}),
                                "self_employed": form1003.get("coBorrowerSelfEmployed")
                            }
                        
                        # Bank Accounts
                        banks = form1003.get("banks", [])
                        if banks:
                            parsed["bank_accounts"] = []
                            for bank in banks:
                                bank_info = {
                                    "bank_name": bank.get("bank", {}).get("name"),
                                    "account_number": bank.get("accountNumber"),
                                    "account_type": bank.get("accountType"),
                                    "ending_balance": bank.get("endingBalance"),
                                    "verification_for": bank.get("verificationFor")
                                }
                                parsed["bank_accounts"].append(bank_info)
                        
                        # Liabilities
                        liabilities = form1003.get("liabilities", [])
                        if liabilities:
                            parsed["liabilities"] = []
                            for liability in liabilities:
                                liability_info = {
                                    "company_name": liability.get("company", {}).get("name"),
                                    "account_number": liability.get("accountNumber"),
                                    "account_type": liability.get("accountType"),
                                    "unpaid_balance": liability.get("unpaidBalance"),
                                    "payment_per_month": liability.get("paymentPerMonths"),
                                    "paid_off_status": liability.get("paidOffStatusIndicator"),
                                    "verification_for": liability.get("verificationFor")
                                }
                                parsed["liabilities"].append(liability_info)
                        
                        # Loan terms
                        parsed["loan_terms"] = {
                            "loan_amount": form1003.get("amount"),
                            "number_of_months": form1003.get("noOfMonths"),
                            "interest_rate": form1003.get("interestRate"),
                            "amortization_type": form1003.get("amortizationType"),
                            "mortgage_applied_for": form1003.get("mortgageAppliedFor"),
                            "purpose_of_loan": form1003.get("purposeOfLoan")
                        }
                    
                    # Loan Associates (Loan Officer, etc.)
                    loan_associates = loan_path.get("LoanAssociates", {})
                    if loan_associates:
                        parsed["loan_team"] = {}
                        for role, associates in loan_associates.items():
                            if associates and len(associates) > 0:
                                primary_associate = associates[0]  # Get first associate
                                parsed["loan_team"][role.lower().replace(" ", "_")] = {
                                    "full_name": primary_associate.get("FullName"),
                                    "email": primary_associate.get("Email"),
                                    "role": primary_associate.get("Role"),
                                    "primary": primary_associate.get("Primary", False)
                                }
                
                return parsed
                
            except Exception as e:
                return {
                    "parse_error": f"Error parsing loan data: {str(e)}",
                    "partial_data": parsed if 'parsed' in locals() else {}
                }

        def _get_simple_value(self, data: dict, key_path: str):
            """
            Simple helper method to get nested values using dot notation (e.g., 'dataObject.fields.address').
            Supports array indexing (e.g., 'array.0.field').
            
            Args:
                data (dict): The JSON data to search in
                key_path (str): The key path (e.g., 'dataObject.fields.address' or 'array.0.field')
                
            Returns:
                Any: The value if found, None otherwise
            """
            try:
                keys = key_path.split('.')
                current_data = data
                
                for key in keys:
                    if isinstance(current_data, dict) and key in current_data:
                        current_data = current_data[key]
                    elif isinstance(current_data, list) and key.isdigit():
                        index = int(key)
                        if 0 <= index < len(current_data):
                            current_data = current_data[index]
                        else:
                            return None
                    else:
                        return None
                        
                return current_data
            except:
                return None

        def push_data(self, field_updates: dict, client_id: str, loan_id: str, get_api_base: str, esfuse_token: str, base_url: str, access_token: str):
            """
            Pushes field updates to Encompass via write_loan_data endpoint.
            First retrieves the encompass_loan_guid using the loan API, then pushes updates.
            Based on the ESFuse API structure from the Postman collection.
            
            Args:
                field_updates (dict): Dictionary of field updates to push to Encompass
                client_id (str): The client ID for the loan lookup
                loan_id (str): The loan ID for the loan lookup
                get_api_base (str): The base URL for the loan lookup API
                esfuse_token (str): The ESFuse authentication token for loan lookup
                base_url (str): The base URL for the ESFuse API
                access_token (str): The access token for the ESFuse API
                
            Returns:
                dict: Success status and Encompass update results
            """
            try:
                if not field_updates:
                    return {
                        "success": False,
                        "error": "No field updates provided"
                    }
                
                if not all([client_id, loan_id, get_api_base, esfuse_token, base_url, access_token]):
                    return {
                        "success": False,
                        "error": "client_id, loan_id, get_api_base, esfuse_token, base_url and access_token are required"
                    }
                
                # STEP 1: Get the encompass_loan_guid using the loan API
                loan_api_url = f"{get_api_base}/loan?clientId={client_id}&loanId={loan_id}"
                loan_headers = {
                    "Authorization": f"Bearer {esfuse_token}"
                }
                
                loan_response = requests.get(loan_api_url, headers=loan_headers, timeout=30)
                
                if loan_response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Failed to get loan GUID. API returned status {loan_response.status_code}: {loan_response.text}"
                    }
                
                loan_data = loan_response.json()
                
                # Flatten the JSON and search for any key ending with "encompass_loan_guid"
                encompass_loan_guid = self._find_encompass_guid(loan_data)
                
                if not encompass_loan_guid:
                    return {
                        "success": False,
                        "error": f"No key ending with 'encompass_loan_guid' found in loan API response. Available top-level keys: {list(loan_data.keys())}"
                    }
                
                # STEP 2: Prepare request body matching the Postman collection structure
                request_body = {
                    "encompass_loan_guid": encompass_loan_guid,
                    "json_data": json.dumps(field_updates)  # Convert dict to JSON string
                }
                
                # Construct the write_loan_data endpoint URL
                write_loan_url = f"{base_url}/api/v1/write_loan_data?token={access_token}"
                
                # Make POST request to write_loan_data endpoint
                response = requests.post(
                    write_loan_url,
                    json=request_body,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "encompass_loan_guid": encompass_loan_guid,
                        "fields_updated": list(field_updates.keys()),
                        "response": response.json() if response.content else None,
                        "status_code": response.status_code
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Encompass API request failed with status {response.status_code}",
                        "response_text": response.text,
                        "status_code": response.status_code
                    }
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Encompass update error: {str(e)}"
                }

        def _find_encompass_guid(self, data, parent_key=""):
            """
            Recursively flatten JSON and find any key ending with 'encompass_loan_guid'.
            
            Args:
                data: JSON data to search (dict, list, or primitive)
                parent_key: Current path in the JSON structure
                
            Returns:
                str: The first GUID value found, or None if not found
            """
            try:
                if isinstance(data, dict):
                    for key, value in data.items():
                        current_key = f"{parent_key}.{key}" if parent_key else key
                        
                        # Check if current key ends with "encompass_loan_guid"
                        if key.endswith("encompass_loan_guid") and value:
                            return value
                        
                        # Recursively search in nested structures
                        if isinstance(value, (dict, list)):
                            result = self._find_encompass_guid(value, current_key)
                            if result:
                                return result
                                
                elif isinstance(data, list):
                    for i, item in enumerate(data):
                        current_key = f"{parent_key}[{i}]" if parent_key else f"[{i}]"
                        result = self._find_encompass_guid(item, current_key)
                        if result:
                            return result
                
                return None
                
            except Exception as e:
                return None

        def pull_doc(self, api_base: str, token: str, client_id: str, doc_id: str):
            """
            Downloads a PDF document from the ESFuse API based on the new curl command structure.
            
            Args:
                api_base (str): The base URL for the ESFuse API 
                token (str): The authorization token (e.g., "esfuse-token")
                client_id (str): The client ID (e.g., "Fintor")
                doc_id (str): The document ID (e.g., "URLA-2019-Borrower-v28")
                
            Returns:
                dict: Success status and file path where PDF was saved
            """
            try:
                # Construct the API URL based on the curl command
                api_url = f"{api_base}/doc?clientId={client_id}&docId={doc_id}"
                

                
                # Set up headers with Bearer token
                headers = {
                    "Authorization": f"Bearer {token}"
                }
                
                # Make GET request to download the document
                response = requests.get(api_url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    # Try to parse as JSON first
                    try:
                        response_json = response.json()
                        
                        # Check if it's a JSON response with document info
                        if isinstance(response_json, dict):
                            return {
                                "success": True,
                                "response_type": "json",
                                "response_data": response_json,
                                "api_url": api_url,
                                "client_id": client_id,
                                "doc_id": doc_id
                            }
                        else:
                            # Fall back to PDF handling
                            raise ValueError("Response is not a valid JSON document")
                            
                    except (json.JSONDecodeError, ValueError):
                        # If not JSON, treat as PDF download
                        # Create filename for local storage
                        filename = f"{doc_id}.pdf"
                        
                        # Save the PDF file locally
                        with open(filename, 'wb') as f:
                            f.write(response.content)
                        
                        return {
                            "success": True,
                            "response_type": "pdf",
                            "filename": filename,
                            "file_size": len(response.content),
                            "api_url": api_url,
                            "client_id": client_id,
                            "doc_id": doc_id
                        }
                    
                else:
                    return {
                        "success": False,
                        "error": f"API request failed with status {response.status_code}",
                        "response_text": response.text,
                        "status_code": response.status_code
                    }
                    
            except requests.exceptions.RequestException as e:
                return {
                    "success": False,
                    "error": f"Request failed: {str(e)}"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}"
                }

        def push_doc(self, 
                    client_id: str, 
                    doc_id: str, 
                    token: str, 
                    api_base: str, 
                    submission_type: str = "Initial Submission", 
                    auto_lock: bool = False, 
                    taskdoc_api_token: str = None, 
                    taskdoc_auth_token: str = None,
                    # Direct submission parameters (bypass DocRepo/TaskDoc extraction)
                    direct_loan_id: str = None,
                    direct_document_ids: list = None,
                    direct_base_url: str = None,
                    direct_api_token: str = None):
            """
            Creates a new loan submission and associates documents with it. 
            
            Two modes of operation:
            1. FULL WORKFLOW: Extract data from DocRepo -> get_task -> create submission
            2. DIRECT MODE: Skip extraction and create submission directly with provided parameters
            
            Args:
                client_id (str): DocRepo client ID
                doc_id (str): DocRepo document ID  
                token (str): DocRepo authentication token
                api_base (str): DocRepo API base URL
                submission_type (str, optional): Type of submission (default: "Initial Submission")
                auto_lock (bool, optional): Locks the submission automatically after creation (default: False)
                taskdoc_api_token (str, optional): TASKDOC API token for get_task call
                taskdoc_auth_token (str, optional): TASKDOC authentication token for get_task call
                
                # DIRECT MODE PARAMETERS (bypass extraction workflow)
                direct_loan_id (str, optional): Loan ID for direct submission
                direct_document_ids (list, optional): List of document IDs for direct submission
                direct_base_url (str, optional): Base URL for direct submission API
                direct_api_token (str, optional): API token for direct submission
                
            Returns:
                dict: Success status, extracted/provided data, and API response results
            """
            try:
                # Check if direct mode parameters are provided
                if (direct_loan_id and direct_document_ids and direct_base_url and direct_api_token):
                    extracted_fields = {
                        "mode": "direct",
                        "taskdoc_loan_id": direct_loan_id,
                        "taskdoc_document_ids": direct_document_ids,
                        "taskdoc_root_url": direct_base_url,
                        "taskdoc_api_token": direct_api_token
                    }
                else:
                    # STEP 1: Extract DocRepo data first (including taskId)
                    docrepo_url = f"{api_base}/doc?clientId={client_id}&docId={doc_id}"
                    docrepo_headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                    
                    try:
                        docrepo_response = requests.get(docrepo_url, headers=docrepo_headers, timeout=30)
                        if docrepo_response.status_code == 200:
                            docrepo_data = docrepo_response.json()
                            
                            # Extract only essential fields for push_doc workflow
                            extracted_fields = {
                                "mode": "full_workflow",
                                "taskId": docrepo_data.get("taskId"),
                                "loanId": docrepo_data.get("loanId"),
                                "clientId": docrepo_data.get("clientId"),
                                "docId": docrepo_data.get("docId")
                            }
                            
                            # STEP 2: Call get_task if taskId exists and tokens are provided
                            task_id = extracted_fields.get('taskId')
                            if task_id and taskdoc_api_token and taskdoc_auth_token:
                                task_details = self.agent.get_task(task_id, taskdoc_api_token, taskdoc_auth_token)
                                extracted_fields['task_details'] = task_details
                                
                                # Extract only required fields from TaskDoc response
                                if task_details.get('status') == 200 and task_details.get('response'):
                                    task_response = task_details.get('response', {})
                                    
                                    # Extract document IDs from parameters.created_result_document_ids
                                    parameters = task_response.get('parameters', {})
                                    document_ids = parameters.get('created_result_document_ids', [])
                                    extracted_fields['taskdoc_document_ids'] = document_ids
                                    
                                    # Extract loan ID from parameters.loan_id
                                    taskdoc_loan_id = parameters.get('loan_id')
                                    extracted_fields['taskdoc_loan_id'] = taskdoc_loan_id
                                    
                                    # Extract API token from app.default_request_data.api_token
                                    app = task_response.get('app', {})
                                    default_request_data = app.get('default_request_data', {})
                                    taskdoc_api_token_extracted = default_request_data.get('api_token')
                                    extracted_fields['taskdoc_api_token'] = taskdoc_api_token_extracted
                                    
                                    # Extract root URL from app.tool_parameters.root_url
                                    tool_parameters = app.get('tool_parameters', {})
                                    taskdoc_root_url = tool_parameters.get('root_url')
                                    extracted_fields['taskdoc_root_url'] = taskdoc_root_url
                                    
                                else:
                                    pass
                                    
                            elif task_id and (not taskdoc_api_token or not taskdoc_auth_token):
                                pass
                            else:
                                pass
                            
                        else:
                            extracted_fields = {"docrepo_error": f"API failed with status {docrepo_response.status_code}"}
                            
                    except Exception as docrepo_error:
                        extracted_fields = {"docrepo_error": str(docrepo_error)}
                
                # STEP 3: Push documents to submission endpoint using extracted data
                if 'taskdoc_loan_id' in extracted_fields and 'taskdoc_root_url' in extracted_fields and 'taskdoc_api_token' in extracted_fields and 'taskdoc_document_ids' in extracted_fields:
                    loan_id = extracted_fields['taskdoc_loan_id']
                    base_url = extracted_fields['taskdoc_root_url']
                    api_token = extracted_fields['taskdoc_api_token']
                    document_ids = extracted_fields['taskdoc_document_ids']
                    
                    if loan_id and base_url and api_token and document_ids:
                        # Construct the submission endpoint URL (handle trailing slashes)
                        base_url_clean = base_url.rstrip('/')
                        submission_url = f"{base_url_clean}/api/v5/loans/{loan_id}/submissions?token={api_token}"
                        
                        # Prepare the request body
                        submission_body = {
                            "document_ids": document_ids,
                            "submission_type": submission_type,
                            "auto_lock": auto_lock
                        }
                        
                        # Set up headers for the submission request
                        submission_headers = {
                            "Content-Type": "application/json"
                        }
                        
                        try:
                            # Make the POST request to create the submission
                            submission_response = requests.post(
                                submission_url, 
                                headers=submission_headers, 
                                json=submission_body, 
                                timeout=30
                            )
                            
                            if submission_response.status_code in [200, 201]:
                                submission_data = submission_response.json() if submission_response.content else {}
                                
                                # Add submission results to extracted fields (include entire response)
                                extracted_fields['submission_result'] = {
                                    "success": True,
                                    "status_code": submission_response.status_code,
                                    "response": submission_data,  # Full response included
                                    "submission_url": submission_url,
                                    "submission_body": submission_body,
                                    "full_response": submission_data  # Also available as full_response for clarity
                                }
                                
                            else:
                                # Try to parse response as JSON for better error details
                                try:
                                    error_json = submission_response.json()
                                except:
                                    error_json = None
                                
                                extracted_fields['submission_result'] = {
                                    "success": False,
                                    "status_code": submission_response.status_code,
                                    "error": f"Submission API failed with status {submission_response.status_code}",
                                    "response_text": submission_response.text,
                                    "response_headers": dict(submission_response.headers),
                                    "submission_url": submission_url,
                                    "submission_body": submission_body
                                }
                                
                        except Exception as submission_error:
                            extracted_fields['submission_result'] = {
                                "success": False,
                                "error": f"Submission request error: {str(submission_error)}",
                                "submission_url": submission_url,
                                "submission_body": submission_body
                            }
                    else:
                        extracted_fields['submission_result'] = {
                            "success": False,
                            "error": "Missing required extracted data for submission"
                        }
                else:
                    extracted_fields['submission_result'] = {
                        "success": False,
                        "error": "TaskDoc data extraction incomplete - cannot create submission"
                    }

                # Return the complete results including submission
                return {
                    "success": True,
                    "docrepo_fields": extracted_fields,
                    "message": "DocRepo data extracted and submission attempted"
                }
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": f"DocRepo extraction error: {str(e)}"
                }