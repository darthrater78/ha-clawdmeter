"""Test the Clawdmeter sensor and binary sensor platforms."""

from unittest.mock import patch

from freezegun.api import FrozenDateTimeFactory
from homeassistant.const import EntityCategory, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from homeassistant.loader import async_get_integration
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    snapshot_platform,
)
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from syrupy.assertion import SnapshotAssertion

from custom_components.clawdmeter.const import (
    DEPRECATED_MODEL_SENSORS,
    DOMAIN,
    USAGE_ENDPOINT,
)

from . import setup_integration

DIAGNOSTIC = "sensor.claude_corgan_max_session_usage"
COMPUTED = "sensor.claude_corgan_max_burn_rate_5_min"
ACCOUNT = "sensor.claude_corgan_max_account"
PLAN = "sensor.claude_corgan_max_plan"
USAGE_RATE = "sensor.claude_corgan_max_usage_rate"


@pytest.mark.usefixtures("mock_usage", "entity_registry_enabled_by_default")
@pytest.mark.parametrize("platform", [Platform.SENSOR, Platform.BINARY_SENSOR])
async def test_all_entities(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    mock_config_entry: MockConfigEntry,
    freezer: FrozenDateTimeFactory,
    platform: Platform,
) -> None:
    """Test all entities are created and match the snapshot.

    This pins entity structure and the single-poll states (derived rolling-window
    metrics are still unknown here); their computed values are covered in
    test_coordinator.
    """
    freezer.move_to("2026-06-25T12:00:00+00:00")
    with patch("custom_components.clawdmeter.PLATFORMS", [platform]):
        await setup_integration(hass, mock_config_entry)

    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)


@pytest.mark.usefixtures("mock_usage")
async def test_account_entities_and_categories(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test the account/plan sensors and the diagnostic vs computed split."""
    await setup_integration(hass, mock_config_entry)

    assert hass.states.get(ACCOUNT).state == "Corgan"
    assert hass.states.get(PLAN).state == "Max"

    # Raw API values (incl. account/plan) are diagnostics.
    assert (
        entity_registry.async_get(ACCOUNT).entity_category is EntityCategory.DIAGNOSTIC
    )
    assert entity_registry.async_get(PLAN).entity_category is EntityCategory.DIAGNOSTIC
    assert (
        entity_registry.async_get(DIAGNOSTIC).entity_category
        is EntityCategory.DIAGNOSTIC
    )
    # Computed projections are primary sensors (no category).
    assert entity_registry.async_get(COMPUTED).entity_category is None
    assert entity_registry.async_get(USAGE_RATE).entity_category is None


@pytest.mark.usefixtures("mock_usage")
async def test_device_reports_integration_version(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test the account device exposes the integration version as sw_version."""
    await setup_integration(hass, mock_config_entry)

    integration = await async_get_integration(hass, DOMAIN)
    device = device_registry.async_get_device(
        identifiers={(DOMAIN, mock_config_entry.entry_id)}
    )
    assert device is not None
    assert device.sw_version == str(integration.version)


def _enable_deprecated_sensor(
    entity_registry: er.EntityRegistry, entry: MockConfigEntry, key: str
) -> str:
    """Pre-register a deprecated sensor as enabled, as on an existing install."""
    return entity_registry.async_get_or_create(
        Platform.SENSOR,
        DOMAIN,
        f"{entry.entry_id}_{key}",
        suggested_object_id=f"claude_corgan_max_{key}",
        config_entry=entry,
    ).entity_id


@pytest.mark.usefixtures("mock_usage")
async def test_deprecated_sensors_disabled_by_default(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    issue_registry: ir.IssueRegistry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test a fresh install creates the per-model sensors disabled, with no issue."""
    await setup_integration(hass, mock_config_entry)

    for key in DEPRECATED_MODEL_SENSORS:
        entity_id = entity_registry.async_get_entity_id(
            Platform.SENSOR, DOMAIN, f"{mock_config_entry.entry_id}_{key}"
        )
        assert entity_id is not None
        entry = entity_registry.async_get(entity_id)
        assert entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION
    assert len(issue_registry.issues) == 0


@pytest.mark.usefixtures("mock_usage")
async def test_deprecated_sensor_enabled_raises_issue(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    issue_registry: ir.IssueRegistry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test an enabled per-model sensor on an install without data raises an issue."""
    mock_config_entry.add_to_hass(hass)
    entity_id = _enable_deprecated_sensor(
        entity_registry, mock_config_entry, "sonnet_usage"
    )
    await setup_integration(hass, mock_config_entry)

    issue = issue_registry.async_get_issue(
        DOMAIN, f"deprecated_model_sensors_{mock_config_entry.entry_id}"
    )
    assert issue is not None
    assert issue.translation_key == "deprecated_model_sensors"
    assert entity_id in issue.translation_placeholders["entities"]

    # Disabling the sensor and reloading clears the issue.
    entity_registry.async_update_entity(
        entity_id, disabled_by=er.RegistryEntryDisabler.USER
    )
    await hass.config_entries.async_reload(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert len(issue_registry.issues) == 0


async def test_deprecated_sensor_with_data_raises_no_issue(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    entity_registry: er.EntityRegistry,
    issue_registry: ir.IssueRegistry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test an account still receiving per-model windows is not nagged."""
    aioclient_mock.get(USAGE_ENDPOINT, json={"seven_day_opus": {"utilization": 8}})
    mock_config_entry.add_to_hass(hass)
    _enable_deprecated_sensor(entity_registry, mock_config_entry, "opus_usage")
    await setup_integration(hass, mock_config_entry)

    assert len(issue_registry.issues) == 0
