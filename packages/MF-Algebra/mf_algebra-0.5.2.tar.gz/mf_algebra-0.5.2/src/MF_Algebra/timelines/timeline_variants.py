from .timeline_core import *


class AutoTimeline(Timeline):
    def __init__(self, auto_fill=True, **kwargs):
        super().__init__(**kwargs)
        self.auto_fill = auto_fill
    
    def set_expression(self, index: int, expression: Expression):
        super().set_expression(index, expression)
        if self.auto_fill and self.get_action(index) is None:
            next_action = self.decide_next_action(index)
            if next_action is not None:
                self.set_action(index, next_action)
        return self
    
    def set_action(self, index: int, action: Action):
        super().set_action(index, action)
        if self.auto_fill and self.get_expression(index+1) is None:
            next_expression = action.get_output_expression(self.get_expression(index))
            self.set_expression(index+1, next_expression)
        return self
    
    def decide_next_action(self, index: int) -> Action:
        # Implement in subclasses. Return None if finished.
        return None

    def resume(self):
        self.add_action_to_end(self.decide_next_action(-1))


class CombinedRuleTimeline(AutoTimeline):
    def __init__(self, *timelines, **kwargs):
        self.constituents = [timeline if isinstance(timeline, type) else timeline.__class__ for timeline in timelines]
        for timeline in self.constituents:
            timeline.__init__(self, **kwargs)
    
    def decide_next_action(self, index: int) -> Action:
        for timeline in self.constituents:
            result = timeline.decide_next_action(self, index)
            if result is not None:
                return result
        return None




