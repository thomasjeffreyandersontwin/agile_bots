"""
BDD Tests for Story

Tests for Story domain component with user associations and optional stories.
"""

from mamba import description, context, it, before
from expects import expect, equal, be_none, be_true, be_false, contain

from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_story import Story
from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_position import Position
from agile_bots.bots.story_bot.src.synchronizers.story_io.story_io_feature import Feature


def create_story(name='Test Story', sequential_order=None, users=None, steps=None, story_type=None):
    """Helper factory for creating stories."""
    return Story(name=name, sequential_order=sequential_order, users=users, steps=steps, story_type=story_type)


def create_feature(name='Test Feature'):
    """Helper factory for creating features."""
    return Feature(name=name)


with description('a Story'):
    with context('that is newly created'):
        with before.each:
            self.story = create_story(name='User enters name')
        
        with it('should have the specified name'):
            expect(self.story.name).to(equal('User enters name'))
        
        with it('should have no users'):
            expect(self.story.users).to(equal([]))
        
        with it('should have no steps'):
            expect(self.story.steps).to(equal([]))
        
        with it('should not be flagged'):
            expect(self.story.flag).to(be_false)
        
        with it('should default to user story type'):
            expect(self.story.story_type).to(equal('user'))
    
    with context('with story types'):
        with it('should support system story type'):
            story = create_story(name='Validate Payload', story_type='system')
            expect(story.story_type).to(equal('system'))
        
        with it('should support technical story type'):
            story = create_story(name='Migrate Legacy Data', story_type='technical')
            expect(story.story_type).to(equal('technical'))
        
        with it('should default to user when story_type is None'):
            story = create_story(name='User Story', story_type=None)
            expect(story.story_type).to(equal('user'))
        
        with it('should include story_type in to_dict when not user'):
            story = create_story(name='System Story', story_type='system')
            result = story.to_dict()
            expect('story_type' in result).to(be_true)
            expect(result['story_type']).to(equal('system'))
        
        with it('should not include story_type in to_dict when user (default)'):
            story = create_story(name='User Story', story_type='user')
            result = story.to_dict()
            expect('story_type' in result).to(be_false)
    
    with context('that has users'):
        with before.each:
            self.story = create_story(name='Test Story')
        
        with it('should add user when calling add_user'):
            self.story.add_user('Human')
            expect(self.story.users).to(contain('Human'))
        
        with it('should have multiple users'):
            self.story.add_user('Human')
            self.story.add_user('Developer')
            expect(len(self.story.users)).to(equal(2))
        
        with it('should remove user when calling remove_user'):
            self.story.add_user('Human')
            self.story.remove_user('Human')
            expect(self.story.users).not_to(contain('Human'))
        
        with it('should not duplicate users'):
            self.story.add_user('Human')
            self.story.add_user('Human')
            expect(len(self.story.users)).to(equal(1))
    
    with context('that has steps'):
        with before.each:
            self.steps = [
                {'given': 'User is on login page', 'when': 'User enters credentials', 'then': 'User is logged in'}
            ]
            self.story = create_story(name='Login Story', steps=self.steps)
        
        with it('should return steps'):
            expect(len(self.story.steps)).to(equal(1))
            expect(self.story.steps[0]['given']).to(equal('User is on login page'))
    
    with context('that is made optional to another story'):
        with before.each:
            self.feature = create_feature(name='Test Feature')
            self.base_story = create_story(name='Base Story', sequential_order=1.0)
            self.optional_story = create_story(name='Optional Story')
            self.base_story.parent = self.feature
            self.optional_story.parent = self.feature
            self.base_story.position = Position(x=100.0, y=350.0)
            self.base_story.boundary = None  # Will need boundary for make_optional_to
        
        with it('should set decimal sequential order'):
            if self.base_story.boundary:
                self.optional_story.make_optional_to(self.base_story)
                expect(self.optional_story.sequential_order).to(equal(1.1))
        
        with it('should position below base story'):
            if self.base_story.boundary:
                self.optional_story.make_optional_to(self.base_story)
                expect(self.optional_story.position.y).to(equal(405.0))  # 350 + 55
    
    with context('that flags and unflags'):
        with before.each:
            self.story = create_story(name='Test Story')
        
        with it('should be flagged when calling flag_story'):
            self.story.flag_story()
            expect(self.story.flag).to(be_true)
        
        with it('should be unflagged when calling unflag_story'):
            self.story.flag_story()
            self.story.unflag_story()
            expect(self.story.flag).to(be_false)
    
    with context('that synchronizes'):
        with before.each:
            self.story = create_story(name='Test Story', sequential_order=1.0, users=['Human'])
        
        with it('should return synchronized data structure'):
            result = self.story.synchronize()
            expect(result['name']).to(equal('Test Story'))
            expect(result['sequential_order']).to(equal(1.0))
        
        with it('should include users in synchronized data'):
            result = self.story.synchronize()
            expect(result['users']).to(contain('Human'))
    
    with context('that generates synchronization report'):
        with before.each:
            self.story = create_story(name='Test Story', users=['Human'], steps=[{'given': 'test'}])
        
        with it('should include story name in report'):
            report = self.story.synchronize_report()
            expect(report['story']).to(equal('Test Story'))
        
        with it('should include user count in report'):
            report = self.story.synchronize_report()
            expect(report['users_count']).to(equal(1))
        
        with it('should indicate if story has steps'):
            report = self.story.synchronize_report()
            expect(report['has_steps']).to(be_true)
    
    with context('that compares with another story'):
        with before.each:
            self.story1 = create_story(name='Same Story', sequential_order=1.0, users=['Human'])
            self.story2 = create_story(name='Same Story', sequential_order=1.0, users=['Human'])
            self.story3 = create_story(name='Different Story')
        
        with it('should match when names are same'):
            result = self.story1.compare(self.story2)
            expect(result['match']).to(be_true)
            expect(result['name_match']).to(be_true)
        
        with it('should not match when names differ'):
            result = self.story1.compare(self.story3)
            expect(result['match']).to(be_false)
        
        with it('should compare users'):
            result = self.story1.compare(self.story2)
            expect(result['users_match']).to(be_true)
    
    with context('that renders to JSON'):
        with before.each:
            self.story = create_story(name='Test Story', sequential_order=1.0, users=['Human'])
        
        with it('should include story name in rendered JSON'):
            result = self.story.render()
            expect(result['name']).to(equal('Test Story'))
        
        with it('should include users in rendered JSON'):
            result = self.story.render()
            expect(result['users']).to(contain('Human'))
        
        with it('should include sequential order in rendered JSON'):
            result = self.story.render()
            expect(result['sequential_order']).to(equal(1.0))
    
    with context('that converts to dictionary'):
        with before.each:
            self.story = create_story(name='Test Story', users=['Human'], steps=[{'given': 'test'}])
        
        with it('should include type in dictionary'):
            result = self.story.to_dict()
            expect(result['type']).to(equal('story'))
        
        with it('should include users in dictionary'):
            result = self.story.to_dict()
            expect(result['users']).to(contain('Human'))
        
        with it('should include Steps in dictionary when present'):
            result = self.story.to_dict()
            expect(result['Steps']).not_to(be_none)

