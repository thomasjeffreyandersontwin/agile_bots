
from agile_bots.src.cli.adapters import JSONAdapter
from agile_bots.src.instructions.instructions import Instructions

class JSONInstructions(JSONAdapter):
    
    def __init__(self, instructions: Instructions):
        self.instructions = instructions
    
    def serialize(self) -> str:
        import json
        return json.dumps(self.to_dict(), indent=2)
    
    def to_dict(self) -> dict:
        return self.instructions.to_dict()
