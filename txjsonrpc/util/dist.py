import os


legalReSTFiles = [
    "README.rst",
    "TODO",
    "DEPENDENCIES",
    ]


def setup(*args, **kwds):
    """
    Compatibility wrapper.
    """
    try:
        from setuptools import setup
    except ImportError:
        from distutils.core import setup
    return setup(*args, **kwds)


def findPackages(library_name):
    """
    Compatibility wrapper.

    Taken from storm setup.py.
    """
    try:
        from setuptools import find_packages
        return find_packages()
    except ImportError:
        pass
    packages = []
    for directory, subdirectories, files in os.walk(library_name):
        if "__init__.py" in files:
            packages.append(directory.replace(os.sep, "."))
    return packages


def hasDocutils():
    """
    Check to see if docutils is installed.
    """
    try:
        import docutils
        return True
    except ImportError:
        return False


def _validateReST(text):
    """
    Make sure that the given ReST text is valid.

    Taken from Zope Corp's zc.twist setup.py.
    """
    import docutils.utils
    import docutils.parsers.rst
    import StringIO

    doc = docutils.utils.new_document("validator")
    # our desired settings
    doc.reporter.halt_level = 5
    doc.reporter.report_level = 1
    stream = doc.reporter.stream = StringIO.StringIO()
    # docutils buglets (?)
    doc.settings.tab_width = 2
    doc.settings.pep_references = doc.settings.rfc_references = False
    doc.settings.trim_footnote_reference_space = None
    # and we're off...
    parser = docutils.parsers.rst.Parser()
    parser.parse(text, doc)
    return stream.getvalue()


def validateReST(text):
    """
    A wrapper that ensafens the validation for pythons that are not embiggened
    with docutils.
    """
    if hasDocutils():
        return _validateReST(text)
    print " *** No docutils; can't validate ReST."
    return ""


def catReST(*args, **kwds):
    """
    Concatenate the contents of one or more ReST files.

    Taken from Zope Corp's zc.twist setup.py.
    """
    # note: distutils explicitly disallows unicode for setup values :-/
    # http://docs.python.org/dist/meta-data.html
    tmp = []
    for arg in args:
        if arg in legalReSTFiles or arg.endswith(".txt"):
            f = open(os.path.join(*arg.split("/")))
            tmp.append(f.read())
            f.close()
            tmp.append("\n\n")
        else:
            print "Warning: '%s' not a legal ReST filename."
            tmp.append(arg)
    if len(tmp) == 1:
        res = tmp[0]
    else:
        res = "".join(tmp)
    out = kwds.get("out")
    stop_on_errors = kwds.get("stop_on_errors")
    if out is True:
        out = "CHECK_THIS_BEFORE_UPLOAD.txt"
    if out:
        f = open(out, "w")
        f.write(res)
        f.close()
        report = validateReST(res)
        if report:
            print report
            if stop_on_errors:
                print "ReST validation error"
                print
                print "See the following:"
                print "  http://docutils.sourceforge.net/docs/user/rst/cheatsheet.txt"
                print "  http://docutils.sourceforge.net/docs/user/rst/quickstart.html"
                print
                raise ValueError("ReST validation error")
    return res

