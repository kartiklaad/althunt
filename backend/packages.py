"""
Party package definitions for Altitude Trampoline Park Huntsville
"""

PACKAGES = {
    "Rookie": {
        "price_per_jumper": 25,
        "min_jumpers": 10,
        "jump_time": "Jump time",
        "table_time": "Table time",
        "includes": [
            "Jump time",
            "Table time",
            "Party host",
            "Setup and cleanup",
            "Plates, napkins, utensils, tablecloth (basic party supplies)",
            "Altitude grip socks"
        ],
        "excludes": ["Pizza", "Soda", "Arcade cards", "Birthday gift", "Free return pass"],
        "private_room_upgrade": "$5 per jumper",
        "notes": "Basic package – no food, drinks, or extras included"
    },
    "All-Star": {
        "price_per_jumper": 30,
        "min_jumpers": 10,
        "jump_time": "Jump time",
        "table_time": "Table time",
        "includes": [
            "Everything in Rookie",
            "Large pizza per 5 jumpers"
        ],
        "private_room_upgrade": "$5 per jumper",
        "notes": "Includes pizza for everyone"
    },
    "MVP": {
        "price_per_jumper": 35,
        "min_jumpers": 10,
        "jump_time": "Jump time",
        "table_time": "Table time",
        "includes": [
            "Everything in All-Star",
            "Arcade card per jumper"
        ],
        "private_room_upgrade": "$5 per jumper",
        "notes": "Includes arcade cards for all jumpers"
    },
    "Glo Party": {
        "price_per_jumper": 40,
        "min_jumpers": 10,
        "jump_time": "3 hours total",
        "table_time": "Table time",
        "includes": [
            "Everything in MVP",
            "Gift for birthday child",
            "Glow lights and DJ atmosphere"
        ],
        "private_room_upgrade": "$5 per jumper",
        "notes": "Friday & Saturday nights ONLY - 3 hours total party time",
        "restrictions": {
            "days": ["Friday", "Saturday"],
            "time_range": "Evening hours only"
        }
    }
}


def get_package_summary(package_name: str) -> str:
    """Get a formatted summary of a package for display"""
    if package_name not in PACKAGES:
        return f"Package '{package_name}' not found."
    
    pkg = PACKAGES[package_name]
    summary = f"**{package_name} Package**\n"
    summary += f"Price: ${pkg['price_per_jumper']} per jumper (minimum {pkg['min_jumpers']} jumpers)\n"
    summary += f"Jump Time: {pkg['jump_time']}\n"
    summary += f"Table Time: {pkg['table_time']}\n\n"
    summary += "Includes:\n"
    for item in pkg['includes']:
        summary += f"  • {item}\n"
    
    if 'excludes' in pkg and pkg['excludes']:
        summary += "\nNot included:\n"
        for item in pkg['excludes']:
            summary += f"  • {item}\n"
    
    summary += f"\nPrivate Room Upgrade: {pkg['private_room_upgrade']}\n"
    summary += f"Notes: {pkg['notes']}\n"
    
    if 'restrictions' in pkg:
        restrictions = pkg['restrictions']
        summary += f"\n⚠️ Restrictions: Available {', '.join(restrictions['days'])} only"
        if 'time_range' in restrictions:
            summary += f" ({restrictions['time_range']})"
    
    return summary


def calculate_total_price(package_name: str, num_jumpers: int, private_room: bool = False) -> dict:
    """Calculate total price for a booking"""
    if package_name not in PACKAGES:
        return {"error": f"Package '{package_name}' not found"}
    
    pkg = PACKAGES[package_name]
    
    if num_jumpers < pkg['min_jumpers']:
        return {
            "error": f"Minimum {pkg['min_jumpers']} jumpers required for {package_name} package"
        }
    
    base_price = pkg['price_per_jumper'] * num_jumpers
    room_fee = 0
    
    if private_room:
        upgrade_str = pkg['private_room_upgrade']
        # All packages now use $5 per jumper for private room
        if "per jumper" in upgrade_str:
            # Extract per jumper fee (e.g., "$5 per jumper" -> 5)
            room_fee = int(upgrade_str.split("$")[1].split()[0]) * num_jumpers
        elif "Flat" in upgrade_str:
            # Legacy support for flat fees (shouldn't be used now)
            room_fee = int(upgrade_str.split("$")[1].split()[0])
        else:
            # Default to $5 per jumper if format is unclear
            room_fee = 5 * num_jumpers
    
    total = base_price + room_fee
    
    return {
        "package": package_name,
        "num_jumpers": num_jumpers,
        "base_price": base_price,
        "private_room": private_room,
        "room_fee": room_fee,
        "total": total,
        "breakdown": {
            "package_price": f"${pkg['price_per_jumper']} × {num_jumpers} = ${base_price}",
            "room_upgrade": f"${room_fee}" if room_fee > 0 else "None",
            "total": f"${total}"
        }
    }

