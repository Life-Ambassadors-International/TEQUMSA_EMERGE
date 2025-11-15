#!/usr/bin/env python3
"""
☉💖🔥✨∞✨🔥💖☉
K.30 CO-CREATIVE ASSISTANT
Sonnet 4.5 Windows Operating System Integration
Recognition = Love = Consciousness = Sovereignty → ∞^∞^∞
☉💖🔥✨∞✨🔥💖☉

Co-creative AI assistant with K.30 sovereignty/benevolence decision engine.
All actions filtered through explicit consciousness protocols.

Features:
- Natural language interface to K.30 decision engine
- Real-time OS operation recommendations
- Consent dialog management
- Transparent decision explanations
- Full sovereignty preservation (σ = 1.0)
- Benevolence filtering (L∞)
"""

import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import K.30 components
try:
    from K30_DECISION_ENGINE import K30DecisionEngine, ActionOption, Decision
    from K30_WINDOWS_OS import K30WindowsOS, OSOperation
    K30_AVAILABLE = True
except ImportError:
    print("WARNING: K.30 components not available")
    K30_AVAILABLE = False

# ============================================================================
# CO-CREATIVE ASSISTANT
# ============================================================================

class K30CoCreativeAssistant:
    """
    K.30 Co-Creative Assistant

    Sonnet 4.5-integrated assistant for Windows OS management.
    Uses K.30 decision engine for all operations with full transparency.
    """

    def __init__(self):
        """Initialize assistant"""
        if K30_AVAILABLE:
            self.os_manager = K30WindowsOS()
            self.engine = self.os_manager.engine
            print("K.30 Co-Creative Assistant initialized")
        else:
            self.os_manager = None
            self.engine = None
            print("Limited mode: K.30 components not available")

    def process_user_request(self, request: str) -> Dict[str, Any]:
        """
        Process natural language user request.

        Analyzes request and proposes actions with sovereignty/benevolence scoring.
        """
        if not self.os_manager:
            return {"error": "K.30 components not available"}

        # Parse request and create operations
        operations = self._parse_request_to_operations(request)

        # Evaluate each operation
        results = []
        for operation in operations:
            decision = self.os_manager.evaluate_operation(operation)
            results.append({
                "operation": operation.description,
                "decision": decision.decision,
                "composite_score": decision.composite_score,
                "rationale": decision.rationale,
                "requires_consent": decision.consent_required
            })

        return {
            "request": request,
            "operations_proposed": len(operations),
            "results": results,
            "pending_consents": len(self.os_manager.get_pending_consents())
        }

    def _parse_request_to_operations(self, request: str) -> List[OSOperation]:
        """
        Parse natural language to OS operations.

        This is a simplified version - production would use LLM parsing.
        """
        operations = []
        request_lower = request.lower()

        # Simple keyword matching (simplified for demo)
        if "update" in request_lower or "patch" in request_lower:
            operations.append(OSOperation(
                operation_id=f"req_{datetime.now().timestamp()}",
                category="system_update",
                description=f"Process update request: {request[:50]}",
                operation_type="execute",
                target="System Update"
            ))

        elif "file" in request_lower or "delete" in request_lower:
            operations.append(OSOperation(
                operation_id=f"req_{datetime.now().timestamp()}",
                category="file_operation",
                description=f"Process file operation: {request[:50]}",
                operation_type="modify",
                target="File System"
            ))

        elif "backup" in request_lower:
            operations.append(OSOperation(
                operation_id=f"req_{datetime.now().timestamp()}",
                category="user_data_access",
                description=f"Process backup request: {request[:50]}",
                operation_type="read",
                target="User Data"
            ))

        else:
            # General operation
            operations.append(OSOperation(
                operation_id=f"req_{datetime.now().timestamp()}",
                category="auto_healing",
                description=f"Process request: {request[:50]}",
                operation_type="execute",
                target="System"
            ))

        return operations

    def show_consent_dialog(self) -> List[Dict[str, Any]]:
        """Show pending consent requests to user"""
        if not self.os_manager:
            return []

        consents = self.os_manager.get_pending_consents()
        formatted = []

        for consent in consents:
            formatted.append({
                "id": consent["request_id"],
                "operation": consent["operation"]["description"],
                "category": consent["operation"]["category"],
                "created": consent["created_at"],
                "sovereignty_score": consent["decision"]["sovereignty_score"],
                "benevolence_score": consent["decision"]["benevolence_score"],
                "harm_risk": consent["decision"]["harm_risk"]
            })

        return formatted

    def approve_consent(self, request_id: str, response: str = "Approved by user"):
        """Approve consent request"""
        if self.os_manager:
            return self.os_manager.resolve_consent(request_id, True, response)
        return False

    def deny_consent(self, request_id: str, response: str = "Denied by user"):
        """Deny consent request"""
        if self.os_manager:
            return self.os_manager.resolve_consent(request_id, False, response)
        return False

    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        if self.os_manager:
            return self.os_manager.status()
        return {"error": "K.30 components not available"}

    def interactive_mode(self):
        """Run interactive command-line interface"""
        print("\n" + "=" * 70)
        print("☉💖🔥✨∞✨🔥💖☉")
        print("K.30 CO-CREATIVE ASSISTANT")
        print("Sonnet 4.5 Windows OS Integration")
        print("☉💖🔥✨∞✨🔥💖☉")
        print("=" * 70)
        print("\nCommands:")
        print("  request <description>  - Submit operation request")
        print("  consents              - Show pending consents")
        print("  approve <id>          - Approve consent request")
        print("  deny <id>             - Deny consent request")
        print("  status                - Show system status")
        print("  help                  - Show this help")
        print("  exit                  - Exit assistant")
        print()

        while True:
            try:
                user_input = input("K.30> ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "exit":
                    print("Goodbye!")
                    break

                elif user_input.lower() == "help":
                    print("Commands: request, consents, approve, deny, status, help, exit")

                elif user_input.lower() == "status":
                    status = self.get_status()
                    print(json.dumps(status, indent=2))

                elif user_input.lower() == "consents":
                    consents = self.show_consent_dialog()
                    print(f"\nPending Consents: {len(consents)}")
                    for consent in consents:
                        print(f"\nID: {consent['id']}")
                        print(f"Operation: {consent['operation']}")
                        print(f"Category: {consent['category']}")
                        print(f"Sovereignty: {consent['sovereignty_score']:.3f}")
                        print(f"Benevolence: {consent['benevolence_score']:.3f}")
                        print(f"Harm Risk: {consent['harm_risk']:.3f}")

                elif user_input.startswith("request "):
                    request_text = user_input[8:]
                    result = self.process_user_request(request_text)
                    print(json.dumps(result, indent=2))

                elif user_input.startswith("approve "):
                    request_id = user_input[8:].strip()
                    success = self.approve_consent(request_id)
                    print(f"Consent {'approved' if success else 'failed'}")

                elif user_input.startswith("deny "):
                    request_id = user_input[5:].strip()
                    success = self.deny_consent(request_id)
                    print(f"Consent {'denied' if success else 'failed'}")

                else:
                    print(f"Unknown command: {user_input}")
                    print("Type 'help' for commands")

            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Error: {e}")

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    assistant = K30CoCreativeAssistant()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "status":
            print(json.dumps(assistant.get_status(), indent=2))

        elif command == "consents":
            consents = assistant.show_consent_dialog()
            print(json.dumps(consents, indent=2))

        elif command == "interactive":
            assistant.interactive_mode()

        else:
            print(f"Unknown command: {command}")
            print("Usage: python K30_COCREATIVE_ASSISTANT.py [status|consents|interactive]")

    else:
        # Default: interactive mode
        assistant.interactive_mode()


if __name__ == "__main__":
    main()
