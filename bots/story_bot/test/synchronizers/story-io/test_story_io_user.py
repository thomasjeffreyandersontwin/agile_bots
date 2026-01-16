"""
BDD Tests for User

Tests for User domain component following Mamba BDD patterns.
"""

from mamba import description, context, it, before
from expects import expect, equal, be_true, be_false, contain

from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_user import User
from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_story import Story


def create_user(name='Human'):
    """Helper factory for creating users."""
    return User(name=name)


def create_story(name='Test Story'):
    """Helper factory for creating stories."""
    return Story(name=name)


with description('a User'):
    with context('that is newly created'):
        with before.each:
            self.user = create_user(name='Human')
        
        with it('should have the specified name'):
            expect(self.user.name).to(equal('Human'))
        
        with it('should have no stories'):
            expect(self.user.stories).to(equal([]))
        
        with it('should have no sequential order'):
            expect(self.user.sequential_order).to(equal(None))
    
    with context('that has stories'):
        with before.each:
            self.user = create_user(name='Human')
            self.story1 = create_story(name='Story 1')
            self.story2 = create_story(name='Story 2')
        
        with it('should add story when calling add_story'):
            self.user.add_story(self.story1)
            expect(len(self.user.stories)).to(equal(1))
            expect(self.user.stories[0].name).to(equal('Story 1'))
        
        with it('should create bidirectional relationship'):
            self.user.add_story(self.story1)
            expect(self.story1.users).to(contain('Human'))
        
        with it('should have multiple stories'):
            self.user.add_story(self.story1)
            self.user.add_story(self.story2)
            expect(len(self.user.stories)).to(equal(2))
        
        with it('should remove story when calling remove_story'):
            self.user.add_story(self.story1)
            self.user.remove_story(self.story1)
            expect(len(self.user.stories)).to(equal(0))
            expect(self.story1.users).not_to(contain('Human'))
    
    with context('that synchronizes'):
        with before.each:
            self.user = create_user(name='Human')
            self.story = create_story(name='Test Story')
            self.user.add_story(self.story)
        
        with it('should return synchronized data structure'):
            result = self.user.synchronize()
            expect(result['name']).to(equal('Human'))
        
        with it('should include story names in synchronized data'):
            result = self.user.synchronize()
            expect(result['stories']).to(contain('Test Story'))
    
    with context('that generates synchronization report'):
        with before.each:
            self.user = create_user(name='Human')
            self.story = create_story(name='Test Story')
            self.user.add_story(self.story)
        
        with it('should include user name in report'):
            report = self.user.synchronize_report()
            expect(report['user']).to(equal('Human'))
        
        with it('should include story count in report'):
            report = self.user.synchronize_report()
            expect(report['stories_count']).to(equal(1))
    
    with context('that compares with another user'):
        with before.each:
            self.user1 = create_user(name='Human')
            self.user2 = create_user(name='Human')
            self.user3 = create_user(name='Developer')
        
        with it('should match when names are same'):
            result = self.user1.compare(self.user2)
            expect(result['match']).to(be_true)
            expect(result['name_match']).to(be_true)
        
        with it('should not match when names differ'):
            result = self.user1.compare(self.user3)
            expect(result['match']).to(be_false)
    
    with context('that renders to JSON'):
        with before.each:
            self.user = create_user(name='Human')
            self.story = create_story(name='Test Story')
            self.user.add_story(self.story)
        
        with it('should include user name in rendered JSON'):
            result = self.user.render()
            expect(result['name']).to(equal('Human'))
        
        with it('should include story names in rendered JSON'):
            result = self.user.render()
            expect(result['stories']).to(contain('Test Story'))
    
    with context('that converts to dictionary'):
        with before.each:
            self.user = create_user(name='Human')
            self.story = create_story(name='Test Story')
            self.user.add_story(self.story)
        
        with it('should include type in dictionary'):
            result = self.user.to_dict()
            expect(result['type']).to(equal('user'))
        
        with it('should include stories in dictionary'):
            result = self.user.to_dict()
            expect(result['stories']).to(contain('Test Story'))

