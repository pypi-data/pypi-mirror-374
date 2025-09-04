# actions.py
from MF_Tools.dual_compatibility import Write, FadeIn, FadeOut
from ..expressions.expression_core import *
from ..utils import *
from .animations import TransformByAddressMap


class Action:
	"""
		Transforms Expressions into other Expressions,
		both as static objects and also with an animation.

		An action is defined by two main things:
		the get_output_expression method, which controls how it acts on static expressions,
		and the get_addressmap method, which controls how it acts as an animation.
		Both set attributes of the corresponding name and return them.

		It may also have a preaddress parameter/attribute which will determine the subexpression
		address at which the action is applied, and a few other attributes which may adjust some
		specifics.

		self.input_expression is set to None during __init__. It is critical that actions
		can exist prior to being given expressions, so that they can be combined together.
		When an input expression is received, this attribute is set, and the method
		.get_output_expression is called, setting self.output_expression.
		This is all that is required for static actions, no animations.

		Now, to create the animation between these expressions:

		get_addressmap is also unique to each action, and returns something like
		[
			["00", "01"],
			["01", "00", {"path_arc":PI/2}],
			[FadeIn, "1"],
			["1", FadeOut]
		]
		which contains all the expression-agnostic information about the animation.
		Often this will simply define and return this list with no computation.

		get_glyphmap combines the input_expression, output_expression, and addressmap
		to create a list like
		[
			([0,1,2], [5,6]),
			([3,4,5], [1,2,3], {"path_arc":PI/2}),
			(FadeIn, [8,9]),
			([6], FadeOut)
		]
		which tells which glyphs of the mobjects to send to which others, and how.

		get_animation then simply parses this glyphmap list to create a list of
		animations, probably to be passed to AnimationGroup, like
		[
			ReplacementTransform(A[0][0,1,2], B[0][5,6]),
			ReplacementTransform(A[0][3,4,5], B[0][1,2,3], path_arc=PI/2),
			FadeIn(B[0][8,9]),
			FadeOut(A[0][6]),
			...
		]
		or something like that, the syntax is partially made up. The ... is
		ReplacementTransforms of all the individual glyphs not mentioned in the glyphmap,
		whose lengths have to exactly match.

		Broadly speaking, that's that!
	"""
	def __init__(self,
		introducer=Write,
		remover=FadeOut,
		preaddress=''
	):
		self.introducer = introducer
		self.remover = remover
		self.preaddress = preaddress

	def get_output_expression(self, input_expression):
  		# define in subclasses
		raise NotImplementedError

	def get_addressmap(self, input_expression, **kwargs):
		# define in subclasses
		raise NotImplementedError

	def get_animation(self, **kwargs):
		def animation(input_exp, output_exp=None):
			if output_exp is None:
				output_exp = self.get_output_expression(input_exp)
			return TransformByAddressMap(
			input_exp,
			output_exp,
			*self.get_addressmap(input_exp),
			default_introducer=self.introducer,
			default_remover=self.remover,
			**kwargs
			)
		return animation
	
	def __call__(self, expr1, expr2=None, **kwargs):
		return self.get_animation(**kwargs)(expr1, expr2)

	def __or__(self, other):
		from .combinations import ParallelAction
		if isinstance(other, ParallelAction):
			return ParallelAction(self, *other.actions)
		elif isinstance(other, Action):
			return ParallelAction(self, other)
		else:
			raise ValueError("Can only use | with other ParallelAction or Action")
	
	def __rshift__(self, other):
		other = Smarten(other)
		from ..expressions.expression_core import Expression
		from ..timelines.timeline_core import Timeline
		if isinstance(other, Expression):
			timeline = Timeline()
			timeline.add_action_to_end(self).add_expression_to_end(other)
			return timeline
		elif isinstance(other, Action):
			timeline = Timeline()
			timeline.add_action_to_end(self).add_action_to_end(other)
			return timeline
		else:
			return NotImplemented

	def __rrshift__(self, other):
		return Smarten(other).__rshift__(self)
	
	def __repr__(self):
		return type(self).__name__ + "(" + self.preaddress + ")"
	
	def copy(self):
		return deepcopy(self)
	
	def both(self, number_of_sides=2):
		# Intended to turn an action on an expression into an action done to both sides of an equation.
		# Can be passed a number to apply to more than 2 sides for, say, a triple equation or inequality.
		return self.pread(*[str(i) for i in range(number_of_sides)])
	
	def pread(self, *addresses):
		if len(addresses) == 0:
			return self
		elif len(addresses) == 1:
			self.preaddress = addresses[0] + self.preaddress
			return self
		else:
			actions = []
			for ad in addresses:
				action = self.copy().pread(ad)
				actions.append(action)
			from .combinations import ParallelAction
			return ParallelAction(*actions)

	def __leq__(self, expr):
		assert isinstance(expr, Expression), "Can only apply expression >= action"
		return self.get_output_expression(expr)


def preaddressfunc(func):
	def wrapper(action, expr, *args, **kwargs):
		expr = expr.copy()
		preaddress = kwargs.get('preaddress', '') or action.preaddress
		if len(preaddress)==0:
			output_expression = func(action, expr)
		else:
			active_part = expr.get_subex(preaddress)
			result = func(action, active_part)
			output_expression = expr.substitute_at_address(result, preaddress)
		output_expression.reset_parentheses()
		return output_expression
	return wrapper

def preaddressmap(getmap):
	def wrapper(action, expr, *args, **kwargs):
		expr = expr.copy()
		preaddress = kwargs.get('preaddress', '') or action.preaddress
		addressmap = getmap(action, expr, *args, **kwargs)
		if preaddress:
			for entry in addressmap:
				for i, ad in enumerate(entry):
					if isinstance(ad, str):
						entry[i] = preaddress + ad
		return addressmap
	return wrapper

def autoparenmap(getmap, mode='stupid'):
	if mode=='stupid':
		def wrapper(action, expr, *args, **kwargs):
			addressmap = list(getmap(action, expr, *args, **kwargs))
			in_expr, out_expr = expr, action.get_output_expression(expr)
			for in_add in in_expr.get_all_addresses():
				if in_expr.get_subex(in_add).parentheses:
					addressmap.append([in_add+'()', FadeOut, {'run_time':0.5}])
				for entry in addressmap:
					if entry[0] == in_add:
						entry[0] = entry[0] + '_'
			for out_add in out_expr.get_all_addresses():
				if out_expr.get_subex(out_add).parentheses:
					addressmap.append([FadeIn, out_add+'()', {'run_time':0.5, 'delay':0.5}])
				for entry in addressmap:
					if entry[1] == out_add:
						entry[1] = entry[1] + '_'
			return addressmap

	if mode=='smart':
		def wrapper(action, expr, *args, **kwargs):
			addressmap = list(getmap(action, expr, *args, **kwargs))
			in_expr, out_expr = expr, action.get_output_expression(expr)
	return wrapper


class IncompatibleExpression(Exception):
	pass





  




 