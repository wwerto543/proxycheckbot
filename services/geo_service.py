import aiohttp

async def get_proxy_info(ip: str):
    try:
        async with aiohttp.ClientSession() as session:
            # Используем бесплатный API для определения страны
            async with session.get(f"http://ip-api.com/json/{ip}", timeout=2) as resp:
                data = await resp.json()
                if data.get("status") == "success":
                    return data.get("country", "Unknown"), data.get("countryCode", "UN")
    except:
        pass
    return "Unknown", "UN"