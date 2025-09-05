"""Ohme API library."""

import logging
import asyncio
import json
from time import time
from enum import Enum
from typing import Any, Optional, Self, Mapping
from dataclasses import dataclass
import datetime
import aiohttp
from .utils import time_next_occurs, ChargeSlot, slot_list, vehicle_to_name
from .const import VERSION, GOOGLE_API_KEY

_LOGGER = logging.getLogger(__name__)


class ChargerStatus(Enum):
    """Charger state enum."""

    UNPLUGGED = "unplugged"
    PENDING_APPROVAL = "pending_approval"
    CHARGING = "charging"
    PLUGGED_IN = "plugged_in"
    PAUSED = "paused"
    FINISHED = "finished"


class ChargerMode(Enum):
    """Charger mode enum."""

    SMART_CHARGE = "smart_charge"
    MAX_CHARGE = "max_charge"
    PAUSED = "paused"


@dataclass
class ChargerPower:
    """Dataclass for reporting power status of charger."""

    watts: float
    amps: float
    volts: int | None
    ct_amps: float


class OhmeApiClient:
    """API client for Ohme EV chargers."""

    def __init__(
        self, email: str, password: str, session: Optional[aiohttp.ClientSession] = None
    ) -> None:
        if email is None or password is None:
            raise AuthException("Credentials not provided")

        # Credentials from configuration
        self.email = email
        self._password = password

        # Charger and its capabilities
        self.device_info: dict[str, Any] = {}
        self._charge_session: dict[str, Any] = {}
        self._advanced_settings: dict[str, Any] = {}
        self._next_session: dict[str, Any] = {}
        self._cars: list[Any] = []

        self.energy: float = 0.0
        self.battery: int = 0

        self._capabilities: dict[str, bool | str | list[str]] = {}
        self._configuration: dict[str, bool | str] = {}
        self.ct_connected: bool = False
        self.cap_available: bool = True
        self.cap_enabled: bool = False
        self.solar_capable: bool = False

        # Authentication
        self._token_birth: float = 0.0
        self._token: str | None = None
        self._refresh_token: str | None = None

        # User info
        self.serial = ""

        # Sessions
        self._session = session
        self._close_session = False
        self._timeout = 10
        self._last_rule: dict[str, Any] = {}

    # Auth methods

    async def async_login(self) -> bool:
        """Refresh the user auth token from the stored credentials."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        async with asyncio.timeout(self._timeout):
            async with self._session.post(
                f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={GOOGLE_API_KEY}",
                data={
                    "email": self.email,
                    "password": self._password,
                    "returnSecureToken": True,
                },
            ) as resp:
                if resp.status != 200:
                    raise AuthException("Incorrect credentials")

                resp_json = await resp.json()
                self._token_birth = time()
                self._token = resp_json["idToken"]
                self._refresh_token = resp_json["refreshToken"]
                return True
        raise AuthException("Incorrect credentials")

    async def _async_refresh_session(self) -> bool:
        """Refresh auth token if needed."""
        if self._token is None:
            return await self.async_login()

        # Don't refresh token unless its over 45 mins old
        if time() - self._token_birth < 2700:
            return True

        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        async with asyncio.timeout(self._timeout):
            async with self._session.post(
                f"https://securetoken.googleapis.com/v1/token?key={GOOGLE_API_KEY}",
                data={
                    "grantType": "refresh_token",
                    "refreshToken": self._refresh_token,
                },
            ) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    msg = f"Ohme auth refresh error: {text}"
                    _LOGGER.error(msg)
                    raise AuthException(msg)

                resp_json = await resp.json()
                self._token_birth = time()
                self._token = resp_json["id_token"]
                self._refresh_token = resp_json["refresh_token"]
                return True

    # Internal methods

    async def _handle_api_error(self, url: str, resp: aiohttp.ClientResponse):
        """Raise an exception if API response failed."""
        if resp.status != 200:
            text = await resp.text()
            msg = f"Ohme API response error: {url}, {resp.status}; {text}"
            _LOGGER.error(msg)
            raise ApiException(msg)

    async def _make_request(
        self,
        method: str,
        url: str,
        data: Optional[Mapping[str, str | bool]] = None,
        skip_json: bool = False,
    ):
        """Make an HTTP request."""
        await self._async_refresh_session()

        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        async with asyncio.timeout(self._timeout):
            async with self._session.request(
                method=method,
                url=f"https://api.ohme.io{url}",
                data=json.dumps(data) if data and method in {"PUT", "POST"} else data,
                headers={
                    "Authorization": f"Firebase {self._token}",
                    "Content-Type": "application/json",
                    "User-Agent": f"ohmepy/{VERSION}",
                },
            ) as resp:
                _LOGGER.debug(
                    "%s request to %s, status code %s", method, url, resp.status
                )
                await self._handle_api_error(url, resp)

                if skip_json and method == "POST":
                    return await resp.text()

                return await resp.json() if method != "PUT" else True

    def _charge_in_progress(self) -> bool:
        """Is a charge in progress? Used to determine if schedule or session should be adjusted."""
        return (
            self.status is not ChargerStatus.UNPLUGGED
            and self.status is not ChargerStatus.PENDING_APPROVAL
        )

    # Simple getters

    def is_capable(self, capability: str) -> bool:
        """Return whether or not this model has a given capability."""
        return bool(self._capabilities[capability])

    def configuration_value(self, value: str) -> bool:
        """Return a boolean configuration value."""
        return bool(self._configuration.get(value))

    @property
    def status(self) -> ChargerStatus:
        """Return status from enum."""
        if self._charge_session["mode"] == "PENDING_APPROVAL":
            return ChargerStatus.PENDING_APPROVAL
        elif self._charge_session["mode"] == "DISCONNECTED":
            return ChargerStatus.UNPLUGGED
        elif self._charge_session["mode"] == "STOPPED":
            return ChargerStatus.PAUSED
        elif self._charge_session["mode"] == "FINISHED_CHARGE":
            return ChargerStatus.FINISHED
        elif (
            self._charge_session.get("power")
            and self._charge_session["power"].get("watt", 0) > 0
        ):
            return ChargerStatus.CHARGING
        else:
            return ChargerStatus.PLUGGED_IN

    @property
    def mode(self) -> Optional[ChargerMode]:
        """Return status from enum."""
        if self._charge_session["mode"] == "SMART_CHARGE":
            return ChargerMode.SMART_CHARGE
        elif self._charge_session["mode"] == "MAX_CHARGE":
            return ChargerMode.MAX_CHARGE
        elif self._charge_session["mode"] == "STOPPED":
            return ChargerMode.PAUSED

        return None

    @property
    def max_charge(self) -> bool:
        """Get if max charge is enabled."""
        return self._charge_session.get("mode") == "MAX_CHARGE"

    @property
    def available(self) -> bool:
        """CT reading."""
        return self._advanced_settings.get("online", False)

    @property
    def power(self) -> ChargerPower:
        """Return all power readings."""

        charge_power = self._charge_session.get("power") or {}
        return ChargerPower(
            watts=charge_power.get("watt", 0),
            amps=charge_power.get("amp", 0),
            volts=charge_power.get("volt", None),
            ct_amps=self._advanced_settings.get("clampAmps", 0),
        )

    @property
    def target_soc(self) -> int:
        """Target state of charge."""
        if (
            self.status is ChargerStatus.PAUSED
            and self._charge_session.get("suspendedRule") is not None
        ):
            return self._charge_session.get("suspendedRule", {}).get("targetPercent", 0)
        elif self._charge_in_progress():
            return int(self._charge_session["appliedRule"]["targetPercent"])

        return int(self._next_session.get("targetPercent", 0))

    @property
    def target_time(self) -> tuple[int, int]:
        """Target state of charge."""
        if self._charge_in_progress():
            target = int(self._charge_session["appliedRule"]["targetTime"])
        else:
            target = int(self._next_session.get("targetTime", 0))

        return (target // 3600, (target % 3600) // 60)

    @property
    def preconditioning(self) -> int:
        """Preconditioning time."""
        if self._charge_in_progress():
            if self._last_rule.get("preconditioningEnabled"):
                return int(self._last_rule.get("preconditionLengthMins", 0))
        else:
            if self._next_session.get("preconditioningEnabled"):
                return int(self._next_session.get("preconditionLengthMins", 0))

        return 0

    @property
    def slots(self) -> list[ChargeSlot]:
        """Slot list."""
        return slot_list(self._charge_session)

    @property
    def next_slot_start(self) -> datetime.datetime | None:
        """Next slot start."""
        return min(
            (
                slot.start
                for slot in self.slots
                if slot.start > datetime.datetime.now().astimezone()
            ),
            default=None,
        )

    @property
    def next_slot_end(self) -> datetime.datetime | None:
        """Next slot start."""
        return min(
            (
                slot.end
                for slot in self.slots
                if slot.end > datetime.datetime.now().astimezone()
            ),
            default=None,
        )

    @property
    def vehicles(self) -> list[str]:
        """Return a list of vehicle names."""
        output = []
        for vehicle in self._cars:
            output.append(vehicle_to_name(vehicle))
        return output

    @property
    def current_vehicle(self) -> Optional[str]:
        """Returns the name of the currently selected vehicle."""
        # The selected vehicle is the first one in this list
        if len(self._cars) > 0:
            return vehicle_to_name(self._cars[0])
        return None

    # Push methods

    async def async_pause_charge(self) -> bool:
        """Pause an ongoing charge"""
        result = await self._make_request(
            "POST", f"/v1/chargeSessions/{self.serial}/stop", skip_json=True
        )
        return bool(result)

    async def async_resume_charge(self) -> bool:
        """Resume a paused charge"""
        result = await self._make_request(
            "POST", f"/v1/chargeSessions/{self.serial}/resume", skip_json=True
        )
        return bool(result)

    async def async_approve_charge(self) -> bool:
        """Approve a charge"""
        result = await self._make_request(
            "PUT", f"/v1/chargeSessions/{self.serial}/approve?approve=true"
        )
        return bool(result)

    async def async_max_charge(self, state: bool = True) -> bool:
        """Enable max charge"""
        result = await self._make_request(
            "PUT",
            f"/v1/chargeSessions/{self.serial}/rule?maxCharge=" + str(state).lower(),
        )
        return bool(result)

    async def async_set_mode(self, mode: ChargerMode | str) -> None:
        """Set charger mode."""
        if isinstance(mode, str):
            mode = ChargerMode(mode)

        if mode is ChargerMode.MAX_CHARGE:
            await self.async_max_charge(True)
        elif mode is ChargerMode.SMART_CHARGE:
            await self.async_max_charge(False)
        elif mode is ChargerMode.PAUSED:
            await self.async_pause_charge()

    async def async_apply_session_rule(
        self,
        max_price: Optional[float] = None,
        target_time: Optional[tuple[int, int]] = None,
        target_percent: Optional[int] = None,
        pre_condition: Optional[bool] = None,
        pre_condition_length: Optional[int] = None,
    ) -> bool:
        """Apply rule to ongoing charge/stop max charge."""
        # Check every property. If we've provided it, use that. If not, use the existing.
        if max_price is None:
            if (
                "settings" in self._last_rule
                and self._last_rule["settings"] is not None
                and len(self._last_rule["settings"]) > 1
            ):
                max_price = self._last_rule["settings"][0]["enabled"]
            else:
                max_price = False

        if target_percent is None:
            target_percent = (
                self._last_rule["targetPercent"]
                if "targetPercent" in self._last_rule
                else 80
            )

        if pre_condition is None:
            pre_condition = (
                self._last_rule["preconditioningEnabled"]
                if "preconditioningEnabled" in self._last_rule
                else False
            )

        if not pre_condition_length:
            pre_condition_length = (
                self._last_rule["preconditionLengthMins"]
                if (
                    "preconditionLengthMins" in self._last_rule
                    and self._last_rule["preconditionLengthMins"] is not None
                )
                else 30
            )

        if target_time is None:
            # Default to 9am
            target_time_cache = (
                self._last_rule["targetTime"]
                if "targetTime" in self._last_rule
                else 32400
            )
            target_time = (target_time_cache // 3600, (target_time_cache % 3600) // 60)

        target_ts = int(
            time_next_occurs(target_time[0], target_time[1]).timestamp() * 1000
        )

        # Convert these to string form
        max_price_str = "true" if max_price else "false"
        pre_condition_str = "true" if pre_condition else "false"

        result = await self._make_request(
            "PUT",
            f"/v1/chargeSessions/{self.serial}/rule?enableMaxPrice={max_price_str}&targetTs={target_ts}&enablePreconditioning={pre_condition_str}&toPercent={target_percent}&preconditionLengthMins={pre_condition_length}",
        )
        return bool(result)

    async def async_change_price_cap(
        self, enabled: Optional[bool] = None, cap: Optional[float] = None
    ) -> bool:
        """Change price cap settings."""
        settings = await self._make_request("GET", "/v1/users/me/settings")
        if enabled is not None:
            settings["chargeSettings"][0]["enabled"] = enabled

        if cap is not None:
            settings["chargeSettings"][0]["value"] = cap

        result = await self._make_request("PUT", "/v1/users/me/settings", data=settings)
        return bool(result)

    async def async_update_schedule(
        self,
        target_percent: Optional[int] = None,
        target_time: Optional[tuple[int, int]] = None,
        pre_condition: Optional[bool] = None,
        pre_condition_length: Optional[int] = None,
    ) -> bool:
        """Update the schedule for the next charge."""
        rule = self._next_session

        # Account for user having no rules
        if not rule:
            return False

        # Update percent and time if provided
        if target_percent is not None:
            rule["targetPercent"] = target_percent
        if target_time is not None:
            rule["targetTime"] = (target_time[0] * 3600) + (target_time[1] * 60)

        # Update pre-conditioning if provided
        if pre_condition is not None:
            rule["preconditioningEnabled"] = pre_condition
        if pre_condition_length:
            rule["preconditionLengthMins"] = pre_condition_length

        await self._make_request("PUT", f"/v1/chargeRules/{rule['id']}", data=rule)
        return True

    async def async_set_target(
        self,
        target_percent: Optional[int] = None,
        target_time: Optional[tuple[int, int]] = None,
        pre_condition_length: Optional[int] = None,
    ) -> bool:
        """Set a target time/percentage."""
        pre_condition: Optional[bool] = None
        if pre_condition_length is not None:
            pre_condition = bool(pre_condition_length)

        if self._charge_in_progress():
            await self.async_apply_session_rule(
                target_time=target_time,
                target_percent=target_percent,
                pre_condition=pre_condition,
                pre_condition_length=pre_condition_length,
            )
        else:
            await self.async_update_schedule(
                target_time=target_time,
                target_percent=target_percent,
                pre_condition=pre_condition,
                pre_condition_length=pre_condition_length,
            )
        return True

    async def async_set_configuration_value(self, values: Mapping[str, bool]) -> bool:
        """Set a configuration value or values."""
        result = await self._make_request(
            "PUT", f"/v1/chargeDevices/{self.serial}/appSettings", data=values
        )
        await asyncio.sleep(1)  # The API is slow to update after this request

        return bool(result)

    async def async_set_vehicle(self, selected_name: str) -> bool:
        """Set the vehicle to be charged."""
        for vehicle in self._cars:
            if vehicle_to_name(vehicle) == selected_name:
                result = await self._make_request(
                    "PUT", f"/v1/car/{vehicle['id']}/select"
                )

                return True
        return False

    # Pull methods

    async def async_get_charge_session(self) -> None:
        """Fetch charge sessions endpoint."""
        # Retry if state is CALCULATING or DELIVERING
        for attempt in range(3):
            resp = await self._make_request("GET", "/v1/chargeSessions")
            resp = resp[0]

            if resp.get("mode") != "CALCULATING" and resp.get("mode") != "DELIVERING":
                break

            if attempt < 2:  # Only sleep if there are more retries left
                await asyncio.sleep(1)

        self._charge_session = resp

        # Store last rule
        if resp["mode"] == "SMART_CHARGE" and "appliedRule" in resp:
            self._last_rule = resp["appliedRule"]

        # Get energy reading
        if self._charge_in_progress() and resp.get("batterySoc") is not None:
            self.energy = max(0, self.energy, resp["batterySoc"].get("wh") or 0)
        else:
            self.energy = 0

        self.battery = (
            ((resp.get("car") or {}).get("batterySoc") or {}).get("percent")
            or (resp.get("batterySoc") or {}).get("percent")
            or 0
        )

        resp = await self._make_request("GET", "/v1/chargeSessions/nextSessionInfo")
        self._next_session = resp.get("rule", {})

    async def async_get_advanced_settings(self) -> None:
        """Get advanced settings (mainly for CT clamp reading)"""
        try:
            resp = await self._make_request(
                "GET", f"/v1/chargeDevices/{self.serial}/advancedSettings"
            )
            self._advanced_settings = resp
        except:
            self._advanced_settings = {}
            return

        # clampConnected is not reliable, so check clampAmps being > 0 as an alternative
        if resp["clampConnected"] or (
            isinstance(resp.get("clampAmps"), float) and resp.get("clampAmps") > 0
        ):
            self.ct_connected = True

    async def async_update_device_info(self) -> bool:
        """Update _device_info with our charger model."""
        resp = await self._make_request("GET", "/v1/users/me/account")
        self._cars = resp.get("cars") or []

        try:
            self.cap_enabled = resp["userSettings"]["chargeSettings"][0]["enabled"]
        except:
            pass

        device = resp["chargeDevices"][0]

        self._capabilities = device["modelCapabilities"]
        self._configuration = device["optionalSettings"]
        self.serial = device["id"]

        self.device_info = {
            "name": device["modelTypeDisplayName"],
            "model": device["modelTypeDisplayName"].replace("Ohme ", ""),
            "sw_version": device["firmwareVersionLabel"],
        }

        if resp["tariff"] is not None and resp["tariff"]["dsrTariff"]:
            self.cap_available = False

        solar_modes = device["modelCapabilities"]["solarModes"]
        if isinstance(solar_modes, list) and len(solar_modes) == 1:
            self.solar_capable = True

        return True

    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> Self:
        """Async enter."""
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit."""
        await self.close()


# Exceptions
class ApiException(Exception): ...


class AuthException(ApiException): ...
