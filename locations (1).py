#!/usr/bin/env python3
"""
Northern Ireland Locations Dataset Generator
Creates a comprehensive dataset of NI locations with aliases for text matching
"""

import pandas as pd
import json

def create_ni_locations():
    """Create comprehensive Northern Ireland locations dataset"""
    
    data = [
        # --- Counties ---
        ("County Antrim", "Antrim|Co. Antrim|Co Antrim", "County", 54.7180, -6.2070),
        ("County Armagh", "Armagh|Co. Armagh|Co Armagh", "County", 54.3503, -6.6528),
        ("County Down", "Down|Co. Down|Co Down|County Down", "County", 54.3280, -5.7150),
        ("County Fermanagh", "Fermanagh|Co. Fermanagh|Co Fermanagh", "County", 54.3441, -7.6320),
        ("County Londonderry", "Londonderry|Derry|Co. Londonderry|Co Londonderry|County Derry", "County", 54.9966, -7.3086),
        ("County Tyrone", "Tyrone|Co. Tyrone|Co Tyrone", "County", 54.5970, -7.3090),
        
        # --- Major Cities ---
        ("Belfast", "Belfast City|West Belfast|South Belfast|East Belfast|North Belfast|Belfast City Centre", "City", 54.5973, -5.9301),
        ("Lisburn", "Lisburn City", "City", 54.5162, -6.0580),
        ("Newry", "Newry City", "City", 54.1751, -6.3402),
        ("Derry", "Londonderry|Derry City|Londonderry City|Derry/Londonderry", "City", 54.9966, -7.3086),
        ("Armagh", "Armagh City", "City", 54.3503, -6.6528),
        
        # --- Major Towns ---
        ("Carrickfergus", "Carrick", "Town", 54.7158, -5.8058),
        ("Larne", "", "Town", 54.8505, -5.8244),
        ("Ballymena", "", "Town", 54.8639, -6.2760),
        ("Newtownabbey", "", "Town", 54.6590, -5.9090),
        ("Portadown", "Portadown Town", "Town", 54.4251, -6.4425),
        ("Coleraine", "", "Town", 55.1331, -6.6649),
        ("Bangor", "Bangor Town", "Town", 54.6534, -5.6688),
        ("Enniskillen", "", "Town", 54.3464, -7.6400),
        ("Omagh", "Omagh Town", "Town", 54.6000, -7.3000),
        ("Cookstown", "", "Town", 54.6433, -6.7456),
        ("Magherafelt", "", "Town", 54.7535, -6.6073),
        ("Dungannon", "", "Town", 54.5039, -6.7673),
        ("Holywood", "", "Town", 54.6378, -5.8231),
        ("Lisnaskea", "", "Town", 54.2500, -7.4440),
        ("Downpatrick", "", "Town", 54.3280, -5.7150),
        ("Ballymoney", "", "Town", 55.0703, -6.5172),
        ("Banbridge", "", "Town", 54.3489, -6.2704),
        ("Antrim", "Antrim Town", "Town", 54.7180, -6.2070),
        ("Newtownards", "Ards", "Town", 54.5927, -5.6909),
        ("Lurgan", "", "Town", 54.4630, -6.3306),
        ("Craigavon", "", "Town", 54.4472, -6.3872),
        
        # --- Belfast Areas/Neighbourhoods ---
        ("Shankill", "Shankill Road|Shankill Area|The Shankill", "Belfast Area", 54.6050, -5.9500),
        ("Falls", "Falls Road|Falls Area|The Falls", "Belfast Area", 54.5950, -5.9600),
        ("Sandy Row", "Sandy Row Area", "Belfast Area", 54.5880, -5.9380),
        ("Ormeau", "Ormeau Road|Ormeau Area", "Belfast Area", 54.5830, -5.9170),
        ("Donegall Pass", "Donegal Pass", "Belfast Area", 54.5860, -5.9330),
        ("Botanic", "Botanic Avenue|Botanic Area|Botanic Gardens", "Belfast Area", 54.5831, -5.9340),
        ("Andersonstown", "Andersonstown Area", "Belfast Area", 54.5744, -5.9745),
        ("Ballymurphy", "Ballymurphy Area", "Belfast Area", 54.5847, -5.9753),
        ("Short Strand", "Short Strand Area|The Short Strand", "Belfast Area", 54.5950, -5.9050),
        ("Ardoyne", "Ardoyne Area", "Belfast Area", 54.6170, -5.9430),
        ("Crumlin Road", "Crumlin Rd|The Crumlin Road", "Belfast Area", 54.6100, -5.9400),
        ("Woodvale", "Woodvale Area", "Belfast Area", 54.6080, -5.9520),
        ("Ballymacarrett", "", "Belfast Area", 54.5987, -5.8987),
        ("Tigers Bay", "Tiger's Bay", "Belfast Area", 54.6090, -5.9250),
        
        # --- Other Notable Locations ---
        ("Stormont", "Stormont Estate|Parliament Buildings", "Government", 54.5975, -5.8320),
        ("City Hall", "Belfast City Hall", "Government", 54.5964, -5.9300),
        ("Queens University", "QUB|Queen's University Belfast|Queens", "Education", 54.5844, -5.9340),
        ("Ulster University", "UU|University of Ulster", "Education", 54.6010, -5.9290),
        
        # --- Border Towns/Areas ---
        ("Strabane", "", "Town", 54.8238, -7.4687),
        ("Castlederg", "", "Town", 54.7089, -7.5928),
        ("Crossmaglen", "", "Town", 54.0775, -6.6078),
        ("Forkhill", "", "Town", 54.0600, -6.4300),
    ]
    
    df = pd.DataFrame(data, columns=["name", "aliases", "region_type", "latitude", "longitude"])
    
    # Add postcode areas (BT codes) for each location
    postcode_mapping = {
        "Belfast": ["BT1", "BT2", "BT3", "BT4", "BT5", "BT6", "BT7", "BT8", "BT9", "BT10", "BT11", "BT12", "BT13", "BT14", "BT15"],
        "Lisburn": ["BT27", "BT28"],
        "Newtownards": ["BT23"],
        "Bangor": ["BT19", "BT20"],
        "Carrickfergus": ["BT38"],
        "Holywood": ["BT18"],
        "Newtownabbey": ["BT36", "BT37"],
        "Larne": ["BT40"],
        "Antrim": ["BT41"],
        "Ballymena": ["BT42", "BT43"],
        "Ballymoney": ["BT53"],
        "Coleraine": ["BT51", "BT52"],
        "Derry": ["BT47", "BT48"],
        "Strabane": ["BT82"],
        "Omagh": ["BT78", "BT79"],
        "Enniskillen": ["BT74", "BT92", "BT93", "BT94"],
        "Dungannon": ["BT70", "BT71"],
        "Cookstown": ["BT80"],
        "Magherafelt": ["BT45", "BT46"],
        "Portadown": ["BT62", "BT63"],
        "Lurgan": ["BT66", "BT67"],
        "Craigavon": ["BT64", "BT65"],
        "Armagh": ["BT60", "BT61"],
        "Newry": ["BT34", "BT35"],
        "Downpatrick": ["BT30"],
        "Banbridge": ["BT32"],
    }
    
    # Create a mapping of postcodes to areas
    postcode_to_area = {}
    for area, postcodes in postcode_mapping.items():
        for postcode in postcodes:
            postcode_to_area[postcode] = area
    
    return df, postcode_to_area

def save_locations_data():
    """Save locations data in multiple formats for use in analyses"""
    df, postcode_mapping = create_ni_locations()
    
    # Save main CSV
    df.to_csv("ni_locations.csv", index=False)
    print(f"✅ Saved ni_locations.csv with {len(df)} locations")
    
    # Create a simplified matching dictionary for quick lookups
    location_dict = {}
    for _, row in df.iterrows():
        # Add main name
        location_dict[row['name'].lower()] = {
            'official_name': row['name'],
            'type': row['region_type'],
            'lat': row['latitude'],
            'lon': row['longitude']
        }
        
        # Add aliases
        if row['aliases']:
            for alias in row['aliases'].split('|'):
                if alias.strip():
                    location_dict[alias.strip().lower()] = {
                        'official_name': row['name'],
                        'type': row['region_type'],
                        'lat': row['latitude'],
                        'lon': row['longitude']
                    }
    
    # Save as JSON for easy loading
    with open("ni_locations_dict.json", "w") as f:
        json.dump(location_dict, f, indent=2)
    print(f"✅ Saved ni_locations_dict.json with {len(location_dict)} searchable terms")
    
    # Save postcode mapping
    with open("ni_postcode_mapping.json", "w") as f:
        json.dump(postcode_mapping, f, indent=2)
    print(f"✅ Saved ni_postcode_mapping.json")
    
    # Display sample
    print("\nSample locations:")
    print(df.head(10))
    
    return df, location_dict, postcode_mapping

if __name__ == "__main__":
    save_locations_data()
