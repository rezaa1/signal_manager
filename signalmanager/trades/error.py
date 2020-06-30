
class Error(Exception):
   """Base class for other exceptions"""
   pass

class InstrumentIsNotTradeable(Error):
   """Raised when the Instrument is marked as do not trade"""
   pass

class InstrumentIsNotFound(Error):
   """Raised when the instrument not found in list"""
   pass

