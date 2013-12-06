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


"""Contains command line-related convenience methods."""

import getopt

def get_params(cmd_line_list, opt_list, mandatory, no_of_args=0):
    """Extracts the parameters and arguments from the command line. Throws a
    C{ValueError} if not all mandatory parameters are given values in the
    command line or if some arguments are not filled.
    @param cmd_line_list: sys.argv[1:]
    @param opt_list: the second parameter to getopt.getopt
    @param mandatory: the list of mandatory parameters
    @param no_of_args: the minimum number of arguments required.
    @return a tuple of (params, args)."""
    params = {}
    opts, args = getopt.getopt(cmd_line_list, opt_list)
    for key, value in opts:
        key = key[1:]
        vals = params.get(key, [])
        vals.append(value)
        params[key] = vals
    for key in mandatory:
        if key not in params:
            raise ValueError('Parameter {0} is missing.'.format(key))
        if len(args) < no_of_args:
            raise ValueError('Not enough arguments.')
    return (params, args)

def get_params_sing(cmd_line_list, opt_list, mandatory, no_of_args=0):
    """Same as C{get_params()}, but each parameter can only be specified once;
    hence, C{params[param]} is not a list, but a singular string."""
    params = {}
    opts, args = getopt.getopt(cmd_line_list, opt_list)
    for key, value in opts:
        params[key[1:]] = value
    for key in mandatory:
        if key not in params:
            raise ValueError('Parameter {0} is missing.'.format(key))
        if len(args) < no_of_args:
            raise ValueError('Not enough arguments.')
    return (params, args)
