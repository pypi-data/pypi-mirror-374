import traceback
import sys
import platform


try:
    from causara.optimization.Model import Model
    from causara.optimization.ObjectiveToPyomo.UserFunctions import numCommon, error, equal, norm, allDifferent, Types
    from causara.utils.utils_public import printInfos, printModels, printDatasets, deleteModel, deleteDataset, categorical, convert_to_pandas, create_key, store_key, create_shortcut
    from causara.optimization.Bounds import Bounds, DecisionVars
    from causara.optimization.Data import Data, Dataset
    from causara.optimization.User.Interface import Interface
    from causara.optimization.Analyzer import Analyzer
    import causara.optimization.Converters as Converters
    import causara.Demos as Demos
    from causara.optimization.GUI.main import GUI
    from causara.optimization.Solver.dev.tests import test_solvers
    from causara.utils.Plot import plot
    from causara.utils.Plot import plot_convergence
    from causara.utils.Plot import generate_convergence_data

    MINIMIZE = 1 # similar to GRB.MINIMIZE
    MAXIMIZE = -1 # similar to GRB.MAXIMIZE

    __all__ = [
        'GUI',
        'Model',
        'Types',
        'error',
        'allDifferent',
        'norm',
        'numCommon',
        'equal',
        'printInfos',
        'printModels',
        'printDatasets',
        'deleteModel',
        'deleteDataset',
        'convert_to_pandas',
        'categorical',
        'Bounds',
        'DecisionVars',
        'Data',
        'Dataset',
        'Interface',
        'create_key',
        'Analyzer',
        'Converters',
        'store_key',
        'create_shortcut',
        'Demos',
        'test_solvers',
        'MINIMIZE',
        'MAXIMIZE',
        'plot',
        'plot_convergence',
        'generate_convergence_data',
    ]

except:
    traceback.print_exc()
    print("\n\n")

    version = sys.version_info
    print(f"Current Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor in (9, 10, 11, 12):
        os_name = platform.system()
        if os_name in ["Windows", "Linux", "Darwin"]:
            traceback.print_exc()
        else:
            print(f"Operating System not recognized: {os_name}")
    else:
        print(f"Python version {version.major}.{version.minor} is not supported. Supported Python version: [3.9, 3.10, 3.11, 3.12]")






