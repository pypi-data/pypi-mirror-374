"""
DIPPERpy versioning information will be here.
"""
try:
    from setuptools_scm import get_version
    __version__ = get_version(root='..', relative_to=__file__)
    print(__version__)
    version = __version__

except Exception:

    __version_usedate__ = True
    if __version_usedate__:
        __version_info__ = ('2025','8', '29')
    else:
        __version_info__ = ('0','0', '1')

    __version__ = '.'.join(__version_info__)
    version = __version__


