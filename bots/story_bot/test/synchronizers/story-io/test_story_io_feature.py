"""
BDD Tests for Feature

Tests for Feature domain component following Mamba BDD patterns.
"""

from mamba import description, context, it, before
from expects import expect, equal, be_none, be_true, be_false

from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_feature import Feature
from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_story import Story
from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_epic import Epic


def create_feature(name='Test Feature', sequential_order=None, story_count=None):
    """Helper factory for creating features."""
    return Feature(name=name, sequential_order=sequential_order, story_count=story_count)


def create_story(name='Test Story'):
    """Helper factory for creating stories."""
    return Story(name=name)


def create_epic(name='Test Epic'):
    """Helper factory for creating epics."""
    return Epic(name=name)


with description('a Feature'):
    with context('that is newly created'):
        with before.each:
            self.feature = create_feature(name='Establish Identity')
        
        with it('should have the specified name'):
            expect(self.feature.name).to(equal('Establish Identity'))
        
        with it('should have no stories'):
            expect(self.feature.stories).to(equal([]))
        
        with it('should have no story count when not specified'):
            expect(self.feature.story_count).to(be_none)
    
    with context('that has story count'):
        with before.each:
            self.feature = create_feature(name='Test Feature', story_count=5)
        
        with it('should return story count'):
            expect(self.feature.story_count).to(equal(5))
        
        with it('should indicate estimated stories'):
            expect(self.feature.story_count).not_to(be_none)
    
    with context('that has stories'):
        with before.each:
            self.feature = create_feature(name='Test Feature')
            self.story1 = create_story(name='Story 1')
            self.story2 = create_story(name='Story 2')
        
        with it('should contain stories added as children'):
            self.story1.parent = self.feature
            expect(len(self.feature.stories)).to(equal(1))
            expect(self.feature.stories[0].name).to(equal('Story 1'))
        
        with it('should have multiple stories'):
            self.story1.parent = self.feature
            self.story2.parent = self.feature
            expect(len(self.feature.stories)).to(equal(2))
    
    with context('that synchronizes'):
        with before.each:
            self.feature = create_feature(name='Test Feature', sequential_order=1.0, story_count=3)
            self.story = create_story(name='Test Story')
            self.story.parent = self.feature
        
        with it('should return synchronized data structure'):
            result = self.feature.synchronize()
            expect(result['name']).to(equal('Test Feature'))
            expect(result['sequential_order']).to(equal(1.0))
        
        with it('should include story count in synchronized data'):
            result = self.feature.synchronize()
            expect(result['story_count']).to(equal(3))
        
        with it('should include nested stories in synchronized data'):
            result = self.feature.synchronize()
            expect(len(result['stories'])).to(equal(1))
    
    with context('that generates synchronization report'):
        with before.each:
            self.feature = create_feature(name='Test Feature', story_count=5)
            self.story = create_story(name='Test Story')
            self.story.parent = self.feature
        
        with it('should include feature name in report'):
            report = self.feature.synchronize_report()
            expect(report['feature']).to(equal('Test Feature'))
        
        with it('should include story count in report'):
            report = self.feature.synchronize_report()
            expect(report['stories_count']).to(equal(1))
            expect(report['estimated_stories']).to(equal(5))
    
    with context('that compares with another feature'):
        with before.each:
            self.feature1 = create_feature(name='Same Feature', sequential_order=1.0)
            self.feature2 = create_feature(name='Same Feature', sequential_order=1.0)
            self.feature3 = create_feature(name='Different Feature')
        
        with it('should match when names are same'):
            result = self.feature1.compare(self.feature2)
            expect(result['match']).to(be_true)
            expect(result['name_match']).to(be_true)
        
        with it('should not match when names differ'):
            result = self.feature1.compare(self.feature3)
            expect(result['match']).to(be_false)
        
        with it('should compare sequential orders'):
            result = self.feature1.compare(self.feature2)
            expect(result['sequential_order_match']).to(be_true)
    
    with context('that renders to JSON'):
        with before.each:
            self.feature = create_feature(name='Test Feature', sequential_order=1.0, story_count=3)
            self.story = create_story(name='Test Story')
            self.story.parent = self.feature
        
        with it('should include feature name in rendered JSON'):
            result = self.feature.render()
            expect(result['name']).to(equal('Test Feature'))
        
        with it('should include story count in rendered JSON'):
            result = self.feature.render()
            expect(result['story_count']).to(equal(3))
        
        with it('should include stories in rendered JSON'):
            result = self.feature.render()
            expect(len(result['stories'])).to(equal(1))
        
        with it('should include empty users list'):
            result = self.feature.render()
            expect(result['users']).to(equal([]))
    
    with context('that converts to dictionary'):
        with before.each:
            self.feature = create_feature(name='Test Feature', story_count=5)
            self.story = create_story(name='Test Story')
            self.story.parent = self.feature
        
        with it('should include type in dictionary'):
            result = self.feature.to_dict()
            expect(result['type']).to(equal('feature'))
        
        with it('should include story count in dictionary when present'):
            result = self.feature.to_dict()
            expect(result['story_count']).to(equal(5))
        
        with it('should include stories in dictionary'):
            result = self.feature.to_dict()
            expect(len(result['stories'])).to(equal(1))

