import aiohttp
import ipaddress
import logging

logger = logging.getLogger(__name__)

# Free, reliable API requiring no token for moderate usage
API_URL = "https://ipwho.is/"

def validate_ip(ip_str: str) -> bool:
    """Validates if a given string is a proper IPv4 or IPv6 public address."""
    try:
        ip = ipaddress.ip_address(ip_str.strip())
        # Return True if it's a valid globally routeable public address
        return ip.is_global
    except ValueError:
        return False

async def fetch_ip_details(ip_str: str) -> dict:
    """Asynchronously pulls geolocation profiles from the API endpoint."""
    target_url = f"{API_URL}{ip_str.strip()}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(target_url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("success") is True:
                        return data
                    else:
                        logger.warning(f"API metadata error for {ip_str}: {data.get('message')}")
                        return {"error": data.get("message", "Unknown API error")}
                elif response.status == 429:
                    return {"error": "Rate limit exceeded. Please try again later."}
                else:
                    return {"error": f"HTTP Error status {response.status}"}
    except aiohttp.ClientConnectorError:
        logger.error("Network connection failure during API call.")
        return {"error": "Network connectivity problem."}
    except Exception as e:
        logger.error(f"Unexpected error in fetch_ip_details: {str(e)}")
        return {"error": "Internal system failure while fetching data."}

def format_ip_data(data: dict) -> str:
    """Transforms raw JSON data into a clean, well-formatted string markup."""
    connection = data.get("connection", {})
    timezone = data.get("timezone", {})
    security = data.get("security", {})

    # Determine type status manually if API field isn't explicitly clear
    ip_type = "Public" if validate_ip(data.get("ip", "")) else "Private/Special"

    report = (
        f"🌐 **IP Analysis Profile**\n"
        f"‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾\n"
        f"🔹 **IP Address:** `{data.get('ip')}`\n"
        f"🔹 **Type:** {ip_type} ({data.get('type', 'Unknown')})\n\n"
        f"📍 **Location Details:**\n"
        f"• **Country:** {data.get('country', 'N/A')} {data.get('country_code', '')}\n"
        f"• **Region/State:** {data.get('region', 'N/A')}\n"
        f"• **City:** {data.get('city', 'N/A')}\n"
        f"• **Postal Code:** {data.get('postal', 'N/A')}\n"
        f"• **Coordinates:** `{data.get('latitude')}, {data.get('longitude')}`\n\n"
        f"🛰️ **Network & Infrastructure:**\n"
        f"• **ISP:** {connection.get('isp', 'N/A')}\n"
        f"• **Organization:** {connection.get('org', 'N/A')}\n"
        f"• **ASN:** AS{connection.get('asn', 'N/A')}\n\n"
        f"⏰ **Time & Currency:**\n"
        f"• **Time Zone:** {timezone.get('id', 'N/A')} ({timezone.get('utc', 'N/A')})\n"
        f"• **Currency:** {data.get('currency', {}).get('name', 'N/A')} ({data.get('currency', {}).get('code', 'N/A')})\n\n"
        f"🛡️ **Security Telemetry:**\n"
        f"• **Anonymous/VPN/Proxy:** {'⚠️ Yes' if security.get('anonymous', False) else '✅ No'}\n"
    )
    return report

