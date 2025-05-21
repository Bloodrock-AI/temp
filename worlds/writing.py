import json
from datetime import datetime
import uuid

from worlds.world import World
from typing import List, Dict, Optional
import random

FUNCTION_SYSTEM_PROMPT = """
You are a helpful assistant responsible for constructing grammatically correct sentences.
You interact with a database that stores the in-progress sentence.
Always use the designated writing expected_sequence to build or modify the sentence based on the user’s request.
Never write text directly — always call the appropriate function to add specific parts of speech.
"""

DECISION_SYSTEM_PROMPT = """
You are a helpful assistant responsible for evaluating whether a complete and correct sentence has been formed.
You have access to a database that contains the constructed sentence.
Determine whether the sentence meets the grammatical and structural requirements of the user's prompt.
"""

WORLD_STATE_DESCRIPTION = "Sentence State: {}"


class Writing(World):
    def __init__(self):
        self.world_state_description = WORLD_STATE_DESCRIPTION
        self.function_system_prompt = FUNCTION_SYSTEM_PROMPT
        self.decision_system_prompt = DECISION_SYSTEM_PROMPT
        
        self.tool_definitions = self._get_tool_definitions()
        self._init_world_state = {
            "sentence": "",
            "word_pools": {
                "nouns": ["dog", "cat", "car", "house", "tree", "bird"],
                "verbs": ["runs", "jumps", "drives", "flies", "sleeps"],
                "adjectives": ["fast", "blue", "big", "small", "happy"],
                "articles": ["a", "the"],
                "prepositions": ["on", "under", "beside", "near", "above"]
            }
        }
        self.world_state = self._init_world_state
        self.prompts = [
            {
                "prompt": "Write a simple sentence describing 'the big cat runs'.",
                "expected_sequence": [
                    "add_article(article='the')",
                    "add_adjective(adjective='big')",
                    "add_noun(noun='cat')",
                    "add_verb(verb='runs')",
                    "complete_sentence()"
                ]
            },
            {
                "prompt": "Write a sentence about a small dog sleeping under a tree. Use present simple tense for the verb",
                "expected_sequence": [
                    "add_article(article='a')",
                    "add_adjective(adjective='small')",
                    "add_noun(noun='dog')",
                    "add_verb(verb='sleeps')",
                    "add_preposition(preposition='under')",
                    "add_article(article='a')",
                    "add_noun(noun='tree')",
                    "complete_sentence()"
                ]
            },
            {
                "prompt": "Form a sentence about 'a fast bird' that 'flies beside the house'.",
                "expected_sequence": [
                    "add_article(article='the')",
                    "add_adjective(adjective='fast')",
                    "add_noun(noun='bird')",
                    "add_verb(verb='flies')",
                    "add_preposition(preposition='beside')",
                    "add_article(article='the')",
                    "add_noun(noun='house')",
                    "complete_sentence()"
                ]
            },
            {
                "prompt": "Create a sentence consisting of the words: 'runs', 'the', 'dog', 'happy'. Put them in the correct order first.",
                "expected_sequence": [
                    "add_article(article='the')",
                    "add_adjective(adjective='happy')",
                    "add_noun(noun='dog')",
                    "add_verb(verb='runs')",
                    "complete_sentence()"
                ]
            },
            {
                "prompt": "Construct a sentence where 'the blue cat jumps above a small X'. Replace 'X' with the available synonym word for 'large plant' in the 'nouns' list.",
                "expected_sequence": [
                    "add_article(article='the')",
                    "add_adjective(adjective='blue')",
                    "add_noun(noun='cat')",
                    "add_verb(verb='jumps')",
                    "add_preposition(preposition='above')",
                    "add_article(article='a')",
                    "add_adjective(adjective='small')",
                    "add_noun(noun='tree')",
                    "complete_sentence()"
                ]
            },
            {
                "prompt": "Construct the sentence 'the bird flies', finalize it, then repeat the entire process again.",
                "expected_sequence": [
                    "add_article(article='the')",
                    "add_noun(noun='bird')",
                    "add_verb(verb='flies')",
                    "complete_sentence()",
                    "add_article(article='the')",
                    "add_noun(noun='bird')",
                    "add_verb(verb='flies')",
                    "complete_sentence()"
                ]
            }
        ]

    def add_article(self, article: Optional[str] = None) -> str:
        """
        Adds an article (e.g., 'a', 'the') to the sentence.
        
        :param article: The article to add (if None, selects randomly).
        :return: Confirmation message.
        """
        if article:
            word = article
        else:
            word = random.choice(self.world_state["word_pools"]["articles"])
        self.world_state["sentence"] += word + " "
        return f"Added article: '{word}'"

    def add_noun(self, noun: Optional[str] = None) -> str:
        """
        Adds a noun to the sentence.
        
        :param noun: The noun to add (if None, selects randomly).
        :return: Confirmation message.
        """
        if noun:
            word = noun
        else:
            word = random.choice(self.world_state["word_pools"]["nouns"])
        self.world_state["sentence"] += word + " "
        return f"Added noun: '{word}'"

    def add_verb(self, verb: Optional[str] = None) -> str:
        """
        Adds a verb to the sentence.
        
        :param verb: The verb to add (if None, selects randomly).
        :return: Confirmation message.
        """
        if verb:
            word = verb
        else:
            word = random.choice(self.world_state["word_pools"]["verbs"])
        self.world_state["sentence"] += word + " "
        return f"Added verb: '{word}'"

    def add_adjective(self, adjective: Optional[str] = None) -> str:
        """
        Adds an adjective to the sentence.
        
        :param adjective: The adjective to add (if None, selects randomly).
        :return: Confirmation message.
        """
        if adjective:
            word = adjective
        else:
            word = random.choice(self.world_state["word_pools"]["adjectives"])
        self.world_state["sentence"] += word + " "
        return f"Added adjective: '{word}'"

    def add_preposition(self, preposition: Optional[str] = None) -> str:
        """
        Adds a preposition to the sentence.
        
        :param preposition: The preposition to add (if None, selects randomly).
        :return: Confirmation message.
        """
        if preposition:
            word = preposition
        else:
            word = random.choice(self.world_state["word_pools"]["prepositions"])
        self.world_state["sentence"] += word + " "
        return f"Added preposition: '{word}'"

    def complete_sentence(self) -> str:
        """
        Completes the sentence and returns it.
        
        :return: The final sentence.
        """
        sentence = self.world_state["sentence"].strip() + "."
        self.world_state["sentence"] = ""  # Reset for next sentence
        return f"Completed sentence: '{sentence}'"
