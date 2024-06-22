import argparse

"""
    config.yml - contains macro and generic settings, like paths to sources, remaker cfg etc...
    -init=COMPILER|CONFIG|ALL - creating/recreating config (yml), downloading/updating compiler executable
    
    -build_graphs - build graphs
    
    -src - specific source path
    -o - optimization level

    exe build -o1
    exe run -o0
"""

def getParser(config=None):

    pathes = config.get('pathes',{})
    runtime = config.get('runtime',{})
    defines = config.get('defines',{})

    parser = argparse.ArgumentParser(
        prog="builder_application",
        description="Compiler application",
        add_help=False)
    
    grp=parser.add_argument_group('Application options')
    
    grp.add_argument('-init',action='store_true',help='Initialize config')
    #grp.add_argument('-debug',action='store_true',help='Debug mode')
    grp.add_argument('-log',help='Enable logging')
    
    sub = parser.add_subparsers(title='Process type',help='subparser helptext',dest='actionType',metavar="PROCESS_TYPE")
    p = sub.add_parser('build',help='Build application')
    

    p = sub.add_parser('run',help='Run application')
    #p._add_container_actions(cflags._container)
    #(p._add_action(act) for act in cflags._actions)

    grp = parser.add_argument_group("Compiler options")
    grp.add_argument('-src',help='Source files for compiler. Default: %(default)s',default=pathes.get('sources',"..\\src"),metavar='FILE')
    
    grp = p.add_argument_group("Optimization options")
    grp.add_argument('-o0',help='No optimization',action='store_false')
    grp.add_argument('-o1',help='Optimization level 1',action='store_true')
    grp.add_argument('-o2',help='Optimization level 2',action='store_true')

    # cflags = parser.add_mutually_exclusive_group()
    # cflags.add_argument('-o0',action='store_true',help='Optimization level 0')
    # cflags.add_argument('-o1',action='store_true',help='Optimization level 1')
    # cflags.add_argument('-o2',action='store_true',help='Optimization level 2')

    parser.add_argument('-help','-h',action='help',help='Show this help message and exit')


    return parser