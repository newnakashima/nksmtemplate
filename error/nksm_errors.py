class IfClauseError(Exception):
    """Raised when if-clauses is invalid"""
    pass

class NotBooleanError(Exception):
    """Raised when if-condition is not Boolean"""
    pass
