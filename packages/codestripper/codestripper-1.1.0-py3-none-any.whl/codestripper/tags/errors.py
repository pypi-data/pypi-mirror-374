class IgnoreFileError(Exception):
    """Error raised when the file should be ignored"""
    def __init__(self, tag):
        self.tag = tag

