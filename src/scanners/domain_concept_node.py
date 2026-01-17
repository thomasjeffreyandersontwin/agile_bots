
from typing import List, Dict, Any, Optional

class DomainConceptNode:
    
    def __init__(
        self,
        data: Dict[str, Any],
        epic_idx: int,
        sub_epic_path: Optional[List[int]] = None,
        concept_idx: int = 0
    ):
        self.data = data
        self.epic_idx = epic_idx
        self.sub_epic_path = sub_epic_path or []
        self.concept_idx = concept_idx
    
    @property
    def name(self) -> str:
        return self.data.get('name', '')
    
    @property
    def responsibilities(self) -> List[Dict[str, Any]]:
        return self.data.get('responsibilities', [])
    
    def map_location(self, field: str = 'name') -> str:
        path_parts = [f"epics[{self.epic_idx}]"]
        
        if self.sub_epic_path:
            for idx in self.sub_epic_path:
                path_parts.append(f"sub_epics[{idx}]")
        
        path_parts.append(f"domain_concepts[{self.concept_idx}]")
        if field != 'name':
            path_parts.append(field)
        
        return ".".join(path_parts)

