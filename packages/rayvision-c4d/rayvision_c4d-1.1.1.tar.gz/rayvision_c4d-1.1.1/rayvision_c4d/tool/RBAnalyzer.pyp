# -*- coding=utf-8 -*-
# author: kanada
# the python version is py26/27/27x and py37/py39
import sys,os,c4d

version = int(c4d.GetC4DVersion())
print("version: %s" % version)
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

if version < 17000:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'python26'))
elif version < 20000:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'python27x'))
elif version < 23000:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'python27'))
elif version < 24000:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'python37'))
elif version < 2023200:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'python39'))
else:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'python310'))


def PluginMessage(id, data):
    if id==c4d.C4DPL_COMMANDLINEARGS:
        try:
            import RBAnalyzer
        finally:
            pass
        
        return True

    return False