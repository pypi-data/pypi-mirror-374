from .expression_core import *


class Variable(Expression):
	def __init__(self, symbol, **kwargs):
		self.symbol = symbol
		self.children = []
		super().__init__(**kwargs)

	@parenthesize
	def __str__(self):
		return self.symbol
	
	def number_of_glyphs(self):
		return len(self.symbol)

	def is_identical_to(self, other):
		return type(self) == type(other) and self.symbol == other.symbol

	def compute(self):
		raise ValueError(f"Expression contains a variable {self.symbol}.")
