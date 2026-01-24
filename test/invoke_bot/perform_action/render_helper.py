"""
Render Test Helper
Handles render action, templates, output generation + render-specific instruction assertions
"""
from helpers.base_helper import BaseHelper


class RenderTestHelper(BaseHelper):
    """Helper for render action and output generation testing"""
    
    def assert_render_output_instructions(self, instructions):
        """Assert RenderOutputAction injected all required fields with actual production data.
        
        Args:
            instructions: Instructions object from RenderOutputAction (shape behavior)
        """
        # Check base instructions exist
        base_instructions = instructions.get('base_instructions', [])
        assert base_instructions, "base_instructions should be present"
        assert len(base_instructions) > 0, "base_instructions should not be empty"
        
        # Check render_instructions from production shape behavior
        render_instructions = instructions.get('render_instructions')
        assert render_instructions is not None, "render_instructions should be set"
        assert isinstance(render_instructions, dict), "render_instructions should be a dict"
        assert render_instructions.get('behaviorName') == 'shape', "render_instructions should have behaviorName='shape'"
        assert 'instructions' in render_instructions, "render_instructions should have 'instructions' field"
        
        # Check render_configs contains actual production configs
        render_configs = instructions.get('render_configs', [])
        assert render_configs is not None, "render_configs should be set"
        assert len(render_configs) > 0, "render_configs should have at least one config from production shape behavior"
        
        # Verify structure of render configs
        for config in render_configs:
            assert 'name' in config, f"Each render config must have 'name': {config}"
            assert 'type' in config, f"Each render config must have 'type': {config}"
            assert config['type'] in ['synchronizer', 'builder', 'template'], f"Config type must be synchronizer/builder/template: {config['type']}"
            assert 'input' in config, f"Each render config must have 'input': {config}"
            assert 'output' in config, f"Each render config must have 'output': {config}"
        
        # Check executed_specs - synchronizers that ran automatically
        executed_specs = instructions.get('executed_specs', [])
        assert executed_specs is not None, "executed_specs should be set"
        # Synchronizers may or may not execute depending on input file existence - that's OK
        
        # Check template_specs - configs that remain for AI to handle
        template_specs = instructions.get('template_specs', [])
        assert template_specs is not None, "template_specs should be set"
    
    def create_render_directory(self, directory_path, **params):
        """Create render output directory structure.
        
        Args:
            directory_path: Path to directory to create (relative to workspace or absolute)
            **params: Additional parameters (for future expansion)
        
        Returns:
            Path to created directory
        """
        from pathlib import Path
        
        # Handle relative vs absolute paths
        if isinstance(directory_path, str):
            directory_path = Path(directory_path)
        
        if not directory_path.is_absolute():
            directory_path = self.parent.workspace / directory_path
        
        directory_path.mkdir(parents=True, exist_ok=True)
        return directory_path
