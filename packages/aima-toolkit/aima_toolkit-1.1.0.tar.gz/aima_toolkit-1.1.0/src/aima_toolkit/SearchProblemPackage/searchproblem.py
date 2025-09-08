from enum import Enum, auto
from typing import Callable, Union, TypeAlias, Iterable
from .node import Node

Heuristic: TypeAlias = Callable[[Node], Union[int, float]]

class SearchStatus(Enum):
    FAILURE = auto()
    CUTOFF = auto()
    SUCCESS = auto()

class SearchProblem[S, A]:
  def __init__(self, initial_state : S):
    self.initial_state = initial_state

  def ACTIONS(self, state: S) -> set[A] | Iterable[A]:
    """
    Return a set of actions, or iterable over the actions, that can be performed on this search problem.

    Args:
        state: The state you wish to check the actions for.

    Returns:
        Set of actions that can be done in the given state.
    """
    raise NotImplementedError("This method should be overridden by subclasses")
  
  def RESULTS(self, state : S, action : A) -> set[S] | Iterable[S]:
    """
    Takes a state and an action done on that state and returns the set of all possible states, or an iterable over the actions
    Args:
      state: The state you wish to do an action on.
      action: The action you wish to do.

    Returns:
      A set of actions that can be done in the given state, or an iterable over the set of actions.
    """
    raise NotImplementedError("This method should be overridden by subclasses")
  
  def ACTION_COST(self, state : S, action : A, new_state : S) -> float:
    """

    Args:
      state: starting state
      action: action to do on the starting state
      new_state: the state you get after performing the action

    Returns:
      The cost of getting from the starting state to the new state whilst doing the given action
    """
    raise NotImplementedError("This method should be overridden by subclasses")
  
  def IS_GOAL(self, state : S) -> bool:
    """

    Args:
      state: The state you are checking

    Returns:
      True if the state is a goal state, False otherwise.
    """
    raise NotImplementedError("This method should be overridden by subclasses")

__all__ = ['SearchProblem', 'Heuristic', 'SearchStatus']