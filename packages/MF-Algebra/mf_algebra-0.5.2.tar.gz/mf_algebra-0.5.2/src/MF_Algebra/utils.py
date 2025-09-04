from MF_Tools.dual_compatibility import (
	Text, dc_Tex as Tex,
	UP, DOWN, LEFT, RIGHT,
	GREEN, BLUE, ORANGE,
	Indicate,
	VGroup, VDict,
	Line,
	Scene
)
import numpy as np


def Smarten(input):
	from .expressions.expression_core import Expression
	from .actions.action_core import Action
	from .timelines.timeline_core import Timeline
	from .expressions.numbers import Integer, Real
	if isinstance(input, (Expression, Action, Timeline)):
		return input.copy()
	elif isinstance(input, int):
		return Integer(input)
	elif isinstance(input, float):
		if input.is_integer():
			return Integer(int(input))
		else:
			return Real(input)
	else:
		raise NotImplementedError(f"Unsupported type {type(input)}")


def add_spaces_around_brackets(input_string): #GPT
	result = []
	i = 0
	length = len(input_string)

	while i < length:
		if input_string[i] == '{' or input_string[i] == '}':
			if i > 0 and input_string[i - 1] != ' ':
				result.append(' ')
			result.append(input_string[i])
			if i < length - 1 and input_string[i + 1] != ' ':
				result.append(' ')
		else:
			result.append(input_string[i])
		i += 1

	# Join the list into a single string and remove any extra spaces
	spaced_string = ''.join(result).split()
	return ' '.join(spaced_string)


def debug_glyph(scene, glyph_mobject):
	from MF_Tools.dual_compatibility import Dot, GlowDot, turn_animation_into_updater, MoveAlongPath, BLUE_A
	glyph_mobject.data_dots = VGroup([
		Dot(d[0], radius=0.01*max(glyph_mobject.get_width(), glyph_mobject.get_height()))
		for d in glyph_mobject.data
	])
	glyph_mobject.data_dots[::2].set_opacity(0.25)
	glyph_mobject.data_dots[1::2].set_opacity(0.1)
	glyph_mobject.writing_dot = GlowDot(color=BLUE, radius=0.06*max(glyph_mobject.get_width(), glyph_mobject.get_height()))
	writing_dot_anim = MoveAlongPath(glyph_mobject.writing_dot, glyph_mobject, run_time=5)
	glyph_mobject.set_opacity(0.1)
	num_dots = len(glyph_mobject.data_dots)
	glyph_mobject.dot_count = Text('Data points: ' + str(num_dots)).next_to(glyph_mobject, DOWN, buff=glyph_mobject.get_height()/4)
	#glyph_mobject.dot_count.scale_to_fit(len_x=glyph_mobject.get_width())
	glyph_mobject.dot_count.scale(0.3)
	scene.add(glyph_mobject.data_dots, glyph_mobject.writing_dot, glyph_mobject.dot_count)
	turn_animation_into_updater(writing_dot_anim, cycle=True)
Scene.debug_glyph = debug_glyph

def debug_glyphs(scene, *mobjects):
	for M in mobjects:
		for g in M:
			debug_glyph(scene, g)
Scene.debug_glyphs = debug_glyphs







def debug_smarttex(scene, smarttex, show_indices=True, show_addresses=True, show_submobjects=True):
	print("Debugging Expression:")
	print(smarttex)
	print("Length: ", len(smarttex))
	print("Type: ", type(smarttex))
	print("Number of children: ", len(smarttex.children))
	if show_indices:
		for index in range(len(smarttex)):
			index_text = Text(str(index), color=GREEN).next_to(smarttex, DOWN)
			scene.add(index_text)
			scene.play(Indicate(smarttex[0][index], color=GREEN))
			scene.remove(index_text)
	if show_addresses:
		for ad in smarttex.get_all_addresses():
			ad_text = Text(ad, color=ORANGE).next_to(smarttex, DOWN)
			subex_type = Text(type(smarttex.get_subex(ad)).__name__, color=ORANGE).next_to(ad_text, DOWN)
			scene.add(ad_text, subex_type)
			scene.play(Indicate(smarttex[ad], color=ORANGE))
			scene.remove(ad_text, subex_type)
	if show_addresses:
		for i, subm in enumerate(smarttex.submobjects[0]):
			subm_number = Text(str(i), color=BLUE).next_to(subm, DOWN)
			scene.add(subm_number)
			scene.play(Indicate(subm, color=BLUE))
			scene.remove(subm_number)


def match_expressions(template, expression):
	"""
		This function will either return a ValueError if the expression
		simply does not match the structure of the template, such as a missing
		operand or a plus in place of a times, or if they do match it will return
		a dictionary of who's who. For example,
		
		template:      (a*b)**n
		expression:    (4*x)**(3+y)
		return value:  {a:4, b:x, n:3+y}

		template:      n + x**5
		expression:    12 + x**3
		return value:  ValueError("Structures do not match at address 11, 5 vs 3")
		
		template:      x**n*x**m
		expression:    2**2*3**3
		return value:  ValueError("Conflicting matches for x: 2 and 3")

		Obviously this has to be recursive, but gee I am feeling a bit challenged atm...
		...
		Ok I think I've done it!
	"""
	from .expressions.variables import Variable
	# Leaf case
	if not template.children:
		if isinstance(template, Variable):
			return {template: expression}
		elif template.is_identical_to(expression):
			return {}
		else:
			raise ValueError("Expressions do not match")
	
	# Node case
	var_dict = {}
	if not isinstance(expression, type(template)):
		raise ValueError("Expressions do not match type")
	if not len(template.children) == len(expression.children):
		raise ValueError("Expressions do not match children length")
	for tc,ec in zip(template.children, expression.children):
		child_dict = match_expressions(tc,ec)
		matching_keys = child_dict.keys() & var_dict.keys()
		if any(not child_dict[key].is_identical_to(var_dict[key]) for key in matching_keys):
			raise ValueError("Conflicting matches for " + str(matching_keys))
		var_dict.update(child_dict)

	return var_dict


def random_number_expression(leaves=range(-5, 10), max_depth=3, max_children_per_node=2, **kwargs):
	import random
	from .expressions.numbers import Integer
	from .expressions.operations import Add, Sub, Mul, Div, Pow, Negative
	nodes = [Add, Sub, Mul, Pow]
	node = random.choice(nodes)
	def generate_child(current_depth):
		if np.random.random() < 1 / (current_depth + 1):
			return Integer(random.choice(leaves))
		else:
			return random_number_expression(leaves, max_depth - 1)
	def generate_children(current_depth, number_of_children):
		return [generate_child(current_depth) for _ in range(number_of_children)]
	if node == Add or node == Mul:
		children = generate_children(max_depth, random.choice(list(range(2,max_children_per_node+1))))
	elif node == Negative:
		children = generate_children(max_depth, 1)
	else:
		children = generate_children(max_depth, 2)
	return node(*children, **kwargs)


def create_graph(expr, node_size=0.5, horizontal_buff=1, vertical_buff=1.5, printing=False):
	def create_node(address):
		from .expressions.numbers import Integer, Real, Rational
		from .expressions.variables import Variable
		from .expressions.operations import Add, Sub, Mul, Div, Pow, Negative
		from .expressions.functions import Function
		from .expressions.sequences import Sequence
		from .expressions.relations import Equation, LessThan, LessThanOrEqualTo, GreaterThan, GreaterThanOrEqualTo
		type_to_symbol_dict = {
			Integer: lambda expr: str(expr.n),
			Real: lambda expr: expr.symbol if expr.symbol else str(expr),
			Rational: lambda expr: "\\div",
			Variable: lambda expr: expr.symbol,
			Add: lambda expr: "+",
			Sub: lambda expr: "-",
			Mul: lambda expr: "\\times",
			Div: lambda expr: "\\div",
			Pow: lambda expr: "\\hat{}",
			Negative: lambda expr: "-",
			Function: lambda expr: expr.symbol,
			Sequence: lambda expr: ",",
			Equation: lambda expr: "=",
			LessThan: lambda expr: "<",
			LessThanOrEqualTo: lambda expr: "\\leq",
			GreaterThan: lambda expr: ">",
			GreaterThanOrEqualTo: lambda expr: "\\geq",
		}
		subex = expr.get_subex(address)
		symbol = type_to_symbol_dict[type(subex)](subex)
		tex = Tex(symbol)
		# if tex.width > tex.height:
		# 	tex.scale_to_fit_width(node_size)
		# else:
		# 	tex.scale_to_fit_height(node_size)
		return tex
	addresses = expr.get_all_addresses()
	if printing: print(addresses)
	max_length = max(len(address) for address in addresses)
	layered_addresses = [
		[ad for ad in addresses if len(ad) == i]
		for i in range(max_length + 1)
	]
	if printing: print(layered_addresses)
	max_index = max(range(len(layered_addresses)), key=lambda i: len(layered_addresses[i]))
	max_layer = layered_addresses[max_index]
	max_width = len(max_layer)
	if printing: print(max_index, max_width, max_layer)
	Nodes = VDict({ad: create_node(ad) for ad in addresses})
	#Max_layer = VGroup(*[Nodes[ad] for ad in max_layer]).arrange(RIGHT,buff=horizontal_buff)
	def position_children(parent_address):
		parent = Nodes[parent_address]
		child_addresses = [ad for ad in layered_addresses[len(parent_address)+1] if ad[:-1] == parent_address]
		if printing: print(child_addresses)
		child_Nodes = VGroup(*[Nodes[ad] for ad in child_addresses]).arrange(RIGHT,buff=1)
		child_Nodes.move_to(parent.get_center()+DOWN*vertical_buff)
	for i in range(max_index, max_length):
		for ad in layered_addresses[i]:
			position_children(ad)
	def position_parent(child_address):
		sibling_Nodes = VGroup(*[Nodes[ad] for ad in layered_addresses[len(child_address)] if ad[:-1] == child_address[:-1]])
		parent_Node = Nodes[child_address[:-1]]
		parent_Node.move_to(sibling_Nodes.get_center()+UP*vertical_buff)
	for i in range(max_index, 0, -1):
		for ad in layered_addresses[i]:
			position_parent(ad)
	Edges = VGroup(*[
		Line(
			Nodes[ad[:-1]].get_bounding_box_point(DOWN),
			Nodes[ad].get_bounding_box_point(UP),
			buff=0.2, stroke_opacity=0.4
			)
		for ad in addresses if len(ad) > 0
		])
	return VGroup(Nodes, Edges)


"""
import MF_Algebra as MF
import sympy as sp
def expression_to_sympy(expr):
	expr = Smarten(expr)
	if isinstance(expr, MF.expressions.numbers.Number):
		if isinstance(expr, MF.expressions.numbers.Integer):
			return sp.Integer(expr.n)
		elif isinstance(expr, MF.expressions.numbers.Real):
			return sp.Float(expr.n)
		elif isinstance(expr, MF.expressions.numbers.Rational):
			return sp.Rational(expr.n, expr.d)
		else:
			raise NotImplementedError(f"Unsupported type {type(expr)}")
	elif isinstance(expr, MF.expressions.variables.Variable):
		return sp.Symbol(expr.symbol)
	elif isinstance(expr, MF.expressions.operations.Operation):
		if isinstance(expr, MF.expressions.operations.Add):
			return sp.Add(*map(expression_to_sympy, expr.children))
		elif isinstance(expr, MF.expressions.operations.Sub):
			return sp.Add(expression_to_sympy(expr.children[0]), -expression_to_sympy(expr.children[1]))
		elif isinstance(expr, MF.expressions.operations.Mul):
			return sp.Mul(*map(expression_to_sympy, expr.children))
		elif isinstance(expr, MF.expressions.operations.Div):
			return sp.Mul(expression_to_sympy(expr.children[0]), sp.Pow(expression_to_sympy(expr.children[1]), -1))
		elif isinstance(expr, MF.expressions.operations.Pow):
			return sp.Pow(expression_to_sympy(expr.children[0]), expression_to_sympy(expr.children[1]))
		elif isinstance(expr, MF.expressions.operations.Negative):
			return sp.Mul(-1, expression_to_sympy(expr.children[0]))
		else:
			raise NotImplementedError(f"Unsupported type {type(expr)}")
	elif isinstance(expr, MF.expressions.sequences.Sequence):
		raise NotImplementedError("Sequences not yet supported")
	elif isinstance(expr, MF.expressions.functions.Function):
		raise NotImplementedError("Functions not yet supported")
	elif isinstance(expr, MF.expressions.relations.Relation):
		raise NotImplementedError("Relations not yet supported")
	else:
		raise NotImplementedError(f"Unsupported type {type(expr)}")

"""