import argparse
from AppCtx import AppContext

"""
    config.yml - contains macro and generic settings, like paths to sources, remaker cfg etc...
    -init=COMPILER|CONFIG|ALL - creating/recreating config (yml), downloading/updating compiler executable
    
    -build_graphs - build graphs
    
    -src - specific source path
    -o - optimization level

    exe build -o1
    exe run -o0
"""

def getParser(ctx:AppContext,config=None):
    pathes = config.get('pathes',{})
    runtime = config.get('runtime',{})
    defines = config.get('defines',{})

    parser = argparse.ArgumentParser(
        prog="RBuilder",
        description="Compiler application",
        add_help=False)
    
    grp=parser.add_argument_group('Application options')
    
    grp.add_argument('-init',action='store_true',help='Initialize config')
    #grp.add_argument('-debug',action='store_true',help='Debug mode')
    grp.add_argument('-log',help='Enable logging to file',dest='logToFile',metavar='FILE')
    grp.add_argument("-verbose",help='Enable verbose logging',action='store_true',default=False,dest='verbose')
    grp.add_argument('-sdk',help="Change ReSDK path. This used for ReNode lib compiler",default=pathes.get('resdk_dir',".\\..\\"),dest='ReSDK_dir')
    
    sub = parser.add_subparsers(title='Process type',help='RBuilder process type',dest='actionType',metavar="PROCESS_TYPE")
    # ----------- build -----------
    p = sub.add_parser(name='build',aliases=['b','compile','make'],help='Build/compile application')
    p.add_argument('-src','-s',help='Source files for compiler. Default: %(default)s',dest='src',default=pathes.get('sources',"..\\src"),metavar='FILE')
    p.add_argument('-link','-l',help='Use source as simlink',action='store_true',dest='symlink')
    
    grp = p.add_argument_group("Compiler options")
    grp.add_argument('-iml',help='Debugger intermediate binary')
    grp.add_argument('-validate','-v',help='Validate preprocessor',action='store_true',dest='validate')
    grp = grp.add_mutually_exclusive_group(required=False)
    grp.add_argument('-o0',help='No optimization',action='store_false',dest='optimize')
    grp.add_argument('-o1',help='Optimization level 1',action='store_true',dest='optimize')
    grp.add_argument('-o2',help='Optimization level 2',action='store_true',dest='optimize')

    # ----------- run -----------
    p = sub.add_parser('run',aliases=['r','start','exec'],help='Run application')
    p.add_argument('-db',help='Create new database',dest='create_db',action='store_true')
    p.add_argument('-rptshow','-rpt',help="Show rpt content on rbuilder exit",type=bool,default=runtime['show_rpt'],dest="show_rpt")
    p.add_argument("-autoreload",'-ar','-r',help="Reload question on vm executed",default=runtime['auto_reload'],dest="auto_reload",action='store_true')
    p.add_argument('-def','-f',help="Define macro variable",nargs="+",metavar="MACRO_NAME",action="append",dest="macroDefines",default=[])
    #p._add_container_actions(cflags._container)
    #(p._add_action(act) for act in cflags._actions)

    #grp = parser.add_argument_group("Compiler options")
    #grp.add_argument('-src',help='Source files for compiler. Default: %(default)s',default=pathes.get('sources',"..\\src"),metavar='FILE')
    
    # grp = p.add_argument_group("Optimization options")
    # grp.add_argument('-o0',help='No optimization',action='store_false')
    # grp.add_argument('-o1',help='Optimization level 1',action='store_true')
    # grp.add_argument('-o2',help='Optimization level 2',action='store_true')

    # cflags = parser.add_mutually_exclusive_group()
    # cflags.add_argument('-o0',action='store_true',help='Optimization level 0')
    # cflags.add_argument('-o1',action='store_true',help='Optimization level 1')
    # cflags.add_argument('-o2',action='store_true',help='Optimization level 2')

    parser.add_argument('-help','-h',action='help',help='Show this help message and exit')


    return parser