"""
BDD Tests for Epic

Tests for Epic domain component following Mamba BDD patterns.
"""

from mamba import description, context, it, before
from expects import expect, equal, be_none, be_true, be_false

from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_epic import Epic
from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_feature import Feature
from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_story import Story


def create_epic(name='Test Epic', sequential_order=None):
    """Helper factory for creating epics."""
    return Epic(name=name, sequential_order=sequential_order)


def create_feature(name='Test Feature', sequential_order=None):
    """Helper factory for creating features."""
    return Feature(name=name, sequential_order=sequential_order)


def create_story(name='Test Story', sequential_order=None):
    """Helper factory for creating stories."""
    return Story(name=name, sequential_order=sequential_order)


with description('an Epic'):
    with context('that is newly created'):
        with before.each:
            self.epic = create_epic(name='Create Character')
        
        with it('should have the specified name'):
            expect(self.epic.name).to(equal('Create Character'))
        
        with it('should have no features'):
            expect(self.epic.features).to(equal([]))
        
        with it('should have no stories'):
            expect(self.epic.stories).to(equal([]))
    
    with context('that has features'):
        with before.each:
            self.epic = create_epic(name='Test Epic')
            self.feature1 = create_feature(name='Feature 1')
            self.feature2 = create_feature(name='Feature 2')
        
        with it('should add feature when calling add_feature'):
            self.epic.add_feature(self.feature1)
            expect(len(self.epic.features)).to(equal(1))
            expect(self.epic.features[0].name).to(equal('Feature 1'))
        
        with it('should set feature parent when adding'):
            self.epic.add_feature(self.feature1)
            expect(self.feature1.parent).to(equal(self.epic))
        
        with it('should have multiple features'):
            self.epic.add_feature(self.feature1)
            self.epic.add_feature(self.feature2)
            expect(len(self.epic.features)).to(equal(2))
        
        with it('should remove feature when calling remove_feature'):
            self.epic.add_feature(self.feature1)
            self.epic.remove_feature(self.feature1)
            expect(len(self.epic.features)).to(equal(0))
    
    with context('that has stories'):
        with before.each:
            self.epic = create_epic(name='Test Epic')
            self.story1 = create_story(name='Story 1')
            self.story2 = create_story(name='Story 2')
        
        with it('should contain stories added directly'):
            self.story1.parent = self.epic
            expect(len(self.epic.stories)).to(equal(1))
            expect(self.epic.stories[0].name).to(equal('Story 1'))
        
        with it('should have multiple stories'):
            self.story1.parent = self.epic
            self.story2.parent = self.epic
            expect(len(self.epic.stories)).to(equal(2))
    
    with context('that synchronizes'):
        with before.each:
            self.epic = create_epic(name='Test Epic', sequential_order=1.0)
            self.feature = create_feature(name='Test Feature')
            self.epic.add_feature(self.feature)
        
        with it('should return synchronized data structure'):
            result = self.epic.synchronize()
            expect(result['name']).to(equal('Test Epic'))
            expect(result['sequential_order']).to(equal(1.0))
            expect(len(result['features'])).to(equal(1))
        
        with it('should include nested features in synchronized data'):
            result = self.epic.synchronize()
            expect(result['features'][0]['name']).to(equal('Test Feature'))
    
    with context('that generates synchronization report'):
        with before.each:
            self.epic = create_epic(name='Test Epic')
            self.feature = create_feature(name='Test Feature')
            self.story = create_story(name='Test Story')
            self.epic.add_feature(self.feature)
            self.story.parent = self.epic
        
        with it('should include epic name in report'):
            report = self.epic.synchronize_report()
            expect(report['epic']).to(equal('Test Epic'))
        
        with it('should include counts in report'):
            report = self.epic.synchronize_report()
            expect(report['features_count']).to(equal(1))
            expect(report['stories_count']).to(equal(1))
            expect(report['total_children']).to(equal(2))
    
    with context('that compares with another epic'):
        with before.each:
            self.epic1 = create_epic(name='Same Epic', sequential_order=1.0)
            self.epic2 = create_epic(name='Same Epic', sequential_order=1.0)
            self.epic3 = create_epic(name='Different Epic')
        
        with it('should match when names are same'):
            result = self.epic1.compare(self.epic2)
            expect(result['match']).to(be_true)
            expect(result['name_match']).to(be_true)
        
        with it('should not match when names differ'):
            result = self.epic1.compare(self.epic3)
            expect(result['match']).to(be_false)
        
        with it('should compare sequential orders'):
            result = self.epic1.compare(self.epic2)
            expect(result['sequential_order_match']).to(be_true)
    
    with context('that renders to JSON'):
        with before.each:
            self.epic = create_epic(name='Test Epic', sequential_order=1.0)
            self.feature = create_feature(name='Test Feature')
            self.epic.add_feature(self.feature)
        
        with it('should include epic name in rendered JSON'):
            result = self.epic.render()
            expect(result['name']).to(equal('Test Epic'))
        
        with it('should include sequential order in rendered JSON'):
            result = self.epic.render()
            expect(result['sequential_order']).to(equal(1.0))
        
        with it('should include features in rendered JSON'):
            result = self.epic.render()
            expect(len(result['features'])).to(equal(1))
        
        with it('should include empty users list'):
            result = self.epic.render()
            expect(result['users']).to(equal([]))
    
    with context('that converts to dictionary'):
        with before.each:
            self.epic = create_epic(name='Test Epic')
            self.feature = create_feature(name='Test Feature')
            self.epic.add_feature(self.feature)
        
        with it('should include type in dictionary'):
            result = self.epic.to_dict()
            expect(result['type']).to(equal('epic'))
        
        with it('should include features in dictionary'):
            result = self.epic.to_dict()
            expect(len(result['features'])).to(equal(1))
            expect(result['features'][0]['type']).to(equal('feature'))

