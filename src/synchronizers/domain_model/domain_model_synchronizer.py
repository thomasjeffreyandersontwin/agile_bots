"""
Domain Model Synchronizers

Handles rendering of domain model documents from story graph JSON.
Three separate synchronizers, one per output type.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, Union


def _load_domain_concepts(input_path: Path) -> Dict[str, Dict]:
    """Load and deduplicate domain concepts from story graph, tracking module and namespace."""
    with open(input_path, 'r', encoding='utf-8') as f:
        story_graph = json.load(f)
    
    domain_concepts = {}
    for epic in story_graph.get('epics', []):
        epic_name = epic.get('name', '')
        # Concepts at epic level - use epic name as namespace fallback
        epic_namespace = epic_name
        sub_epics = epic.get('sub_epics', [])
        
        for concept in epic.get('domain_concepts', []):
            name = concept['name']
            if name not in domain_concepts:
                concept_with_metadata = concept.copy()
                # Use module if present, otherwise fall back to namespace
                if 'module' not in concept_with_metadata:
                    concept_with_metadata['module'] = epic_namespace
                concept_with_metadata['namespace'] = epic_namespace
                domain_concepts[name] = concept_with_metadata
        
        # Concepts at sub-epic level - use sub-epic name as namespace fallback
        for sub_epic in sub_epics:
            sub_epic_name = sub_epic.get('name', '')
            for concept in sub_epic.get('domain_concepts', []):
                name = concept['name']
                if name not in domain_concepts:
                    concept_with_metadata = concept.copy()
                    # Use module if present, otherwise fall back to namespace
                    if 'module' not in concept_with_metadata:
                        concept_with_metadata['module'] = sub_epic_name
                    concept_with_metadata['namespace'] = sub_epic_name
                    domain_concepts[name] = concept_with_metadata
    
    return domain_concepts


def _normalize_namespace(namespace: str, class_names: list) -> str:
    """
    Normalize namespace/module name to avoid conflicts with class names.
    If namespace/module matches a class name, add underscore prefix.
    
    Args:
        namespace: Original namespace/module name
        class_names: List of all class names in the domain
    
    Returns:
        Normalized namespace/module name
    """
    normalized = namespace
    # Check if namespace/module conflicts with any class name
    if normalized in class_names:
        normalized = f"_{normalized}"
    return normalized




def _get_solution_info(project_path: Path, kwargs: Dict) -> tuple:
    """Extract solution name, slug, and purpose from project or kwargs."""
    solution_name = kwargs.get('solution_name')
    solution_name_slug = kwargs.get('solution_name_slug')
    if not solution_name:
        # Try to extract from project path
        solution_name = project_path.name.replace('_', ' ').replace('-', ' ').title()
    if not solution_name_slug:
        solution_name_slug = solution_name.lower().replace(' ', '-')
    
    # Try to get solution purpose from clarification.json
    solution_purpose = kwargs.get('solution_purpose')
    if not solution_purpose:
        clarification_path = project_path / 'docs' / 'stories' / 'clarification.json'
        if clarification_path.exists():
            try:
                with open(clarification_path, 'r', encoding='utf-8') as f:
                    clarification = json.load(f)
                    shape_data = clarification.get('shape', {})
                    key_questions = shape_data.get('key_questions', {})
                    goals = key_questions.get('goals', '')
                    if goals:
                        solution_purpose = goals
            except Exception:
                pass
    
    if not solution_purpose:
        solution_purpose = f"Domain model for {solution_name}"
    
    return solution_name, solution_name_slug, solution_purpose


def _get_source_material(project_path: Path) -> str:
    """Generate source material section."""
    input_file = project_path / 'input.txt'
    if not input_file.exists():
        input_file = project_path / 'docs' / 'context' / 'input.txt'
    
    input_path_str = str(input_file.relative_to(project_path.parent.parent)) if input_file.exists() else 'input.txt'
    
    return f"""**Primary Source:** `{input_path_str}`
**Date Generated:** 2025-01-27
**Context:** Shape phase - Domain model extracted from story-graph.json"""


class DomainModelDescriptionSynchronizer:
    """Synchronizer for rendering domain model description markdown."""
    
    def render(self, input_path: Union[str, Path], output_path: Union[str, Path], 
               renderer_command: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Render domain model description markdown from story graph JSON.
        
        Args:
            input_path: Path to story graph JSON file
            output_path: Path for output file (or directory, will append filename)
            renderer_command: Optional command variant (unused)
            **kwargs: Additional arguments:
                - solution_name: Solution name (default: extracted from path)
                - solution_name_slug: Slug version (default: extracted from path)
                - solution_purpose: Purpose text (default: from clarification.json if available)
                - project_path: Base project path (default: parent of input_path)
        
        Returns:
            Dictionary with output_path and summary
        """
        input_path = Path(input_path)
        project_path = kwargs.get('project_path', input_path.parent.parent.parent)
        project_path = Path(project_path)
        
        solution_name, solution_name_slug, solution_purpose = _get_solution_info(project_path, kwargs)
        domain_concepts = _load_domain_concepts(input_path)
        
        # Group concepts by module
        concepts_by_module = {}
        for concept_name, concept in domain_concepts.items():
            module = concept.get('module', 'Unknown')
            if module not in concepts_by_module:
                concepts_by_module[module] = []
            concepts_by_module[module].append((concept_name, concept))
        
        # Generate domain descriptions grouped by module
        module_sections = []
        for module in sorted(concepts_by_module.keys()):
            module_lines = [f"### Module: {module}\n"]
            
            concepts_in_module = sorted(concepts_by_module[module], key=lambda x: x[0])
            for concept_name, concept in concepts_in_module:
                desc_lines = [f"#### {concept_name}\n"]
                
                # Build description from responsibilities
                responsibilities = concept.get('responsibilities', [])
                if responsibilities:
                    desc_lines.append("**Key Responsibilities:**")
                    for resp in responsibilities:
                        resp_name = resp.get('name', '')
                        collaborators = resp.get('collaborators', [])
                        if collaborators:
                            desc_lines.append(f"- **{resp_name}**: This responsibility involves collaboration with {', '.join(collaborators)}.")
                        else:
                            desc_lines.append(f"- **{resp_name}**: {resp_name}")
                
                module_lines.append("\n".join(desc_lines))
            
            module_sections.append("\n\n".join(module_lines))
        
        domain_model_descriptions_text = "\n\n".join(module_sections)
        source_material = _get_source_material(project_path)
        
        # Determine output path
        output_path = Path(output_path)
        if output_path.is_dir() or not output_path.suffix:
            # If directory or no extension, append filename
            output_path = output_path / f'{solution_name_slug}-domain-model-description.md'
        
        # Template
        content = f"""# Domain Model Description: {solution_name}

**File Name**: `{solution_name_slug}-domain-model-description.md`
**Location**: `{project_path.name}/docs/stories/{solution_name_slug}-domain-model-description.md`

## Solution Purpose
{solution_purpose}

---

## Domain Model Descriptions

{domain_model_descriptions_text}

---

## Source Material

{source_material}
"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            'output_path': str(output_path),
            'summary': {
                'domain_concepts': len(domain_concepts),
                'file': str(output_path.name)
            }
        }


class DomainModelDiagramSynchronizer:
    """Synchronizer for rendering domain model diagram markdown with Mermaid."""
    
    def render(self, input_path: Union[str, Path], output_path: Union[str, Path], 
               renderer_command: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Render domain model diagram markdown from story graph JSON.
        
        Args:
            input_path: Path to story graph JSON file
            output_path: Path for output file (or directory, will append filename)
            renderer_command: Optional command variant (unused)
            **kwargs: Additional arguments:
                - solution_name: Solution name (default: extracted from path)
                - solution_name_slug: Slug version (default: extracted from path)
                - solution_purpose: Purpose text (default: from clarification.json if available)
                - project_path: Base project path (default: parent of input_path)
        
        Returns:
            Dictionary with output_path and summary
        """
        input_path = Path(input_path)
        project_path = kwargs.get('project_path', input_path.parent.parent.parent)
        project_path = Path(project_path)
        
        solution_name, solution_name_slug, solution_purpose = _get_solution_info(project_path, kwargs)
        domain_concepts = _load_domain_concepts(input_path)
        
        # Group concepts by module
        concepts_by_module = {}
        for concept_name, concept in domain_concepts.items():
            module = concept.get('module', 'Unknown')
            if module not in concepts_by_module:
                concepts_by_module[module] = []
            concepts_by_module[module].append((concept_name, concept))
        
        # Get all class names for module normalization
        all_class_names = list(domain_concepts.keys())
        
        # Normalize module names
        module_mapping = {}  # original_module -> normalized_module
        
        for module in concepts_by_module.keys():
            normalized_module = _normalize_namespace(module, all_class_names)
            module_mapping[module] = normalized_module
        
        # Generate Mermaid diagram grouped by module
        mermaid_classes = []
        mermaid_relationships = []
        seen_relationships = set()
        
        # Generate classes grouped by module using namespace blocks
        for module in sorted(concepts_by_module.keys()):
            normalized_module = module_mapping[module]
            concepts_in_module = sorted(concepts_by_module[module], key=lambda x: x[0])
            
            # Start module namespace block
            module_block = [f"    namespace {normalized_module} {{"]
            
            for concept_name, concept in concepts_in_module:
                responsibilities = concept.get('responsibilities', [])
                resp_methods = []
                for resp in responsibilities:
                    resp_name = resp.get('name', '').replace(' ', '_').lower()
                    resp_methods.append(f"            +{resp_name}()")
                
                # Class definition with methods - single closing brace
                if resp_methods:
                    class_def = f"        class {concept_name} {{\n" + "\n".join(resp_methods) + "\n        }"
                else:
                    class_def = f"        class {concept_name}"
                module_block.append(class_def)
            
            # Close module namespace block
            module_block.append("    }")
            mermaid_classes.extend(module_block)
            mermaid_classes.append("")  # Blank line between modules
        
        # Generate relationships using original class names (Mermaid handles module namespace resolution)
        for concept_name, concept in domain_concepts.items():
            responsibilities = concept.get('responsibilities', [])
            
            for resp in responsibilities:
                collaborators = resp.get('collaborators', [])
                for collab in collaborators:
                    if collab in domain_concepts:
                        # Use original class names - Mermaid will resolve module namespaces automatically
                        rel_key = f"{concept_name}->{collab}"
                        if rel_key not in seen_relationships:
                            seen_relationships.add(rel_key)
                            mermaid_relationships.append(f"    {concept_name} --> {collab} : uses")
        
        # Generate pure Mermaid syntax (no markdown wrapper)
        mermaid_content = "classDiagram\n" + "\n".join(mermaid_classes) + "\n    \n    %% Associations\n" + "\n".join(mermaid_relationships)
        
        # Determine output path - use .mmd extension
        output_path = Path(output_path)
        if output_path.is_dir() or not output_path.suffix:
            # If directory or no extension, append filename with .mmd extension
            output_path = output_path / f'{solution_name_slug}-domain-model-diagram.mmd'
        elif output_path.suffix == '.md':
            # If .md extension, change to .mmd
            output_path = output_path.with_suffix('.mmd')
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(mermaid_content)
        
        return {
            'output_path': str(output_path),
            'summary': {
                'domain_concepts': len(domain_concepts),
                'file': str(output_path.name)
            }
        }


class DomainModelOutlineSynchronizer:
    """Synchronizer for rendering domain outline markdown for src/ directory."""
    
    def render(self, input_path: Union[str, Path], output_path: Union[str, Path], 
               renderer_command: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Render domain outline markdown from story graph JSON.
        
        Args:
            input_path: Path to story graph JSON file
            output_path: Path for output file (or directory, will use domain_outline.md)
            renderer_command: Optional command variant (unused)
            **kwargs: Additional arguments:
                - project_path: Base project path (default: parent of input_path)
        
        Returns:
            Dictionary with output_path and summary
        """
        input_path = Path(input_path)
        project_path = kwargs.get('project_path', input_path.parent.parent.parent)
        project_path = Path(project_path)
        
        domain_concepts = _load_domain_concepts(input_path)
        
        # Group concepts by module
        concepts_by_module = {}
        for concept_name, concept in domain_concepts.items():
            module = concept.get('module', 'Unknown')
            if module not in concepts_by_module:
                concepts_by_module[module] = []
            concepts_by_module[module].append((concept_name, concept))
        
        # Generate outline grouped by module
        outline_lines = []
        for module in sorted(concepts_by_module.keys()):
            outline_lines.append(f"## Module: {module}")
            outline_lines.append("")
            
            concepts_in_module = sorted(concepts_by_module[module], key=lambda x: x[0])
            for concept_name, concept in concepts_in_module:
                outline_lines.append(concept_name)
                for resp in concept.get('responsibilities', []):
                    collaborators = resp.get('collaborators', [])
                    collab_str = ",".join(collaborators) if collaborators else ""
                    outline_lines.append(f"    {resp.get('name', '')}: {collab_str}")
                outline_lines.append("")
            
            outline_lines.append("")  # Extra blank line between modules
        
        content = "\n".join(outline_lines)
        
        # Determine output path
        output_path = Path(output_path)
        if output_path.is_dir() or not output_path.suffix:
            # If directory or no extension, use domain_outline.md
            output_path = output_path / 'domain_outline.md'
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            'output_path': str(output_path),
            'summary': {
                'domain_concepts': len(domain_concepts),
                'file': str(output_path.name)
            }
        }
