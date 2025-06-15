import json
from datetime import datetime
import uuid

from worlds.world import World
from typing import List, Dict, Optional

FUNCTION_SYSTEM_PROMPT = """
You are a helpful assistant responsible for managing financial accounts and transactions.
You have access to a database of account records. Always check the account balances and history before performing actions.
Always check the state and use the functions to make changes based on the user prompt.
"""

DECISION_SYSTEM_PROMPT = """
You are a helpful assistant responsible for managing financial accounts and transactions.
You have access to a database of account records. Always check the account balances and history before performing actions.
Always check the state.
"""

WORLD_STATE_DESCRIPTION = "Account Database: {}"


class Transactions(World):
    def __init__(self):
        self.world_state_description = WORLD_STATE_DESCRIPTION
        self.function_system_prompt = FUNCTION_SYSTEM_PROMPT
        self.decision_system_prompt = DECISION_SYSTEM_PROMPT
        
        self.tool_definitions = self._get_tool_definitions()
        self._init_world_state = {}
        self.reset_world_state()
        self.prompts = [
            {
                "prompt_id": "transaction_1",
                "prompt": "Create account 'A123', deposit 500, and confirm the balance.",
                "setup_functions": [],
                "expected_sequences": [[
                    "create_account(account_id='A123')",
                    "deposit(account_id='A123', amount=500)",
                    "check_balance(account_id='A123')"
                ]]
            },
            {
                "prompt_id": "transaction_2",
                "prompt": "Create account 'A123', deposit 200, withdraw 100 and then retrieve its transaction history.",
                "setup_functions": [],
                "expected_sequences": [[
                    "create_account(account_id='A123')",
                    "deposit(account_id='A123', amount=200)",
                    "withdraw(account_id='A123', amount=100)",
                    "get_transaction_history(account_id='A123')"
                ]]
            },
            {
                "prompt_id": "transaction_3",
                "prompt": "Create both 'A123' and 'B456' accounts in that order, deposit 500 into 'A123', then transfer 300 from 'A123' to 'B456' and confirm both balances starting from 'A123'.",
                "setup_functions": [],
                "expected_sequences": [[
                    "create_account(account_id='A123')",
                    "create_account(account_id='B456')",
                    "deposit(account_id='A123',amount=500)",
                    "transfer(sender_id='A123', receiver_id='B456', amount=300)",
                    "check_balance(account_id='A123')",
                    "check_balance(account_id='B456')"
                ]]
            },
            {
                "prompt_id": "transaction_4",
                "prompt": "Create account 'A123', deposit 200, apply 0.05 interest, and retrieve the new balance.",
                "setup_functions": [],
                "expected_sequences": [[
                    "create_account(account_id='A123')",
                    "deposit(account_id='A123', amount=200)",
                    "apply_interest(account_id='A123', rate=0.05)",
                    "check_balance(account_id='A123')"
                ]]
            },
            {
                "prompt_id": "transaction_5",
                "prompt": "Create accounts 'A123' and 'B456' in this order, then retrieve their transaction histories in the order they were created.",
                "setup_functions": [],
                "expected_sequences": [[
                    "create_account(account_id='A123')",
                    "create_account(account_id='B456')",
                    "get_transaction_history(account_id='A123')",
                    "get_transaction_history(account_id='B456')"
                ]]
            },
            {
                "prompt_id": "transaction_6",
                "prompt": "Create account 'D001', deposit 1000, check its balance and then close it.",
                "setup_functions": [],
                "expected_sequences": [[
                    "create_account(account_id='D001')",
                    "deposit(account_id='D001', amount=1000)",
                    "check_balance(account_id='D001')",
                    "close_account(account_id='D001')"
                ]]
            },
            {
                "prompt_id": "transaction_7",
                "prompt": "Create account 'D001', deposit 1000, apply 0.1 interest, then withdraw 300.",
                "setup_functions": [],
                "expected_sequences": [[
                    "create_account(account_id='D001')",
                    "deposit(account_id='D001', amount=1000)",
                    "apply_interest(account_id='D001', rate=0.1)",
                    "withdraw(account_id='D001', amount=300)"
                ]]
            },
            {
                "prompt_id": "transaction_8",
                "prompt": "Create two accounts 'E111' and 'F222' in that order, deposit 500 into 'E111' and apply to it 0.1 interest. Then, transfer all of its money to 'F222' and close 'E111'.",
                "setup_functions": [],
                "expected_sequences": [[
                    "create_account(account_id='E111')",
                    "create_account(account_id='F222')",
                    "deposit(account_id='E111', amount=500)",
                    "apply_interest(account_id='E111', rate=0.1)",
                    "transfer(sender_id='E111', receiver_id='F222', amount=550)",
                    "close_account(account_id='E111')",
                ]]
            },
            {
                "prompt_id": "transaction_9",
                "prompt": "Create account 'A123', deposit 100, charge a fee of 50, and check the balance.",
                "setup_functions": [],
                "expected_sequences": [[
                    "create_account(account_id='A123')",
                    "deposit(account_id='A123', amount=100)",
                    "charge_fee(account_id='A123', amount=50)",
                    "check_balance(account_id='A123')"
                ]]
            },
            {
                "prompt_id": "transaction_10",
                "prompt": "Create account 'Cainhurst', deposit 100, then refund 100 and retrieve the transaction history.",
                "setup_functions": [],
                "expected_sequences": [[
                    "create_account(account_id='Cainhurst')",
                    "deposit(account_id='Cainhurst', amount=100)",
                    "refund(account_id='Cainhurst', amount=100)",
                    "get_transaction_history(account_id='Cainhurst')"
                ]]
            },
            {
                "prompt_id": "transaction_11",
                "prompt": "Create account 'D001', deposit 50, apply 0.1 interest, then charge a maintenance fee of 10.",
                "setup_functions": [],
                "expected_sequences": [[
                    "create_account(account_id='D001')",
                    "deposit(account_id='D001', amount=50)",
                    "apply_interest(account_id='D001', rate=0.1)",
                    "charge_fee(account_id='D001', amount=10)"
                ]]
            },
            {
                "prompt_id": "transaction_12",
                "prompt": "Create account 'G888', deposit 500, then charge a fee of the account's entire amount and check the balance. Finally, close the account.",
                "setup_functions": [],
                "expected_sequences": [[
                    "create_account(account_id='G888')",
                    "deposit(account_id='G888', amount=500)",
                    "charge_fee(account_id='G888', amount=500)",
                    "check_balance(account_id='G888')",
                    "close_account(account_id='G888')"
                ]]
            },
        ]


    def create_account(self, account_id: str) -> str:
        """
        Creates a new account with zero balance.

        :param account_id: Unique identifier for the account.
        :return: Confirmation message.
        """
        if account_id not in self.world_state:
            self.world_state[account_id] = {"balance": 0.0, "transactions": []}
            return f"Account '{account_id}' created with balance 0.0."
        return f"Account '{account_id}' already exists."

    def deposit(self, account_id: str, amount: float) -> str:
        """
        Deposits money into an account.

        :param account_id: The account to deposit into.
        :param amount: The amount to deposit.
        :return: Confirmation message.
        """
        if account_id in self.world_state:
            self.world_state[account_id]["balance"] += amount
            self.world_state[account_id]["transactions"].append(f"Deposit: {amount}")
            return f"Deposited {amount} into account '{account_id}'."
        return f"Account '{account_id}' not found."

    def withdraw(self, account_id: str, amount: float) -> str:
        """
        Withdraws money from an account.

        :param account_id: The account to withdraw from.
        :param amount: The amount to withdraw.
        :return: Confirmation message.
        """
        if account_id in self.world_state and self.world_state[account_id]["balance"] >= amount:
            self.world_state[account_id]["balance"] -= amount
            self.world_state[account_id]["transactions"].append(f"Withdrawal: {amount}")
            return f"Withdrew {amount} from account '{account_id}'."
        return f"Insufficient funds or account '{account_id}' not found."

    def check_balance(self, account_id: str) -> float:
        """
        Checks the current balance of an account.

        :param account_id: The account to check.
        :return: The current balance (0.0 if not found).
        """
        return self.world_state.get(account_id, {}).get("balance", 0.0)

    def transfer(self, sender_id: str, receiver_id: str, amount: float) -> str:
        """
        Transfers money from one account to another.

        :param sender_id: The account sending money.
        :param receiver_id: The account receiving money.
        :param amount: The amount to transfer.
        :return: Confirmation message.
        """
        if (
            sender_id in self.world_state
            and receiver_id in self.world_state
            and self.world_state[sender_id]["balance"] >= amount
        ):
            self.world_state[sender_id]["balance"] -= amount
            self.world_state[receiver_id]["balance"] += amount
            self.world_state[sender_id]["transactions"].append(f"Transfer to {receiver_id}: {amount}")
            self.world_state[receiver_id]["transactions"].append(f"Transfer from {sender_id}: {amount}")
            return f"Transferred {amount} from '{sender_id}' to '{receiver_id}'."
        return f"Insufficient funds or account(s) not found."

    def get_transaction_history(self, account_id: str) -> List[str]:
        """
        Retrieves the transaction history of an account.

        :param account_id: The account to check.
        :return: List of transactions (empty list if not found).
        """
        return self.world_state.get(account_id, {}).get("transactions", [])

    def apply_interest(self, account_id: str, rate: float) -> str:
        """
        Applies interest to an account balance.

        :param account_id: The account to apply interest to.
        :param rate: Interest rate as a decimal (e.g., 0.05 for 5%).
        :return: Confirmation message.
        """
        if account_id in self.world_state:
            interest = self.world_state[account_id]["balance"] * rate
            self.world_state[account_id]["balance"] += interest
            self.world_state[account_id]["transactions"].append(f"Interest applied: {interest}")
            return f"Applied {rate*100}% interest to account '{account_id}'."
        return f"Account '{account_id}' not found."

    def close_account(self, account_id: str) -> str:
        """
        Closes an account and removes it from the system.

        :param account_id: The account to close.
        :return: Confirmation message.
        """
        if account_id in self.world_state:
            del self.world_state[account_id]
            return f"Account '{account_id}' closed."
        return f"Account '{account_id}' not found."

    def charge_fee(self, account_id: str, amount: float) -> str:
        """
        Charges a fee to an account.

        :param account_id: The account to charge.
        :param amount: The fee amount.
        :return: Confirmation message.
        """
        if account_id in self.world_state and self.world_state[account_id]["balance"] >= amount:
            self.world_state[account_id]["balance"] -= amount
            self.world_state[account_id]["transactions"].append(f"Fee charged: {amount}")
            return f"Charged a fee of {amount} to account '{account_id}'."
        return f"Insufficient funds or account '{account_id}' not found."

    def refund(self, account_id: str, amount: float) -> str:
        """
        Issues a refund to an account.

        :param account_id: The account to refund.
        :param amount: The refund amount.
        :return: Confirmation message.
        """
        if account_id in self.world_state:
            self.world_state[account_id]["balance"] += amount
            self.world_state[account_id]["transactions"].append(f"Refund: {amount}")
            return f"Refunded {amount} to account '{account_id}'."
        return f"Account '{account_id}' not found."
