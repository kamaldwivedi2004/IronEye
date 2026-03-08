with open('alert_system.py', 'r') as f:
    content = f.read()

content = content.replace(
    'from dotenv               import load_dotenv',
    'from dotenv               import load_dotenv\nimport urllib.request\nimport json'
)

geo_func = """
# --- Geolocation (IP-based) ---
def get_location():
    try:
        url = "http://ip-api.com/json/?fields=city,regionName,country,lat,lon,status"
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read().decode())
        if data.get("status") == "success":
            return data
    except Exception:
        pass
    return {}

"""

content = content.replace('\n# --- Config', geo_func + '\n# --- Config')
content = content.replace('\n# \u2500\u2500\u2500 Config', geo_func + '\n# \u2500\u2500\u2500 Config')

content = content.replace(
    '        ts   = datetime.now().strftime("%B %d, %Y at %I:%M:%S %p")',
    '        ts   = datetime.now().strftime("%B %d, %Y at %I:%M:%S %p")\n        _loc = get_location()\n        loc_str = f"{_loc.get(\'city\',\'Unknown\')}, {_loc.get(\'regionName\',\'\')}, {_loc.get(\'country\',\'\')}" if _loc else "Location unavailable"\n        maps_url = f"https://maps.google.com/?q={_loc[\'lat\']},{_loc[\'lon\']}" if _loc else "#"'
)

content = content.replace(
    '<b style="color:#e74c3c">NOT in database</b></td></tr>',
    '<b style="color:#e74c3c">NOT in database</b></td></tr>\n              <tr><td style="padding:8px; color:#777">Location</td><td style="padding:8px"><b>{loc_str}</b></td></tr>\n              <tr><td style="padding:8px; color:#777">Maps</td><td style="padding:8px"><a href="{maps_url}">Open in Google Maps</a></td></tr>'
)

with open('alert_system.py', 'w') as f:
    f.write(content)
print("Done!")
