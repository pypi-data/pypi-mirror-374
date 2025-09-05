import importlib.util
from subprocess import Popen,CREATE_NEW_CONSOLE
import sys,os

def install(command):
    Popen(
        command,
        creationflags=CREATE_NEW_CONSOLE,
        shell=False if os.name=='nt' else True
    ).wait()

def installPip():
    from JooFunc.pip_in import main
    main()
def installPackages(**libs):
    try: import pip
    except:
        try:
            installPip()
            import pip
        except: print('Faild To Install Pip ... Exit') ; sys.exit(0)
    try: import colorama
    except:
        try:
            print('Installing Colorama ...',end='\r')
            install('pip install colorama')
            import colorama
            print('Done')
        except: print('Faild To Install colorama ... Exit') ; sys.exit(0)

    from JooFunc.colors import fr,fw,fg,fc
    packageError = []
    for lib,pipLib in libs.items():
        try:
            exec(f'import {lib}')
            print(f'\r{fc}{lib}{fw} ... {fg} OK             {fw}')
        except:
            try:
                if (spec:=importlib.util.find_spec(lib)) is not None:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[lib] = module
                    spec.loader.exec_module(module)
                elif not lib in sys.modules:
                    print(f'\r{fc}{lib}{fw} ... {fr}Try To Install{fw}',end='')
                    install('pip install '+pipLib)
                    exec(f'import {lib}')
                    print(f'\r{fc}{lib}{fw} ... {fg}OK             {fw}')
            except:
                print(f'\r{fc}{lib}{fw} ... {fr}Faild to Import{fw}')
                packageError.append(libs[lib])
    if packageError:
        print(f'{fr}Please , Install Missed Modules {fw}:- {fr}')
        [print(f'{fw}Package Name: {fg}pip install {fc}{pipLib}{fw}') for pipLib in packageError]
        print(fw)
        sys.exit(0)
