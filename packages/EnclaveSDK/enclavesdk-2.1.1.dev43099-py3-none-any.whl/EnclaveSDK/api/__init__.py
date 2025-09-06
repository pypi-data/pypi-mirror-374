# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from EnclaveSDK.api.auth_api import AuthApi
    from EnclaveSDK.api.data_api import DataApi
    from EnclaveSDK.api.escrow_api import EscrowApi
    from EnclaveSDK.api.log_api import LogApi
    from EnclaveSDK.api.mlflow_api import MlflowApi
    from EnclaveSDK.api.report_api import ReportApi
    from EnclaveSDK.api.run_api import RunApi
    from EnclaveSDK.api.writeback_api import WritebackApi

else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from EnclaveSDK.api.auth_api import AuthApi
from EnclaveSDK.api.data_api import DataApi
from EnclaveSDK.api.escrow_api import EscrowApi
from EnclaveSDK.api.log_api import LogApi
from EnclaveSDK.api.mlflow_api import MlflowApi
from EnclaveSDK.api.report_api import ReportApi
from EnclaveSDK.api.run_api import RunApi
from EnclaveSDK.api.writeback_api import WritebackApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
