import pandas as pd
import itertools
from typing import Dict, List, Tuple

# HEADS UP: Sometimes my comments are just my thoughts as I write or organize my code. 
# Most times they're helpful

# Define constants
CONSTRAINTS = {
    "Stamina": 1000,
    "Hit Rating": 300,
    "Expertise Rating": 100
}

MULTIPLIERS = {
    "Attack Power": 1,
    "Strength": 1.2,
    "Agility": 1.7,
    "Intellect": 0.5,
    "Spell Power": 0.8,
    "Critical Strike Rating": 1.3,
    "Haste Rating": 2,
    "Armor Penetration": 1.1
}

EQUIPMENT_SLOTS = [
    "Belt.xlsx",
    "Chest Armor.xlsx",
    "Cloak.xlsx",
    "Gloves.xlsx",
    "Helmets.xlsx",
    "Necklace.xlsx",
    "Pants.xlsx",
    "Ring 1.xlsx",
    "Ring 2.xlsx",
    "Shoes.xlsx",
    "Shoulder Piece.xlsx",
    "Wrist Guards.xlsx"
]

def calculate_item_stats(data: Dict) -> Dict:
    # Calculate power, constraints and cost for a single item
    total_power = 0
    total_constraints = {constraint: 0 for constraint in CONSTRAINTS}
    total_cost = 0
    
    for attribute, value in data.items():
        if attribute in MULTIPLIERS:
            total_power += (MULTIPLIERS[attribute] * value)
        elif attribute in CONSTRAINTS:
            total_constraints[attribute] += value
        else:
            # There's no need for error handling here since every excel sheet has the same format, however, if this were a real-world scenario, I would add error handling.
            total_cost += int(value[:-1])
            
    return {
        "Power": total_power,
        "Constraints": total_constraints,
        "Cost": total_cost
    }

def process_equipment_file(file: str) -> Dict:
    # Process an equipment/armor file and return formatted data (AKA: data structures I can programatically work with)
    df = pd.read_excel(file) # create a dataframe from the excel file
    items = df.iloc[:, 0] # get the item names
    attributes = df.columns[1:] # get the attribute names
    
    #link items and attributes together
    correlations = {
        item: dict(zip(attributes, df.iloc[index, 1:])) 
        for index, item in enumerate(items)
    }
    
    return {
        item: calculate_item_stats(data)
        for item, data in correlations.items()
    }

def find_valid_build(sorted_items_by_slot, build_type: str) -> dict:
    # Find the best valid build that meets all constraints
    current_offset = 0
    valid_build = None
    
    # Keep trying builds until a valid one is found
    while not valid_build:
        current_build = {}
        for slot, items in sorted_items_by_slot.items():
            if current_offset < len(items):
                current_build[slot] = items[current_offset]
        
        if not current_build:
            break
            
        # Constraints are necessary. Let's make sure the build meets them.
        total_constraints = {
            constraint: sum(item[1]['Constraints'][constraint] 
            for item in current_build.values())
            for constraint in CONSTRAINTS
        }
        
        if all(total_constraints[const] >= min_val 
               for const, min_val in CONSTRAINTS.items()):
            valid_build = current_build
            break
            
        current_offset += 1
    
    return valid_build

def main():
     # Create a dictionary to store the processed equipment/armor data
    results_by_file = {}
    
    # Process all equipment files
    for file in EQUIPMENT_SLOTS:
        file_key = file.replace('.xlsx', '')
        result = process_equipment_file(file)
        items = list(result.items())
        
        # Create three sorted lists for different optimization goals
        results_by_file[file_key] = {
            'optimal': sorted(items, 
                key=lambda attr: attr[1]['Power'] / attr[1]['Cost'] if attr[1]['Cost'] > 0 else attr[1]['Power'] / 0.0001, 
                reverse=True),
            'power': sorted(items, 
                key=lambda attr: attr[1]['Power'], 
                reverse=True),
            'cost': sorted(items, 
                key=lambda attr: attr[1]['Cost'])
        }

    # Find valid builds for each optimization type
    builds = {
        'Optimal Build': find_valid_build({slot: items['optimal'] 
            for slot, items in results_by_file.items()}, 'optimal'),
        'Highest Power Build': find_valid_build({slot: items['power'] 
            for slot, items in results_by_file.items()}, 'power'),
        'Lowest Cost Build': find_valid_build({slot: items['cost'] 
            for slot, items in results_by_file.items()}, 'cost')
    }
    
    # Display results for each valid build
    for build_name, build_items in builds.items():
        if build_items:
            total_power = sum(item[1]['Power'] for item in build_items.values())
            total_cost = sum(item[1]['Cost'] for item in build_items.values())
            total_constraints = {
                constraint: sum(item[1]['Constraints'][constraint] 
                for item in build_items.values())
                for constraint in CONSTRAINTS
            }
            
            print(f"\n{build_name}:")
            print("-" * 50)
            for slot, item in build_items.items():
                print(f"{slot}: {item[0]}")
            print(f"\nTotal Power: {total_power}")
            print(f"Total Cost: {total_cost}")
            print(f"Power/Cost Ratio: {total_power/total_cost if total_cost > 0 else 0}")
            print(f"Constraints: {total_constraints}")

if __name__ == "__main__":
    main()