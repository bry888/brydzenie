# Copyright 2015 Google Inc. All Rights Reserved.

"""Cloud resource list filter expression evaluator.

The "evaluator" is a parsed resource expression tree with branching factor 2 for
binary operator nodes, 1 for NOT and function nodes, and 0 for TRUE nodes.
Evaluation for a resource object starts with expression_tree_root.Evaluate(obj)
which recursively evaluates child nodes. The logic operators use left-right
shortcut pruning, so an evaluation may not visit every node in the expression
tree.
"""

from googlecloudsdk.core.resource import resource_property


class Expr(object):
  """Expression base class."""
  pass


class ExprTRUE(Expr):
  """TRUE node.

  Always evaluates True.
  """

  def Evaluate(self, unused_obj):
    return True


class ExprConnective(Expr):
  """Base logic node.

  Attributes:
    left: Left Expr operand.
    right: Right Expr operand.
  """

  def __init__(self, left=None, right=None):
    super(ExprConnective, self).__init__()
    self._left = left
    self._right = right


class ExprAND(ExprConnective):
  """AND node.

  AND with left-to-right shortcut pruning.
  """

  def __init__(self, *args, **kwargs):
    super(ExprAND, self).__init__(*args, **kwargs)

  def Evaluate(self, obj):
    if not self._left.Evaluate(obj):
      return False
    if not self._right.Evaluate(obj):
      return False
    return True


class ExprOR(ExprConnective):
  """OR node.

  OR with left-to-right shortcut pruning.
  """

  def __init__(self, *args, **kwargs):
    super(ExprOR, self).__init__(*args, **kwargs)

  def Evaluate(self, obj):
    if self._left.Evaluate(obj):
      return True
    if self._right.Evaluate(obj):
      return True
    return False


class ExprNOT(ExprConnective):
  """NOT node."""

  def __init__(self, expr=None):
    super(ExprNOT, self).__init__()
    self._expr = expr

  def Evaluate(self, obj):
    return not self._expr.Evaluate(obj)


class ExprGlobal(Expr):
  """Global restriction function call node.

  Attributes:
    func: The function implementation Expr. Must match this description:
          func(obj, args)

          Args:
            obj: The current resource object.
            args: The possibly empty list of arguments.

          Returns:
            True on success.
    args: List of function call actual arguments.
  """

  def __init__(self, func=None, args=None):
    super(ExprGlobal, self).__init__()
    self._func = func
    self._args = args

  def Evaluate(self, unused_obj):
    return self._func(*self._args)


class ExprOperand(Expr):
  """Operand node.

  Operand values are strings that represent string or numeric constants. The
  numeric value, if any, is precomputed by the constructor. If an operand has a
  numeric value then the actual key values are converted to numbers at
  Evaluate() time if possible for Apply(); if the conversion fails then the key
  and operand string values are passed to Apply().
  """

  def __init__(self, value):
    super(ExprOperand, self).__init__()
    self.string_value = value
    try:
      self.numeric_value = int(value)
    except ValueError:
      try:
        self.numeric_value = float(value)
      except ValueError:
        self.numeric_value = None


class ExprOperator(Expr):
  """Base term (<key operator operand>) node.

  ExprOperator subclasses must define the function Apply(self, value, operand)
  that returns the result of <value> <op> <operand>.

  Attributes:
    key: Resource object key (list of str, int and/or None values).
    operand: The term ExprOperand operand.
    transform: Optional key value transform function.
    args: Optional list of transform actual args.
  """

  def __init__(self, key=None, operand=None, transform=None, args=None):
    super(ExprOperator, self).__init__()
    self._key = key
    self._operand = operand
    self._transform = transform
    self._args = args

  def Evaluate(self, obj):
    """Evaluate a term node.

    Args:
      obj: The resource object to evaluate.
    Returns:
      The value of the operator applied to the key value and operand.
    """
    value = resource_property.Get(obj, self._key)
    if self._transform:
      try:
        value = (self._transform(value, *self._args) if self._key
                 else self._transform(*self._args))
      except (AttributeError, TypeError, ValueError):
        value = None
    if self._operand.numeric_value is not None:
      try:
        return self.Apply(float(value), self._operand.numeric_value)
      except (TypeError, ValueError):
        pass
    try:
      return self.Apply(value, self._operand.string_value)
    except (AttributeError, TypeError, ValueError):
      return False


class ExprLT(ExprOperator):
  """LT node."""

  def __init__(self, *args, **kwargs):
    super(ExprLT, self).__init__(*args, **kwargs)

  def Apply(self, value, operand):
    return value < operand


class ExprLE(ExprOperator):
  """LE node."""

  def __init__(self, *args, **kwargs):
    super(ExprLE, self).__init__(*args, **kwargs)

  def Apply(self, value, operand):
    return value <= operand


def _IsIn(matcher, value):
  """Applies matcher to determine if the expression operand is in value.

  Args:
    matcher: Boolean match function that takes value as an argument and returns
      True if the expression operand is in value.
    value: The value to match against.

  Returns:
    True if the expression operand is in value.
  """
  if matcher(value):
    return True
  try:
    for index in value:
      if matcher(index):
        return True
  except TypeError:
    pass
  return False


class ExprInMatch(ExprOperator):
  """Membership and anchored prefix*suffix match node."""

  def __init__(self, prefix=None, suffix=None, *args, **kwargs):
    """Initializes the anchored prefix and suffix patterns.

    Args:
      prefix: The anchored prefix pattern string.
      suffix: The anchored suffix pattern string.
      *args: Super class positional args.
      **kwargs: Super class keyword args.
    """
    super(ExprInMatch, self).__init__(*args, **kwargs)
    self._prefix = prefix
    self._suffix = suffix

  def Apply(self, value, unused_operand):
    """Applies the : anchored case insensitive match operation."""

    def _InMatch(value):
      """Applies case insensitive string prefix/suffix match to value."""
      if value is None:
        return False
      v = str(value).lower()
      return ((not self._prefix or v.startswith(self._prefix)) and
              (not self._suffix or v.endswith(self._suffix)))

    return _IsIn(_InMatch, value)


class ExprIn(ExprOperator):
  """Membership case-insensitive match node."""

  def __init__(self, *args, **kwargs):
    super(ExprIn, self).__init__(*args, **kwargs)
    self._operand.string_value = self._operand.string_value.lower()

  def Apply(self, value, operand):
    """Checks if operand is a member of value ignoring case differences.

    Args:
      value: The number, string, dict or list object value.
      operand: Number or string operand.

    Returns:
      True if operand is a member of value ignoring case differences.
    """

    def _InEq(subject):
      """Applies case insensitive string contains equality check to subject."""
      if operand == subject:
        return True
      try:
        if operand == subject.lower():
          return True
      except AttributeError:
        pass
      try:
        if operand in subject:
          return True
      except TypeError:
        pass
      try:
        if operand in subject.lower():
          return True
      except AttributeError:
        pass
      try:
        if int(operand) in subject:
          return True
      except ValueError:
        pass
      try:
        if float(operand) in subject:
          return True
      except ValueError:
        pass
      return False

    return _IsIn(_InEq, value)


class ExprHAS(ExprOperator):
  """Case insensitive membership node.

  This is the pre-compile Expr for the ':' operator. It compiles into either an
  ExprInMatch node for prefix*suffix matching or an ExprIn node for membership.
  """

  def __new__(cls, key=None, operand=None, transform=None, args=None):
    """Checks for prefix*suffix operand.

    The * operator splits the operand into prefix and suffix matching strings.

    Args:
      key: Resource object key (list of str, int and/or None values).
      operand: The term ExprOperand operand.
      transform: Optional key value transform function.
      args: Optional list of transform actual args.

    Returns:
      ExprInMatch if operand is an anchored pattern, ExprIn otherwise.
    """
    if '*' not in operand.string_value:
      return ExprIn(key=key, operand=operand, transform=transform, args=args)
    pattern = operand.string_value.lower()
    i = pattern.find('*')
    prefix = pattern[:i]
    suffix = pattern[i + 1:]
    return ExprInMatch(key=key, operand=operand, transform=transform, args=args,
                       prefix=prefix, suffix=suffix)


class ExprMatch(ExprOperator):
  """Anchored prefix*suffix match node."""

  def __init__(self, prefix=None, suffix=None, *args, **kwargs):
    """Initializes the anchored prefix and suffix patterns.

    Args:
      prefix: The anchored prefix pattern string.
      suffix: The anchored suffix pattern string.
      *args: Super class positional args.
      **kwargs: Super class keyword args.
    """
    super(ExprMatch, self).__init__(*args, **kwargs)
    self._prefix = prefix
    self._suffix = suffix

  def Apply(self, value, unused_operand):
    return ((not self._prefix or value.startswith(self._prefix)) and
            (not self._suffix or value.endswith(self._suffix)))


class _ExprEQ(ExprOperator):
  """Case sensitive EQ node with no match optimization."""

  def __init__(self, *args, **kwargs):
    super(_ExprEQ, self).__init__(*args, **kwargs)

  def Apply(self, value, operand):
    return operand == value


class ExprEQ(ExprOperator):
  """Case sensitive EQ node."""

  def __new__(cls, key=None, operand=None, transform=None, args=None):
    """Checks for prefix*suffix operand.

    The * operator splits the operand into prefix and suffix matching strings.

    Args:
      key: Resource object key (list of str, int and/or None values).
      operand: The term ExprOperand operand.
      transform: Optional key value transform function.
      args: Optional list of transform actual args.

    Returns:
      ExprMatch if operand is an anchored pattern, _ExprEQ otherwise.
    """
    if '*' not in operand.string_value:
      return _ExprEQ(key=key, operand=operand, transform=transform, args=args)
    pattern = operand.string_value
    i = pattern.find('*')
    prefix = pattern[:i]
    suffix = pattern[i + 1:]
    return ExprMatch(key=key, operand=operand, transform=transform, args=args,
                     prefix=prefix, suffix=suffix)


class ExprNE(ExprOperator):
  """NE node."""

  def __init__(self, *args, **kwargs):
    super(ExprNE, self).__init__(*args, **kwargs)

  def Apply(self, value, operand):
    try:
      return operand != value.lower()
    except AttributeError:
      return operand != value


class ExprGE(ExprOperator):
  """GE node."""

  def __init__(self, *args, **kwargs):
    super(ExprGE, self).__init__(*args, **kwargs)

  def Apply(self, value, operand):
    return value >= operand


class ExprGT(ExprOperator):
  """GT node."""

  def __init__(self, *args, **kwargs):
    super(ExprGT, self).__init__(*args, **kwargs)

  def Apply(self, value, operand):
    return value > operand
