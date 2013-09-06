"""
Copyright 2011-13 Attila Zseder
Email: zseder@gmail.com

This file is part of hunmisc project
url: https://github.com/zseder/hunmisc

hunmisc is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""



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
        config = dict(SafeConfigParser.items(self, nodes[0], raw, vars))
        path = nodes[0]

        # Now this is a pain. We have to clear the DEFAULT section, lest the
        # code below overwrites the options that have defaults. The reason is
        # that crappy ConfigParser does not have a method that enumerates only
        # the keys defined in particular section; the keys in the DEFAULT
        # section are always included.
        tmp_defaults = self._defaults
        self._defaults = {}

        for node in nodes[1:]:
            path = node if len(path) == 0 else path + '.' + node
            try:
                next_config = dict(SafeConfigParser.items(self, path, raw, vars))
                for key in self.options(path):
                    # Overwrite only the keys defined in the child section
                    config[key] = next_config[key]
            except ConfigParser.NoSectionError:
                pass

        self._defaults = tmp_defaults

        return config.iteritems()

