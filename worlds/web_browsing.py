import json
from datetime import datetime
import uuid

from worlds.world import World
from typing import List, Dict, Optional
import os
FUNCTION_SYSTEM_PROMPT = """
You are a helpful assistant responsible for simulating web browsing behavior.
You interact with a database that tracks the current and previous URLs.
Always use the appropriate functions to move between URLs, retrieve page contents from local HTML files, and record navigation history.
Never browse independently — every action must go through the appropriate function.
"""

DECISION_SYSTEM_PROMPT = """
You are a helpful assistant responsible for evaluating whether a web browsing goal has been accomplished.
You have access to a database that stores the user's current and previous URLs.
Determine whether the user's objective has been met based on executed browsing actions and the final browsing state.
"""

WORLD_STATE_DESCRIPTION = "Web Browsing State: {}"

class WebBrowsing(World):
    def __init__(self):
        self.world_state_description = WORLD_STATE_DESCRIPTION
        self.function_system_prompt = FUNCTION_SYSTEM_PROMPT
        self.decision_system_prompt = DECISION_SYSTEM_PROMPT
        
        self.tool_definitions = self._get_tool_definitions()
        self._init_world_state = {
            "current_url": None,
            "history": []  # Stores previously visited URLs
        }
        self.reset_world_state()
        self.prompts = [
            {
                "prompt_id": "web_browsing_1",
                "prompt": "Move to 'page1.html' and retrieve its HTML source.",
                "setup_functions": [], 
                "expected_sequences": [["move_to_url(file_name='page1.html')", "get_page_source()"]]
            },
            {
                "prompt_id": "web_browsing_2",
                "prompt": "Navigate to 'page2.html', then search for the text: 'Matt then discusses his former job,'.",
                "setup_functions": [], 
                "expected_sequences": [["move_to_url(file_name='page2.html')", "find_text_in_page(text='Matt then discusses his former job,')"]]
            },
            {
                "prompt_id": "web_browsing_3",
                "prompt": "Go to 'page3.html', retrieve the page source, and confirm the current URL.",
                "setup_functions": [], 
                "expected_sequences": [["move_to_url(file_name='page3.html')", "get_page_source()", "get_current_url()"]]
            },
            {
                "prompt_id": "web_browsing_4",
                "prompt": "Move to 'page1.html'. Then, move to 'page2.html'. Then go back to the previous page.",
                "setup_functions": [], 
                "expected_sequences": [["move_to_url(file_name='page1.html')","move_to_url(file_name='page2.html')", "go_back()"]]
            },
            {
                "prompt_id": "web_browsing_5",
                "prompt": "Retrieve the current URL before and after navigating to 'page3.html'.",
                "setup_functions": [], 
                "expected_sequences": [["get_current_url()", "move_to_url('page3.html')", "get_current_url()"]]
            },
            {
                "prompt_id": "web_browsing_6",
                "prompt": "View the browsing history after visiting 'page3.html', 'page1.html' and 'page2.html' in that specific order.",
                "setup_functions": [], 
                "expected_sequences": [["move_to_url(file_name='page3.html')", "move_to_url(file_name='page1.html')", "move_to_url(file_name='page2.html')", "view_browsing_history()"]]
            }
        ]

    def move_to_url(self, file_name: str) -> str:
        """
        Navigates to a given web page by loading its HTML file.
        
        :param file_name: The name of the HTML file to navigate to.
        :return: Confirmation message.
        """
        if os.path.exists(file_name):
            if self.world_state["current_url"]:
                self.world_state["history"].append(self.world_state["current_url"])
            self.world_state["current_url"] = file_name
            return f"Moved to {file_name}."
        return "Page not found."

    def get_page_source(self, ) -> Optional[str]:
        """
        Retrieves the HTML source of the current page.
        
        :return: The HTML source of the current page, or None if no page is loaded.
        """
        if self.world_state["current_url"]:
            with open(self.world_state["current_url"], "r", encoding="utf-8") as file:
                return file.read()
        return "No page loaded."

    def find_text_in_page(self, text: str) -> bool:
        """
        Searches for a given text in the current page's HTML source.
        
        :param text: The text to search for.
        :return: True if the text is found, False otherwise.
        """
        if self.world_state["current_url"]:
            with open(self.world_state["current_url"], "r", encoding="utf-8") as file:
                return text in file.read()
        return False

    def get_current_url(self) -> Optional[str]:
        """
        Retrieves the currently loaded page's file name.
        
        :return: The name of the currently loaded HTML file, or None if no page is loaded.
        """
        return self.world_state["current_url"]

    def go_back(self) -> str:
        """
        Navigates back to the previous page if available.
        
        :return: Confirmation message.
        """
        if self.world_state["history"]:
            self.world_state["current_url"] = self.world_state["history"].pop()
            return f"Went back to {self.world_state['current_url']}."
        self.world_state["current_url"] = None
        return "No previous page to go back to."

    def view_browsing_history(self) -> List[str]:
        """
        Returns the list of previously visited URLs.
        
        :return: List of visited URLs.
        """
        return self.world_state["history"]
