import json
import random
from faker import Faker

fake = Faker()

# Define Mahindra-specific part categories and their technical attributes
part_types = [
    {
        "type": "Battery",
        "attributes": lambda: {
            "voltage_rating": random.choice([12, 24]),
            "capacity_ah": random.choice([60, 70, 80, 100, 120]),
            "cold_cranking_amps": random.choice([400, 500, 600, 700]),
            "battery_type": random.choice(["Lead-Acid", "AGM", "Lithium-Ion"]),
            "dimensions_mm": f"{random.randint(200,350)}x{random.randint(120,200)}x{random.randint(180,250)}",
            "terminal_type": random.choice(["Top Post", "Side Post", "Bolt Terminal"]),
            "weight_kg": round(random.uniform(10, 35), 1)
        }
    },
    {
        "type": "Clutch Plate",
        "attributes": lambda: {
            "outer_diameter_mm": random.randint(180, 300),
            "inner_diameter_mm": random.randint(100, 180),
            "material": random.choice(["Ceramic", "Organic", "Metallic"]),
            "friction_coefficient": round(random.uniform(0.3, 0.5), 2),
            "num_springs": random.choice([4, 6, 8]),
            "temperature_resistance_c": random.choice([250, 300, 350])
        }
    },
    {
        "type": "Engine Disc/Flywheel",
        "attributes": lambda: {
            "diameter_mm": random.randint(200, 350),
            "weight_kg": round(random.uniform(5, 15), 2),
            "material": random.choice(["Forged Steel", "Aluminum", "Composite"]),
            "surface_finish": random.choice(["Machined", "Polished", "Coated"]),
            "balancing_spec": random.choice(["ISO 1940 G2.5", "ISO 1940 G6.3"]),
            "bolt_pattern": f"{random.choice([6,8,10])}-bolt"
        }
    },
    {
        "type": "Brake Pad",
        "attributes": lambda: {
            "material": random.choice(["Ceramic", "Semi-Metallic", "Organic"]),
            "friction_coefficient": round(random.uniform(0.35, 0.5), 2),
            "thickness_mm": random.randint(10, 20),
            "heat_resistance_c": random.choice([400, 500, 600]),
            "noise_level_db": random.randint(60, 80)
        }
    },
    {
        "type": "Tyre/Wheel",
        "attributes": lambda: {
            "size": random.choice(["205/55R16", "215/60R17", "185/65R15", "235/65R17"]),
            "material": random.choice(["Rubber", "Alloy", "Steel"]),
            "load_index": random.choice([91, 95, 98, 102]),
            "speed_rating": random.choice(["T", "H", "V", "W"]),
            "tread_pattern": random.choice(["Symmetric", "Asymmetric", "Directional"]),
            "pressure_rating_psi": random.choice([30, 32, 35])
        }
    },
    {
        "type": "Radiator",
        "attributes": lambda: {
            "dimensions_mm": f"{random.randint(400,700)}x{random.randint(300,500)}x{random.randint(30,60)}",
            "material": random.choice(["Aluminum", "Copper", "Plastic"]),
            "core_type": random.choice(["Single", "Dual"]),
            "cooling_capacity_btu": random.randint(8000, 20000),
            "hose_connection_mm": random.choice([28, 32, 36])
        }
    },
    {
        "type": "Exhaust System",
        "attributes": lambda: {
            "pipe_diameter_mm": random.choice([45, 50, 55, 60]),
            "material": random.choice(["Stainless Steel", "Aluminized Steel"]),
            "noise_level_db": random.randint(70, 90),
            "emission_compliance": random.choice(["BS6", "BS4", "Euro 6"])
        }
    }
]

models = ["XUV500", "Scorpio", "Thar", "Bolero", "Marazzo", "Alturas", "KUV100", "TUV300", "Verito", "e2o"]

parts = []
base_parts = []
# 1. Create 50 base parts
for i in range(50):
    part_type = random.choice(part_types)
    part_number = f"MHPN-BASE-{10000+i:05d}"
    part_name = f"Mahindra {part_type['type']}"
    system = part_type['type']
    sub_system = fake.word().capitalize() + " Subsystem"
    manufacturer = "Mahindra"
    compatible = random.sample(models, random.randint(1, 3))
    cost = round(random.uniform(500, 20000), 2)
    stock = random.randint(0, 100)
    attributes = part_type['attributes']()
    part = {
        "part_number": part_number,
        "part_name": part_name,
        "system": system,
        "sub_system": sub_system,
        "manufacturer": manufacturer,
        "compatible_models": compatible,
        "cost": cost,
        "stock": stock,
        "description": fake.sentence(nb_words=8)
    }
    part.update(attributes)
    base_parts.append(part)
    parts.append(part)

# 2. For each base part, create 4 similar variants (total 200 similar parts)
for base in base_parts:
    for j in range(4):
        variant = base.copy()
        variant["part_number"] = base["part_number"] + f"-V{j+1}"
        # Slightly tweak 1-2 technical attributes
        for key in variant:
            if isinstance(variant[key], (int, float)) and key not in ["stock", "cost"]:
                variant[key] = variant[key] + random.choice([-1, 0, 1])
            if isinstance(variant[key], str) and key not in ["part_number", "part_name", "system", "sub_system", "manufacturer", "description"]:
                if random.random() < 0.3:
                    variant[key] = variant[key]  # keep same, or add a small suffix
        variant["description"] = fake.sentence(nb_words=8)
        parts.append(variant)

# 3. Fill the rest with random Mahindra parts as before
for i in range(500 - len(parts)):
    part_type = random.choice(part_types)
    part_number = f"MHPN-{20000+i:05d}"
    part_name = f"Mahindra {part_type['type']}"
    system = part_type['type']
    sub_system = fake.word().capitalize() + " Subsystem"
    manufacturer = "Mahindra"
    compatible = random.sample(models, random.randint(1, 3))
    cost = round(random.uniform(500, 20000), 2)
    stock = random.randint(0, 100)
    attributes = part_type['attributes']()
    part = {
        "part_number": part_number,
        "part_name": part_name,
        "system": system,
        "sub_system": sub_system,
        "manufacturer": manufacturer,
        "compatible_models": compatible,
        "cost": cost,
        "stock": stock,
        "description": fake.sentence(nb_words=8)
    }
    part.update(attributes)
    parts.append(part)

with open("synthetic_car_parts_500.jsonl", "w", encoding="utf-8") as f:
    for part in parts:
        f.write(json.dumps(part, ensure_ascii=False) + "\n")

print("Synthetic Mahindra OEM dataset 'synthetic_car_parts_500.jsonl' created with 500 parts, including at least 200 similar variants.")
