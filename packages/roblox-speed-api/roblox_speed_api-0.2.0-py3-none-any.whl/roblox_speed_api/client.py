# ---------- Thumbnails (users) ----------

    async def get_user_avatar_headshot(
        self,
        user_id: int,
        *,
        size: str = "420x420",
        format: str = "Png",
        circular: bool = False,
    ) -> Dict[str, Any]:
        """
        thumbnails.roblox.com/v1/users/avatar-headshot?userIds=...&size=...&format=Png&isCircular=false
        Returns the first 'data' item or raises if empty.
        """
        url = "https://thumbnails.roblox.com/v1/users/avatar-headshot"
        params = {
            "userIds": str(user_id),
            "size": size,
            "format": format,
            "isCircular": "true" if circular else "false",
        }
        data = await self._request("GET", url, params=params)
        items = (data or {}).get("data") or []
        if not items:
            import httpx as _httpx
            raise RobloxAPIError(404, str(_httpx.URL(url).copy_merge_params(params)), {"message": "Headshot not found"})
        return items[0]

    async def get_user_avatar_fullbody(
        self,
        user_id: int,
        *,
        size: str = "720x720",
        format: str = "Png",
        circular: bool = False,
    ) -> Dict[str, Any]:
        """
        thumbnails.roblox.com/v1/users/avatar (full-body)
        """
        url = "https://thumbnails.roblox.com/v1/users/avatar"
        params = {
            "userIds": str(user_id),
            "size": size,
            "format": format,
            "isCircular": "true" if circular else "false",
        }
        data = await self._request("GET", url, params=params)
        items = (data or {}).get("data") or []
        if not items:
            import httpx as _httpx
            raise RobloxAPIError(404, str(_httpx.URL(url).copy_merge_params(params)), {"message": "Avatar not found"})
        return items[0]

    # ---------- Social: followers/followings ----------

    async def get_followers(
        self, user_id: int, *, limit: int = 100, cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        url = f"https://friends.roblox.com/v1/users/{user_id}/followers"
        params = {"limit": str(limit), "cursor": cursor, "sortOrder": "Asc"}
        return await self._request("GET", url, params=params)

    async def get_followings(
        self, user_id: int, *, limit: int = 100, cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        url = f"https://friends.roblox.com/v1/users/{user_id}/followings"
        params = {"limit": str(limit), "cursor": cursor, "sortOrder": "Asc"}
        return await self._request("GET", url, params=params)

    # ---------- Groups/roles of a user ----------

    async def get_user_groups_roles(self, user_id: int) -> Dict[str, Any]:
        """
        groups.roblox.com/v2/users/{userId}/groups/roles
        """
        url = f"https://groups.roblox.com/v2/users/{user_id}/groups/roles"
        return await self._request("GET", url)

    # ---------- Badges of a user ----------

    async def get_user_badges(
        self, user_id: int, *, limit: int = 100, cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        badges.roblox.com/v1/users/{userId}/badges
        """
        url = f"https://badges.roblox.com/v1/users/{user_id}/badges"
        params = {"limit": str(limit), "cursor": cursor, "sortOrder": "Asc"}
        return await self._request("GET", url, params=params)

    # ---------- Games/places/thumbnails ----------

    async def get_universe_icons(
        self,
        universe_ids: list[int],
        *,
        size: str = "150x150",
        format: str = "Png",
        circular: bool = False,
    ) -> Dict[str, Any]:
        """
        thumbnails.roblox.com/v1/games/icons?universeIds=1,2,...
        """
        url = "https://thumbnails.roblox.com/v1/games/icons"
        params = {
            "universeIds": ",".join(str(x) for x in universe_ids),
            "size": size,
            "format": format,
            "isCircular": "true" if circular else "false",
        }
        return await self._request("GET", url, params=params)

    async def get_place_details(self, place_ids: list[int]) -> list[Dict[str, Any]]:
        """
        games.roblox.com/v1/games/multiget-place-details?placeIds=...
        """
        url = "https://games.roblox.com/v1/games/multiget-place-details"
        params = {"placeIds": ",".join(str(x) for x in place_ids)}
        data = await self._request("GET", url, params=params)
        # returns a list
        return data or []

    async def get_game_servers(
        self,
        place_id: int,
        *,
        server_type: str = "Public",  # or "Vip"
        limit: int = 100,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        games.roblox.com/v1/games/{placeId}/servers/{serverType}
        """
        url = f"https://games.roblox.com/v1/games/{place_id}/servers/{server_type}"
        params = {"limit": str(limit), "cursor": cursor, "sortOrder": "Asc"}
        return await self._request("GET", url, params=params)

    # ---------- Catalog/assets details (batch) ----------

    async def get_assets_details(self, asset_ids: list[int]) -> list[Dict[str, Any]]:
        """
        POST catalog.roblox.com/v1/catalog/items/details
        body: {"items": [{"itemType":"Asset","id": <id>}, ...]}
        Batches up to 120 ids per request.
        """
        if not asset_ids:
            return []
        url = "https://catalog.roblox.com/v1/catalog/items/details"
        out: list[Dict[str, Any]] = []
        CHUNK = 120
        for i in range(0, len(asset_ids), CHUNK):
            chunk = asset_ids[i : i + CHUNK]
            payload = {"items": [{"itemType": "Asset", "id": int(a)} for a in chunk]}
            data = await self._request("POST", url, json_body=payload, use_cache=False)
            items = (data or {}).get("data") or []
            out.extend(items)
        return out

    # ---------- Presence (requires auth) ----------

    async def get_presence(self, user_ids: list[int]) -> Dict[str, Any]:
        """
        presence.roblox.com/v1/presence/users (POST)
        Requires authenticated session cookie.
        """
        if not self._auth_cookie:
            raise RobloxAPIError(401, "https://presence.roblox.com/v1/presence/users", {"message": "Auth required"})
        url = "https://presence.roblox.com/v1/presence/users"
        payload = {"userIds": [int(x) for x in user_ids]}
        return await self._request("POST", url, json_body=payload, use_cache=False)