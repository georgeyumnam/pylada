""" Sets general lada parameters. """
readonly_jobparams = False
""" Whether items can be modified in parallel using attribute syntax. """
naked_end = True
""" Whether last item is returned as is or wrapped in ForwardingDict. """
only_existing_jobparams = True
""" Whether attributes can be added or only modified. """
unix_re  = True
""" If True, then all regex matching is done using unix-command-line patterns. """
auto_import_modules = []
""" Modules to import when starting ipython. """
try_import_matplotlib = False
""" Whether to try and import matplotlib or not. 

    It seems that matplotlib is installed hopper, with the dire consequences
    one expects from Cray.
"""