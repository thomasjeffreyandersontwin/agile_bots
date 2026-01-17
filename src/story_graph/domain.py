from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Collaborator:
    name: str

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_str(cls, name: str) -> 'Collaborator':
        return cls(name=name)

@dataclass
class Responsibility:
    name: str
    collaborators: List[Collaborator]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Responsibility':
        return cls(name=data.get('name', ''), collaborators=[Collaborator.from_str(c) for c in data.get('collaborators', [])])

    def to_dict(self) -> Dict[str, Any]:
        return {'name': self.name, 'collaborators': [c.name for c in self.collaborators]}

@dataclass
class DomainConcept:
    name: str
    responsibilities: List[Responsibility]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainConcept':
        return cls(name=data.get('name', ''), responsibilities=[Responsibility.from_dict(r) for r in data.get('responsibilities', [])])

    def to_dict(self) -> Dict[str, Any]:
        return {'name': self.name, 'responsibilities': [r.to_dict() for r in self.responsibilities]}

@dataclass
class StoryUser:
    name: str

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_str(cls, user_name: str) -> 'StoryUser':
        return cls(name=user_name)

    @classmethod
    def from_list(cls, user_names: List[str]) -> List['StoryUser']:
        return [cls.from_str(name) for name in user_names]

    def to_str(self) -> str:
        return str(self)