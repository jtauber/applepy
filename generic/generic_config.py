import inspect


class BaseConfig(object):
    LOCAL_HOST_IP = "127.0.0.1"


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
