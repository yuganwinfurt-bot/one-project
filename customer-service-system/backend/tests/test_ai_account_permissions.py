from types import SimpleNamespace

import pytest

from app.common.exceptions import BusinessException
from app.services.business_agent_service import require_business


@pytest.mark.parametrize('resource', ['users', 'members', 'customer', 'customers', 'staff', 'admin', 'roles', 'permissions', 'password'])
@pytest.mark.parametrize('role', ['admin', 'user'])
def test_ai_cannot_modify_account_resources_even_for_an_administrator(resource, role):
    with pytest.raises(BusinessException) as exc:
        require_business(None, SimpleNamespace(role=role, status=1), resource)
    assert exc.value.code == 403
