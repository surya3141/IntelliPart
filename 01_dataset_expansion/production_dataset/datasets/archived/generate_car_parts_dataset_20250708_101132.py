"""
This script generates a synthetic dataset of car parts in JSONL format.

The dataset includes detailed information about each part, such as its name,
system, sub-system, material, and various technical specifications. The data
is designed to be realistic and suitable for use in training machine learning
models, testing search algorithms, and performing data analysis.
"""

import json
import random
from pathlib import Path
import os
import glob
import shutil
from datetime import datetime
import sys


def get_script_root():
    return Path(__file__).parent.resolve()
# Define car systems and typical parts with their technical attributes
systems = [
    {
    "parts": [
        {
            "part_name": "Spark Plug Iridium M14",
            "system": "ENGINE",
            "sub_system": "Ignition System",
            "part_type": "Spark Plug",
            "material": "Iridium",
            "thread_size": "M14",
            "resistance": "5kΩ",
            "heat_range": "6",
            "gap": "1.0mm",
            "electrode_type": "Single",
            "insulator_material": "Ceramic",
            "hex_size": "16mm",
            "torque_specs": "20-30 Nm",
            "part_number": "03SP1001",
            "oem_part_number": "SP-IR-14-001"
        },
        {
            "part_name": "Piston Al-Si Alloy 82mm",
            "system": "ENGINE",
            "sub_system": "Piston System",
            "part_type": "Piston",
            "material": "Aluminum-Silicon Alloy",
            "diameter": "82mm",
            "stroke": "92mm",
            "weight": "0.5kg",
            "compression_height": "30mm",
            "pin_diameter": "20mm",
            "ring_groove_width": "1.2mm, 1.5mm, 2.0mm",
            "surface_treatment": "Phosphate Coating",
            "part_number": "03PI1002",
            "oem_part_number": "PI-AL-82-002"
        },
        {
            "part_name": "Crankshaft Forged Steel 550mm",
            "system": "ENGINE",
            "sub_system": "Crankshaft System",
            "part_type": "Crankshaft",
            "material": "Forged Steel",
            "length": "550mm",
            "weight": "14kg",
            "journal_diameter": "60mm",
            "stroke_length": "80mm",
            "number_of_main_bearings": "5",
            "counterweight_design": "Full Counterweight",
            "part_number": "03CR1003",
            "oem_part_number": "CR-FS-550-003"
        },
        {
            "part_name": "Disc Brake Cast Iron 280mm",
            "system": "BRAKES",
            "sub_system": "Front Brakes",
            "part_type": "Disc Brake",
            "material": "Cast Iron",
            "diameter": "280mm",
            "thickness": "22mm",
            "ventilation": "Vented",
            "bolt_pattern": "5x114.3",
            "number_of_cooling_vanes": "32",
            "friction_material_compatibility": "Semi-Metallic",
            "part_number": "06DB1004",
            "oem_part_number": "DB-CI-280-004"
        },
        {
            "part_name": "Brake Pad Ceramic 15mm",
            "system": "BRAKES",
            "sub_system": "Front Brakes",
            "part_type": "Brake Pad",
            "material": "Ceramic",
            "thickness": "15mm",
            "width": "50mm",
            "friction_coefficient": "0.35",
            "backing_plate_material": "Steel",
            "shim_type": "Integrated",
            "brake_system_compatibility": "ABS",
            "part_number": "06BP1005",
            "oem_part_number": "BP-CE-15-005"
        },
        {
            "part_name": "Shock Absorber Hydraulic 450mm",
            "system": "SUSPENSION",
            "sub_system": "Front Suspension",
            "part_type": "Shock Absorber",
            "type": "Hydraulic",
            "length": "450mm",
            "diameter": "45mm",
            "stroke": "140mm",
            "mounting_type": "Eye to Eye",
            "damping_force": "1500N",
            "spring_rate_compatibility": "Progressive",
            "part_number": "04SA1006",
            "oem_part_number": "SA-HY-450-006"
        },
        {
            "part_name": "Coil Spring Steel 12mm",
            "system": "SUSPENSION",
            "sub_system": "Front Suspension",
            "part_type": "Coil Spring",
            "material": "Steel",
            "wire_diameter": "12mm",
            "free_length": "350mm",
            "spring_rate": "30N/mm",
            "number_of_turns": "8",
            "end_type": "Closed and Ground",
            "vehicle_weight_compatibility": "1500kg",
            "part_number": "04CS1007",
            "oem_part_number": "CS-ST-12-007"
        },
        {
            "part_name": "Battery AGM 60Ah",
            "system": "ELECTRICAL POWER SUPPLY",
            "sub_system": "Starting and Charging",
            "part_type": "Battery",
            "type": "AGM",
            "capacity": "60Ah",
            "voltage": "12V",
            "CCA": "600A",
            "dimensions": "242x175x190mm",
            "terminal_type": "SAE",
            "case_material": "Polypropylene",
            "weight": "15kg",
            "part_number": "14BA1008",
            "oem_part_number": "BA-AGM-60-008"
        },
        {
            "part_name": "Alternator 90A",
            "system": "ELECTRICAL POWER SUPPLY",
            "sub_system": "Starting and Charging",
            "part_type": "Alternator",
            "output": "90A",
            "voltage": "12V",
            "weight": "6kg",
            "pulley_type": "Serpentine",
            "mounting_style": "Saddle Mount",
            "rotation": "Clockwise",
            "operating_temperature": "-40°C to 125°C",
            "part_number": "14AL1009",
            "oem_part_number": "AL-90-009"
        },
        {
            "part_name": "Headlamp LED 1500lm",
            "system": "LIGHTING",
            "sub_system": "Front Lighting",
            "part_type": "Headlamp",
            "type": "LED",
            "luminous_flux": "1500lm",
            "voltage": "12V",
            "power": "15W",
            "color_temperature": "6000K",
            "beam_pattern": "Low Beam",
            "lens_material": "Polycarbonate",
            "ingress_protection": "IP67",
            "part_number": "17HL1010",
            "oem_part_number": "HL-LED-1500-010"
        },
        {
            "part_name": "Tail Lamp Halogen",
            "system": "LIGHTING",
            "sub_system": "Rear Lighting",
            "part_type": "Tail Lamp",
            "type": "Halogen",
            "voltage": "12V",
            "power": "10W",
            "bulb_type": "P21/5W",
            "lens_color": "Red",
            "mounting_location": "Rear Bumper",
            "part_number": "17TL1011",
            "oem_part_number": "TL-HL-10-011"
        },
        {
            "part_name": "Steering Rack Rack and Pinion",
            "system": "STEERING",
            "sub_system": "Steering Mechanism",
            "part_type": "Steering Rack",
            "type": "Rack and Pinion",
            "length": "1120mm",
            "input_torque": "4Nm",
            "steering_ratio": "16:1",
            "travel_length": "150mm",
            "mounting_points": "3",
            "part_number": "11SR1012",
            "oem_part_number": "SR-RP-1120-012"
        },
        {
            "part_name": "Power Steering Pump Hydraulic",
            "system": "STEERING",
            "sub_system": "Power Steering",
            "part_type": "Power Steering Pump",
            "type": "Hydraulic",
            "flow_rate": "8L/min",
            "pressure": "120bar",
            "fluid_type": "ATF",
            "drive_type": "Belt-Driven",
            "operating_temperature": "-20°C to 90°C",
            "part_number": "11PS1013",
            "oem_part_number": "PS-HY-8-120-013"
        },
        {
            "part_name": "Air Filter Element",
            "system": "ENGINE",
            "sub_system": "Air Intake System",
            "part_type": "Air Filter",
            "material": "Paper",
            "length": "250mm",
            "width": "150mm",
            "height": "50mm",
            "filtration_efficiency": "99%",
            "part_number": "03AF1014",
            "oem_part_number": "AF-EL-250-014"
        },
        {
            "part_name": "Oil Filter Cartridge",
            "system": "ENGINE",
            "sub_system": "Lubrication System",
            "part_type": "Oil Filter",
            "material": "Cellulose",
            "height": "80mm",
            "diameter": "76mm",
            "thread_size": "M20x1.5",
            "filtration_rating": "20 microns",
            "part_number": "03OF1015",
            "oem_part_number": "OF-CA-80-015"
        },
        {
            "part_name": "Fuel Filter Inline",
            "system": "FUEL",
            "sub_system": "Fuel Delivery",
            "part_type": "Fuel Filter",
            "material": "Paper",
            "length": "150mm",
            "diameter": "60mm",
            "fitting_size": "8mm",
            "filtration_rating": "10 microns",
            "part_number": "10FF1016",
            "oem_part_number": "FF-IN-150-016"
        },
        {
            "part_name": "Coolant Temperature Sensor",
            "system": "ENGINE",
            "sub_system": "Cooling System",
            "part_type": "Temperature Sensor",
            "material": "Brass",
            "thread_size": "M12x1.5",
            "resistance_at_25C": "2.5kΩ",
            "operating_temperature": "-40°C to 130°C",
            "part_number": "03CT1017",
            "oem_part_number": "CT-SE-12-017"
        },
        {
            "part_name": "Radiator Hose Upper",
            "system": "ENGINE",
            "sub_system": "Cooling System",
            "part_type": "Radiator Hose",
            "material": "EPDM Rubber",
            "inner_diameter": "38mm",
            "length": "600mm",
            "operating_pressure": "3 bar",
            "part_number": "03RH1018",
            "oem_part_number": "RH-UP-38-018"
        },
        {
            "part_name": "Thermostat",
            "system": "ENGINE",
            "sub_system": "Cooling System",
            "part_type": "Thermostat",
            "material": "Stainless Steel",
            "opening_temperature": "88°C",
            "housing_material": "Aluminum",
            "part_number": "03TH1019",
            "oem_part_number": "TH-ST-88-019"
        },
        {
            "part_name": "Water Pump",
            "system": "ENGINE",
            "sub_system": "Cooling System",
            "part_type": "Water Pump",
            "material": "Aluminum",
            "flow_rate": "60 L/min",
            "pressure": "1 bar",
            "number_of_blades": "8",
            "part_number": "03WP1020",
            "oem_part_number": "WP-AL-60-020"
        },
        {
            "part_name": "Serpentine Belt",
            "system": "ENGINE",
            "sub_system": "Accessory Drive",
            "part_type": "Belt",
            "material": "EPDM Rubber",
            "width": "20mm",
            "length": "2000mm",
            "number_of_ribs": "6",
            "part_number": "03SB1021",
            "oem_part_number": "SB-EP-20-021"
        },
        {
            "part_name": "Tensioner Pulley",
            "system": "ENGINE",
            "sub_system": "Accessory Drive",
            "part_type": "Pulley",
            "material": "Steel",
            "diameter": "76mm",
            "bearing_type": "Ball Bearing",
            "part_number": "03TP1022",
            "oem_part_number": "TP-ST-76-022"
        },
        {
            "part_name": "Idler Pulley",
            "system": "ENGINE",
            "sub_system": "Accessory Drive",
            "part_type": "Pulley",
            "material": "Steel",
            "diameter": "76mm",
            "bearing_type": "Ball Bearing",
            "part_number": "03IP1023",
            "oem_part_number": "IP-ST-76-023"
        },
        {
            "part_name": "Exhaust Manifold",
            "system": "EXHAUST",
            "sub_system": "Exhaust System",
            "part_type": "Manifold",
            "material": "Cast Iron",
            "outlet_diameter": "60mm",
            "number_of_ports": "4",
            "part_number": "09EM1024",
            "oem_part_number": "EM-CI-60-024"
        },
        {
            "part_name": "Catalytic Converter",
            "system": "EXHAUST",
            "sub_system": "Exhaust System",
            "part_type": "Converter",
            "material": "Ceramic",
            "length": "300mm",
            "diameter": "100mm",
            "cell_density": "400 CPSI",
            "part_number": "09CC1025",
            "oem_part_number": "CC-CE-300-025"
        },
        {
            "part_name": "Muffler",
            "system": "EXHAUST",
            "sub_system": "Exhaust System",
            "part_type": "Muffler",
            "material": "Steel",
            "length": "400mm",
            "diameter": "150mm",
            "noise_reduction": "25 dB",
            "part_number": "09MF1026",
            "oem_part_number": "MF-ST-400-026"
        },
        {
            "part_name": "Oxygen Sensor",
            "system": "ENGINE",
            "sub_system": "Emission Control",
            "part_type": "Sensor",
            "material": "Zirconia",
            "thread_size": "M18x1.5",
            "response_time": "100ms",
            "part_number": "03OS1027",
            "oem_part_number": "OS-ZI-18-027"
        },
        {
            "part_name": "EGR Valve",
            "system": "ENGINE",
            "sub_system": "Emission Control",
            "part_type": "Valve",
            "material": "Aluminum",
            "operating_voltage": "12V",
            "flow_rate": "100 L/min",
            "part_number": "03EG1028",
            "oem_part_number": "EG-VA-12-028"
        },
        {
            "part_name": "Throttle Body",
            "system": "ENGINE",
            "sub_system": "Fuel Delivery",
            "part_type": "Throttle Body",
            "material": "Aluminum",
            "diameter": "60mm",
            "operating_voltage": "12V",
            "part_number": "03TB1029",
            "oem_part_number": "TB-AL-60-029"
        },
        {
            "part_name": "Fuel Injector",
            "system": "ENGINE",
            "sub_system": "Fuel Delivery",
            "part_type": "Injector",
            "material": "Steel",
            "flow_rate": "250 cc/min",
            "resistance": "12 ohms",
            "part_number": "03FI1030",
            "oem_part_number": "FI-ST-250-030"
        },
        {
            "part_name": "Fuel Pump",
            "system": "FUEL",
            "sub_system": "Fuel Delivery",
            "part_type": "Pump",
            "material": "Steel",
            "operating_voltage": "12V",
            "flow_rate": "100 L/hr",
            "part_number": "10FP1031",
            "oem_part_number": "FP-ST-12-031"
        },
        {
            "part_name": "Fuel Tank",
            "system": "FUEL",
            "sub_system": "Fuel Storage",
            "part_type": "Tank",
            "material": "Plastic",
            "capacity": "60 L",
            "wall_thickness": "5mm",
            "part_number": "10FT1032",
            "oem_part_number": "FT-PL-60-032"
        },
        {
            "part_name": "Fuel Line",
            "system": "FUEL",
            "sub_system": "Fuel Delivery",
            "part_type": "Line",
            "material": "Rubber",
            "inner_diameter": "8mm",
            "operating_pressure": "6 bar",
            "part_number": "10FL1033",
            "oem_part_number": "FL-RB-8-033"
        },
        {
            "part_name": "ABS Sensor",
            "system": "BRAKES",
            "sub_system": "ABS System",
            "part_type": "Sensor",
            "material": "Plastic",
            "operating_voltage": "5V",
            "gap": "1mm",
            "part_number": "06AS1034",
            "oem_part_number": "AS-PL-5-034"
        },
        {
            "part_name": "Brake Caliper",
            "system": "BRAKES",
            "sub_system": "Front Brakes",
            "part_type": "Caliper",
            "material": "Aluminum",
            "piston_diameter": "40mm",
            "number_of_pistons": "2",
            "part_number": "06BC1035",
            "oem_part_number": "BC-AL-40-035"
        },
        {
            "part_name": "Brake Master Cylinder",
            "system": "BRAKES",
            "sub_system": "Hydraulics",
            "part_type": "Cylinder",
            "material": "Aluminum",
            "bore_diameter": "25mm",
            "outlet_ports": "2",
            "part_number": "06MC1036",
            "oem_part_number": "MC-AL-25-036"
        },
        {
            "part_name": "Brake Booster",
            "system": "BRAKES",
            "sub_system": "Hydraulics",
            "part_type": "Booster",
            "material": "Steel",
            "diameter": "200mm",
            "input_force": "500N",
            "part_number": "06BB1037",
            "oem_part_number": "BB-ST-200-037"
        },
        {
            "part_name": "Brake Hose",
            "system": "BRAKES",
            "sub_system": "Hydraulics",
            "part_type": "Hose",
            "material": "Rubber",
            "inner_diameter": "3.2mm",
            "length": "500mm",
            "part_number": "06BH1038",
            "oem_part_number": "BH-RB-3-038"
        },
        {
            "part_name": "Parking Brake Cable",
            "system": "BRAKES",
            "sub_system": "Rear Brakes",
            "part_type": "Cable",
            "material": "Steel",
            "length": "1500mm",
            "tensile_strength": "2000N",
            "part_number": "06PC1039",
            "oem_part_number": "PC-ST-1500-039"
        },
        {
            "part_name": "Leaf Spring",
            "system": "SUSPENSION",
            "sub_system": "Rear Suspension",
            "part_type": "Spring",
            "material": "Steel",
            "length": "1200mm",
            "width": "70mm",
            "number_of_leaves": "5",
            "part_number": "04LS1040",
            "oem_part_number": "LS-ST-1200-040"
        },
        {
            "part_name": "Stabilizer Bar",
            "system": "SUSPENSION",
            "sub_system": "Front Suspension",
            "part_type": "Bar",
            "material": "Steel",
            "diameter": "25mm",
            "length": "1000mm",
            "part_number": "04SB1041",
            "oem_part_number": "SB-ST-25-041"
        },
        {
            "part_name": "Control Arm",
            "system": "SUSPENSION",
            "sub_system": "Front Suspension",
            "part_type": "Arm",
            "material": "Steel",
            "length": "400mm",
            "bushing_material": "Rubber",
            "part_number": "04CA1042",
            "oem_part_number": "CA-ST-400-042"
        },
        {
            "part_name": "Ball Joint",
            "system": "SUSPENSION",
            "sub_system": "Front Suspension",
            "part_type": "Joint",
            "material": "Steel",
            "taper_angle": "7 degrees",
            "thread_size": "M14x1.5",
            "part_number": "04BJ1043",
            "oem_part_number": "BJ-ST-7-043"
        },
        {
            "part_name": "Wheel Hub",
            "system": "SUSPENSION",
            "sub_system": "Front Suspension",
            "part_type": "Hub",
            "material": "Steel",
            "bolt_pattern": "5x114.3",
            "flange_diameter": "140mm",
            "part_number": "04WH1044",
            "oem_part_number": "WH-ST-5-044"
        },
        {
            "part_name": "Wheel Bearing",
            "system": "SUSPENSION",
            "sub_system": "Front Suspension",
            "part_type": "Bearing",
            "material": "Steel",
            "inner_diameter": "40mm",
            "outer_diameter": "72mm",
            "part_number": "04WB1045",
            "oem_part_number": "WB-ST-40-045"
        },
        {
            "part_name": "Tie Rod End",
            "system": "STEERING",
            "sub_system": "Steering Linkage",
            "part_type": "End",
            "material": "Steel",
            "thread_size": "M14x1.5",
            "taper_angle": "7 degrees",
            "part_number": "11TE1046",
            "oem_part_number": "TE-ST-14-046"
        },
        {
            "part_name": "Steering Knuckle",
            "system": "STEERING",
            "sub_system": "Steering Linkage",
            "part_type": "Knuckle",
            "material": "Steel",
            "steering_arm_length": "150mm",
            "ball_joint_taper": "7 degrees",
            "part_number": "11SK1047",
            "oem_part_number": "SK-ST-150-047"
        },
        {
            "part_name": "Steering Column",
            "system": "STEERING",
            "sub_system": "Steering Mechanism",
            "part_type": "Column",
            "material": "Steel",
            "length": "800mm",
            "diameter": "48mm",
            "part_number": "11SC1048",
            "oem_part_number": "SC-ST-800-048"
        },
        {
            "part_name": "Steering Wheel",
            "system": "STEERING",
            "sub_system": "Steering Mechanism",
            "part_type": "Wheel",
            "material": "Plastic",
            "diameter": "350mm",
            "grip_material": "Leather",
            "part_number": "11SW1049",
            "oem_part_number": "SW-PL-350-049"
        },
        {
            "part_name": "Power Steering Fluid Reservoir",
            "system": "STEERING",
            "sub_system": "Power Steering",
            "part_type": "Reservoir",
            "material": "Plastic",
            "capacity": "1 L",
            "operating_pressure": "5 bar",
            "part_number": "11PR1050",
            "oem_part_number": "PR-PL-1-050"
        },
        {
            "part_name": "Headlight Bulb",
            "system": "LIGHTING",
            "sub_system": "Front Lighting",
            "part_type": "Bulb",
            "type": "Halogen",
            "voltage": "12V",
            "power": "55W",
            "part_number": "17HB1051",
            "oem_part_number": "HB-HL-12-051"
        },
        {
            "part_name": "Taillight Lens",
            "system": "LIGHTING",
            "sub_system": "Rear Lighting",
            "part_type": "Lens",
            "material": "Plastic",
            "color": "Red",
            "part_number": "17TL1052",
            "oem_part_number": "TL-PL-RD-052"
        },
        {
            "part_name": "Turn Signal Bulb",
            "system": "LIGHTING",
            "sub_system": "Signaling",
            "part_type": "Bulb",
            "type": "Incandescent",
            "voltage": "12V",
            "power": "21W",
            "part_number": "17TB1053",
            "oem_part_number": "TB-IN-12-053"
        },
        {
            "part_name": "Fog Light",
            "system": "LIGHTING",
            "sub_system": "Front Lighting",
            "part_type": "Light",
            "type": "LED",
            "voltage": "12V",
            "power": "15W",
            "part_number": "17FL1054",
            "oem_part_number": "FL-LED-12-054"
        },
        {
            "part_name": "License Plate Light",
            "system": "LIGHTING",
            "sub_system": "Rear Lighting",
            "part_type": "Light",
            "type": "LED",
            "voltage": "12V",
            "power": "5W",
            "part_number": "17LL1055",
            "oem_part_number": "LL-LED-12-055"
        },
        {
            "part_name": "Wiper Blade",
            "system": "BODY",
            "sub_system": "Wiping System",
            "part_type": "Blade",
            "material": "Rubber",
            "length": "500mm",
            "connector_type": "Hook",
            "part_number": "01WB1056",
            "oem_part_number": "WB-RB-500-056"
        },
        {
            "part_name": "Wiper Motor",
            "system": "BODY",
            "sub_system": "Wiping System",
            "part_type": "Motor",
            "material": "Steel",
            "operating_voltage": "12V",
            "torque": "5 Nm",
            "part_number": "01WM1057",
            "oem_part_number": "WM-ST-12-057"
        },
        {
            "part_name": "Windshield Washer Pump",
            "system": "BODY",
            "sub_system": "Wiping System",
            "part_type": "Pump",
            "material": "Plastic",
            "operating_voltage": "12V",
            "flow_rate": "2 L/min",
            "part_number": "01WP1058",
            "oem_part_number": "WP-PL-12-058"
        },
        {
            "part_name": "Door Handle",
            "system": "BODY",
            "sub_system": "Door System",
            "part_type": "Handle",
            "material": "Plastic",
            "finish": "Chrome",
            "part_number": "01DH1059",
            "oem_part_number": "DH-PL-CH-059"
        },
        {
            "part_name": "Door Lock Actuator",
            "system": "BODY",
            "sub_system": "Door System",
            "part_type": "Actuator",
            "material": "Steel",
            "operating_voltage": "12V",
            "force": "100 N",
            "part_number": "01DA"
        },
        {
            "part_name": "Side Mirror",
            "system": "BODY",
            "sub_system": "Exterior",
            "part_type": "Mirror",
            "material": "Glass",
            "adjustment_type": "Electric",
            "part_number": "01SM1061",
            "oem_part_number": "SM-GL-12-061"
        },        {
            "part_name": "Seat Belt",
            "system": "SAFETY",
            "sub_system": "Restraints",
            "part_type": "Belt",
            "material": "Polyester",
            "length": "3000mm",
            "width": "50mm",
            "part_number": "25SB1062",
            "oem_part_number": "SB-PO-3000-062"
        },
        {
            "part_name": "Airbag Module",
            "system": "SAFETY",
            "sub_system": "Restraints",
            "part_type": "Module",
            "material": "Steel",
            "gas_type": "Argon",
            "deployment_time": "20ms",
            "part_number": "25AM1063",
            "oem_part_number": "AM-ST-AR-063"
        },
        {
            "part_name": "Horn",
            "system": "SAFETY",
            "sub_system": "Warning System",
            "part_type": "Horn",
            "material": "Steel",
            "operating_voltage": "12V",
            "sound_level": "110 dB",
            "part_number": "25HO1064",
            "oem_part_number": "HO-ST-12-064"
        },
        {
            "part_name": "Reverse Camera",
            "system": "SAFETY",
            "sub_system": "Vision Assistance",
            "part_type": "Camera",
            "material": "Plastic",
            "resolution": "720p",
            "field_of_view": "170 degrees",
            "part_number": "25RC1065",
            "oem_part_number": "RC-PL-720-065"
        },
        {
            "part_name": "Parking Sensor",
            "system": "SAFETY",
            "sub_system": "Vision Assistance",
            "part_type": "Sensor",
            "material": "Plastic",
            "range": "2.5m",
            "frequency": "40 kHz",
            "part_number": "25PS1066",
            "oem_part_number": "PS-PL-2.5-066"
        },
        {
            "part_name": "Battery Cable",
            "system": "ELECTRICAL POWER SUPPLY",
            "sub_system": "Wiring",
            "part_type": "Cable",
            "material": "Copper",
            "gauge": "4 AWG",
            "length": "500mm",
            "part_number": "14BC1067",
            "oem_part_number": "BC-CP-4-067"
        },
        {
            "part_name": "Fuse",
            "system": "ELECTRICAL POWER SUPPLY",
            "sub_system": "Protection",
            "part_type": "Fuse",
            "type": "Blade",
            "amperage": "10A",
            "voltage": "32V",
            "part_number": "14FU1068",
            "oem_part_number": "FU-BL-10-068"
        },
        {
            "part_name": "Relay",
            "system": "ELECTRICAL POWER SUPPLY",
            "sub_system": "Switching",
            "part_type": "Relay",
            "material": "Plastic",
            "operating_voltage": "12V",
            "current_rating": "30A",
            "part_number": "14RE1069",
            "oem_part_number": "RE-PL-12-069"
        },
        {
            "part_name": "Starter Motor",
            "system": "ELECTRICAL POWER SUPPLY",
            "sub_system": "Starting System",
            "part_type": "Motor",
            "material": "Steel",
            "operating_voltage": "12V",
            "power": "1.5 kW",
            "part_number": "14SM1070",
            "oem_part_number": "SM-ST-12-070"
        },
        {
            "part_name": "Spark Plug Wire",
            "system": "ELECTRICAL POWER SUPPLY",
            "sub_system": "Ignition System",
            "part_type": "Wire",
            "material": "Silicone",
            "resistance": "500 ohms/meter",
            "length": "400mm",
            "part_number": "14SW1071",
            "oem_part_number": "SW-SI-500-071"
        },
        {
            "part_name": "Clutch Disc",
            "system": "CLUTCH",
            "sub_system": "Clutch System",
            "part_type": "Disc",
            "material": "Organic",
            "diameter": "240mm",
            "spline_count": "23",
            "part_number": "08CD1072",
            "oem_part_number": "CD-OR-240-072"
        },
        {
            "part_name": "Pressure Plate",
            "system": "CLUTCH",
            "sub_system": "Clutch System",
            "part_type": "Plate",
            "material": "Steel",
            "diameter": "240mm",
            "clamp_load": "5000N",
            "part_number": "08PP1073",
            "oem_part_number": "PP-ST-240-073"
        },
        {
            "part_name": "Release Bearing",
            "system": "CLUTCH",
            "sub_system": "Clutch System",
            "part_type": "Bearing",
            "material": "Steel",
            "inner_diameter": "40mm",
            "outer_diameter": "72mm",
            "part_number": "08RB1074",
            "oem_part_number": "RB-ST-40-074"
        },
        {
            "part_name": "Clutch Cable",
            "system": "CLUTCH",
            "sub_system": "Clutch System",
            "part_type": "Cable",
            "material": "Steel",
            "length": "1200mm",
            "tensile_strength": "2000N",
            "part_number": "08CC1075",
            "oem_part_number": "CC-ST-1200-075"
        },
        {
            "part_name": "Flywheel",
            "system": "ENGINE",
            "sub_system": "Rotating Assembly",
            "part_type": "Wheel",
            "material": "Steel",
            "diameter": "280mm",
            "tooth_count": "130",
            "part_number": "03FW1076",
            "oem_part_number": "FW-ST-280-076"
        },
        {
            "part_name": "Connecting Rod",
            "system": "ENGINE",
            "sub_system": "Rotating Assembly",
            "part_type": "Rod",
            "material": "Forged Steel",
            "length": "150mm",
            "big_end_diameter": "55mm",
            "part_number": "03CR1077",
            "oem_part_number": "CR-FS-150-077"
        },
        {
            "part_name": "Camshaft",
            "system": "ENGINE",
            "sub_system": "Valve Train",
            "part_type": "Shaft",
            "material": "Cast Iron",
            "lobe_lift": "10mm",
            "duration": "270 degrees",
            "part_number": "03CS1078",
            "oem_part_number": "CS-CI-10-078"
        },
        {
            "part_name": "Valve Spring",
            "system": "ENGINE",
            "sub_system": "Valve Train",
            "part_type": "Spring",
            "material": "Steel",
            "free_length": "50mm",
            "spring_rate": "40 N/mm",
            "part_number": "03VS1079",
            "oem_part_number": "VS-ST-50-079"
        },
        {
            "part_name": "Timing Belt",
            "system": "ENGINE",
            "sub_system": "Valve Train",
            "part_type": "Belt",
            "material": "Rubber",
            "width": "25mm",
            "tooth_count": "150",
            "part_number": "03TB1080",
            "oem_part_number": "TB-RB-25-080"
        },
        {
            "part_name": "Radiator Fan",
            "system": "ENGINE",
            "sub_system": "Cooling System",
            "part_type": "Fan",
            "material": "Plastic",
            "diameter": "400mm",
            "number_of_blades": "7",
            "part_number": "03RF1081",
            "oem_part_number": "RF-PL-400-081"
        },
        {
            "part_name": "Coolant Reservoir",
            "system": "ENGINE",
            "sub_system": "Cooling System",
            "part_type": "Reservoir",
            "material": "Plastic",
            "capacity": "2 L",
            "part_number": "03CR1082",
            "oem_part_number": "CR-PL-2-082"
        },
        {
            "part_name": "Heater Core",
            "system": "CLIMATE CONTROL",
            "sub_system": "Heating System",
            "part_type": "Core",
            "material": "Aluminum",
            "length": "200mm",
            "width": "150mm",
            "part_number": "12HC1083",
            "oem_part_number": "HC-AL-200-083"
        },
        {
            "part_name": "AC Compressor",
            "system": "CLIMATE CONTROL",
            "sub_system": "Cooling System",
            "part_type": "Compressor",
            "material": "Aluminum",
            "displacement": "150 cc",
            "part_number": "12AC1084",
            "oem_part_number": "AC-AL-150-084"
        },
        {
            "part_name": "Condenser Fan",
            "system": "CLIMATE CONTROL",
            "sub_system": "Cooling System",
            "part_type": "Fan",
            "material": "Plastic",
            "diameter": "300mm"
        }
    ]
    }
]

def generate_car_parts_dataset(output_file: str, num_records: int):
    """
    Generates a dataset of car parts and saves it to a JSONL file.

    Args:
        output_file (str): The path to the output JSONL file.
        num_records (int): The number of records to generate.
    """
    
    # Ensure the data directory exists
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        for i in range(num_records):
            part_template = random.choice(random.choice(systems)['parts'])
            
            # Create a mutable copy
            part = part_template.copy()
            
            # Add unique identifier
            part['record_id'] = f"REC-{i+1:05d}"
            
            # Simulate variations
            part['cost'] = f"₹{random.uniform(50, 5000):.2f}"
            part['stock'] = random.randint(0, 200)
            part['production_year'] = random.randint(2018, 2024)
            part['warranty_period'] = f"{random.choice([1, 2, 3, 5])} years"
            part['country_of_origin'] = random.choice(["Germany", "Japan", "USA", "China", "South Korea"])
            
            # Add some descriptive text
            part['description'] = f"{part['part_name']} for {part['system']} system. Manufactured by {random.choice(['Bosch', 'Denso', 'Magna', 'ZF', 'Continental'])}."
            
            # Write as JSONL
            f.write(json.dumps(part) + '\n')
            
    print(f"✅ Generated {num_records} records and saved to {output_file}")

def delete_existing_batches(batch_dir, pattern="automotive_parts_batch_*.jsonl"):
    batch_path = Path(batch_dir)
    for file in batch_path.glob(pattern):
        try:
            file.unlink()
        except Exception as e:
            print(f"Failed to delete {file}: {e}")

def move_existing_batches_to_archive(batch_dir, pattern="automotive_parts_batch_*.jsonl"):
    batch_path = Path(batch_dir)
    files_to_move = list(batch_path.glob(pattern))
    # Always create the archive folder under datasets/archived/<timestamp>
    archive_path = batch_path / "archived" / datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path.mkdir(parents=True, exist_ok=True)
    if not files_to_move:
        print(f"No batch files found to archive. Created archive folder: {archive_path}")
        return
    for file in files_to_move:
        try:
            shutil.move(str(file), str(archive_path / file.name))
        except Exception as e:
            print(f"Failed to move {file} to archive: {e}")
    print(f"Moved {len(files_to_move)} batch files to {archive_path}")

if __name__ == "__main__":
    output_dir = Path("01_dataset_expansion/production_dataset")
    batch_dir = output_dir / "datasets"
    batch_dir.mkdir(parents=True, exist_ok=True)
    output_file = str(output_dir / "expanded_car_parts_dataset.jsonl")
    num_records = 10000  # Generate 10,000 records

    # Move all existing batch files to a timestamped archive folder under datasets/archived before generating new ones
    move_existing_batches_to_archive(batch_dir)

    # Create folders for documentation, images, and technical drawings (and their own archived subfolders)
    for subfolder in ["documentation", "images", "technical_drawings"]:
        folder = output_dir / subfolder
        folder.mkdir(exist_ok=True)
        (folder / "archived").mkdir(exist_ok=True)

    # Generate the dataset
    generate_car_parts_dataset(output_file, num_records)

    # Print a confirmation message
    print(f"Generated {num_records} records and saved to {output_file}")
