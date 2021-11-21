# 异常类

class DatabaseException(Exception):
  pass

class ConnectException(DatabaseException):
  pass

class ParameterException(DatabaseException):
  pass