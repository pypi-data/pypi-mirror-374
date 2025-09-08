# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from pyesi_openapi.api.alliance_api import AllianceApi
    from pyesi_openapi.api.assets_api import AssetsApi
    from pyesi_openapi.api.calendar_api import CalendarApi
    from pyesi_openapi.api.character_api import CharacterApi
    from pyesi_openapi.api.clones_api import ClonesApi
    from pyesi_openapi.api.contacts_api import ContactsApi
    from pyesi_openapi.api.contracts_api import ContractsApi
    from pyesi_openapi.api.corporation_api import CorporationApi
    from pyesi_openapi.api.dogma_api import DogmaApi
    from pyesi_openapi.api.faction_warfare_api import FactionWarfareApi
    from pyesi_openapi.api.fittings_api import FittingsApi
    from pyesi_openapi.api.fleets_api import FleetsApi
    from pyesi_openapi.api.incursions_api import IncursionsApi
    from pyesi_openapi.api.industry_api import IndustryApi
    from pyesi_openapi.api.insurance_api import InsuranceApi
    from pyesi_openapi.api.killmails_api import KillmailsApi
    from pyesi_openapi.api.location_api import LocationApi
    from pyesi_openapi.api.loyalty_api import LoyaltyApi
    from pyesi_openapi.api.mail_api import MailApi
    from pyesi_openapi.api.market_api import MarketApi
    from pyesi_openapi.api.planetary_interaction_api import PlanetaryInteractionApi
    from pyesi_openapi.api.routes_api import RoutesApi
    from pyesi_openapi.api.search_api import SearchApi
    from pyesi_openapi.api.skills_api import SkillsApi
    from pyesi_openapi.api.sovereignty_api import SovereigntyApi
    from pyesi_openapi.api.status_api import StatusApi
    from pyesi_openapi.api.universe_api import UniverseApi
    from pyesi_openapi.api.user_interface_api import UserInterfaceApi
    from pyesi_openapi.api.wallet_api import WalletApi
    from pyesi_openapi.api.wars_api import WarsApi
    
else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from pyesi_openapi.api.alliance_api import AllianceApi
from pyesi_openapi.api.assets_api import AssetsApi
from pyesi_openapi.api.calendar_api import CalendarApi
from pyesi_openapi.api.character_api import CharacterApi
from pyesi_openapi.api.clones_api import ClonesApi
from pyesi_openapi.api.contacts_api import ContactsApi
from pyesi_openapi.api.contracts_api import ContractsApi
from pyesi_openapi.api.corporation_api import CorporationApi
from pyesi_openapi.api.dogma_api import DogmaApi
from pyesi_openapi.api.faction_warfare_api import FactionWarfareApi
from pyesi_openapi.api.fittings_api import FittingsApi
from pyesi_openapi.api.fleets_api import FleetsApi
from pyesi_openapi.api.incursions_api import IncursionsApi
from pyesi_openapi.api.industry_api import IndustryApi
from pyesi_openapi.api.insurance_api import InsuranceApi
from pyesi_openapi.api.killmails_api import KillmailsApi
from pyesi_openapi.api.location_api import LocationApi
from pyesi_openapi.api.loyalty_api import LoyaltyApi
from pyesi_openapi.api.mail_api import MailApi
from pyesi_openapi.api.market_api import MarketApi
from pyesi_openapi.api.planetary_interaction_api import PlanetaryInteractionApi
from pyesi_openapi.api.routes_api import RoutesApi
from pyesi_openapi.api.search_api import SearchApi
from pyesi_openapi.api.skills_api import SkillsApi
from pyesi_openapi.api.sovereignty_api import SovereigntyApi
from pyesi_openapi.api.status_api import StatusApi
from pyesi_openapi.api.universe_api import UniverseApi
from pyesi_openapi.api.user_interface_api import UserInterfaceApi
from pyesi_openapi.api.wallet_api import WalletApi
from pyesi_openapi.api.wars_api import WarsApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
