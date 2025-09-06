# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from kalshi_api_v2_external.api.api_keys_api import ApiKeysApi
    from kalshi_api_v2_external.api.communications_api import CommunicationsApi
    from kalshi_api_v2_external.api.events_api import EventsApi
    from kalshi_api_v2_external.api.exchange_api import ExchangeApi
    from kalshi_api_v2_external.api.markets_api import MarketsApi
    from kalshi_api_v2_external.api.milestones_api import MilestonesApi
    from kalshi_api_v2_external.api.multivariate_collections_api import MultivariateCollectionsApi
    from kalshi_api_v2_external.api.portfolio_api import PortfolioApi
    from kalshi_api_v2_external.api.series_api import SeriesApi
    from kalshi_api_v2_external.api.structured_targets_api import StructuredTargetsApi
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from kalshi_api_v2_external.api.api_keys_api import ApiKeysApi
from kalshi_api_v2_external.api.communications_api import CommunicationsApi
from kalshi_api_v2_external.api.events_api import EventsApi
from kalshi_api_v2_external.api.exchange_api import ExchangeApi
from kalshi_api_v2_external.api.markets_api import MarketsApi
from kalshi_api_v2_external.api.milestones_api import MilestonesApi
from kalshi_api_v2_external.api.multivariate_collections_api import MultivariateCollectionsApi
from kalshi_api_v2_external.api.portfolio_api import PortfolioApi
from kalshi_api_v2_external.api.series_api import SeriesApi
from kalshi_api_v2_external.api.structured_targets_api import StructuredTargetsApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
