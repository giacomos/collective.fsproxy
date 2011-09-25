from Products.validation.interfaces.IValidator import IValidator
from collective.fsproxy.utils import cleanPath
from collective.fsproxy.utils import isDirectory
from zope.interface import implements

class isValidFilesystemPath(object):
    implements(IValidator)

    name = "isValidFilesystemPath"
    title = "Check if a filesystem path is valid"
    description = """Check if a filesystem path is syntactly correct and
                     refers to an existing directory."""

    def __init__(self, name=None):
        if name is not None:
            self.name=name
        

    def __call__(self, value, *args, **kwargs):
        path=cleanPath(value)

        try:
            if not isDirectory(path):
                return "Not a directory"
        except OSError, e:
            return e.strerror

        return 1

class isValidFilesystemFile(object):
    implements(IValidator)

    name = "isValidFilesystemFile"
    title = "Check if a filesystem path is valid"
    description = """Check if a filesystem path is syntactly correct and
                     refers to an existing directory."""

    def __init__(self, name=None):
        if name is not None:
            self.name=name
        

    def __call__(self, value, *args, **kwargs):
        path=cleanPath(value)

        try:
            if isDirectory(path):
                return "Not a file"
        except OSError, e:
            return e.strerror

        return 1
