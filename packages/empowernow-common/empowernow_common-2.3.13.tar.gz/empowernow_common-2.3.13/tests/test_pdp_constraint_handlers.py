import pytest

from empowernow_common.authzen.client import EnhancedPDP, Constraint, ConstraintViolationError


@pytest.fixture
def epdp():
    return EnhancedPDP(
        base_url="https://pdp.example.com",
        client_id="client",
        client_secret="secret",
        token_url="https://pdp.example.com/token",
    )


@pytest.mark.asyncio
async def test_model_constraint_blocks_disallowed_model(epdp):
    request = {
        "resource": {"properties": {"model": "gpt-3.5-turbo"}},
        "context": {},
    }

    constraint = Constraint(
        id="model",
        type="model",
        parameters={"allow": ["gpt-4.1", "gpt-4o-mini"]},
    )

    with pytest.raises(ConstraintViolationError):
        await epdp._apply_constraints(request, [constraint])


@pytest.mark.asyncio
async def test_model_constraint_allows_permitted_model(epdp):
    request = {
        "resource": {"properties": {"model": "gpt-4o-mini"}},
        "context": {},
    }

    constraint = Constraint(
        id="model",
        type="model",
        parameters={"allow": ["gpt-4.1", "gpt-4o-mini"]},
    )

    # Should not raise
    result = await epdp._apply_constraints(request, [constraint])
    assert result == request


