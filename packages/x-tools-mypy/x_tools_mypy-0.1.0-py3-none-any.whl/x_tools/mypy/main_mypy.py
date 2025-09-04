""" Main entry point for the MyPy tool """
import sys
from mypy.api import run as mypy_api_run

from x_tools.utils.models.tp_file_path import get_path
from x_tools.utils.cfg_toml import TomlCfgs

from x_tools.utils.models.mdl_git_repos import TGitRepos, repos_all, repos_of_ebr, repos_of_osr    # noqa   pylint: disable=unused-import
from x_tools.utils.models.tp_file_path import TpFilePath    # , get_path, get_paths


def run_mypy_for_one_module(
        check_module: TpFilePath,
        inx: int = 0,
    ):
    print( f"\n\nvvv--- Checking module {inx}: {check_module} ----vvv" )
    stdout, stderr, exit_code = mypy_api_run( [str(check_module)] )
    if exit_code != 1:
        print( 'exit_code:', exit_code )
    if stderr:
        print( 'stderr:\n', stderr )
    print()

    return stdout


def run_mypy(
        root_dir: TpFilePath     ,
        check_modules: list[TpFilePath],
    ):
    """ Main entry point for the PyLnt tool
        AI: Create code that runs Mypy for all python packages and submodules received in check_modules and prints the output to stdout
    """
    print( "\n\nvvv===================== Run MyPy =====================vvv" )
    sys_path_orig = sys.path
    for inx, check_module in enumerate(check_modules, 1):

        if not check_module.startswith( root_dir ):
            module_path = get_path(root_dir, check_module)
        else:
            module_path = get_path(check_module)

        sys.path = sys_path_orig
        sys.path.append( module_path )   # Ex: r'c:\__My\__PRJ_Work\PyLint\db_monitor' )

        # ===== Check =====
        toml_cfg = TomlCfgs( module_path )
        mypy_stdout = run_mypy_for_one_module( module_path, inx=inx )

        wrn_cnt = 0
        for ln in mypy_stdout.splitlines():
            if toml_cfg.ignore_path(ln):
                continue
            # don't print last line  with MyPy summary
            if all( [ (substr in ln) for substr in ['Found', 'file (checked', 'source files'] ] ):
                continue
            wrn_cnt += 1

            ln = ln.replace( ': ', '~|~', 1 )
            ln1, ln2 = ln.split( '~|~', 1 )
            print( f'{ln1:<80} {ln2}' )

        print( f'\nTotal wrns: {wrn_cnt}' )


    # for module_path in check_modules:
    #     print(f"Checking: {module_path}")
    #     result = subprocess.run(
    #         ["mypy", str(module_path)],
    #         cwd=str(root_dir),
    #         capture_output=True,
    #         text=True
    #     )
    #     print(result.stdout)
    #     if result.stderr:
    #         print(result.stderr)
