
import ConfigParser
from ConfigParser import SafeConfigParser

class CascadingConfigParser(SafeConfigParser):
    """
    An extension to the ConfigParser format that enables cascading of properties.
    More specifically, section names in the format of <tt>parent.child</tt> are
    considered to be part of a section name tree whose root is @c DEFAULT.
    <tt>parent.child</tt> inherits all key-value mappings from @c parent.
    """
    def __init__(self, config_file=None, defaults=None, dict_type=None):
        if dict_type is not None:
            SafeConfigParser.__init__(self, defaults, dict_type)
        else:
            SafeConfigParser.__init__(self, defaults)
        if config_file is not None:
            self.read(config_file)

    def items(self, section, raw=False, vars=None):
        """
        Same as @c super.items(), but options from ancestors in the section
        tree are included in the result.
        """
        nodes = section.split('.')
        config = {}
        path = ''
        for node in nodes:
            path = node if len(path) == 0 else path + '.' + node
            try:
                config.update(SafeConfigParser.items(self, path, raw, vars))
            except ConfigParser.NoSectionError:
                pass
        return config

