"""Contains command line-related convenience methods."""

import getopt

def get_params(cmd_line_list, opt_list, mandatory, no_of_args = 0):
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
        if len(params.get(key, [])) == 0:
            raise ValueError('Parameter {0} is missing.'.format(key))
        if len(args) < no_of_args:
            raise ValueError('Not enough arguments.')
    return (params, args)
