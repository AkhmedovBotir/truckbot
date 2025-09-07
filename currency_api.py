import aiohttp
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import CBU_API_URL

class CurrencyAPI:
    def __init__(self):
        self.base_url = CBU_API_URL

    async def get_currency_data(self, date: str = None) -> List[Dict[str, Any]]:
        """Fetch currency data from CBU API"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        url = f"{self.base_url}{date}/"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        print(f"API request failed with status: {response.status}")
                        return []
        except Exception as e:
            print(f"Error fetching currency data: {e}")
            return []

    async def get_currency_by_code(self, code: str, date: str = None) -> Optional[Dict[str, Any]]:
        """Get specific currency by code"""
        currencies = await self.get_currency_data(date)
        for currency in currencies:
            if currency.get('Ccy') == code:
                return currency
        return None

    async def get_available_currencies(self) -> List[Dict[str, str]]:
        """Get list of available currencies with codes and names"""
        currencies = await self.get_currency_data()
        return [
            {
                'code': curr.get('Ccy', ''),
                'name': curr.get('CcyNm_EN', ''),
                'rate': curr.get('Rate', '0')
            }
            for curr in currencies if curr.get('Ccy')
        ]

    def format_currency_info(self, currency_data: Dict[str, Any], template: str) -> str:
        """Format currency information using template"""
        try:
            return template.format(
                currency_name=currency_data.get('CcyNm_EN', 'Unknown'),
                currency_code=currency_data.get('Ccy', 'Unknown'),
                rate=currency_data.get('Rate', '0'),
                date=currency_data.get('Date', datetime.now().strftime('%Y-%m-%d'))
            )
        except Exception as e:
            print(f"Error formatting currency info: {e}")
            return f"Currency: {currency_data.get('Ccy', 'Unknown')}\nRate: {currency_data.get('Rate', '0')} UZS"

# Global currency API instance
currency_api = CurrencyAPI()