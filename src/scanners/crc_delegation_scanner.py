"""
CRC Delegation Violation Scanner

Scans CRC model cards to detect responsibilities that are already
fulfilled through delegation to existing collaborators.

Usage:
    python -m src.scanners.crc_delegation_scanner docs/crc/crc-model-outline.md
"""

import re
from typing import List, Tuple, Optional, Set
from dataclasses import dataclass


@dataclass
class Responsibility:
    """Represents a single responsibility on a CRC card."""
    text: str
    collaborators: List[str]
    line_number: int


@dataclass
class CRCCard:
    """Represents a CRC (Class-Responsibility-Collaborator) card."""
    name: str
    module: Optional[str]
    responsibilities: List[Responsibility]
    line_number: int


@dataclass
class Violation:
    """Represents a detected delegation violation."""
    card_name: str
    responsibility: str
    reason: str
    line_number: int
    severity: str  # "error", "warning", "info"


# Domain verb mapping for collaborator types
COLLABORATOR_DOMAINS = {
    "children": ["add", "remove", "find", "get", "resequence", "contains", "delete", "count"],
    "collection": ["add", "remove", "find", "get", "resequence", "contains", "count"],
    "serializer": ["save", "load", "write", "read", "persist", "serialize", "deserialize"],
    "persister": ["save", "load", "write", "read", "persist"],
    "navigator": ["move", "navigate", "position", "order", "determine"],
    "positioner": ["move", "position", "place", "adjust"],
    "validator": ["validate", "check", "verify"],
    "calculator": ["calculate", "compute", "derive"],
    "factory": ["create", "instantiate", "build", "generate"],
    "builder": ["build", "construct", "assemble"],
    "manager": ["manage", "coordinate", "orchestrate"],
    "handler": ["handle", "process", "execute"],
    "analyzer": ["analyze", "examine", "evaluate"],
}

# Implementation detail keywords
IMPLEMENTATION_KEYWORDS = [
    "write to", "read from", "check all", "verify", "roll back",
    "in-memory", "file", "update node", "write updated", "from json",
    "to json", "adjust position if", "resequence from"
]

# Business constraint indicators
CONSTRAINT_INDICATORS = [
    "validate cannot", "validate does not", "validate must not",
    "enforce", "prevent", "require", "constraint",
    "maintain separate", "distinguish between", "identify if"
]


def parse_crc_file(file_path: str) -> List[CRCCard]:
    """Parse CRC model outline file into CRC cards."""
    cards = []
    current_card = None
    current_module = None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Module declaration
        if stripped.startswith("## Module:"):
            current_module = stripped.split(":", 1)[1].strip()
            continue
        
        # Class name (no leading whitespace, not empty, not a comment)
        if stripped and not line.startswith(" ") and not line.startswith("#"):
            # Save previous card
            if current_card:
                cards.append(current_card)
            
            # Start new card
            current_card = CRCCard(
                name=stripped,
                module=current_module,
                responsibilities=[],
                line_number=line_num
            )
        
        # Responsibility (indented)
        elif current_card and line.startswith("    ") and stripped:
            # Parse responsibility
            parts = stripped.split(":", 1)
            if len(parts) == 2:
                resp_text = parts[0].strip()
                collab_text = parts[1].strip()
                collaborators = [c.strip() for c in collab_text.split(",") if c.strip()]
                
                current_card.responsibilities.append(
                    Responsibility(
                        text=resp_text,
                        collaborators=collaborators,
                        line_number=line_num
                    )
                )
    
    # Don't forget the last card
    if current_card:
        cards.append(current_card)
    
    return cards


def extract_verb(responsibility_text: str) -> str:
    """Extract the action verb from a responsibility."""
    # Handle patterns like "Get/Set name" or "Get/Update name"
    if "/" in responsibility_text:
        responsibility_text = responsibility_text.split("/")[0]
    
    # First word is usually the verb
    words = responsibility_text.split()
    if words:
        return words[0].lower()
    return ""


def extract_target(responsibility_text: str) -> str:
    """Extract the target object from 'Get X' or 'Set X' patterns."""
    # Handle "Get scenarios", "Get children", etc.
    match = re.match(r"(?:Get|Set|Add|Remove|Delete|Update)\s+(\w+)", responsibility_text, re.IGNORECASE)
    if match:
        return match.group(1)
    return ""


def get_domain_verbs(collaborator_name: str) -> Set[str]:
    """Get domain verbs for a collaborator based on its type."""
    collab_lower = collaborator_name.lower()
    verbs = set()
    
    for domain_type, domain_verbs in COLLABORATOR_DOMAINS.items():
        if domain_type in collab_lower:
            verbs.update(domain_verbs)
    
    return verbs


def is_implementation_detail(responsibility_text: str) -> bool:
    """Check if responsibility describes implementation (HOW) vs responsibility (WHAT)."""
    lower_text = responsibility_text.lower()
    return any(keyword in lower_text for keyword in IMPLEMENTATION_KEYWORDS)


def is_business_constraint(responsibility_text: str) -> bool:
    """Check if this is a unique business rule/constraint."""
    lower_text = responsibility_text.lower()
    return any(indicator in lower_text for indicator in CONSTRAINT_INDICATORS)


def count_collaborators_in_responsibility(responsibility: Responsibility) -> int:
    """Count how many collaborators are involved in this responsibility."""
    return len(responsibility.collaborators)


def check_delegation_violation(card: CRCCard, responsibility: Responsibility) -> Optional[Violation]:
    """
    Check if a responsibility violates delegation patterns.
    Returns None if no violation, otherwise returns a Violation object.
    """
    resp_text = responsibility.text
    resp_verb = extract_verb(resp_text)
    
    # Skip JSON* classes for serialization checks (that's their purpose)
    is_json_class = card.name.startswith("JSON")
    
    # Skip property declarations
    if "property" in resp_text.lower():
        return None
    
    # Rule 1: Check if responsibility overlaps with collaborator domain
    for collab in responsibility.collaborators:
        domain_verbs = get_domain_verbs(collab)
        if resp_verb in domain_verbs:
            # Exception: If it's coordinating multiple collaborators, it's OK
            if count_collaborators_in_responsibility(responsibility) >= 2:
                continue
            
            # Exception: Business constraints are always OK
            if is_business_constraint(resp_text):
                continue
            
            return Violation(
                card_name=card.name,
                responsibility=resp_text,
                reason=f"'{resp_verb}' is already handled by collaborator '{collab}'",
                line_number=responsibility.line_number,
                severity="error"
            )
    
    # Rule 2: Check for "Add/Remove X" duplication where X is an existing collaborator
    # Note: "Get X" is often a valid accessor, so we focus on mutation operations
    if resp_verb in ["add", "remove", "delete", "create"]:
        target = extract_target(resp_text)
        if target:
            # Get all collaborator names from ALL responsibilities
            all_collabs = set()
            for resp in card.responsibilities:
                all_collabs.update(resp.collaborators)
            
            # Check if target matches a collection collaborator
            for collab in all_collabs:
                # Only flag if it's a clear collection type
                if "children" in collab.lower() or "collection" in collab.lower():
                    if target.lower() in collab.lower() or collab.lower() in target.lower():
                        # Exception: Business constraints are OK
                        if is_business_constraint(resp_text):
                            continue
                        
                        return Violation(
                            card_name=card.name,
                            responsibility=resp_text,
                            reason=f"'{target}' operations already handled by collaborator '{collab}'",
                            line_number=responsibility.line_number,
                            severity="warning"
                        )
    
    # Rule 3: Check for implementation details (skip for JSON/View classes - that's their purpose)
    if not is_json_class and not card.name.endswith("View") and not card.name.endswith("Adapter"):
        if is_implementation_detail(resp_text):
            return Violation(
                card_name=card.name,
                responsibility=resp_text,
                reason="Describes implementation detail (HOW) instead of responsibility (WHAT)",
                line_number=responsibility.line_number,
                severity="warning"
            )
    
    # All checks passed
    return None


def scan_crc_file(file_path: str) -> List[Violation]:
    """Scan a CRC file for delegation violations."""
    cards = parse_crc_file(file_path)
    violations = []
    
    for card in cards:
        for responsibility in card.responsibilities:
            # Skip module declarations and property declarations
            if "module:" in responsibility.text.lower():
                continue
            if "property:" in responsibility.text.lower():
                continue
            
            violation = check_delegation_violation(card, responsibility)
            if violation:
                violations.append(violation)
    
    return violations


def format_violation_report(violations: List[Violation]) -> str:
    """Format violations into a readable report."""
    if not violations:
        return "[OK] No delegation violations found!"
    
    # Group by severity
    errors = [v for v in violations if v.severity == "error"]
    warnings = [v for v in violations if v.severity == "warning"]
    
    report = []
    report.append(f"\n{'='*80}")
    report.append("CRC DELEGATION VIOLATION REPORT")
    report.append(f"{'='*80}\n")
    
    if errors:
        report.append(f"[ERROR] ERRORS: {len(errors)}")
        report.append("-" * 80)
        for v in errors:
            report.append(f"\n  Line {v.line_number}: {v.card_name}")
            report.append(f"  Responsibility: {v.responsibility}")
            report.append(f"  Problem: {v.reason}")
        report.append("\n")
    
    if warnings:
        report.append(f"[WARNING] WARNINGS: {len(warnings)}")
        report.append("-" * 80)
        for v in warnings:
            report.append(f"\n  Line {v.line_number}: {v.card_name}")
            report.append(f"  Responsibility: {v.responsibility}")
            report.append(f"  Problem: {v.reason}")
        report.append("\n")
    
    report.append(f"{'='*80}")
    report.append(f"Total issues: {len(violations)} ({len(errors)} errors, {len(warnings)} warnings)")
    report.append(f"{'='*80}\n")
    
    return "\n".join(report)


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.scanners.crc_delegation_scanner <crc-file>")
        print("Example: python -m src.scanners.crc_delegation_scanner docs/crc/crc-model-outline.md")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print(f"Scanning {file_path}...")
    violations = scan_crc_file(file_path)
    report = format_violation_report(violations)
    
    print(report)
    
    # Exit with error code if violations found
    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
