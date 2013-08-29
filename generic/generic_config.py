import inspect
import importlib
import os


class BaseConfig(object):
    LOCAL_HOST_IP = "127.0.0.1"

    def get_cpu_script(self):
        cpu_module = importlib.import_module(self.CPU_MODULE)
        cpu_module_path = cpu_module.__file__

        # FIXME: Use .py instead of .pyc (if exist)
        cpu_module_path = os.path.splitext(cpu_module_path)[0] + ".py"

        return cpu_module_path

    def print_debug_info(self):
        print "Config: '%s'" % self.__class__.__name__

        for name, value in inspect.getmembers(self): # , inspect.isdatadescriptor):
            if name.startswith("_"):
                continue
#             print name, type(value)
            if not isinstance(value, (int, basestring, list, tuple, dict)):
                continue
            if isinstance(value, (int,)):
                print "%20s = %-4s (in hex: %7s)" % (
                    name, value, repr(hex(value))
                )
            else:
                print "%20s = %s" % (name, value)
