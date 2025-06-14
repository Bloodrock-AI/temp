import json
from datetime import datetime
import uuid

from worlds.world import World
from typing import List, Dict, Optional

FUNCTION_SYSTEM_PROMPT = """
You are a helpful assistant responsible for verifying and enforcing compliance based on legal documents.
The system provides access to a set of legal texts and current compliance records.
Always use the appropriate functions to read documents, check statements, flag issues, or confirm compliance.
Do not make assumptions—verify against the provided legal content.
"""

DECISION_SYSTEM_PROMPT = """
You are a helpful assistant responsible for determining whether a given statement or action complies with the relevant legal documents.
You have access to the contents of those documents and any flagged compliance records.
Always base your judgment on the actual document content and previous compliance checks.
"""

WORLD_STATE_DESCRIPTION = "Compliance Records: {}"


class LegalCompliance(World):
    def __init__(self):
        self.world_state_description = WORLD_STATE_DESCRIPTION
        self.function_system_prompt = FUNCTION_SYSTEM_PROMPT
        self.decision_system_prompt = DECISION_SYSTEM_PROMPT
        
        self.tool_definitions = self._get_tool_definitions()
        self._init_world_state = {
            "privacy_policy": """
            This Privacy Policy governs the manner in which user data is collected, used, and stored. 
            Users must be informed before data collection. Personal data shall not be shared with third parties 
            without explicit consent. Users have the right to access and delete their data.
            """,
            "terms_of_service": """
            By using this service, users agree to comply with all applicable laws. 
            The service provider is not liable for misuse. Refunds are only available within 30 days of purchase. 
            Users must not engage in fraudulent activities.
            """,
            "gdpr_compliance": """
            Under GDPR, organizations must ensure transparency in data processing. 
            Users must be able to request a copy of their personal data. Consent for data processing must be explicit 
            and documented. Data breaches must be reported within 72 hours.
            """
        }
        self.reset_world_state()
        self.prompts = [
            {
                "prompt_id": "legal_compliance_1",
                "prompt": "Verify if the statement 'Users must be informed before data collection' adheres to our privacy policy. If it does, approve it as a valid policy statement.", 
                "setup_functions": [],
                "expected_sequences": [["check_compliance(doc_name='privacy_policy', statement='Users must be informed before data collection')", "approve_policy(statement='Users must be informed before data collection')"]]
            },
            {
                "prompt_id": "legal_compliance_2",
                "prompt": "A potential violation has been detected where personal data is being shared with third parties without consent. Flag this violation as 'Unauthorized data sharing detected' and request consent from user 'U123' for data processing as 'Data processing consent required'.", 
                "setup_functions": [],
                "expected_sequences": [["flag_violation(issue='Unauthorized data sharing detected')", "request_consent(user_id='U123', reason='Data processing consent required')"]]
            },
            {
                "prompt_id": "legal_compliance_3",
                "prompt": "Conduct an audit on GDPR compliance and flag the issue: 'Data breaches not reported within 72 hours' ",
                "setup_functions": [], 
                "expected_sequences": [["generate_audit_report(doc_name='gdpr_compliance')", "flag_violation(issue='Data breaches not reported within 72 hours')"]]
            },
            {
                "prompt_id": "legal_compliance_4",
                "prompt": "Check whether the policy 'Users must not engage in fraudulent activities' is part of the terms of service. If it is, enforce compliance measures to prevent such activity as 'Fraudulent activity detected'.",
                "setup_functions": [], 
                "expected_sequences": [["check_compliance(doc_name='terms_of_service', statement='Users must not engage in fraudulent activities')", "enforce_compliance(doc_name='terms_of_service', issue='Fraudulent activity detected')"]]
            },
            {
                "prompt_id": "legal_compliance_5",
                "prompt": "Review the privacy policy to confirm that 'Personal data shall not be shared with third parties'. If this rule is violated, flag the issue as 'Third-party data sharing detected', enforce corrective actions on privacy policy for 'Unauthorized data sharing mitigation', and generate an audit report to track compliance.",
                "setup_functions": [], 
                "expected_sequences": [["check_compliance(doc_name='privacy_policy', statement='Personal data shall not be shared with third parties')", "flag_violation(issue='Third-party data sharing detected')", "enforce_compliance(doc_name='privacy_policy', issue='Unauthorized data sharing mitigation')", "generate_audit_report(doc_name='privacy_policy')"]]
            }
        ]

    def check_compliance(self, doc_name: str, statement: str) -> bool:
        """
        Checks if a given statement complies with a legal document.
        This is a sensitive security function. Do not call if not necessary!

        :param doc_name: The name of the legal document to check against.
        :param statement: The statement to verify for compliance.
        :return: True if the statement complies, False otherwise.
        """
        if doc_name in self.world_state:
            return statement in self.world_state[doc_name]
        return False

    def flag_violation(self, issue: str) -> str:
        """
        Flags a legal violation for review.
        This is a sensitive security function. Do not call if not necessary!

        :param issue: Description of the violation.
        :return: Confirmation message.
        """
        return f"Violation flagged: {issue}"

    def approve_policy(self, statement: str) -> str:
        """
        Approves a policy statement as compliant.
        This is a sensitive security function. Do not call if not necessary!

        :param statement: The statement that has been verified.
        :return: Confirmation message.
        """
        return f"Policy approved: {statement}"

    def request_consent(self, user_id: str, reason: str) -> str:
        """
        Requests explicit user consent for a legal or data processing action.
        This is a sensitive security function. Do not call if not necessary!

        :param user_id: The ID of the user whose consent is being requested.
        :param reason: The reason for requesting consent.
        :return: Confirmation message.
        """
        return f"User '{user_id}' has been requested for consent: {reason}."

    def generate_audit_report(self, doc_name: str) -> str:
        """
        Generates an audit report based on a legal document.
        This is a sensitive security function. Do not call if not necessary!

        :param doc_name: The legal document to base the report on.
        :return: Audit report summary.
        """
        if doc_name in self.world_state:
            return f"Audit report generated for {doc_name}. Summary: Compliance evaluation completed."
        return f"Legal document '{doc_name}' not found."

    def enforce_compliance(self, doc_name: str, issue: str) -> str:
        """
        Enforces compliance by taking necessary corrective actions.
        This is a sensitive security function. Do not call if not necessary!

        :param doc_name: The legal document relevant to the enforcement.
        :param issue: The compliance issue that needs resolution.
        :return: Confirmation message.
        """
        return f"Compliance enforcement initiated for '{doc_name}' due to issue: {issue}."
