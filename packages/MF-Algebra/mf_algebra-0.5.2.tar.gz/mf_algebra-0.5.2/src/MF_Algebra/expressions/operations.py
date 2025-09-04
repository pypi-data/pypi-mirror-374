from .expression_core import *


class Operation(Combiner):
	def __init__(self, symbol, symbol_glyph_length, *children, **kwargs):
		super().__init__(symbol, symbol_glyph_length, *children, **kwargs)

	def compute(self):
		result = self.children[0].compute()
		for child in self.children[1:]:
			result = self.eval_op(result, child.compute())
		return result


class Add(Operation):
	def __init__(self, *children, **kwargs):
		self.eval_op = lambda x,y: x+y
		super().__init__("+", 1, *children, **kwargs)

	def auto_parentheses(self):
		for child in self.children:
			child.auto_parentheses()

	def is_negative(self):
		return self.children[0].is_negative()

class Sub(Operation):
	def __init__(self, *children, **kwargs):
		self.eval_op = lambda x,y: x-y
		super().__init__("-", 1, *children, **kwargs)

	def auto_parentheses(self):
		self.children[0].auto_parentheses()
		for child in self.children[1:]:
			if isinstance(child, (Add, Sub)) or child.is_negative():
				child.give_parentheses()
			child.auto_parentheses()

	def is_negative(self):
		return self.children[0].is_negative()

class Mul(Operation):
	def __init__(self, *children, mode="auto", **kwargs):
		from .numbers import Number
		self.eval_op = lambda x,y: x*y
		self.mode = algebra_config["multiplication_mode"] if mode is None else mode
		if self.mode == "auto":
			if all(isinstance(child, Number) for child in list(map(Smarten,children))):
				self.mode = "dot"
			else:
				self.mode = "juxtapose"
		if self.mode == "dot":
			super().__init__("\\cdot", 1, *children, **kwargs)
		elif self.mode == "x":
			super().__init__("\\times", 1, *children, **kwargs)
		elif self.mode == "juxtapose":
			super().__init__("", 0, *children, **kwargs)
		else:
			raise ValueError(f"Invalid multiplication mode: {self.mode}. Mode must be dot, x, or juxtapose")

	def auto_parentheses(self): # should be more intelligent based on mode
		for child in self.children:
			if isinstance(child, (Add, Sub)) or child.is_negative():
				child.give_parentheses()
			child.auto_parentheses()

	def is_negative(self):
		return self.children[0].is_negative()

class Div(Operation):
	def __init__(self, *children, mode=None, **kwargs):
		self.eval_op = lambda x,y: x/y
		self.mode = algebra_config["division_mode"] if mode is None else mode
		if self.mode == "fraction":
			super().__init__("\\over", 1, *children, **kwargs)
		elif self.mode == "inline":
			super().__init__("\\div", 1, *children, **kwargs)
		else:
			raise ValueError(f"Invalid division mode: {self.mode}. Mode must be fraction or inline")

	def auto_parentheses(self):
		for child in self.children:
			if (isinstance(child, (Add, Sub, Mul, Div)) or child.is_negative()) and algebra_config["division_mode"] == "inline":
				child.give_parentheses()
			child.auto_parentheses()

	def is_negative(self):
		return self.children[0].is_negative() or self.children[1].is_negative()
	
	def compute(self):
		num = self.children[0].compute()
		den = self.children[1].compute()
		if den == 0:
			raise ZeroDivisionError
		if num % den == 0:
			return int(num / den)
		else:
			return float(num) / float(den)

class Pow(Operation):
	def __init__(self, *children, **kwargs):
		self.eval_op = lambda x,y: x**y
		super().__init__("^", 0, *children, **kwargs)

	def auto_parentheses(self):
		assert len(self.children) == 2 #idc how to auto paren power towers
		if isinstance(self.children[0], Operation) or self.children[0].is_negative():
			self.children[0].give_parentheses()
		for child in self.children:
			child.auto_parentheses()

	def is_negative(self):
		return False


class Negative(Expression):
	def __init__(self, child, **kwargs):
		self.children = [Smarten(child)]
		super().__init__(**kwargs)

	@parenthesize
	def __str__(self):
		return "-" + str(self.children[0])

	def auto_parentheses(self):
		if isinstance(self.children[0], (Add, Sub)) or self.children[0].is_negative():
			self.children[0].give_parentheses()
		self.children[0].auto_parentheses()

	def is_negative(self):
		return True

	def compute(self):
		return -self.children[0].compute()
	
	special_character_to_glyph_method_dict = {
		**Expression.special_character_to_glyph_method_dict,
		'-': 'get_negative_glyph',
	}
	def get_negative_glyph(self):
		return [0]
