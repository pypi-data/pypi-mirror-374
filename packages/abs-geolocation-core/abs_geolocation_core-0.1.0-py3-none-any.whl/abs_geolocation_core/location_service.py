"""
LocationService – Azure Maps powered location utilities

Features implemented:
1) geocode_address – Get location by address
2) reverse_geocode – Get address by latitude/longitude
3) distance_between – Haversine distance in meters (optionally by road via route)
4) get_route – Route between two or more locations
5) elevation_along – Elevation for points or line (profile) [Azure Maps Elevation]
6) weather_at – Current weather at a location [Azure Maps Weather]
7) traffic_at – Traffic flow/relative congestion at a location [Azure Maps Traffic]
8) nearest_by_distance – Find nearest candidate(s) to an origin by straight-line distance
9) nearest_by_drive_distance – Find nearest by driving distance using Route Matrix
10) nearest_by_drive_time – Find nearest by driving time using Route Matrix
11) nearest_ranked – Rank candidates by (time, distance)
12) nearest_ranked_with_weather – Rank candidates by (time, distance) + weather filter
13) nearest_ranked_with_weather_traffic – Rank candidates by (time, distance) + weather + traffic

Notes
- Works with either Subscription Key or short-lived SAS tokens.
- For SAS, pass a callable that returns a fresh token string each call.
- Uses httpx for async I/O, retries, and timeouts.

You will need to enable the corresponding Azure Maps services for your resource
(Search, Routing, Elevation, Weather, Traffic). Some endpoints have different api-version values;
these are parameterized and can be adjusted via constructor.
"""
from __future__ import annotations

import math
import time
from typing import Any, Callable, Dict, Iterable, List, Literal, Optional, Sequence, Tuple
import base64
import hmac
import hashlib
import urllib.parse

import httpx


Coord = Tuple[float, float]  # (lat, lon)


# def generate_azure_maps_sas_token(
#     *,
#     resource_uri: str,
#     key: str,
#     key_name: str,
#     ttl_seconds: int = 3600,
#     now_epoch_seconds: Optional[int] = None,
# ) -> str:
#     """
#     Generate a Shared Access Signature (SAS) token for Azure Maps.

#     The resulting token string can be used directly as the Authorization header value.
#     Example: "SharedAccessSignature sr=...&sig=...&se=...&skn=..."

#     Args:
#         resource_uri: The Azure Maps resource URI to sign (e.g. "https://atlas.microsoft.com/").
#         key: The Azure Maps shared key as provided in the Azure portal (base64 string).
#         key_name: The key name (e.g. "primary" or "secondary").
#         ttl_seconds: Token lifetime in seconds (default 3600).
#         now_epoch_seconds: Optional current epoch seconds override (for testing).

#     Returns:
#         The SAS token string.
#     """
#     # Per Azure Maps docs, sign the string: "{resourceUri}\n{expiry}"
#     # - Use the base64-decoded key as HMAC-SHA256 secret
#     # - signature = base64(hmac_sha256(stringToSign))
#     # - token = SharedAccessSignature sr=encodeURIComponent(resourceUri)&sig=encodeURIComponent(signature)&se=expiry&skn=keyName
#     resource = resource_uri.lower()
#     expiry = int(now_epoch_seconds if now_epoch_seconds is not None else time.time()) + int(ttl_seconds)
#     string_to_sign = f"{resource}\n{expiry}".encode("utf-8")
#     decoded_key = base64.b64decode(key)
#     signature = hmac.new(decoded_key, string_to_sign, hashlib.sha256).digest()
#     signature_b64 = base64.b64encode(signature).decode("utf-8")
#     token = (
#         "SharedAccessSignature "
#         f"sr={urllib.parse.quote(resource, safe='')}"
#         f"&sig={urllib.parse.quote(signature_b64, safe='')}"
#         f"&se={expiry}"
#         f"&skn={urllib.parse.quote(key_name, safe='')}"
#     )
#     return token


class AzureMapsAuth:
    def __init__(self, subscription_key: str = None, sas_token_provider=None):
        self.subscription_key = subscription_key
        self.sas_token_provider = sas_token_provider

    def get_headers(self) -> dict:
        """Return authentication headers depending on the auth type."""
        if self.sas_token_provider:
            token = self.sas_token_provider()
            return {"Authorization": token}
        elif self.subscription_key:
            return {"subscription-key": self.subscription_key}
        else:
            raise ValueError("Either subscription_key or sas_token_provider must be provided")

    # @classmethod
    # def from_sas(
    #     cls,
    #     *,
    #     resource_uri: str = "https://atlas.microsoft.com/",
    #     key: str,
    #     key_name: str,
    #     ttl_seconds: int = 3600,
    # ) -> "AzureMapsAuth":
    #     """
    #     Build an AzureMapsAuth that generates short-lived SAS tokens for each request.

    #     Args:
    #         resource_uri: The resource URI to sign. Typically "https://atlas.microsoft.com/".
    #         key: The Azure Maps primary/secondary key (base64-encoded string from the portal).
    #         key_name: The key name, e.g. "primary" or "secondary".
    #         ttl_seconds: Token lifetime in seconds.

    #     Returns:
    #         AzureMapsAuth configured with a SAS token provider.
    #     """

    #     def _provider() -> str:
    #         return generate_azure_maps_sas_token(
    #             resource_uri=resource_uri,
    #             key=key,
    #             key_name=key_name,
    #             ttl_seconds=ttl_seconds,
    #         )

    #     return cls(sas_token_provider=_provider)


class LocationService:
    BASE_URL = "https://atlas.microsoft.com"

    def __init__(
        self,
        auth: AzureMapsAuth,
        *,
        api_version_search: str = "1.0",
        api_version_route: str = "2025-01-01",
        api_version_matrix: str = "2.0",
        api_version_elevation: str = "1.0",
        api_version_weather: str = "1.1",
        api_version_traffic: str = "2025-01-01",
        timeout: float = 10.0,
        max_retries: int = 3,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        self.auth = auth
        self.timeout = timeout
        self.max_retries = max_retries
        limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
        self._client = httpx.AsyncClient(timeout=timeout, limits=limits, transport=transport)
        self.api_version_search = api_version_search
        self.api_version_route = api_version_route
        self.api_version_matrix = api_version_matrix
        self.api_version_elevation = api_version_elevation
        self.api_version_weather = api_version_weather
        self.api_version_traffic = api_version_traffic

    async def _request(self, method: str, url: str, params=None, json=None, data=None):
        headers = self.auth.get_headers()

        # If subscription-key, Azure Maps expects it in query params not headers
        if "subscription-key" in headers:
            if params is None:
                params = {}
            params["subscription-key"] = headers["subscription-key"]
            headers = {}
        resp = await self._client.request(method, url, params=params, headers=headers, json=json, data=data)
        resp.raise_for_status()
        return resp.json()

    # 1. Get the location by address (geocoding)
    async def geocode_address(self, address: str, *, country_set: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        url = f"{self.BASE_URL}/search/address/json"
        params = {"api-version": self.api_version_search, "query": address, "limit": limit}
        if country_set:
            params["countrySet"] = country_set
        data = await self._request("GET", url, params=params)
        return data.get("results", [])

    # 2. Get the address by latitude and longitude (reverse geocoding)
    async def reverse_geocode(self, coord: Coord) -> Dict[str, Any]:
        lat, lon = coord
        url = f"{self.BASE_URL}/search/address/reverse/json"
        params = {"api-version": self.api_version_search, "query": f"{lat},{lon}"}
        return await self._request("GET", url, params=params)

    # 3. Haversine great-circle distance in meters (option: driving distance via route)
    @staticmethod
    def haversine_meters(a: Coord, b: Coord) -> float:
        R = 6371000.0
        lat1, lon1 = map(math.radians, a)
        lat2, lon2 = map(math.radians, b)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        return 2 * R * math.asin(math.sqrt(h))

    async def distance_between(
        self,
        a: Coord,
        b: Coord,
        *,
        by: Literal["straight", "drive"] = "straight",
        travel_mode: Literal["car", "truck", "taxi", "bus", "van", "motorcycle", "bicycle", "pedestrian"] = "car",
    ) -> float:
        if by == "straight":
            return self.haversine_meters(a, b)
        # by road: use route/directions to get travel distance
        lat1, lon1 = a
        lat2, lon2 = b
        url = f"{self.BASE_URL}/route/directions/json"
        params = {
            "api-version": self.api_version_route,
            "query": f"{lat1},{lon1}:{lat2},{lon2}",
            "travelMode": travel_mode,
            "computeBestOrder": False,
        }
        data = await self._request("GET", url, params=params)
        routes = data.get("routes", [])
        if not routes:
            return float("nan")
        # Sum first leg distance
        return float(routes[0].get("summary", {}).get("lengthInMeters", float("nan")))

    # 4. Get the route between two or more locations
    async def get_route(self, coordinates: list[dict], travel_mode: str = "car"):
        """
        Get route between multiple coordinates.
        coordinates: list of dicts like [{"lat": 12.97, "lon": 77.59}, {"lat": 13.08, "lon": 80.27}]
        """
        # Convert to Azure Maps route query format. Accept dicts or (lat, lon) tuples.
        parts = []
        for c in coordinates:
            if isinstance(c, dict):
                lat, lon = c["lat"], c["lon"]
            else:
                lat, lon = c  # assumes tuple/list (lat, lon)
            parts.append(f"{lat},{lon}")
        coord_str = ":".join(parts)

        url = f"{self.BASE_URL}/route/directions/json"
        params = {
            "api-version": self.api_version_route,
            "query": coord_str,
            "travelMode": travel_mode,
            "instructionsType": "text",
            "maxAlternatives": 0,
        }
        return await self._request("GET", url, params=params)

    # 5. Elevation – point(s) and line (profile)
    async def elevation_points(self, points: Sequence[Coord]) -> Dict[str, Any]:
        pts = ",".join(f"{lat},{lon}" for lat, lon in points)
        url = f"{self.BASE_URL}/elevation/point/json"
        params = {"api-version": self.api_version_elevation, "points": pts}
        return await self._request("GET", url, params=params)

    async def elevation_along(self, coords: Sequence[Coord]) -> Dict[str, Any]:
        if len(coords) < 2:
            raise ValueError("At least two coordinates required for elevation profile")
        line = ":".join(f"{lat},{lon}" for lat, lon in coords)
        url = f"{self.BASE_URL}/elevation/line/json"
        params = {"api-version": self.api_version_elevation, "path": line}
        return await self._request("GET", url, params=params)

    # 6. Weather – current conditions at a location
    async def weather_at(self, coord: Coord) -> Dict[str, Any]:
        lat, lon = coord
        url = f"{self.BASE_URL}/weather/currentConditions/json"
        params = {"api-version": self.api_version_weather, "query": f"{lat},{lon}"}
        return await self._request("GET", url, params=params)

    # 7. Traffic – flow segment at a point
    async def traffic_at(self, coord: Coord, *, zoom: int = 10) -> Dict[str, Any]:
        lat, lon = coord
        url = f"{self.BASE_URL}/traffic/flowSegment/relative/json"
        params = {"api-version": self.api_version_traffic, "point": f"{lat},{lon}", "zoom": zoom}
        return await self._request("GET", url, params=params)

    # 8. Nearest candidate(s) by straight-line distance
    async def nearest_by_distance(self, origin: Coord, candidates: Sequence[Coord], *, k: int = 1) -> List[Tuple[Coord, float]]:
        ranked = sorted(((c, self.haversine_meters(origin, c)) for c in candidates), key=lambda x: x[1])
        return ranked[:k]

    # 9 & 10. Nearest by drive distance or time – Route Matrix
    async def _route_matrix(self, origins: Sequence[Coord], destinations: Sequence[Coord], *, travel_mode: str = "car") -> Dict[str, Any]:
        url = f"{self.BASE_URL}/route/matrix/sync/json"
        origins_str = [{"lat": lat, "lon": lon} for lat, lon in origins]
        dests_str = [{"lat": lat, "lon": lon} for lat, lon in destinations]
        params = {"api-version": self.api_version_matrix}
        payload = {
            "origins": [{"point": o} for o in origins_str],
            "destinations": [{"point": d} for d in dests_str],
            "travelMode": travel_mode,
            "computeTravelTimeFor": "all",
        }
        return await self._request("POST", url, params=params, json=payload)

    async def nearest_by_drive_distance(
        self,
        origin: Coord,
        candidates: Sequence[Coord],
        *,
        travel_mode: str = "car",
        k: int = 1,
    ) -> List[Tuple[Coord, float]]:
        matrix = await self._route_matrix([origin], candidates, travel_mode=travel_mode)
        # distances appear in matrix["matrix"][row][col]["response"]["routeSummary"]["lengthInMeters"]
        row = matrix.get("matrix", [])[0]
        pairs: List[Tuple[Coord, float]] = []
        for cand, cell in zip(candidates, row):
            dist = float(cell.get("response", {}).get("routeSummary", {}).get("lengthInMeters", float("inf")))
            pairs.append((cand, dist))
        return sorted(pairs, key=lambda x: x[1])[:k]

    async def nearest_by_drive_time(
        self,
        origin: Coord,
        candidates: Sequence[Coord],
        *,
        travel_mode: str = "car",
        k: int = 1,
    ) -> List[Tuple[Coord, float]]:
        matrix = await self._route_matrix([origin], candidates, travel_mode=travel_mode)
        row = matrix.get("matrix", [])[0]
        pairs: List[Tuple[Coord, float]] = []
        for cand, cell in zip(candidates, row):
            t = float(cell.get("response", {}).get("routeSummary", {}).get("travelTimeInSeconds", float("inf")))
            pairs.append((cand, t))
        return sorted(pairs, key=lambda x: x[1])[:k]

    # 11–13. Composite ranking with optional weather/traffic constraints
    async def nearest_ranked(
        self,
        origin: Coord,
        candidates: Sequence[Coord],
        *,
        weight_time: float = 0.7,
        weight_distance: float = 0.3,
        travel_mode: str = "car",
        k: int = 1,
    ) -> List[Tuple[Coord, Dict[str, float]]]:
        matrix = await self._route_matrix([origin], candidates, travel_mode=travel_mode)
        row = matrix.get("matrix", [])[0]
        scored: List[Tuple[Coord, Dict[str, float]]] = []
        for cand, cell in zip(candidates, row):
            summ = cell.get("response", {}).get("routeSummary", {})
            t = float(summ.get("travelTimeInSeconds", float("inf")))
            d = float(summ.get("lengthInMeters", float("inf")))
            score = weight_time * t + weight_distance * d
            scored.append((cand, {"score": score, "time_s": t, "dist_m": d}))
        scored.sort(key=lambda x: x[1]["score"])  # lower is better
        return scored[:k]

    async def nearest_ranked_with_weather(
        self,
        origin: Coord,
        candidates: Sequence[Coord],
        *,
        disallow_precip: bool = False,
        max_wind_kph: Optional[float] = None,
        travel_mode: str = "car",
        k: int = 1,
    ) -> List[Tuple[Coord, Dict[str, float]]]:
        # First, rank by time/distance
        base = await self.nearest_ranked(origin, candidates, travel_mode=travel_mode, k=len(candidates))
        # Filter by weather
        result: List[Tuple[Coord, Dict[str, float]]] = []
        for cand, meta in base:
            w = await self.weather_at(cand)
            # Simplified parsing – adjust based on your weather provider response
            obs = (w.get("results") or w.get("weather") or [None])[0] or {}
            has_precip = bool(obs.get("hasPrecipitation") or obs.get("precipitationType"))
            wind_kph = float(obs.get("windSpeed", {}).get("value", 0)) if isinstance(obs.get("windSpeed"), dict) else float(obs.get("windSpeed", 0))
            if disallow_precip and has_precip:
                continue
            if max_wind_kph is not None and wind_kph > max_wind_kph:
                continue
            meta = {**meta, "wind_kph": wind_kph, "precip": float(has_precip)}
            result.append((cand, meta))
            if len(result) >= k:
                break
        return result

    async def nearest_ranked_with_weather_traffic(
        self,
        origin: Coord,
        candidates: Sequence[Coord],
        *,
        disallow_precip: bool = False,
        max_wind_kph: Optional[float] = None,
        min_traffic_speed_ratio: Optional[float] = None,
        travel_mode: str = "car",
        k: int = 1,
    ) -> List[Tuple[Coord, Dict[str, float]]]:
        base = await self.nearest_ranked_with_weather(
            origin,
            candidates,
            disallow_precip=disallow_precip,
            max_wind_kph=max_wind_kph,
            travel_mode=travel_mode,
            k=len(candidates),
        )
        result: List[Tuple[Coord, Dict[str, float]]] = []
        for cand, meta in base:
            t = await self.traffic_at(cand)
            # Parse traffic flow segment (relative speed vs freeflow)
            flow = t.get("flowSegmentData", {})
            current_speed = float(flow.get("currentSpeed", 0))
            free_speed = float(flow.get("freeFlowSpeed", 0))
            ratio = (current_speed / free_speed) if free_speed > 0 else 0.0
            if min_traffic_speed_ratio is not None and ratio < min_traffic_speed_ratio:
                continue
            meta = {**meta, "traffic_speed_ratio": ratio}
            result.append((cand, meta))
            if len(result) >= k:
                break
        return result

    async def aclose(self) -> None:
        await self._client.aclose()

    async def suggest_places(
        self,
        query: str,
        *,
        lat: float = None,
        lon: float = None,
        country_set: Optional[str] = None,
        limit: int = 10,
        typeahead: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get suggested places for an address query.

        Args:
            query (str): The search text, e.g. "Surat".
            lat (float, optional): Latitude for search biasing.
            lon (float, optional): Longitude for search biasing.
            country_set (str, optional): Restrict results to a country code (e.g. "IN").
            limit (int): Max number of suggestions.
            typeahead (bool): If true, optimize for autocomplete queries.

        Returns:
            list[dict]: Suggested places.
        """
        params = {
            "api-version": self.api_version_search,
            "query": query,
            "limit": limit,
            "typeahead": str(typeahead).lower(),
        }
        if lat and lon:
            params["lat"], params["lon"] = lat, lon
        if country_set:
            params["countrySet"] = country_set

        url = f"{self.BASE_URL}/search/fuzzy/json"
        data = await self._request("GET", url, params=params)

        results = data.get("results", [])
        return results



# ---------- Example usage ----------
# import asyncio
#
# async def main():
#     auth = AzureMapsAuth(subscription_key="<YOUR_KEY>")  # or sas_token_provider=lambda: "sv=...&sig=..."
#     svc = LocationService(auth)
#     places = await svc.geocode_address("Mumbai Central, Mumbai")
#     print(places[0]["position"])  # lat/lon from geocode result
#     origin = (19.0760, 72.8777)  # Mumbai
#     dest = (18.5204, 73.8567)    # Pune
#     route = await svc.get_route([origin, dest])
#     print(route["routes"][0]["summary"])
#     best = await svc.nearest_by_drive_time(origin, [(18.5204, 73.8567), (21.1458, 79.0882)])
#     print(best)
#     await svc.aclose()
#
# if __name__ == "__main__":
#     asyncio.run(main())
