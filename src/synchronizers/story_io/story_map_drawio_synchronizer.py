"""
DrawIO Story Map Synchronizer for Story Bot (Shared)

Synchronizes story graph structure from DrawIO story map diagrams.
The DrawIO file is the source of truth - this synchronizer reads-only.

Supports two modes:
- Outline mode (shaping): No increments, preserves layout, detects large deletions
- Increments mode (prioritization): Includes increments for marketable releases

Pattern: DrawIO → synchronizer → story-graph-drawio-extracted.json → merge → story_graph.json
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import json
import xml.etree.ElementTree as ET
import re
import sys
import difflib
from datetime import datetime


def get_cell_value(cell) -> str:
    """Extract text value from a cell, handling HTML entities."""
    value = cell.get('value', '')
    value = value.replace('&amp;', '&').replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    value = re.sub(r'<[^>]+>', '', value)
    return value.strip()


def extract_step_from_acceptance_criteria(ac_text: str) -> str:
    """
    Extract step text from acceptance criteria box.
    Handles "When ... Then ..." format, HTML formatting, and plain text.
    
    Args:
        ac_text: Text from acceptance criteria box (may contain HTML)
    
    Returns:
        Step text (description) - cleaned and formatted
    """
    if not ac_text:
        return ""
    
    # Remove HTML tags and clean up entities
    # First replace <br> with space, then remove all other HTML tags
    text = ac_text.replace('<br>', ' ').replace('<br/>', ' ').replace('<br />', ' ')
    text = text.replace('&amp;', '&').replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
    text = re.sub(r'<[^>]+>', '', text)  # Remove remaining HTML tags
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    
    # Try to extract "When ... Then ..." format
    # Pattern: "When [condition] Then [outcome]" (handles both HTML and plain text)
    # The renderer creates: "<b>When</b> {when_text}<br><b>Then</b> {then_text}"
    # After HTML removal: "When {when_text} Then {then_text}"
    when_match = re.search(r'When\s+([^Tt]+?)(?:\s+Then|$)', text, re.IGNORECASE | re.DOTALL)
    then_match = re.search(r'Then\s+(.+)', text, re.IGNORECASE | re.DOTALL)
    
    if when_match and then_match:
        when_part = when_match.group(1).strip()
        then_part = then_match.group(1).strip()
        # Return as single description
        return f"{when_part} {then_part}".strip()
    elif when_match:
        return when_match.group(1).strip()
    elif then_match:
        return then_match.group(1).strip()
    else:
        # Return cleaned text as-is (remove any dictionary-like strings)
        text = text.strip()
        # Remove any malformed dictionary strings
        if text.startswith("{'") or text.startswith('{"'):
            # Try to extract just the description if it's a malformed dict string
            desc_match = re.search(r"'description':\s*'([^']+)'", text)
            if desc_match:
                return desc_match.group(1).strip()
        # If text contains "User --> Description" format, extract description
        if '-->' in text:
            parts = text.split('-->', 1)
            if len(parts) == 2:
                return parts[1].strip()
        return text.strip()


def extract_story_count_from_value(cell) -> Optional[int]:
    """
    Extract story count/estimated_stories from cell HTML value.
    Checks both bottom position (outline mode) and top-right position (increments mode).
    """
    raw_value = cell.get('value', '')
    
    # First try top-right position (increments mode): "position: absolute; top: 2px; right: 5px; ... X stories"
    top_right_match = re.search(r'position:\s*absolute[^>]*>(\d+)\s*stories', raw_value, re.IGNORECASE | re.DOTALL)
    if top_right_match:
        return int(top_right_match.group(1))
    
    # Try bottom position (outline mode): Look for pattern like "~## stories" or "<number> stories" in HTML
    # Pattern: <span>##</span><span>stories</span> or similar
    match = re.search(r'(\d+)\s*&nbsp;.*?stories', raw_value, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # Also try parsing from HTML structure
    match = re.search(r'<span[^>]*>(\d+)</span>.*?<span[^>]*>stories</span>', raw_value, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def extract_story_type_from_style(style: str) -> str:
    """
    Extract story_type from DrawIO cell style based on fillColor.
    
    Returns:
        'user' (default), 'system', or 'technical'
    """
    if 'fillColor=#1a237e' in style:  # Dark blue - system story
        return 'system'
    elif 'fillColor=#000000' in style or 'fillColor=#000' in style:  # Black - technical story
        return 'technical'
    else:
        return 'user'  # Default (yellow or other)


def extract_geometry(cell) -> Optional[Dict[str, float]]:
    """Extract geometry information from a cell."""
    geom = cell.find('mxGeometry')
    if geom is None:
        return None
    x = float(geom.get('x', 0))
    y = float(geom.get('y', 0))
    width = float(geom.get('width', 0))
    height = float(geom.get('height', 0))
    return {'x': x, 'y': y, 'width': width, 'height': height}


def get_increments_and_boundaries(drawio_path: Path) -> List[Dict[str, Any]]:
    """
    Get all increment squares (white squares on the left) and their boundaries.
    
    Returns:
        List of increment dictionaries with id, name, x, y, width, height
    """
    tree = ET.parse(drawio_path)
    root = tree.getroot()
    cells = root.findall('.//mxCell')
    
    increments = []
    
    for cell in cells:
        cell_id = cell.get('id', '')
        style = cell.get('style', '')
        geom = extract_geometry(cell)
        
        # Check for increment squares: white squares (strokeColor=#f8f7f7) positioned on the left (negative X)
        if 'strokeColor=#f8f7f7' in style and geom and geom['x'] < 0:
            value = get_cell_value(cell)
            # Only include if it has a non-empty name (filter out empty strings and whitespace-only)
            if value and value.strip():
                increments.append({
                    'id': cell_id,
                    'name': value.strip(),
                    'x': geom['x'],
                    'y': geom['y'],
                    'width': geom['width'],
                    'height': geom['height']
                })
    
    # Sort by Y position (top to bottom)
    increments.sort(key=lambda x: x['y'])
    
    return increments


def get_epics_features_and_boundaries(drawio_path: Path) -> Dict[str, Any]:
    """
    Get all epics and sub_epics with their boundaries (x, y, width, height).
    
    Returns:
        Dictionary with 'epics' and 'sub_epics' lists
    """
    tree = ET.parse(drawio_path)
    root = tree.getroot()
    cells = root.findall('.//mxCell')
    
    epics = []
    sub_epics = []
    
    # First pass: collect all cells and build parent-child relationships
    cell_map = {}  # id -> cell
    parent_map = {}  # id -> parent_id
    group_cells = {}  # group_id -> list of child cell ids
    
    for cell in cells:
        cell_id = cell.get('id', '')
        if cell_id:
            cell_map[cell_id] = cell
            parent_id = cell.get('parent', '')
            if parent_id:
                parent_map[cell_id] = parent_id
                if parent_id not in group_cells:
                    group_cells[parent_id] = []
                group_cells[parent_id].append(cell_id)
    
    # Second pass: extract epics and features, and look for estimated stories in groups
    for cell in cells:
        cell_id = cell.get('id', '')
        style = cell.get('style', '')
        value = get_cell_value(cell)
        geom = extract_geometry(cell)
        
        if geom is None:
            continue
        
        # Epics: purple boxes (fillColor=#e1d5e7)
        # NEVER match by ID - extract all epics by position/containment only
        if 'fillColor=#e1d5e7' in style:
            # If epic is in a group, use group's absolute position + epic's relative position
            parent_id = parent_map.get(cell_id)
            absolute_x = geom['x']
            absolute_y = geom['y']
            if parent_id:
                parent_cell = cell_map.get(parent_id)
                if parent_cell is not None:
                    parent_geom = extract_geometry(parent_cell)
                    if parent_geom:
                        # Epic's x/y are relative to group, add group's absolute position
                        absolute_x = parent_geom['x'] + geom['x']
                        absolute_y = parent_geom['y'] + geom['y']
            
            epic_data = {
                'id': cell_id,
                'name': value,
                'epic_num': None,  # Will assign by position/order
                'x': absolute_x,
                'y': absolute_y,
                'width': geom['width'],
                'height': geom['height']
            }
            # Extract estimated_stories from cell HTML value (legacy format)
            estimated_stories = extract_story_count_from_value(cell)
            
            # NEW: Also check for estimated stories text box in parent group
            parent_id = parent_map.get(cell_id)
            if parent_id and not estimated_stories:
                # Look for text cells with pattern "~{number} stories" in the same group
                group_children = group_cells.get(parent_id, [])
                for child_id in group_children:
                    child_cell = cell_map.get(child_id)
                    if child_cell is None:
                        continue
                    child_style = child_cell.get('style', '')
                    child_value = get_cell_value(child_cell)
                    # Check if it's a text cell with estimated stories pattern
                    if 'text;' in child_style or 'whiteSpace=wrap' in child_style:
                        # Look for pattern "~{number} stories" in the value
                        match = re.search(r'~(\d+)\s*stories', child_value, re.IGNORECASE)
                        if match:
                            estimated_stories = int(match.group(1))
                            break
            
            if estimated_stories:
                epic_data['estimated_stories'] = estimated_stories
                epic_data['total_stories'] = estimated_stories  # Also set total_stories
            epics.append(epic_data)
        
        # Sub-epics: green boxes (fillColor=#d5e8d4)
        # NEVER match by ID - extract all sub-epics by position/containment only
        elif 'fillColor=#d5e8d4' in style:
            # If sub-epic is in a group, use group's absolute position + sub-epic's relative position
            parent_id = parent_map.get(cell_id)
            absolute_x = geom['x']
            absolute_y = geom['y']
            if parent_id:
                parent_cell = cell_map.get(parent_id)
                if parent_cell is not None:
                    parent_geom = extract_geometry(parent_cell)
                    if parent_geom:
                        # Sub-epic's x/y are relative to group, add group's absolute position
                        absolute_x = parent_geom['x'] + geom['x']
                        absolute_y = parent_geom['y'] + geom['y']
            
            sub_epic_data = {
                'id': cell_id,
                'name': value,
                'epic_num': None,  # Will assign by position/containment
                'feat_num': None,  # Will assign by position/order within epic
                'x': absolute_x,
                'y': absolute_y,
                'width': geom['width'],
                'height': geom['height']
            }
            # Extract estimated_stories (story_count) from cell HTML value (legacy format)
            estimated_stories = extract_story_count_from_value(cell)
            
            # NEW: Also check for estimated stories text box in parent group
            parent_id = parent_map.get(cell_id)
            if parent_id and not estimated_stories:
                # Look for text cells with pattern "~{number} stories" in the same group
                group_children = group_cells.get(parent_id, [])
                for child_id in group_children:
                    child_cell = cell_map.get(child_id)
                    if child_cell is None:
                        continue
                    child_style = child_cell.get('style', '')
                    child_value = get_cell_value(child_cell)
                    # Check if it's a text cell with estimated stories pattern
                    if 'text;' in child_style or 'whiteSpace=wrap' in child_style:
                        # Look for pattern "~{number} stories" in the value
                        match = re.search(r'~(\d+)\s*stories', child_value, re.IGNORECASE)
                        if match:
                            estimated_stories = int(match.group(1))
                            break
            
            if estimated_stories:
                sub_epic_data['estimated_stories'] = estimated_stories
                sub_epic_data['story_count'] = estimated_stories  # Legacy field
                sub_epic_data['total_stories'] = estimated_stories  # Also set total_stories
            sub_epics.append(sub_epic_data)
    
    # Assign epic_num to epics by position/order (left to right, top to bottom)
    epics.sort(key=lambda x: (x['x'], x['y']))
    for idx, epic in enumerate(epics, 1):
        if epic.get('epic_num') is None:
            epic['epic_num'] = idx
    
    # Assign epic_num to features by position/containment
    # Epics may be in a group with different coordinate space, so we need to be more flexible
    for sub_epic in sub_epics:
        if sub_epic['epic_num'] is None:
            sub_epic_x = sub_epic['x']
            sub_epic_y = sub_epic['y']
            
            # Try multiple strategies to assign sub-epic to epic:
            # 1. Check if sub-epic is within epic's horizontal bounds (X coordinate)
            # 2. Check if sub-epic is within epic's vertical bounds (Y coordinate) 
            # 3. Use closest epic by distance
            best_epic = None
            best_score = float('inf')
            
            for epic in sorted(epics, key=lambda e: e['x']):
                epic_x = epic['x']
                epic_y = epic['y']
                epic_width = epic.get('width', 0)
                epic_height = epic.get('height', 60)  # Default height
                epic_right = epic_x + epic_width if epic_width > 0 else float('inf')
                epic_bottom = epic_y + epic_height
                
                # Check horizontal containment (primary)
                x_contained = epic_x <= sub_epic_x <= epic_right
                # Check vertical proximity (sub-epics are usually below epics)
                y_proximity = sub_epic_y > epic_y and sub_epic_y < epic_bottom + 1000  # Sub-epics can be well below epics
                
                # Calculate distance score (lower is better)
                distance = ((epic_x - sub_epic_x) ** 2 + (epic_y - sub_epic_y) ** 2) ** 0.5
                
                # Prefer epics that contain the sub-epic horizontally
                if x_contained:
                    score = distance * 0.1  # Much lower score for contained sub-epics
                elif y_proximity:
                    score = distance * 0.5  # Medium score for vertical proximity
                else:
                    score = distance  # Full distance for others
                
                if score < best_score:
                    best_score = score
                    best_epic = epic
            
            if best_epic:
                sub_epic['epic_num'] = best_epic['epic_num']
            # Fallback: assign to closest epic by X position
            elif epics:
                closest_epic = min(epics, key=lambda e: abs(e['x'] - sub_epic['x']))
                sub_epic['epic_num'] = closest_epic['epic_num']
    
    # Assign feat_num to sub-epics by position/order within each epic (left to right)
    # Also detect nested sub-epics (sub-epics inside other sub-epics) for N-level nesting
    for epic in epics:
        epic_sub_epics = [f for f in sub_epics if f['epic_num'] == epic['epic_num']]
        # Sort by X position to get order
        epic_sub_epics.sort(key=lambda f: f['x'])
        # Assign feat_num based on order (starting from 1)
        for idx, sub_epic in enumerate(epic_sub_epics, 1):
            if sub_epic.get('feat_num') is None:
                sub_epic['feat_num'] = idx
    
    # Detect nested sub-epics (sub-epics inside other sub-epics) for N-level nesting
    # A sub-epic is nested if it's contained within another sub-epic's bounds
    for sub_epic in sub_epics:
        sub_epic['parent_feat_num'] = None  # Track parent sub-epic for nesting
        sub_epic['parent_epic_num'] = sub_epic.get('epic_num')  # Track which epic it belongs to
        
        sub_epic_x = sub_epic['x']
        sub_epic_y = sub_epic['y']
        sub_epic_width = sub_epic.get('width', 0)
        sub_epic_height = sub_epic.get('height', 0)
        sub_epic_right = sub_epic_x + sub_epic_width
        sub_epic_bottom = sub_epic_y + sub_epic_height
        
        # Check if this sub-epic is nested inside another sub-epic
        # Look for sub-epics in the same epic that contain this sub-epic
        same_epic_sub_epics = [f for f in sub_epics 
                             if f.get('epic_num') == sub_epic.get('epic_num') 
                             and f.get('id') != sub_epic.get('id')]
        
        best_parent = None
        best_score = float('inf')
        
        for parent_sub_epic in same_epic_sub_epics:
            parent_x = parent_sub_epic['x']
            parent_y = parent_sub_epic['y']
            parent_width = parent_sub_epic.get('width', 0)
            parent_height = parent_sub_epic.get('height', 0)
            parent_right = parent_x + parent_width
            parent_bottom = parent_y + parent_height
            
            # Check if this sub-epic is nested below parent sub-epic
            # Nested sub-epics are positioned BELOW the parent and horizontally aligned/overlapping
            # They don't need to be completely inside - they're typically below the parent
            tolerance = 10  # Allow small overlap/offset
            parent_bottom = parent_y + parent_height
            
            # Check horizontal alignment/overlap
            horizontal_overlap = (
                (parent_x - tolerance <= sub_epic_x <= parent_right + tolerance) or
                (parent_x - tolerance <= sub_epic_right <= parent_right + tolerance) or
                (sub_epic_x <= parent_x and sub_epic_right >= parent_right)  # Sub-epic spans parent
            )
            
            # Check if sub-epic is below parent (not above)
            is_below = sub_epic_y >= parent_bottom - tolerance
            
            # Check if sub-epic is not too far below (within reasonable distance, max 200px)
            max_distance_below = parent_bottom + 200
            is_within_range = sub_epic_y < max_distance_below
            
            # Sub-epic is nested if it's horizontally aligned and below parent
            is_contained = horizontal_overlap and is_below and is_within_range
            
            if is_contained:
                # Calculate containment score (prefer smaller, more specific parents)
                parent_area = parent_width * parent_height
                score = parent_area  # Smaller area = better (more specific parent)
                
                if score < best_score:
                    best_score = score
                    best_parent = parent_sub_epic
        
        if best_parent:
            sub_epic['parent_feat_num'] = best_parent.get('feat_num')
            sub_epic['parent_epic_num'] = best_parent.get('epic_num')
    
    # Sort sub-epics by epic_num, then parent_feat_num (None first), then feat_num, then x
    sub_epics.sort(key=lambda x: (
        x['epic_num'] if x['epic_num'] is not None else 999, 
        x['parent_feat_num'] if x['parent_feat_num'] is not None else 0,  # Sub-epics without parents come first
        x['feat_num'] if x['feat_num'] is not None else 999, 
        x['x']
    ))
    
    return {
        'epics': epics,
        'sub_epics': sub_epics
    }


def build_stories_for_epics_features(drawio_path: Path, epics: List[Dict], sub_epics: List[Dict], 
                                     return_layout: bool = False) -> Dict[str, Any]:
    """
    Go through each epic and sub-epic, and build all stories.
    Preserves layout and spacing from DrawIO.
    
    Args:
        drawio_path: Path to DrawIO file
        epics: List of epic dictionaries
        sub_epics: List of sub-epic dictionaries
        return_layout: If True, also return layout data (X/Y coordinates) for stories
    
    Returns:
        Dictionary with epics containing sub-epics containing stories.
        If return_layout=True, also includes 'layout' key with story coordinates.
    """
    tree = ET.parse(drawio_path)
    root = tree.getroot()
    cells = root.findall('.//mxCell')
    
    # Extract all stories
    all_stories = []
    user_cells = []
    acceptance_criteria_cells = []
    background_rectangles = []  # Story groups (grey background rectangles)
    
    for cell in cells:
        cell_id = cell.get('id', '')
        style = cell.get('style', '')
        value = get_cell_value(cell)
        geom = extract_geometry(cell)
        
        if geom is None:
            continue
        
        # Acceptance criteria: wider boxes (width > 100, height > 50, rounded=0, yellow fill)
        # These appear below stories in exploration mode
        # Check for AC boxes first to exclude them from story detection
        is_ac_box = (cell_id.startswith('ac_') or 
                    ('fillColor=#fff2cc' in style and 'rounded=0' in style and 
                     geom['width'] > 100 and geom['height'] > 50))
        
        if is_ac_box:
            # This is an acceptance criteria box
            # Extract raw value to preserve <br> tags for splitting
            raw_value = cell.get('value', '')
            # Decode XML entities but keep HTML tags (especially <br>)
            ac_text = raw_value.replace('&amp;', '&').replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>')
            acceptance_criteria_cells.append({
                'id': cell_id,
                'text': ac_text,
                'x': geom['x'],
                'y': geom['y'],
                'width': geom['width'],
                'height': geom['height']
            })
            continue  # Skip story detection for AC boxes
        
        # Stories: detect by fillColor (yellow #fff2cc, dark blue #1a237e, black #000000)
        # NEVER match by ID - extract all stories by position/containment only
        # Exclude AC boxes (already handled above)
        is_story = ('fillColor=#fff2cc' in style or 'fillColor=#1a237e' in style or 'fillColor=#000000' in style or 'fillColor=#000' in style)
        if is_story:
            # Extract all stories - will assign to features by name matching and position/containment
            story_type = extract_story_type_from_style(style)
            all_stories.append({
                'id': cell_id,
                'name': value,
                'epic_num': None,  # Will assign by position/containment
                'feat_num': None,  # Will assign by name matching and position/containment
                'x': geom['x'],
                'y': geom['y'],
                'width': geom['width'],
                'height': geom['height'],
                'story_type': story_type
            })
        
        # Legacy AC detection (should not be reached if AC boxes are detected above)
        elif ('fillColor=#fff2cc' in style and 'rounded=0' in style and 
              geom['width'] > 100 and geom['height'] > 50):
            # This is likely an acceptance criteria box
            # Extract step text from value (handles "When ... Then ..." format)
            ac_text = value
            acceptance_criteria_cells.append({
                'id': cell_id,
                'text': ac_text,
                'x': geom['x'],
                'y': geom['y'],
                'width': geom['width'],
                'height': geom['height']
            })
        
        # Background rectangles (story groups): light grey with dashed border
        # These are the horizontal groups of stories
        elif ('fillColor=#F7F7F7' in style or 'fillColor=#f7f7f7' in style) and 'dashed=1' in style:
            background_rectangles.append({
                'id': cell_id,
                'x': geom['x'],
                'y': geom['y'],
                'width': geom['width'],
                'height': geom['height']
            })
        
        # Users: blue boxes (fillColor=#dae8fc)
        elif 'fillColor=#dae8fc' in style:
            user_name = value
            if user_name:
                user_cells.append({
                    'id': cell_id,
                    'name': user_name,
                    'x': geom['x'],
                    'y': geom['y']
                })
    
    # Sort acceptance criteria cells by Y position (top to bottom) for proper matching
    acceptance_criteria_cells.sort(key=lambda ac: (ac['y'], ac['x']))
    
    # Assign epic/feature to stories by position/containment and name matching (NEVER by ID)
    for story in all_stories:
        story_x = story['x']
        story_y = story['y']
        story_name = story['name'].lower()
        
        # Assign epic by position/containment (X coordinate within epic bounds)
        if story['epic_num'] is None:
            for epic in sorted(epics, key=lambda e: e['x']):
                epic_x = epic['x']
                epic_width = epic.get('width', 0)
                epic_right = epic_x + epic_width if epic_width > 0 else float('inf')
                # Story belongs to epic if it's within epic's horizontal bounds
                if epic_x <= story_x <= epic_right:
                    story['epic_num'] = epic['epic_num']
                    break
            # If still None, assign to closest epic by X position
            if story['epic_num'] is None and epics:
                closest_epic = min(epics, key=lambda e: abs(e['x'] - story_x))
                story['epic_num'] = closest_epic['epic_num']
        
        # Assign sub-epic by name matching (fuzzy) AND position/containment
        if story['epic_num'] is not None:
            epic_sub_epics = [f for f in sub_epics if f['epic_num'] == story['epic_num']]
            if epic_sub_epics:
                # First, try to match by name (fuzzy matching)
                best_match = None
                best_similarity = 0.0
                
                for sub_epic in epic_sub_epics:
                    sub_epic_name = sub_epic['name'].lower()
                    # Check if story name contains sub-epic name or vice versa (exact match)
                    if sub_epic_name in story_name or story_name in sub_epic_name:
                        similarity = 1.0
                    else:
                        # Fuzzy match using SequenceMatcher
                        similarity = difflib.SequenceMatcher(None, story_name, sub_epic_name).ratio()
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = sub_epic
                
                # If fuzzy match found (similarity > 0.3), verify by position/containment
                if best_match and best_similarity > 0.3:
                    sub_epic_x = best_match['x']
                    sub_epic_width = best_match.get('width', 200)
                    sub_epic_right = sub_epic_x + sub_epic_width
                    # Verify story is within sub-epic's horizontal bounds
                    if sub_epic_x <= story_x <= sub_epic_right:
                        story['feat_num'] = best_match.get('feat_num', 0)
                
                # If no fuzzy match or position doesn't match, assign by position/containment only
                if story['feat_num'] is None:
                    for sub_epic in sorted(epic_sub_epics, key=lambda f: f['x']):
                        sub_epic_x = sub_epic['x']
                        sub_epic_width = sub_epic.get('width', 200)
                        sub_epic_right = sub_epic_x + sub_epic_width
                        # Story belongs to sub-epic if it's within sub-epic's horizontal bounds
                        if sub_epic_x <= story_x <= sub_epic_right:
                            story['feat_num'] = sub_epic.get('feat_num', 0)
                            break
                    
                    # If still None, assign to closest sub-epic by X position
                    if story['feat_num'] is None:
                        closest_sub_epic = min(epic_sub_epics, key=lambda f: abs(f['x'] - story_x))
                        story['feat_num'] = closest_sub_epic.get('feat_num', 0)
    
    # After initial assignment, reassign stories to the deepest nested feature that contains them
    # This ensures stories belong to child features, not parent features
    for story in all_stories:
        if story.get('epic_num') is None or story.get('feat_num') is None:
            continue
        
        story_x = story['x']
        story_y = story['y']
        story_center_x = story_x + story.get('width', 50) / 2
        
        # Find all sub-epics in the same epic that contain this story
        epic_num = story['epic_num']
        containing_sub_epics = []
        
        for sub_epic in sub_epics:
            if sub_epic.get('epic_num') != epic_num:
                continue
            
            sub_epic_x = sub_epic['x']
            sub_epic_y = sub_epic['y']
            sub_epic_width = sub_epic.get('width', 0)
            sub_epic_height = sub_epic.get('height', 0)
            sub_epic_right = sub_epic_x + sub_epic_width
            sub_epic_bottom = sub_epic_y + sub_epic_height
            
            # Check if story is contained within this sub-epic (horizontal containment)
            # Allow some vertical tolerance for stories below sub-epics
            tolerance = 50
            if (sub_epic_x <= story_center_x <= sub_epic_right and 
                sub_epic_y - tolerance <= story_y <= sub_epic_bottom + 200):
                containing_sub_epics.append(sub_epic)
        
        # If multiple sub-epics contain this story, prefer the deepest nested one (child over parent)
        if containing_sub_epics:
            # Sort by depth: sub-epics with parent_feat_num (nested) come first
            # Among nested sub-epics, prefer the one with the smallest area (most specific)
            containing_sub_epics.sort(key=lambda f: (
                0 if f.get('parent_feat_num') is not None else 1,  # Nested first
                f.get('width', 0) * f.get('height', 0)  # Smaller area = more specific
            ))
            best_sub_epic = containing_sub_epics[0]
            story['feat_num'] = best_sub_epic.get('feat_num')
    
    # Match users to stories based on cell ID pattern (user_e{epic}f{feat}s{story}_{user})
    # Fallback to position-based matching: match each user to the CLOSEST story below it
    stories_with_users = {}
    # Build set of all story IDs for quick lookup
    all_story_ids = {story['id'] for story in all_stories}
    
    # First pass: match users by cell ID pattern
    for story in all_stories:
        story_id = story['id']  # e.g., "e1f1s4"
        story_users = []
        
        for user_cell in user_cells:
            user_cell_id = user_cell['id']  # e.g., "user_e1f1s4_User A"
            user_name = user_cell['name']
            
            # Match by cell ID pattern (user_e{epic}f{feat}s{story}_{user})
            if user_cell_id.startswith('user_') and story_id:
                # Extract story pattern from user cell ID: user_e1f1s4_User C -> e1f1s4
                # Pattern is: user_{story_id}_{user_name}
                if user_cell_id.startswith(f'user_{story_id}_'):
                    # Exact match by ID - this user belongs to this story
                    if user_name not in story_users:
                        story_users.append(user_name)
        
        stories_with_users[story['id']] = story_users
    
    # Second pass: Simple left-to-right, top-to-bottom algorithm
    # Parse diagram left to right, top to bottom
    # When you see a user sticky:
    #   - Go DOWN: assign to all stories below until you see another user sticky → stop
    #   - Go RIGHT: if you see a user sticky → stop, otherwise continue assigning
    # Next row: go down, go right, overwrite previous assignment
    column_tolerance = 100  # pixels - for grouping into columns
    y_tolerance = 50  # pixels - for checking if users are at same row level
    
    # Get all user cells that aren't already matched by ID
    unmatched_users = []
    for user_cell in user_cells:
        user_cell_id = user_cell['id']
        
        # Skip if already matched by ID pattern
        if user_cell_id.startswith('user_'):
            already_assigned = False
            if '_' in user_cell_id:
                parts = user_cell_id.split('_', 2)
                if len(parts) >= 2:
                    potential_story_id = parts[1]
                    if potential_story_id in all_story_ids:
                        already_assigned = True
            
            if already_assigned:
                continue
        
        unmatched_users.append({
            'x': user_cell['x'],
            'y': user_cell['y'],
            'name': user_cell['name']
        })
    
    # Sort users by y (top to bottom), then by x (left to right)
    unmatched_users.sort(key=lambda u: (u['y'], u['x']))
    
    # Process each user sticky in order (top to bottom, left to right)
    for i, user_info in enumerate(unmatched_users):
        user_name = user_info['name']
        user_x = user_info['x']
        user_y = user_info['y']
        
        # Step 1: Go DOWN - assign to all stories below in same column until you see another user sticky
        # Find the next user sticky below in the same column
        next_user_below_y = float('inf')
        for j in range(i + 1, len(unmatched_users)):
            other_user = unmatched_users[j]
            if abs(other_user['x'] - user_x) <= column_tolerance and other_user['y'] > user_y:
                next_user_below_y = other_user['y']
                break
        
        # Assign this user to all stories in same column below it
        for story in all_stories:
            story_id = story['id']
            story_x = story['x']
            story_y = story['y']
            
            # Check if story is in same column and below user, above next user
            # Story must be within tolerance AND not clearly to the left of user
            # (stories to the left belong to a different column)
            if (abs(story_x - user_x) <= column_tolerance and 
                story_x >= user_x - column_tolerance/2 and  # Don't match stories clearly to the left
                story_y > user_y and story_y < next_user_below_y):
                # Overwrite previous assignment (simple overwrite rule)
                stories_with_users[story_id] = [user_name]
        
        # Step 2: Go RIGHT - check next column to the RIGHT, if ANY user sticky there, STOP
        # Find the next column to the RIGHT (must be > user_x, not left)
        next_column_x = None
        for story in all_stories:
            if story['x'] > user_x:  # Only columns to the RIGHT
                if next_column_x is None or story['x'] < next_column_x:
                    next_column_x = story['x']
        
        if next_column_x is not None:
            # Check if there's ANY user sticky in the next column (anywhere in that column)
            has_user_in_next_column = False
            for other_user in unmatched_users:
                if abs(other_user['x'] - next_column_x) <= column_tolerance:
                    has_user_in_next_column = True
                    break
            
            # If no user sticky in next column, continue assigning to stories in that column
            if not has_user_in_next_column:
                # Assign to all stories in next column below user (only to the RIGHT)
                for story in all_stories:
                    story_id = story['id']
                    story_x = story['x']
                    story_y = story['y']
                    
                    # Check if story is in next column (to the RIGHT) and below user
                    if (story_x > user_x and  # Must be to the RIGHT
                        abs(story_x - next_column_x) <= column_tolerance and 
                        story_y > user_y):
                        # Overwrite previous assignment
                        stories_with_users[story_id] = [user_name]
    
    # Final resolution: if a story has multiple users, keep the one with closest column (smallest x distance)
    for story in all_stories:
        if story['id'] in stories_with_users:
            current_users = stories_with_users[story['id']]
            if len(current_users) > 1:
                # Multiple users assigned - keep the one with closest x position
                story_x = story['x']
                best_user = None
                min_x_distance = float('inf')
                for user_name in current_users:
                    # Find this user's x position
                    for user_info in unmatched_users:
                        if user_info['name'] == user_name:
                            x_distance = abs(story_x - user_info['x'])
                            if x_distance < min_x_distance:
                                min_x_distance = x_distance
                                best_user = user_name
                            break
                if best_user:
                    stories_with_users[story['id']] = [best_user]
                else:
                    # Fallback: keep first user
                    stories_with_users[story['id']] = [current_users[0]]
            else:
                # Single user - just deduplicate
                deduplicated = []
                for user in current_users:
                    if user not in deduplicated:
                        deduplicated.append(user)
                stories_with_users[story['id']] = deduplicated
    
    # Assign sequential order based on left-to-right position and vertical stacking
    _assign_sequential_order(all_stories)
    
    # Assign sequential order to epics (left to right)
    sorted_epics = sorted(epics, key=lambda x: (x['x'], x['epic_num']))
    for idx, epic in enumerate(sorted_epics, 1):
        epic['sequential_order'] = idx
    
    # Assign sequential order to sub-epics (left to right within each epic)
    for epic in sorted_epics:
        epic_sub_epics = sorted([f for f in sub_epics if f['epic_num'] == epic['epic_num']], 
                               key=lambda x: (x['x'], x.get('feat_num', 0)))
        for idx, sub_epic in enumerate(epic_sub_epics, 1):
            sub_epic['sequential_order'] = idx
    
    # Build epic/feature/story hierarchy
    result = {'epics': []}
    
    # Track which stories have been assigned to prevent duplicates
    assigned_story_ids = set()
    # Track which acceptance criteria boxes have been assigned to prevent duplicates
    assigned_ac_ids = set()
    
    def build_sub_epic_recursive(sub_epic_dict, parent_epic_num, all_sub_epics, all_stories, background_rectangles, 
                                  stories_with_users, acceptance_criteria_cells, assigned_story_ids, assigned_ac_ids):
        """
        Recursively build a sub_epic and its nested sub_epics.
        
        Args:
            sub_epic_dict: Sub-epic dictionary to build sub_epic from
            parent_epic_num: Epic number this sub-epic belongs to
            all_sub_epics: List of all sub-epics
            all_stories: List of all stories
            background_rectangles: List of background rectangles
            stories_with_users: Dictionary mapping story IDs to users
            acceptance_criteria_cells: List of acceptance criteria cells
            assigned_story_ids: Set of already assigned story IDs (modified in place)
            assigned_ac_ids: Set of already assigned AC IDs (modified in place)
        
        Returns:
            Dictionary representing the sub_epic with nested sub_epics
        """
        sub_epic_data = {
            'name': sub_epic_dict['name'],
            'sequential_order': sub_epic_dict['sequential_order'],
            'estimated_stories': sub_epic_dict.get('estimated_stories'),  # Include even if null
            'sub_epics': [],
            'story_groups': []
        }
        
        # Get child sub-epics (nested sub_epics) - sub-epics that have this sub-epic as parent
        child_sub_epics = [f for f in all_sub_epics 
                         if f.get('parent_feat_num') == sub_epic_dict.get('feat_num') 
                         and f.get('epic_num') == parent_epic_num]
        child_sub_epics.sort(key=lambda x: (x['x'], x.get('feat_num', 0)))
        
        # Recursively build nested sub_epics
        for child_sub_epic in child_sub_epics:
            nested_sub_epic = build_sub_epic_recursive(
                child_sub_epic, parent_epic_num, all_sub_epics, all_stories, 
                background_rectangles, stories_with_users, acceptance_criteria_cells,
                assigned_story_ids, assigned_ac_ids
            )
            sub_epic_data['sub_epics'].append(nested_sub_epic)
        
        # If this sub-epic has nested sub_epics (child sub-epics), it should NOT have any stories
        # All stories should belong to the nested sub_epics
        if child_sub_epics:
            return sub_epic_data  # Return without processing stories
        
        # Get stories for this sub_epic - only stories that belong to this sub-epic
        # and are NOT contained within any child sub-epic
        epic_stories = [s for s in all_stories if s['epic_num'] == parent_epic_num]
        sub_epic_stories = [s for s in epic_stories 
                       if s.get('feat_num') == sub_epic_dict.get('feat_num')]
        
        # Filter out stories that belong to child sub-epics (nested sub_epics)
        # A story belongs to a child sub-epic if it's contained within that sub-epic's bounds
        sub_epic_x = sub_epic_dict['x']
        sub_epic_y = sub_epic_dict['y']
        sub_epic_width = sub_epic_dict.get('width', 0)
        sub_epic_height = sub_epic_dict.get('height', 0)
        sub_epic_right = sub_epic_x + sub_epic_width
        sub_epic_bottom = sub_epic_y + sub_epic_height
        
        stories_for_this_sub_epic = []
        for story in sub_epic_stories:
            story_x = story['x']
            story_y = story['y']
            story_center_x = story_x + story.get('width', 50) / 2
            story_center_y = story_y + story.get('height', 50) / 2
            
            # Check if story is contained within any child sub-epic
            belongs_to_child = False
            for child_sub_epic in child_sub_epics:
                child_x = child_sub_epic['x']
                child_y = child_sub_epic['y']
                child_width = child_sub_epic.get('width', 0)
                child_height = child_sub_epic.get('height', 0)
                child_right = child_x + child_width
                child_bottom = child_y + child_height
                
                # Check if story is contained within child sub-epic
                if (child_x <= story_center_x <= child_right and
                    child_y <= story_center_y <= child_bottom):
                    belongs_to_child = True
                    break
            
            # Only add story if it doesn't belong to a child sub-epic
            if not belongs_to_child:
                stories_for_this_sub_epic.append(story)
        
        # Get stories for this sub_epic, sorted by sequential_order
        feat_stories = stories_for_this_sub_epic
        feat_stories.sort(key=lambda s: (
            s.get('sequential_order', 999) if isinstance(s.get('sequential_order'), (int, float)) else 999,
            s['x']
        ))
        
        # Group stories by background rectangles (story groups)
        # Match stories to background rectangles based on containment
        story_groups = {}  # Maps group_id -> list of stories
        group_rectangles = {}  # Maps group_id -> rectangle info
        
        # Filter background rectangles that belong to this sub-epic (horizontally aligned)
        sub_epic_left = sub_epic_dict['x']
        sub_epic_right = sub_epic_dict['x'] + sub_epic_dict.get('width', 0)
        sub_epic_bottom = sub_epic_dict['y'] + sub_epic_dict.get('height', 0)
        
        for bg_rect in background_rectangles:
                bg_x = bg_rect['x']
                bg_y = bg_rect['y']
                bg_width = bg_rect['width']
                bg_height = bg_rect['height']
                bg_right = bg_x + bg_width
                bg_bottom = bg_y + bg_height
                
                # Check if rectangle is below sub-epic and horizontally overlaps
                if (bg_y >= sub_epic_bottom - 50 and  # Below or slightly overlapping sub-epic
                    bg_x < sub_epic_right and bg_right > sub_epic_left):  # Horizontally overlaps
                    
                    group_id = bg_rect['id']
                    story_groups[group_id] = []
                    group_rectangles[group_id] = {
                        'x': bg_x,
                        'y': bg_y,
                        'width': bg_width,
                        'height': bg_height
                    }
        
        # Assign ALL stories to groups based on containment
        # No nested stories - all stories are flat within story groups
        ungrouped_stories = []
        
        for story in feat_stories:
                story_x = story['x']
                story_y = story['y']
                story_center_x = story_x + story.get('width', 50) / 2
                story_center_y = story_y + story.get('height', 50) / 2
                
                assigned = False
                for group_id, rect_info in group_rectangles.items():
                    rect_x = rect_info['x']
                    rect_y = rect_info['y']
                    rect_right = rect_x + rect_info['width']
                    rect_bottom = rect_y + rect_info['height']
                    
                    # Check if story center is within rectangle bounds
                    if (rect_x <= story_center_x <= rect_right and
                        rect_y <= story_center_y <= rect_bottom):
                        story_groups[group_id].append(story)
                        assigned = True
                        break
                
                if not assigned:
                    ungrouped_stories.append(story)
        
        # Sort groups by Y position (top to bottom), then X position (left to right)
        sorted_group_ids = sorted(group_rectangles.keys(), 
                                 key=lambda gid: (group_rectangles[gid]['y'], group_rectangles[gid]['x']))
        
        # Determine group types and connectors based on relative positioning
        # Group TYPE: Groups at same Y level (horizontal) = "and" type, groups at different Y levels (vertical) = "or" type
        # Group CONNECTOR: How this group connects to the previous group
        y_tolerance = 20  # Tolerance for grouping groups into rows
        base_story_y = 337
        opt_story_y = 402
        or_story_y_start = 404.75
        
        group_types = {}  # Group's own type (and/or based on positioning)
        group_connectors = {}  # How group connects to previous group
        previous_group_y = None
        
        for group_id in sorted_group_ids:
            group_y = group_rectangles[group_id]['y']
            
            if previous_group_y is None:
                # First group - determine type based on absolute Y position
                if abs(group_y - base_story_y) <= 10:
                    group_types[group_id] = 'and'  # Horizontal group
                elif abs(group_y - opt_story_y) <= 10:
                    group_types[group_id] = 'opt'  # Optional group
                else:
                    group_types[group_id] = 'or'  # Vertical group
                # First group has no connector (it's the first)
                group_connectors[group_id] = None
            else:
                # Determine type based on Y position relative to base row
                if abs(group_y - base_story_y) <= 10:
                    group_types[group_id] = 'and'  # Horizontal group
                elif abs(group_y - opt_story_y) <= 10:
                    group_types[group_id] = 'opt'  # Optional group
                elif abs(group_y - previous_group_y) <= y_tolerance:
                    group_types[group_id] = 'and'  # Same Y as previous = horizontal
                else:
                    group_types[group_id] = 'or'  # Different Y = vertical
                
                # Determine connector: how this group connects to previous group
                if abs(group_y - previous_group_y) <= y_tolerance:
                    # Same Y level (horizontal) - "and" connector
                    group_connectors[group_id] = 'and'
                else:
                    # Different Y level (vertical) - "or" connector
                    group_connectors[group_id] = 'or'
            
            previous_group_y = group_y
        
        # Process ungrouped stories - create a default group for them
        if ungrouped_stories:
            # Sort ungrouped stories by Y, then X
            ungrouped_stories.sort(key=lambda s: (s['y'], s['x']))
            # Create a default group for ungrouped top-level stories
            default_group_id = 'ungrouped'
            story_groups[default_group_id] = ungrouped_stories
            # Determine type and connector for default group based on first story's Y
            if ungrouped_stories:
                first_ungrouped_y = ungrouped_stories[0]['y']
                if abs(first_ungrouped_y - base_story_y) <= y_tolerance:
                    group_types[default_group_id] = 'and'
                elif abs(first_ungrouped_y - opt_story_y) <= y_tolerance:
                    group_types[default_group_id] = 'opt'
                else:
                    group_types[default_group_id] = 'or'
                # Default group has no connector (it's ungrouped, so no previous group)
                group_connectors[default_group_id] = None
            sorted_group_ids.append(default_group_id)
        
        # Determine connectors for stories based on Y position and X position
        # According to story-map-construction-rules.mdc:
        # - Sequential stories (connector="and"): Y-position = Base story row (y=337)
        # - Optional stories (connector="opt"): Y-position = y=402 (65px below base row)
        # - Alternative stories (connector="or"): Y-position = Below sequential stories (y=404.75+)
        # So: Stories at y=337 (base row) should be "and" (sequential)
        #     Stories at y=402 should be "opt" (optional)
        #     Stories at y=404.75+ should be "or" (alternatives)
        base_story_y = 337
        opt_story_y = 402  # Optional stories start at y=402
        or_story_y_start = 404.75  # Alternative stories start at y=404.75+
        y_tolerance = 10  # pixels tolerance for base row
        x_tolerance = 10  # pixels tolerance for same X position
        story_connectors = {}
        previous_x = None
        previous_y = None
        
        for story in feat_stories:
                story_x = story['x']
                story_y = story['y']
                
                if previous_x is None:
                    # First story - check Y position
                    if abs(story_y - base_story_y) <= y_tolerance:
                        # At base row - sequential "and"
                        story_connectors[story['id']] = 'and'
                    elif abs(story_y - opt_story_y) <= y_tolerance:
                        # At optional row (y=402) - optional "opt"
                        story_connectors[story['id']] = 'opt'
                    else:
                        # Below base row (y=404.75+) - alternative "or"
                        story_connectors[story['id']] = 'or'
                elif abs(story_y - base_story_y) <= y_tolerance:
                    # At base row (y=337) - sequential "and" connector
                    story_connectors[story['id']] = 'and'
                elif abs(story_y - opt_story_y) <= y_tolerance:
                    # At optional row (y=402) - optional "opt" connector
                    story_connectors[story['id']] = 'opt'
                elif abs(story_y - previous_y) <= y_tolerance:
                    # Same Y as previous (both below base row) - check X
                    if abs(story_x - previous_x) < x_tolerance:
                        # Same X position - inherit previous connector type
                        story_connectors[story['id']] = story_connectors.get(feat_stories[feat_stories.index(story) - 1]['id'], 'or')
                    else:
                        # Different X position - "or" (alternative path)
                        story_connectors[story['id']] = 'or'
                else:
                    # Different Y position from previous - check if opt or or
                    if story_y >= or_story_y_start:
                        story_connectors[story['id']] = 'or'
                    elif abs(story_y - opt_story_y) <= y_tolerance:
                        story_connectors[story['id']] = 'opt'
                    else:
                        story_connectors[story['id']] = 'or'
                
                previous_x = story_x
                previous_y = story_y
        
        # Group stories by Y position (rows) within this sub-epic
        # Traversal logic: Go left to right, capture sequence of "and" stories (first row)
        # If there's a next row, add stories to nested children of first story in first row
        y_tolerance_row = 20  # Tolerance for grouping stories into rows (increased to handle slight Y variations)
        stories_by_row = {}
        for story in feat_stories:
                story_y = story['y']
                # Find which row this story belongs to (group by similar Y)
                row_key = None
                for existing_y in stories_by_row.keys():
                    if abs(story_y - existing_y) <= y_tolerance_row:
                        row_key = existing_y
                        break
                if row_key is None:
                    row_key = story_y
                if row_key not in stories_by_row:
                    stories_by_row[row_key] = []
                stories_by_row[row_key].append(story)
        
        # Sort rows by Y position (top to bottom)
        sorted_rows = sorted(stories_by_row.items())
        first_row_y = sorted_rows[0][0] if sorted_rows else None
        
        # Process stories row by row
        # No nested stories - all stories are flat within story groups
        # Initialize temp_stories before processing stories
        if 'temp_stories' not in sub_epic_data:
            sub_epic_data['temp_stories'] = {}  # Maps group_id -> list of story_data
        
        for story_idx, story in enumerate(feat_stories):
                # Skip if this story has already been assigned to another sub_epic (prevent duplicates)
                if story['id'] in assigned_story_ids:
                    continue
                
                story_x = story['x']
                story_y = story['y']
                
                story_data = {
                    'name': story['name'],
                    'sequential_order': story.get('sequential_order', 1),
                    'connector': story_connectors.get(story['id'], 'and'),  # Extract from position
                    'users': stories_with_users.get(story['id'], []),
                    'story_type': story.get('story_type', 'user'),
                    'x': story_x,  # Store x position for sorting
                    'y': story_y   # Store y position for sorting
                }
                
                # Match acceptance criteria to this story based on position and shape
                # AC boxes are wider (width > 100) and positioned below stories
                story_ac = []
                tolerance_x = 100  # Increased tolerance for AC boxes (they can be wider than stories)
                story_height = 50  # Approximate story height
                story_width = story.get('width', 50)
                story_right = story_x + story_width
                
                # Find all AC boxes that belong to this story
                # AC boxes are:
                # - Below the story (y > story_y + story_height)
                # - Horizontally aligned (within tolerance or overlapping)
                # - Wider than stories (width > 100)
                # - Not already assigned to another story
                for ac in acceptance_criteria_cells:
                    if ac['id'] in assigned_ac_ids:
                        continue  # Skip already assigned AC boxes
                    
                    ac_x = ac['x']
                    ac_y = ac['y']
                    ac_width = ac['width']
                    ac_height = ac['height']
                    ac_right = ac_x + ac_width
                    
                    # Check if AC box is wider than story (AC boxes are typically 250px wide, stories are 50px)
                    is_wider = ac_width > 100
                    
                    # Check if acceptance criteria is below story
                    is_below = ac_y > story_y + story_height
                    
                    # Check if AC is not too far below (within reasonable distance, max 500px)
                    max_distance_below = story_y + story_height + 500
                    is_within_range = ac_y < max_distance_below
                    
                    # Check horizontal alignment/overlap
                    # AC boxes can be wider than stories, so check if they overlap horizontally
                    is_aligned = (abs(ac_x - story_x) < tolerance_x or 
                                 (ac_x <= story_x <= ac_right) or 
                                 (story_x <= ac_x <= story_right))
                    
                    # Match if: wider, below, within range, and aligned
                    # OR if AC box ID matches this story's ID pattern (more reliable)
                    ac_id = ac['id']
                    story_id_pattern = story['id']  # e.g., "e1f1s1"
                    
                    # Check if AC box ID contains this story's ID (format: ac_e1f1s1_0)
                    ac_matches_story = ac_id.startswith(f'ac_{story_id_pattern}_')
                    
                    if (is_wider and is_below and is_within_range and is_aligned) or ac_matches_story:
                        # Extract all text from AC box - keep as one entry (don't split by <br>)
                        import re
                        ac_text = ac['text']
                        # Replace <br> tags with newlines to preserve line breaks
                        ac_text_clean = ac_text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
                        ac_text_clean = re.sub(r'<[^>]+>', '', ac_text_clean)  # Remove HTML tags
                        # Normalize whitespace but preserve newlines
                        ac_text_clean = re.sub(r'[ \t]+', ' ', ac_text_clean)  # Normalize spaces/tabs
                        ac_text_clean = re.sub(r' *\n *', '\n', ac_text_clean)  # Clean up around newlines
                        ac_text_clean = ac_text_clean.strip()  # Remove leading/trailing whitespace
                        
                        if ac_text_clean:
                            story_ac.append({
                                'description': ac_text_clean,
                                'sequential_order': len(story_ac) + 1
                            })
                        
                        assigned_ac_ids.add(ac['id'])  # Mark this AC as assigned
                
                # Add acceptance_criteria only if found
                if story_ac:
                    story_data['acceptance_criteria'] = story_ac
                
                # No nested stories - stories are flat within story groups
                
                # Find which group this story belongs to
                story_group_id = None
                for group_id, group_stories in story_groups.items():
                    if story in group_stories:
                        story_group_id = group_id
                        break
                
                # If story not in any group, add to ungrouped
                if story_group_id is None:
                    if 'ungrouped' not in story_groups:
                        story_groups['ungrouped'] = []
                        group_types['ungrouped'] = 'and'  # Default type
                        group_connectors['ungrouped'] = None  # No connector (ungrouped)
                        if 'ungrouped' not in sorted_group_ids:
                            sorted_group_ids.append('ungrouped')
                    story_group_id = 'ungrouped'
                    story_groups['ungrouped'].append(story)
                
                # Store story_data temporarily - we'll organize into groups after processing all stories
                # temp_stories already initialized before the loop
                if story_group_id not in sub_epic_data['temp_stories']:
                    sub_epic_data['temp_stories'][story_group_id] = []
                sub_epic_data['temp_stories'][story_group_id].append(story_data)
                assigned_story_ids.add(story['id'])  # Mark this story as assigned
        
        # Now organize stories into story groups and determine group type based on story layout
        for group_idx, group_id in enumerate(sorted_group_ids, 1):
                group_stories = sub_epic_data['temp_stories'].get(group_id, [])
                if group_stories:
                    # Determine group TYPE based on how stories are laid out within the group
                    # Need to check the actual story positions from the original story data
                    group_story_y_positions = []
                    group_story_x_positions = []
                    for story_data in group_stories:
                        # Find the original story to get its position
                        story_name = story_data['name']
                        for story in feat_stories:
                            if story['name'] == story_name:
                                group_story_y_positions.append(story['y'])
                                group_story_x_positions.append(story['x'])
                                break
                    
                    # Determine group type: if stories are at same Y level (within tolerance), it's "and" (horizontal)
                    # If stories are at different Y levels, it's "or" (vertical)
                    story_y_tolerance = 20  # Tolerance for considering stories at same Y level
                    if len(group_story_y_positions) > 1:
                        min_y = min(group_story_y_positions)
                        max_y = max(group_story_y_positions)
                        if abs(max_y - min_y) <= story_y_tolerance:
                            # Stories are at same Y level - horizontal layout (left to right) = "and" type
                            group_type = 'and'
                        else:
                            # Stories are at different Y levels - vertical layout (top to bottom) = "or" type
                            group_type = 'or'
                    else:
                        # Single story - default to "and" type
                        group_type = 'and'
                    
                    # Sort stories within group based on group type
                    # For "and" type (horizontal): sort by X position (left to right)
                    # For "or" type (vertical): sort by Y position (top to bottom), then X (left to right)
                    group_stories_with_positions = []
                    for story_data in group_stories:
                        story_name = story_data['name']
                        story_y = None
                        story_x = None
                        # Find the original story to get its position - use the story's own x/y if available
                        # Otherwise look it up in feat_stories
                        if 'x' in story_data and 'y' in story_data:
                            story_x = story_data['x']
                            story_y = story_data['y']
                        else:
                            for story in feat_stories:
                                if story['name'] == story_name:
                                    story_y = story['y']
                                    story_x = story['x']
                                    break
                        group_stories_with_positions.append((story_y or 0, story_x or 0, story_data))
                    
                    # Sort based on group type
                    if group_type == 'and':
                        # Horizontal layout: sort by X position (left to right) only
                        group_stories_with_positions.sort(key=lambda s: float(s[1]))  # Sort by X (ensure numeric)
                    else:
                        # Vertical layout: sort by Y first (top to bottom), then X (left to right)
                        group_stories_with_positions.sort(key=lambda s: (float(s[0]), float(s[1])))  # Sort by Y, then X (ensure numeric)
                    group_stories = [story_data for _, _, story_data in group_stories_with_positions]
                    
                    # Renumber stories within group to 1, 2, 3...
                    for story_idx, story_data in enumerate(group_stories, 1):
                        story_data['sequential_order'] = story_idx
                        # Remove x and y coordinates - they're only used for sorting, layout info is stored separately
                        story_data.pop('x', None)
                        story_data.pop('y', None)
                    
                    story_group_data = {
                        'type': group_type,  # Group's own type: "and" = horizontal (left to right), "or" = vertical (top to bottom)
                        'connector': group_connectors.get(group_id, 'and'),  # How it connects to previous group
                        'stories': group_stories
                    }
                    sub_epic_data['story_groups'].append(story_group_data)
        
        # Clean up temp data
        if 'temp_stories' in sub_epic_data:
            del sub_epic_data['temp_stories']
        
        # Return the completed sub_epic_data with nested sub_epics and story_groups
        return sub_epic_data
    
    # Main loop: build epic hierarchy using recursive function
    for epic in sorted_epics:
        epic_data = {
            'name': epic['name'],
            'sequential_order': epic['sequential_order'],
            'estimated_stories': epic.get('estimated_stories'),  # Include even if null
            'sub_epics': [],
            'stories': []
        }
        
        # Get top-level sub-epics for this epic (sub-epics without a parent sub-epic)
        epic_sub_epics = sorted([f for f in sub_epics 
                               if f['epic_num'] == epic['epic_num'] 
                               and f.get('parent_feat_num') is None], 
                               key=lambda x: (x['x'], x.get('feat_num', 0)))
        
        # Build each top-level sub-epic recursively (which will include nested sub_epics)
        for sub_epic_dict in epic_sub_epics:
            sub_epic_data = build_sub_epic_recursive(
                sub_epic_dict, epic['epic_num'], sub_epics, all_stories, 
                background_rectangles, stories_with_users, acceptance_criteria_cells,
                assigned_story_ids, assigned_ac_ids
            )
            epic_data['sub_epics'].append(sub_epic_data)
        
        # Epics don't have direct stories - only through sub_epics -> story_groups (legacy code removed)
        
        result['epics'].append(epic_data)
    
    # Build layout data if requested
    if return_layout:
        layout_data = {}
        
        # Store epic coordinates and dimensions
        for epic in sorted_epics:
            epic_key = f"EPIC|{epic['name']}"
            layout_data[epic_key] = {
                'x': epic['x'],
                'y': epic['y'],
                'width': epic.get('width', 0),
                'height': epic.get('height', 0)
            }
        
        # Store sub-epic coordinates and dimensions
        for sub_epic in sub_epics:
            epic = next((e for e in sorted_epics if e['epic_num'] == sub_epic['epic_num']), None)
            if epic:
                sub_epic_key = f"SUB_EPIC|{epic['name']}|{sub_epic['name']}"
                layout_data[sub_epic_key] = {
                    'x': sub_epic['x'],
                    'y': sub_epic['y'],
                    'width': sub_epic.get('width', 0),
                    'height': sub_epic.get('height', 0)
                }
        
        # Store story coordinates
        for story in all_stories:
            # Create key: epic_name|sub_epic_name|story_name
            epic = next((e for e in sorted_epics if e['epic_num'] == story['epic_num']), None)
            if epic:
                epic_sub_epics = sorted([f for f in sub_epics if f['epic_num'] == epic['epic_num']], 
                                      key=lambda x: (x['x'], x.get('feat_num', 0)))
                sub_epic = next((f for f in epic_sub_epics if f.get('feat_num') == story.get('feat_num')), None)
                if sub_epic:
                    key = f"{epic['name']}|{sub_epic['name']}|{story['name']}"
                    layout_data[key] = {
                        'x': story['x'],
                        'y': story['y']
                    }
        
        # Store user coordinates - match users to their stories/epics/features
        # Skip users at top of map (y < 50) - these are "deleted" users
        for user_cell in user_cells:
            user_name = user_cell['name']
            user_x = user_cell['x']
            user_y = user_cell['y']
            
            # Skip users at top of map (deleted users)
            if user_y < 50:
                continue
            
            # Try to find which story this user is associated with
            tolerance = 25
            matched = False
            for story in all_stories:
                story_x = story['x']
                story_y = story['y']
                # User is above and horizontally aligned with story
                if abs(user_x - story_x) <= tolerance and user_y < story_y:
                    epic = next((e for e in sorted_epics if e['epic_num'] == story['epic_num']), None)
                    if epic:
                        epic_sub_epics = sorted([f for f in sub_epics if f['epic_num'] == epic['epic_num']], 
                                              key=lambda x: (x['x'], x.get('feat_num', 0)))
                        sub_epic = next((f for f in epic_sub_epics if f.get('feat_num') == story.get('feat_num')), None)
                        if sub_epic:
                            # Story-level user: epic_name|sub_epic_name|story_name|user_name
                            story_key = f"{epic['name']}|{sub_epic['name']}|{story['name']}"
                            user_key = f"{story_key}|{user_name}"
                            layout_data[user_key] = {
                                'x': user_x,
                                'y': user_y
                            }
                            matched = True
                            break
            
            # If not matched to a story, check if it's epic or feature level
            if not matched:
                # Check epic level (users above epic Y position)
                for epic in sorted_epics:
                    if abs(user_x - epic['x']) <= 100 and user_y < epic['y'] + 100:
                        # Epic-level user: epic_name|user_name
                        user_key = f"{epic['name']}|{user_name}"
                        layout_data[user_key] = {
                            'x': user_x,
                            'y': user_y
                        }
                        matched = True
                        break
                
                # Check sub-epic level (users above sub-epic Y position)
                if not matched:
                    for sub_epic in sub_epics:
                        if abs(user_x - sub_epic['x']) <= 100 and user_y < sub_epic['y'] + 100:
                            epic = next((e for e in sorted_epics if e['epic_num'] == sub_epic['epic_num']), None)
                            if epic:
                                # Sub-epic-level user: epic_name|sub_epic_name|user_name
                                user_key = f"{epic['name']}|{sub_epic['name']}|{user_name}"
                                layout_data[user_key] = {
                                    'x': user_x,
                                    'y': user_y
                                }
                                matched = True
                                break
        
        result['layout'] = layout_data
    
    return result


def _assign_sequential_order(all_stories: List[Dict]):
    """
    Assign sequential_order to stories based on left-to-right position.
    When a story is below another story (higher Y), use num.num format.
    Sequential order is global across all stories in the map.
    """
    # Sort all stories by X position (left to right), then by Y position (top to bottom)
    all_stories.sort(key=lambda x: (x['x'], x['y']))
    
    # Tolerance for considering stories at the same X position (for vertical stacking)
    x_tolerance = 30  # pixels
    
    stories_by_x_group = {}
    
    # Group stories by X position (within tolerance)
    for story in all_stories:
        story_x = story['x']
        
        # Find if this story belongs to an existing X group
        found_group = False
        for group_x, group_stories in stories_by_x_group.items():
            if abs(story_x - group_x) <= x_tolerance:
                # Add to existing group
                group_stories.append(story)
                found_group = True
                break
        
        if not found_group:
            # Create new X group
            stories_by_x_group[story_x] = [story]
    
    # Sort X groups by X position
    sorted_x_groups = sorted(stories_by_x_group.items(), key=lambda x: x[0])
    
    # Assign sequential order globally
    current_order = 1
    for group_x, group_stories in sorted_x_groups:
        # Sort stories in this group by Y position (top to bottom)
        group_stories.sort(key=lambda x: x['y'])
        
        if len(group_stories) == 1:
            # Single story - just assign order number
            group_stories[0]['sequential_order'] = current_order
            current_order += 1
        else:
            # Multiple stories stacked vertically - use num.num format
            base_order = current_order
            for idx, story in enumerate(group_stories):
                if idx == 0:
                    # First story in stack gets base order
                    story['sequential_order'] = base_order
                else:
                    # Subsequent stories get base_order.idx format
                    story['sequential_order'] = float(f"{base_order}.{idx}")
            current_order += 1


def build_increments_from_extracted_epics(drawio_path: Path, increments: List[Dict], 
                                          extracted_epics: List[Dict]) -> List[Dict[str, Any]]:
    """
    Build increments from already-extracted epics (with story_groups).
    Post-processing step that flattens story_groups into direct stories array.
    
    Algorithm:
    1. For each increment, iterate through all extracted epics
    2. Recursively traverse epic → sub_epic → nested sub_epics (to bottom)
    3. For each story in story_groups, check if Y position matches increment Y
    4. If match, add story to parent sub_epic (ignore groups, flatten to direct stories array)
    5. If parent not added yet, add parent first (build hierarchy on-demand)
    6. Renumber sequential_order to reflect flat list (no grouping)
    
    Args:
        drawio_path: Path to DrawIO file (for story Y position lookup)
        increments: List of increment markers with Y positions
        extracted_epics: Already-extracted epics with story_groups structure
    
    Returns:
        List of increment dictionaries with epics, sub_epics, and flattened stories
    """
    tree = ET.parse(drawio_path)
    root = tree.getroot()
    cells = root.findall('.//mxCell')
    
    # Build map of story name -> Y position from DrawIO
    story_positions = {}
    for cell in cells:
        style = cell.get('style', '')
        value = get_cell_value(cell)
        geom = extract_geometry(cell)
        
        if geom is None:
            continue
        
        # Stories: yellow boxes
        is_story = 'fillColor=#fff2cc' in style and 'strokeColor=#d6b656' in style
        if is_story and value:
            story_positions[value] = geom['y']
    
    increment_tolerance = 100  # pixels
    
    # First pass: assign each story to its CLOSEST increment
    story_to_increment = {}  # story_name -> increment_index
    for story_name, story_y in story_positions.items():
        closest_inc_idx = None
        closest_distance = float('inf')
        
        for inc_idx, increment in enumerate(increments, 1):
            distance = abs(story_y - increment['y'])
            if distance <= increment_tolerance and distance < closest_distance:
                closest_distance = distance
                closest_inc_idx = inc_idx
        
        if closest_inc_idx is not None:
            story_to_increment[story_name] = closest_inc_idx
    
    # Build increments
    result = []
    for inc_idx, increment in enumerate(increments, 1):
        inc_data = {
            'name': increment['name'],
            'priority': inc_idx,
            'epics': []
        }
        
        # Iterate through all extracted epics
        for epic in extracted_epics:
            inc_epic = None  # Will create on-demand
            
            # Recursively process sub_epics
            def process_sub_epic(sub_epic):
                """Recursively process sub_epic and return sub_epic with matching stories"""
                collected_stories = []
                nested_sub_epics_with_stories = []
                
                # Check stories in story_groups
                for group in sub_epic.get('story_groups', []):
                    for story in group.get('stories', []):
                        story_name = story['name']
                        
                        # Only include if this story belongs to current increment
                        if story_to_increment.get(story_name) == inc_idx:
                            collected_stories.append(story.copy())
                
                # Recursively process nested sub_epics
                for nested_sub_epic in sub_epic.get('sub_epics', []):
                    nested_result = process_sub_epic(nested_sub_epic)
                    if nested_result:  # Only include if it has stories
                        nested_sub_epics_with_stories.append(nested_result)
                
                # Only return sub_epic if it has stories or nested sub_epics with stories
                if collected_stories or nested_sub_epics_with_stories:
                    return {
                        'name': sub_epic['name'],
                        'sequential_order': sub_epic.get('sequential_order', 1),
                        'sub_epics': nested_sub_epics_with_stories,
                        'stories': collected_stories
                    }
                return None
            
            # Process all sub_epics in this epic
            epic_sub_epics_with_stories = []
            for sub_epic in epic.get('sub_epics', []):
                result_sub_epic = process_sub_epic(sub_epic)
                if result_sub_epic:
                    epic_sub_epics_with_stories.append(result_sub_epic)
            
            # Only add epic to increment if it has sub_epics with stories
            if epic_sub_epics_with_stories:
                inc_data['epics'].append({
                    'name': epic['name'],
                    'sequential_order': epic.get('sequential_order', 1),
                    'sub_epics': epic_sub_epics_with_stories
                })
        
        result.append(inc_data)
    
    # Final cleanup: recursively remove empty sub_epics (no stories, no nested sub_epics)
    def cleanup_empty_sub_epics(sub_epics_list):
        """Recursively remove empty sub_epics"""
        cleaned = []
        for se in sub_epics_list:
            # Recursively clean nested sub_epics first
            if se.get('sub_epics'):
                se['sub_epics'] = cleanup_empty_sub_epics(se['sub_epics'])
            
            # Keep sub_epic if it has stories (non-empty list) OR non-empty nested sub_epics
            has_stories = len(se.get('stories', [])) > 0
            has_nested = len(se.get('sub_epics', [])) > 0
            if has_stories or has_nested:
                cleaned.append(se)
        return cleaned
    
    for inc_data in result:
        for epic in inc_data.get('epics', []):
            epic['sub_epics'] = cleanup_empty_sub_epics(epic.get('sub_epics', []))
        
        # Remove epics that have no sub_epics after cleanup
        inc_data['epics'] = [
            epic for epic in inc_data.get('epics', [])
            if epic.get('sub_epics')
        ]
    
    return result


def _detect_large_deletions(
    original_data: Dict[str, Any],
    extracted_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Detect large deletions (entire epics or features missing).
    Returns a report of potential accidental deletions.
    """
    deletions = {
        'missing_epics': [],
        'missing_sub_epics': [],
        'epics_with_many_missing_stories': [],
        'sub_epics_with_many_missing_stories': []
    }
    
    # Build maps for comparison
    original_epics = {epic['name']: epic for epic in original_data.get('epics', [])}
    extracted_epics = {epic['name']: epic for epic in extracted_data.get('epics', [])}
    
    # Helper to get sub_epics
    def get_sub_epics(epic):
        return epic.get('sub_epics', [])
    
    # Find missing epics
    for epic_name, epic in original_epics.items():
        if epic_name not in extracted_epics:
            original_story_count = sum(
                len(se.get('stories', [])) 
                for se in get_sub_epics(epic)
            )
            deletions['missing_epics'].append({
                'name': epic_name,
                'story_count': original_story_count,
                'sub_epic_count': len(get_sub_epics(epic))
            })
    
    # Find missing sub_epics and epics with many missing stories
    for epic_name, original_epic in original_epics.items():
        if epic_name in extracted_epics:
            extracted_epic = extracted_epics[epic_name]
            
            original_sub_epics = {se['name']: se for se in get_sub_epics(original_epic)}
            extracted_sub_epics = {se['name']: se for se in get_sub_epics(extracted_epic)}
            
            # Find missing sub_epics
            for sub_epic_name, sub_epic in original_sub_epics.items():
                if sub_epic_name not in extracted_sub_epics:
                    deletions['missing_sub_epics'].append({
                        'epic': epic_name,
                        'name': sub_epic_name,
                        'story_count': len(sub_epic.get('stories', []))
                    })
            
            # Check for epics with many missing stories
            original_story_count = sum(
                len(se.get('stories', [])) 
                for se in get_sub_epics(original_epic)
            )
            extracted_story_count = sum(
                len(se.get('stories', [])) 
                for se in get_sub_epics(extracted_epic)
            )
            
            if original_story_count > 0:
                missing_ratio = (original_story_count - extracted_story_count) / original_story_count
                if missing_ratio > 0.5:  # More than 50% missing
                    deletions['epics_with_many_missing_stories'].append({
                        'name': epic_name,
                        'original_count': original_story_count,
                        'extracted_count': extracted_story_count,
                        'missing_count': original_story_count - extracted_story_count,
                        'missing_ratio': missing_ratio
                    })
            
            # Check for sub_epics with many missing stories
            for sub_epic_name, original_sub_epic in original_sub_epics.items():
                if sub_epic_name in extracted_sub_epics:
                    extracted_sub_epic = extracted_sub_epics[sub_epic_name]
                    orig_stories = len(original_sub_epic.get('stories', []))
                    extr_stories = len(extracted_sub_epic.get('stories', []))
                    
                    if orig_stories > 0:
                        missing_ratio = (orig_stories - extr_stories) / orig_stories
                        if missing_ratio > 0.5:  # More than 50% missing
                            deletions['sub_epics_with_many_missing_stories'].append({
                                'epic': epic_name,
                                'name': sub_epic_name,
                                'original_count': orig_stories,
                                'extracted_count': extr_stories,
                                'missing_count': orig_stories - extr_stories,
                                'missing_ratio': missing_ratio
                            })
    
    return deletions


def _display_large_deletions(deletions: Dict[str, Any]) -> None:
    """Display large deletion warnings in a prominent format."""
    has_warnings = False
    
    if deletions.get('missing_epics'):
        has_warnings = True
        print("\n" + "!"*80)
        print("WARNING: ENTIRE EPICS MISSING FROM DRAWIO")
        print("!"*80)
        for epic in deletions['missing_epics']:
            print(f"  MISSING EPIC: {epic['name']}")
            print(f"    - {epic['sub_epic_count']} sub_epics")
            print(f"    - {epic['story_count']} stories")
            print(f"    - This may be an accidental deletion!")
        print("!"*80)
    
    if deletions.get('missing_sub_epics'):
        has_warnings = True
        print("\n" + "!"*80)
        print("WARNING: ENTIRE SUB-EPICS MISSING FROM DRAWIO")
        print("!"*80)
        for sub_epic in deletions['missing_sub_epics']:
            print(f"  MISSING SUB-EPIC: {sub_epic['epic']} > {sub_epic['name']}")
            print(f"    - {sub_epic['story_count']} stories")
            print(f"    - This may be an accidental deletion!")
        print("!"*80)
    
    if deletions.get('epics_with_many_missing_stories'):
        has_warnings = True
        print("\n" + "-"*80)
        print("WARNING: EPICS WITH MANY MISSING STORIES (>50%)")
        print("-"*80)
        for epic in deletions['epics_with_many_missing_stories']:
            print(f"  EPIC: {epic['name']}")
            print(f"    - Original: {epic['original_count']} stories")
            print(f"    - Extracted: {epic['extracted_count']} stories")
            print(f"    - Missing: {epic['missing_count']} stories ({epic['missing_ratio']:.1%})")
        print("-"*80)
    
    if deletions.get('sub_epics_with_many_missing_stories'):
        has_warnings = True
        print("\n" + "-"*80)
        print("WARNING: SUB-EPICS WITH MANY MISSING STORIES (>50%)")
        print("-"*80)
        for sub_epic in deletions['sub_epics_with_many_missing_stories']:
            print(f"  SUB-EPIC: {sub_epic['epic']} > {sub_epic['name']}")
            print(f"    - Original: {sub_epic['original_count']} stories")
            print(f"    - Extracted: {sub_epic['extracted_count']} stories")
            print(f"    - Missing: {sub_epic['missing_count']} stories ({sub_epic['missing_ratio']:.1%})")
        print("-"*80)
    
    if has_warnings:
        print("\n" + "="*80)
        print("RECOMMENDATION: Review these deletions carefully before merging.")
        print("Large batches of deleted stories may indicate accidental deletion.")
        print("="*80 + "\n")


def _flatten_stories_from_original(original_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten all stories from original story graph into a list with context."""
    stories = []
    
    for epic in original_data.get('epics', []):
        epic_name = epic.get('name', '')
        for sub_epic in epic.get('sub_epics', []):
            sub_epic_name = sub_epic.get('name', '')
            # Only use story_groups (no legacy direct stories support)
            for story_group in sub_epic.get('story_groups', []):
                for story in story_group.get('stories', []):
                    story_data = {
                        'name': story.get('name', ''),
                        'users': story.get('users', []),
                        'Steps': story.get('Steps', []),
                        'acceptance_criteria': story.get('acceptance_criteria', []),
                        'epic_name': epic_name,
                        'sub_epic_name': sub_epic_name
                    }
                    stories.append(story_data)
    
    return stories


def _flatten_stories_from_extracted(extracted_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten all stories from extracted story graph into a list with context."""
    stories = []
    
    for epic in extracted_data.get('epics', []):
        epic_name = epic.get('name', '')
        for sub_epic in epic.get('sub_epics', []):
            sub_epic_name = sub_epic.get('name', '')
            # Only use story_groups (no legacy direct stories support)
            for story_group in sub_epic.get('story_groups', []):
                for story in story_group.get('stories', []):
                    story_data = {
                        'name': story.get('name', ''),
                        'users': story.get('users', []),
                        'sequential_order': story.get('sequential_order'),
                        'epic_name': epic_name,
                        'sub_epic_name': sub_epic_name
                    }
                    if 'story_type' in story and story.get('story_type') != 'user':
                        story_data['story_type'] = story['story_type']
                    stories.append(story_data)
    
    return stories


def _fuzzy_match_story(extracted_story: Dict[str, Any], original_stories: List[Dict[str, Any]], 
                       threshold: float = 0.7) -> Optional[Tuple[Dict[str, Any], float]]:
    """
    Find best matching story from original using fuzzy matching.
    
    Returns:
        Tuple of (matched_story, similarity_score) or None if no match above threshold
    """
    extracted_name = extracted_story['name'].lower()
    best_match = None
    best_score = 0.0
    
    for orig_story in original_stories:
        orig_name = orig_story['name'].lower()
        
        # Calculate similarity
        similarity = difflib.SequenceMatcher(None, extracted_name, orig_name).ratio()
        
        # Bonus for same epic/sub_epic context
        context_bonus = 0.0
        if extracted_story.get('epic_name') == orig_story.get('epic_name'):
            context_bonus += 0.1
        ext_sub_epic = extracted_story.get('sub_epic_name', '')
        orig_sub_epic = orig_story.get('sub_epic_name', '')
        if ext_sub_epic == orig_sub_epic:
            context_bonus += 0.1
        
        # Bonus for user overlap
        extracted_users = set(u.lower() for u in extracted_story.get('users', []))
        orig_users = set(u.lower() for u in orig_story.get('users', []))
        if extracted_users and orig_users:
            user_overlap = len(extracted_users & orig_users) / max(len(extracted_users), len(orig_users))
            context_bonus += user_overlap * 0.1
        
        total_score = min(1.0, similarity + context_bonus)
        
        if total_score > best_score:
            best_score = total_score
            best_match = orig_story
    
    if best_score >= threshold:
        return (best_match, best_score)
    return None


def generate_merge_report(
    extracted_path: Path,
    original_path: Path,
    report_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Generate a merge report comparing extracted and original story graphs.
    
    Args:
        extracted_path: Path to extracted story graph JSON
        original_path: Path to original story graph JSON
        report_path: Optional path to write report JSON
        
    Returns:
        Dictionary containing merge report data
    """
    # Load both JSON files
    with open(extracted_path, 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)
    
    with open(original_path, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    # Flatten stories for comparison
    extracted_stories = _flatten_stories_from_extracted(extracted_data)
    original_stories = _flatten_stories_from_original(original_data)
    
    # Match stories
    exact_matches = []
    fuzzy_matches = []
    new_stories = []
    unmatched_original = []
    
    matched_original_indices = set()
    
    for ext_story in extracted_stories:
        # Try exact match first
        exact_match = None
        for idx, orig_story in enumerate(original_stories):
            if (ext_story['name'].lower() == orig_story['name'].lower() and
                idx not in matched_original_indices):
                exact_match = (orig_story, idx)
                break
        
        if exact_match:
            orig_story, idx = exact_match
            exact_matches.append({
                'extracted': ext_story,
                'original': orig_story,
                'match_type': 'exact',
                'confidence': 1.0
            })
            matched_original_indices.add(idx)
        else:
            # Try fuzzy match
            fuzzy_result = _fuzzy_match_story(ext_story, original_stories)
            if fuzzy_result:
                orig_story, score = fuzzy_result
                # Find index of matched story
                for idx, o in enumerate(original_stories):
                    if o['name'] == orig_story['name'] and idx not in matched_original_indices:
                        fuzzy_matches.append({
                            'extracted': ext_story,
                            'original': orig_story,
                            'match_type': 'fuzzy',
                            'confidence': score
                        })
                        matched_original_indices.add(idx)
                        break
            else:
                # New story in extracted
                new_stories.append(ext_story)
    
    # Find unmatched original stories
    for idx, orig_story in enumerate(original_stories):
        if idx not in matched_original_indices:
            unmatched_original.append(orig_story)
    
    # Build report
    report = {
        'timestamp': datetime.now().isoformat(),
        'extracted_file': str(extracted_path),
        'original_file': str(original_path),
        'summary': {
            'total_extracted_stories': len(extracted_stories),
            'total_original_stories': len(original_stories),
            'exact_matches': len(exact_matches),
            'fuzzy_matches': len(fuzzy_matches),
            'new_stories': len(new_stories),
            'removed_stories': len(unmatched_original)
        },
        'exact_matches': exact_matches,
        'fuzzy_matches': fuzzy_matches,
        'new_stories': new_stories,
        'removed_stories': unmatched_original
    }
    
    # Write report if path provided
    if report_path:
        report_path = Path(report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    
    return report


def merge_story_graphs(
    extracted_path: Path,
    original_path: Path,
    report_path: Path,
    output_path: Path
) -> Dict[str, Any]:
    """
    Merge extracted story graph with original, preserving Steps from original.
    
    Args:
        extracted_path: Path to extracted story graph JSON
        original_path: Path to original story graph JSON
        report_path: Path to merge report JSON
        output_path: Path to write merged story graph JSON
        
    Returns:
        Dictionary containing merged story graph
    """
    # Load files
    with open(extracted_path, 'r', encoding='utf-8') as f:
        extracted_data = json.load(f)
    
    with open(original_path, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # Create maps for matches: key -> extracted story and original story
    # This allows us to update original stories with extracted data
    extracted_story_map = {}  # Maps key -> extracted story data
    original_story_map = {}   # Maps key -> original story data
    
    for match in report.get('exact_matches', []):
        ext_story = match['extracted']
        orig_story = match['original']
        sub_epic_name = ext_story.get('sub_epic_name', '')
        key = f"{ext_story['epic_name']}|{sub_epic_name}|{ext_story['name']}"
        extracted_story_map[key] = ext_story
        original_story_map[key] = orig_story
    
    for match in report.get('fuzzy_matches', []):
        ext_story = match['extracted']
        orig_story = match['original']
        sub_epic_name = ext_story.get('sub_epic_name', '')
        key = f"{ext_story['epic_name']}|{sub_epic_name}|{ext_story['name']}"
        extracted_story_map[key] = ext_story
        original_story_map[key] = orig_story
    
    # Merge: start with original structure to preserve all stories, then update extracted stories
    # This ensures the merged file has the full structure, not just extracted stories
    merged_data = json.loads(json.dumps(original_data))  # Deep copy of original
    
    # Also need to get the actual extracted story objects (not just flattened data)
    # Create a map of extracted stories by key for updating
    extracted_full_story_map = {}
    for epic in extracted_data.get('epics', []):
        epic_name = epic.get('name', '')
        for sub_epic in epic.get('sub_epics', []):
            sub_epic_name = sub_epic.get('name', '')
            # Only use story_groups (no legacy direct stories support)
            for story_group in sub_epic.get('story_groups', []):
                for story in story_group.get('stories', []):
                    story_name = story.get('name', '')
                    key = f"{epic_name}|{sub_epic_name}|{story_name}"
                    extracted_full_story_map[key] = story
    
    # Merge epics - only use story_groups (no legacy direct stories support)
    for epic in merged_data.get('epics', []):
        epic_name = epic.get('name', '')
        for sub_epic in epic.get('sub_epics', []):
            sub_epic_name = sub_epic.get('name', '')
            
            # Merge stories in story_groups
            for story_group in sub_epic.get('story_groups', []):
                for story in story_group.get('stories', []):
                    story_name = story.get('name', '')
                    key = f"{epic_name}|{sub_epic_name}|{story_name}"
                    
                    # If we have a match, update story with extracted data (users, connector, etc.)
                    # but preserve acceptance_criteria from original
                    if key in extracted_full_story_map:
                        ext_story = extracted_full_story_map[key]
                        # Update with extracted data (users, connector, sequential_order, etc.)
                        if 'users' in ext_story:
                            story['users'] = ext_story['users']
                        if 'connector' in ext_story:
                            story['connector'] = ext_story['connector']
                        if 'sequential_order' in ext_story:
                            story['sequential_order'] = ext_story['sequential_order']
                        if 'story_type' in ext_story:
                            story['story_type'] = ext_story['story_type']
                        # Preserve acceptance_criteria from original (don't overwrite)
                        # The original AC is already in the story since we started with original
    
    # Merge increments (if present)
    # Increments use direct stories arrays (no story_groups)
    def merge_sub_epic_stories(sub_epic, epic_name, sub_epic_name):
        """Recursively merge stories in sub_epic (handles both story_groups and direct stories)"""
        # Handle story_groups format (epics section)
        for story_group in sub_epic.get('story_groups', []):
            for story in story_group.get('stories', []):
                story_name = story.get('name', '')
                key = f"{epic_name}|{sub_epic_name}|{story_name}"
                
                if key in extracted_full_story_map:
                    ext_story = extracted_full_story_map[key]
                    if 'users' in ext_story:
                        story['users'] = ext_story['users']
                    if 'connector' in ext_story:
                        story['connector'] = ext_story['connector']
                    if 'sequential_order' in ext_story:
                        story['sequential_order'] = ext_story['sequential_order']
                    if 'story_type' in ext_story:
                        story['story_type'] = ext_story['story_type']
        
        # Handle direct stories array format (increments section)
        for story in sub_epic.get('stories', []):
            story_name = story.get('name', '')
            key = f"{epic_name}|{sub_epic_name}|{story_name}"
            
            if key in extracted_full_story_map:
                ext_story = extracted_full_story_map[key]
                if 'users' in ext_story:
                    story['users'] = ext_story['users']
                if 'connector' in ext_story:
                    story['connector'] = ext_story['connector']
                if 'sequential_order' in ext_story:
                    story['sequential_order'] = ext_story['sequential_order']
                if 'story_type' in ext_story:
                    story['story_type'] = ext_story['story_type']
        
        # Recursively handle nested sub_epics
        for nested_sub_epic in sub_epic.get('sub_epics', []):
            merge_sub_epic_stories(nested_sub_epic, epic_name, nested_sub_epic.get('name', ''))
    
    for increment in merged_data.get('increments', []):
        for epic in increment.get('epics', []):
            epic_name = epic.get('name', '')
            for sub_epic in epic.get('sub_epics', []):
                sub_epic_name = sub_epic.get('name', '')
                merge_sub_epic_stories(sub_epic, epic_name, sub_epic_name)
    
    # Merge increments: add new increments from extracted_data that don't exist in merged_data
    if 'increments' not in merged_data:
        merged_data['increments'] = []
    
    if 'increments' in extracted_data:
        # Create a map of existing increment names for quick lookup
        existing_increment_names = {inc.get('name') for inc in merged_data['increments']}
        
        # Add increments from extracted_data that don't already exist
        for extracted_increment in extracted_data['increments']:
            increment_name = extracted_increment.get('name')
            if increment_name and increment_name not in existing_increment_names:
                merged_data['increments'].append(extracted_increment)
                existing_increment_names.add(increment_name)
    
    # Write merged result
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)
    
    return merged_data


def display_merge_report(report: Dict[str, Any]) -> None:
    """Display merge report in a human-readable format."""
    print("\n" + "="*80)
    print("STORY GRAPH MERGE REPORT")
    print("="*80)
    print(f"Generated: {report['timestamp']}")
    print(f"Extracted: {report['extracted_file']}")
    print(f"Original: {report['original_file']}")
    print("\n" + "-"*80)
    print("SUMMARY")
    print("-"*80)
    summary = report['summary']
    print(f"Total Extracted Stories: {summary['total_extracted_stories']}")
    print(f"Total Original Stories: {summary['total_original_stories']}")
    print(f"Exact Matches: {summary['exact_matches']}")
    print(f"Fuzzy Matches: {summary['fuzzy_matches']}")
    print(f"New Stories (in extracted): {summary['new_stories']}")
    print(f"Removed Stories (in original only): {summary['removed_stories']}")
    
    if report['fuzzy_matches']:
        print("\n" + "-"*80)
        print("FUZZY MATCHES (Require Review)")
        print("-"*80)
        for match in report['fuzzy_matches']:
            print(f"\nExtracted: {match['extracted']['name']}")
            sub_epic_name = match['extracted'].get('sub_epic_name', '')
            print(f"  Epic: {match['extracted']['epic_name']} | Sub-Epic: {sub_epic_name}")
            print(f"Original: {match['original']['name']}")
            orig_sub_epic_name = match['original'].get('sub_epic_name', '')
            print(f"  Epic: {match['original']['epic_name']} | Sub-Epic: {orig_sub_epic_name}")
            print(f"Confidence: {match['confidence']:.2%}")
            print(f"Has Steps: {'Yes' if match['original'].get('Steps') else 'No'}")
            print(f"Has Acceptance Criteria: {'Yes' if match['original'].get('acceptance_criteria') else 'No'}")
    
    if report['new_stories']:
        print("\n" + "-"*80)
        print("NEW STORIES (No match in original)")
        print("-"*80)
        for story in report['new_stories'][:10]:  # Show first 10
            sub_epic_name = story.get('sub_epic_name', '')
            print(f"  - {story['name']} ({story['epic_name']} > {sub_epic_name})")
        if len(report['new_stories']) > 10:
            print(f"  ... and {len(report['new_stories']) - 10} more")
    
    if report['removed_stories']:
        print("\n" + "-"*80)
        print("REMOVED STORIES (In original but not in extracted)")
        print("-"*80)
        for story in report['removed_stories'][:10]:  # Show first 10
            sub_epic_name = story.get('sub_epic_name', '')
            print(f"  - {story['name']} ({story['epic_name']} > {sub_epic_name})")
        if len(report['removed_stories']) > 10:
            print(f"  ... and {len(report['removed_stories']) - 10} more")
    
    # Display large deletions if present
    if 'large_deletions' in report:
        _display_large_deletions(report['large_deletions'])
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("1. Review fuzzy matches above")
    print("2. Confirm which matches are correct")
    print("3. Run merge command to apply changes")
    print("="*80 + "\n")


def is_exploration_mode(drawio_path: Path) -> bool:
    """
    Detect if DrawIO file is in exploration mode (has acceptance criteria boxes).
    
    Args:
        drawio_path: Path to DrawIO file
        
    Returns:
        True if exploration mode (has AC boxes), False otherwise
    """
    try:
        tree = ET.parse(drawio_path)
        root = tree.getroot()
        cells = root.findall('.//mxCell')
        
        for cell in cells:
            cell_id = cell.get('id', '')
            # Check for AC boxes (IDs starting with 'ac_')
            if cell_id.startswith('ac_'):
                return True
        
        return False
    except Exception:
        return False


def generate_extract_report(data: Dict[str, Any], output_path: Optional[Path] = None) -> str:
    """
    Generate a plain English report of what was extracted from DrawIO.
    
    Args:
        data: The extracted story graph data
        output_path: Optional path to write the report to
        
    Returns:
        Plain English report as a string
    """
    lines = []
    lines.append("=" * 80)
    lines.append("STORY GRAPH EXTRACTION REPORT")
    lines.append("=" * 80)
    lines.append("")
    lines.append("This report shows what was extracted from the DrawIO file.")
    lines.append("")
    
    epics = data.get('epics', [])
    total_features = sum(len(epic.get('sub_epics', [])) for epic in epics)
    total_stories = 0
    
    for epic in epics:
        for sub_epic in epic.get('sub_epics', []):
            for story_group in sub_epic.get('story_groups', []):
                total_stories += len(story_group.get('stories', []))
    
    lines.append("SUMMARY")
    lines.append(f"  Epics: {len(epics)}")
    lines.append(f"  Sub-Epics: {total_features}")
    lines.append(f"  Stories: {total_stories}")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")
    
    for epic_idx, epic in enumerate(epics, 1):
        epic_name = epic.get('name', 'Unnamed Epic')
        features = epic.get('sub_epics', [])
        
        lines.append(f"EPIC {epic_idx}: {epic_name}")
        lines.append("-" * 80)
        
        if not features:
            lines.append("  No sub-epics found in this epic.")
            lines.append("")
            continue
        
        for sub_epic_idx, sub_epic in enumerate(features, 1):
            sub_epic_name = sub_epic.get('name', 'Unnamed Sub-Epic')
            story_groups = sub_epic.get('story_groups', [])
            
            lines.append(f"  Sub-Epic {sub_epic_idx}: {sub_epic_name}")
            
            if not story_groups:
                lines.append("    No stories found in this sub-epic.")
                lines.append("")
                continue
            
            story_count = 0
            for story_group in story_groups:
                stories = story_group.get('stories', [])
                story_count += len(stories)
                
                for story in stories:
                    story_name = story.get('name', 'Unnamed Story')
                    users = story.get('users', [])
                    user_text = f" (for {', '.join(users)})" if users else ""
                    lines.append(f"    - {story_name}{user_text}")
            
            lines.append(f"    Total stories in this feature: {story_count}")
            lines.append("")
        
        lines.append("")
    
    report_text = "\n".join(lines)
    
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"Extract report saved to: {output_path}")
    
    return report_text


def synchronize_story_graph_from_drawio_outline(
    drawio_path: Path,
    output_path: Optional[Path] = None,
    original_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Synchronize story graph structure from DrawIO outline (shaping behavior).
    No increments - just epics, features, and stories.
    Preserves layout and spacing to maintain visual clarity.
    Detects and flags large deletions (entire epics/features missing).
    
    Args:
        drawio_path: Path to DrawIO story map outline file (story-map-outline.drawio)
        output_path: Optional path to write extracted JSON
        original_path: Optional path to original story graph for merge report and deletion detection
        
    Returns:
        Dictionary with extracted story graph structure (epics only, no increments)
    """
    # Step 1: Get epics and sub_epics
    epics_sub_epics = get_epics_features_and_boundaries(drawio_path)
    epics = epics_sub_epics['epics']
    sub_epics = epics_sub_epics['sub_epics']
    
    # Step 2: Build stories for epics/sub_epics (preserves layout)
    # AC extraction is based on position and shape (wider boxes below stories), works for both regular and exploration mode
    epics_with_stories = build_stories_for_epics_features(drawio_path, epics, sub_epics, return_layout=True)
    
    result = {
        'epics': epics_with_stories['epics']
        # No increments for outline
    }
    
    # DrawIO is the source of truth - only extract what's actually in the DrawIO
    # Do NOT merge in features from original JSON that aren't in DrawIO
    # If a feature was deleted from DrawIO, it should be deleted from the extracted JSON
    
    layout_data = epics_with_stories.get('layout', {})
    
    # Write extracted JSON
    if output_path:
        output_path = Path(output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Write separate layout JSON file
        layout_path = output_path.parent.resolve() / f"{output_path.stem}-layout.json"
        # Ensure parent directory exists and is accessible
        try:
            layout_path.parent.mkdir(parents=True, exist_ok=True)
            # Use a temporary file in a shorter path if the target path is too long
            if len(str(layout_path)) > 260:  # Windows MAX_PATH limit
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8')
                json.dump(layout_data, temp_file, indent=2, ensure_ascii=False)
                temp_file.close()
                import shutil
                shutil.move(temp_file.name, str(layout_path))
            else:
                with open(str(layout_path), 'w', encoding='utf-8') as f:
                    json.dump(layout_data, f, indent=2, ensure_ascii=False)
            print(f"Layout data saved to: {layout_path}")
        except Exception as e:
            print(f"Warning: Could not save layout file to {layout_path}: {e}")
            # Try saving to a shorter path as fallback
            try:
                import tempfile
                fallback_path = Path(tempfile.gettempdir()) / f"{output_path.stem}-layout.json"
                with open(str(fallback_path), 'w', encoding='utf-8') as f:
                    json.dump(layout_data, f, indent=2, ensure_ascii=False)
                print(f"Layout data saved to fallback location: {fallback_path}")
            except Exception as e2:
                print(f"Error: Could not save layout file even to fallback location: {e2}")
        
        # Generate merge report and detect large deletions if original path provided
        if original_path and original_path.exists():
            report_path = output_path.parent / f"{output_path.stem}-merge-report.json"
            report = generate_merge_report(output_path, original_path, report_path)
            
            # Detect large deletions
            with open(original_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
            deletions = _detect_large_deletions(original_data, result)
            report['large_deletions'] = deletions
            
            # Write updated report with deletion info
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            display_merge_report(report)
            print(f"\nMerge report saved to: {report_path}")
        
        # Generate plain English extract report
        if output_path:
            extract_report_path = output_path.parent / f"{output_path.stem}-extract-report.txt"
            extract_report_text = generate_extract_report(result, extract_report_path)
            print(f"\nExtract report saved to: {extract_report_path}")
            print("\n" + extract_report_text)
    
    return result


def synchronize_story_graph_from_drawio_increments(
    drawio_path: Path,
    output_path: Optional[Path] = None,
    original_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Synchronize story graph structure from DrawIO with increments (prioritization behavior).
    Includes both epics/features/stories AND increments.
    
    Args:
        drawio_path: Path to DrawIO story map file (story-map.drawio)
        output_path: Optional path to write extracted JSON
        original_path: Optional path to original story graph for merge report
        
    Returns:
        Dictionary with extracted story graph structure (epics and increments)
    """
    # Step 1: Get increments
    increments = get_increments_and_boundaries(drawio_path)
    
    # Step 2: Get epics and sub-epics
    epics_sub_epics = get_epics_features_and_boundaries(drawio_path)
    epics = epics_sub_epics['epics']
    sub_epics = epics_sub_epics['sub_epics']
    
    # Step 3: Build stories for epics/sub_epics
    epics_with_stories = build_stories_for_epics_features(drawio_path, epics, sub_epics)
    
    # Step 4: Build stories for increments (use already-extracted epics with story_groups)
    increments_with_stories = build_increments_from_extracted_epics(drawio_path, increments, epics_with_stories['epics'])
    
    result = {
        'epics': epics_with_stories['epics'],
        'increments': increments_with_stories
    }
    
    # Write extracted JSON
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        # Generate merge report if original path provided
        if original_path and original_path.exists():
            report_path = output_path.parent / f"{output_path.stem}-merge-report.json"
            report = generate_merge_report(output_path, original_path, report_path)
            display_merge_report(report)
            print(f"\nMerge report saved to: {report_path}")
    
    return result


# Keep the original function for backward compatibility
# It now delegates to the increments version
def synchronize_story_map_from_drawio(
    drawio_path: Path,
    output_path: Optional[Path] = None,
    original_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Synchronize story graph structure from DrawIO file (backward compatibility).
    Delegates to synchronize_story_graph_from_drawio_increments.
    """
    return synchronize_story_graph_from_drawio_increments(drawio_path, output_path, original_path)


if __name__ == "__main__":
    """Command-line interface for synchronizing story maps from DrawIO."""
    import argparse
    import tempfile
    
    parser = argparse.ArgumentParser(description='Synchronize story graph from DrawIO story map')
    parser.add_argument('drawio_path', type=Path, nargs='?', help='Path to DrawIO story map file')
    parser.add_argument('--output', type=Path, help='Output path for extracted JSON')
    parser.add_argument('--original', type=Path, help='Path to original story graph JSON for merge report')
    parser.add_argument('--merge', action='store_true', help='Merge extracted with original based on report')
    parser.add_argument('--report', type=Path, help='Path to merge report JSON (required for --merge)')
    parser.add_argument('--merged-output', type=Path, help='Output path for merged JSON (default: overwrites original)')
    parser.add_argument('--outline', action='store_true', help='Use outline mode (no increments, for shaping)')
    
    args = parser.parse_args()
    
    try:
        # Handle merge operation
        if args.merge:
            if not args.report:
                print("Error: --report is required when using --merge", file=sys.stderr)
                sys.exit(1)
            
            if not args.original:
                print("Error: --original is required when using --merge", file=sys.stderr)
                sys.exit(1)
            
            # Determine output path
            if args.merged_output:
                output_path = args.merged_output
            else:
                output_path = args.original  # Overwrite original by default
            
            # Find extracted file from report
            with open(args.report, 'r', encoding='utf-8') as f:
                report = json.load(f)
            extracted_path = Path(report['extracted_file'])
            
            if not extracted_path.exists():
                print(f"Error: Extracted file not found: {extracted_path}", file=sys.stderr)
                sys.exit(1)
            
            print(f"Merging story graphs...")
            print(f"  Extracted: {extracted_path}")
            print(f"  Original: {args.original}")
            print(f"  Report: {args.report}")
            print(f"  Output: {output_path}")
            
            merged = merge_story_graphs(extracted_path, args.original, args.report, output_path)
            
            print(f"\nSuccessfully merged story graphs!")
            print(f"  Epics: {len(merged.get('epics', []))}")
            if 'increments' in merged:
                print(f"  Increments: {len(merged.get('increments', []))}")
            print(f"  Merged output written to: {output_path}")
            sys.exit(0)
        
        # Handle extraction operation
        if not args.drawio_path:
            parser.print_help()
            sys.exit(1)
        
        # If no output specified, create temp file
        if not args.output:
            temp_dir = Path(tempfile.gettempdir())
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            args.output = temp_dir / f"story-graph-extracted-{timestamp}.json"
            print(f"Using temporary file: {args.output}")
        
        # Choose function based on mode or file name
        if args.outline or 'outline' in str(args.drawio_path).lower():
            result = synchronize_story_graph_from_drawio_outline(args.drawio_path, args.output, args.original)
            print(f"\nSuccessfully synchronized story map outline from DrawIO")
        else:
            result = synchronize_story_graph_from_drawio_increments(args.drawio_path, args.output, args.original)
            print(f"\nSuccessfully synchronized story map from DrawIO")
        
        print(f"Epics: {len(result['epics'])}")
        if 'increments' in result:
            print(f"Increments: {len(result['increments'])}")
        print(f"Output written to: {args.output}")
        
        if args.original:
            report_path = args.output.parent / f"{args.output.stem}-merge-report.json"
            print("\nMerge report generated. Review the report above before proceeding with merge.")
            print(f"\nTo merge, run:")
            print(f"  python {Path(__file__).name} --merge --report {report_path} --original {args.original} --merged-output {args.original}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

