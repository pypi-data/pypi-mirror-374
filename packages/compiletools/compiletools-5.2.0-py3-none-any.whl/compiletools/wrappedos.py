""" Wrap and memoize a variety of os calls """
import os
import shutil
import functools


@functools.lru_cache(maxsize=None)
def getmtime(realpath):
    """ Cached version of os.path.getmtime """
    return os.path.getmtime(realpath)


@functools.lru_cache(maxsize=None)
def isfile(trialpath):
    """ Cached version of os.path.isfile """
    return os.path.isfile(trialpath)


@functools.lru_cache(maxsize=None)
def isdir(trialpath):
    """ Cached version of os.path.isdir """
    return os.path.isdir(trialpath)


@functools.lru_cache(maxsize=None)
def realpath(trialpath):
    """ Cache os.path.realpath """
    # Note: We can't raise an exception on file non-existence
    # because this is sometimes called in order to create the file.
    rp = os.path.realpath(trialpath)
    return rp


@functools.lru_cache(maxsize=None)
def dirname(trialpath):
    """ A cached verion of os.path.dirname """
    return os.path.dirname(trialpath)


@functools.lru_cache(maxsize=None)
def basename(trialpath):
    """ A cached version of os.path.basename """
    return os.path.basename(trialpath)


def isc(trialpath):
    """ Is the given file a C file ? """
    return os.path.splitext(trialpath)[1] == ".c"



def copy(src, dest):
    """ copy the src to the dest and print any errors """
    try:
        shutil.copy2(src, dest)
    except IOError as err:
        print("Unable to copy file {}".format(err))


def clear_cache():
    getmtime.cache_clear()
    isfile.cache_clear()
    isdir.cache_clear()
    realpath.cache_clear()
    dirname.cache_clear()
    basename.cache_clear()
