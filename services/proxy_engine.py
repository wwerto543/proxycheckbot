import asyncio
import aiohttp
import time
import logging

# Настройка логирования для отладки
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyEngine:
    def __init__(self, max_streams: int = 300, timeout: int = 7):
        self.semaphore = asyncio.Semaphore(max_streams)
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.check_url = "http://ip-api.com/json/" # Используем для чека и GeoIP одновременно

    async def fetch_geo_and_status(self, session: aiohttp.ClientSession, proxy_url: str):
        """Проверяет прокси и сразу забирает данные о стране."""
        try:
            async with session.get(self.check_url, proxy=proxy_url, timeout=self.timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "valid": True,
                        "country": data.get("country", "Unknown"),
                        "country_code": data.get("countryCode", "UN"),
                        "city": data.get("city", "Unknown"),
                        "ip": data.get("query", "0.0.0.0")
                    }
        except Exception:
            pass
        return {"valid": False}

    async def check_proxy_task(self, raw_proxy: str):
        """Ядро проверки: перебор протоколов и замер задержки."""
        raw_proxy = raw_proxy.strip()
        if not raw_proxy:
            return None

        # Очищаем строку от возможных протоколов, если они уже есть
        clean_address = raw_proxy.split("://")[-1]
        
        # Список протоколов для авто-перебора
        protocols = ["http://", "socks5://", "socks4://"]
        
        async with self.semaphore:
            async with aiohttp.ClientSession() as session:
                for proto in protocols:
                    proxy_url = f"{proto}{clean_address}"
                    start_time = time.perf_counter()
                    
                    result = await self.fetch_geo_and_status(session, proxy_url)
                    
                    if result["valid"]:
                        end_time = time.perf_counter()
                        latency = int((end_time - start_time) * 1000)
                        
                        return {
                            "raw": raw_proxy,
                            "full_address": proxy_url,
                            "protocol": proto.replace("://", ""),
                            "country": result["country"],
                            "country_code": result["country_code"],
                            "latency": latency,
                            "valid": True
                        }
        
        return {"raw": raw_proxy, "valid": False}

    async def run_checker(self, proxy_list: list):
        """Запуск массовой проверки."""
        tasks = [self.check_proxy_task(p) for p in proxy_list]
        return await asyncio.gather(*tasks)

# Пример использования (для тестов):
# engine = ProxyEngine()
# results = await engine.run_checker(["1.2.3.4:8080", "5.6.7.8:1080"])