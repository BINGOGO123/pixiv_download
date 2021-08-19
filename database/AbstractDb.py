from abc import ABCMeta, abstractmethod

class AbstractDb(metaclass=ABCMeta):
  @abstractmethod
  def execute(self, sql):
    pass

  @abstractmethod
  def escape_execute(self, sql, *data):
    pass