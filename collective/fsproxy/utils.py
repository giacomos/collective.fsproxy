import os.path
import os
import stat

def cleanPath(path):
    """Cleanup a path to produce a normalized filesystem path.

    If possible a path is made relative to the INSTANCE_HOME
    """

    path=os.path.normpath(path)
    return path


def isDirectory(path):
    """Test if an absolute path refers to a directory.

    Unlike the os.path.isdir method this method will raise an exception if
    the file does not exist. This allows us to use a single stat(2) call
    to test both existance and directorishness.
    """
    mode=os.stat(path)[stat.ST_MODE]
    return stat.S_ISDIR(mode)

