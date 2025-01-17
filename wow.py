import pandas as pd
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt

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

# this function creates a visual representation of the cost vs power analysis
def visualize_cost_vs_power(builds):
    costs = [build['cost'] for build in builds]
    powers = [build['power'] for build in builds]
    
    plt.figure(figsize=(10, 6))
    plt.scatter(costs, powers)
    plt.title('Cost vs Power Analysis')
    plt.xlabel('Cost')
    plt.ylabel('Power')
    
    # Add build numbers as labels
    for i, (cost, power) in enumerate(zip(costs, powers)):
        plt.annotate(f'Build {i+1}', (cost, power))
    
    plt.show()

# this function calculates power, constraints and cost for a single item
# useful for loop processing
def calculate_item_stats(data: Dict) -> Dict:
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

# this function processes an excel file and returns a dictionary of items and their stats
def process_equipment_file(file: str) -> Dict:
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

# this function checks if the constraints are met for a given build
def constraints_met(build: Dict) -> bool:
    total_constraints = {
        constraint: sum(item[0][1]['Constraints'][constraint] 
        for item in build.values())
        for constraint in CONSTRAINTS
    }
    
    return all(total_constraints[const] >= min_val 
              for const, min_val in CONSTRAINTS.items())

# this function displays the builds in text format
def display_builds(builds: List[Dict]):
    for i, build_data in enumerate(builds, 1):
        print(f"\nBuild #{i}")
        print("-" * 50)
        
        for slot, item in build_data['build'].items():
            item_name = item[0][0]
            item_power = item[0][1]['Power']
            print(f"{slot:<15} : {item_name:<30} (Power: {item_power:.2f})")
        
        # Calculate total constraints for this build
        total_constraints = {
            constraint: sum(item[0][1]['Constraints'][constraint] 
            for item in build_data['build'].values())
            for constraint in CONSTRAINTS
        }
        
        print(f"\nBuild {i} Summary:")
        print(f"Total Power: {build_data['power']:.2f}")
        print(f"Total Cost: {build_data['cost']}")
        print(f"Power/Cost Ratio: {build_data['power']/build_data['cost']:.2f}")
        print(f"Total Constraints: {total_constraints}")

# this function generates builds based on the power_by_slot dictionary defined in main()
# as of right now it only generates 10 builds, but it could be modified to generate more
def generate_builds(power_by_slot: Dict, max_builds: int = 10) -> List[Dict]:
    builds = []
    
    # First find highest power valid builds
    for i in range(10):  # Try top 10 items per slot, should already be sorted. I've found that less than 10 items per slot generates a more expensive build list. 10 Gives a more balanced distribution.
        current_build = {
            slot: [items[i]] for slot, items in power_by_slot.items()
        }
        
        if constraints_met(current_build):
            builds.append({
                'build': current_build.copy(),
                'power': sum(item[0][1]['Power'] for item in current_build.values()),
                'cost': sum(item[0][1]['Cost'] for item in current_build.values())
            })
    
    # If we need more builds, generate variations from the best build
    if builds and len(builds) < max_builds:
        best_build = builds[0]['build']
        slots = list(power_by_slot.keys())
        
        # generations will work by swapping out the weakest item in the best build
        while len(builds) < max_builds:
            weakest_slot = min(slots, key=lambda s: best_build[s][0][1]['Power'])
            items = power_by_slot[weakest_slot]
            current_idx = next((i for i, item in enumerate(items) 
                              if item == best_build[weakest_slot][0]), 0)
            
            if current_idx + 1 < len(items):
                best_build[weakest_slot] = [items[current_idx + 1]]
                if constraints_met(best_build):
                    builds.append({
                        'build': best_build.copy(),
                        'power': sum(item[0][1]['Power'] for item in best_build.values()),
                        'cost': sum(item[0][1]['Cost'] for item in best_build.values())
                    })
            
            slots.remove(weakest_slot)
            if not slots:
                break
    
    builds.sort(key=lambda x: x['power'], reverse=True)
    return builds[:max_builds]

def main():
    # Create a dictionary to store the processed equipment/armor data
    power_by_slot = {}
    
    # Process then sort all equipment files
    for file in EQUIPMENT_SLOTS:
        file_key = file.replace('.xlsx', '')
        result = process_equipment_file(file)
        power_by_slot[file_key] = sorted(
            result.items(), 
            key=lambda attr: attr[1]['Power'], 
            reverse=True
        )

    # Make the builds then display them
    builds = generate_builds(power_by_slot)
    display_builds(builds)
    visualize_cost_vs_power(builds)

if __name__ == "__main__":
    main()
