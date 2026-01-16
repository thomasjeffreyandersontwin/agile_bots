"""
BDD Tests for Increment

Tests for Increment domain component following Mamba BDD patterns.
"""

from mamba import description, context, it, before
from expects import expect, equal, be_true, be_false

from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_increment import Increment
from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_epic import Epic
from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_feature import Feature
from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_story import Story
from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_position import Position, Boundary


def create_increment(name='Increment 1', priority=1):
    """Helper factory for creating increments."""
    return Increment(name=name, priority=priority)


def create_epic(name='Test Epic'):
    """Helper factory for creating epics."""
    return Epic(name=name)


def create_story(name='Test Story', users=None):
    """Helper factory for creating stories."""
    return Story(name=name, users=users)


with description('an Increment'):
    with context('that is newly created'):
        with before.each:
            self.increment = create_increment(name='First Release', priority=1)
        
        with it('should have the specified name'):
            expect(self.increment.name).to(equal('First Release'))
        
        with it('should have the specified priority'):
            expect(self.increment.priority).to(equal(1))
        
        with it('should have no epics'):
            expect(self.increment.epics).to(equal([]))
        
        with it('should have no stories'):
            expect(self.increment.stories).to(equal([]))
    
    with context('that has epics'):
        with before.each:
            self.increment = create_increment(name='Test Increment')
            self.epic = create_epic(name='Test Epic')
        
        with it('should contain epics added as children'):
            self.epic.parent = self.increment
            expect(len(self.increment.epics)).to(equal(1))
            expect(self.increment.epics[0].name).to(equal('Test Epic'))
    
    with context('that has stories'):
        with before.each:
            self.increment = create_increment(name='Test Increment')
            self.increment.boundary = Boundary(x=0, y=450, width=500, height=200)
            self.story = create_story(name='Test Story')
        
        with it('should add story when calling add_story'):
            self.increment.add_story(self.story)
            expect(len(self.increment.stories)).to(equal(1))
            expect(self.increment.stories[0].name).to(equal('Test Story'))
        
        with it('should set story parent when adding'):
            self.increment.add_story(self.story)
            expect(self.story.parent).to(equal(self.increment))
    
    with context('that synchronizes'):
        with before.each:
            self.increment = create_increment(name='Test Increment', priority=1)
            self.epic = create_epic(name='Test Epic')
            self.epic.parent = self.increment
        
        with it('should return synchronized data structure'):
            result = self.increment.synchronize()
            expect(result['name']).to(equal('Test Increment'))
            expect(result['priority']).to(equal(1))
        
        with it('should include epics in synchronized data'):
            result = self.increment.synchronize()
            expect(len(result['epics'])).to(equal(1))
    
    with context('that generates synchronization report'):
        with before.each:
            self.increment = create_increment(name='Test Increment', priority=1)
            self.epic = create_epic(name='Test Epic')
            self.story = create_story(name='Test Story')
            self.epic.parent = self.increment
            self.story.parent = self.increment
        
        with it('should include increment name in report'):
            report = self.increment.synchronize_report()
            expect(report['increment']).to(equal('Test Increment'))
        
        with it('should include priority in report'):
            report = self.increment.synchronize_report()
            expect(report['priority']).to(equal(1))
        
        with it('should include counts in report'):
            report = self.increment.synchronize_report()
            expect(report['epics_count']).to(equal(1))
            expect(report['stories_count']).to(equal(1))
    
    with context('that compares with another increment'):
        with before.each:
            self.increment1 = create_increment(name='Same Increment', priority=1)
            self.increment2 = create_increment(name='Same Increment', priority=1)
            self.increment3 = create_increment(name='Different Increment', priority=2)
        
        with it('should match when name and priority are same'):
            result = self.increment1.compare(self.increment2)
            expect(result['match']).to(be_true)
            expect(result['name_match']).to(be_true)
            expect(result['priority_match']).to(be_true)
        
        with it('should not match when priority differs'):
            result = self.increment1.compare(self.increment3)
            expect(result['match']).to(be_false)
    
    with context('that renders to JSON'):
        with before.each:
            self.increment = create_increment(name='Test Increment', priority=1)
            self.epic = create_epic(name='Test Epic')
            self.epic.parent = self.increment
        
        with it('should include increment name in rendered JSON'):
            result = self.increment.render()
            expect(result['name']).to(equal('Test Increment'))
        
        with it('should include priority in rendered JSON'):
            result = self.increment.render()
            expect(result['priority']).to(equal(1))
        
        with it('should include epics in rendered JSON'):
            result = self.increment.render()
            expect(len(result['epics'])).to(equal(1))
    
    with context('that converts to dictionary'):
        with before.each:
            self.increment = create_increment(name='Test Increment', priority=1)
            self.epic = create_epic(name='Test Epic')
            self.epic.parent = self.increment
        
        with it('should include type in dictionary'):
            result = self.increment.to_dict()
            expect(result['type']).to(equal('increment'))
        
        with it('should include priority in dictionary'):
            result = self.increment.to_dict()
            expect(result['priority']).to(equal(1))
        
        with it('should include epics in dictionary'):
            result = self.increment.to_dict()
            expect(len(result['epics'])).to(equal(1))

