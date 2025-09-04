
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from eis.claim.api.claim_partner_roles_api import ClaimPartnerRolesApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from eis.claim.api.claim_partner_roles_api import ClaimPartnerRolesApi
from eis.claim.api.claim_partners_api import ClaimPartnersApi
from eis.claim.api.claim_regulations_api import ClaimRegulationsApi
from eis.claim.api.claim_statuses_api import ClaimStatusesApi
from eis.claim.api.claims_api import ClaimsApi
from eis.claim.api.health_check_api import HealthCheckApi
from eis.claim.api.settlements_api import SettlementsApi
