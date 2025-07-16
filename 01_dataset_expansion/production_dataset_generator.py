#!/usr/bin/env python3
"""
IntelliPart Production Dataset Generator
Generates 200,000+ automotive parts with 50+ technical attributes each
Includes image integration and production-grade error handling
"""

import json
import random
import uuid
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, asdict
import csv
from pathlib import Path

# Setup production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dataset_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TechnicalSpecification:
    """Technical specifications for automotive parts"""
    length_mm: float
    width_mm: float
    height_mm: float
    weight_kg: float
    material: str
    operating_temp_min: int
    operating_temp_max: int
    pressure_rating_bar: Optional[float] = None
    voltage_rating: Optional[str] = None
    current_rating_amp: Optional[float] = None

@dataclass
class CompatibilityInfo:
    """Vehicle compatibility information"""
    vehicle_models: List[str]
    engine_types: List[str]
    year_range: str
    trim_levels: List[str]
    region_compatibility: List[str]

@dataclass
class SupplyChainData:
    """Supply chain and procurement information"""
    primary_supplier: str
    alternate_suppliers: List[str]
    lead_time_days: int
    minimum_order_qty: int
    current_stock: int
    reorder_point: int
    max_stock_level: int
    supplier_rating: float
    country_of_origin: str

@dataclass
class QualityMetrics:
    """Quality and performance metrics"""
    defect_rate_ppm: int
    warranty_months: int
    mtbf_hours: Optional[int]
    return_rate_percent: float
    customer_rating: float
    quality_grade: str
    certification_standards: List[str]

@dataclass
class EnvironmentalData:
    """Environmental and sustainability data"""
    recyclable_percentage: int
    eco_friendly_rating: str
    carbon_footprint_kg: float
    hazardous_materials: List[str]
    environmental_certifications: List[str]

@dataclass
class VisualAssets:
    """Visual and documentation assets"""
    primary_image: str
    technical_drawings: List[str]
    installation_guide: str
    maintenance_manual: str
    exploded_view: str

@dataclass
class AutomotivePart:
    """Complete automotive part with all attributes"""
    # Basic Information
    part_id: str
    name: str
    category: str
    subcategory: str
    manufacturer: str
    oem_part_number: str
    aftermarket_numbers: List[str]
    
    # Technical Specifications
    technical_specs: TechnicalSpecification
    
    # Compatibility
    compatibility: CompatibilityInfo
    
    # Supply Chain
    supply_chain: SupplyChainData
    
    # Quality Metrics
    quality: QualityMetrics
    
    # Environmental Data
    environmental: EnvironmentalData
    
    # Visual Assets
    visual_assets: VisualAssets
    
    # Pricing Information
    cost_price: float
    retail_price: float
    discount_percentage: float
    
    # Additional Attributes (to reach 50+)
    installation_time_minutes: int
    service_interval_km: Optional[int]
    replacement_frequency_months: Optional[int]
    performance_impact: str
    criticality_level: str
    seasonal_demand: str
    market_availability: str
    innovation_score: int
    technology_generation: str
    export_potential: str

class ProductionDatasetGenerator:
    """Production-grade dataset generator for automotive parts"""
    
    def __init__(self, output_dir: str = "production_dataset"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "images").mkdir(exist_ok=True)
        (self.output_dir / "technical_drawings").mkdir(exist_ok=True)
        (self.output_dir / "documentation").mkdir(exist_ok=True)
        (self.output_dir / "datasets").mkdir(exist_ok=True)
        
        # Initialize data pools
        self._initialize_data_pools()
        
        logger.info(f"Dataset generator initialized. Output directory: {self.output_dir}")
    
    def _initialize_data_pools(self):
        """Initialize data pools for realistic part generation"""
        
        # Vehicle models (Mahindra focus)
        self.vehicle_models = [
            "XUV300", "XUV500", "XUV700", "Scorpio", "Scorpio-N", "Thar", "Bolero",
            "Marazzo", "TUV300", "KUV100", "Verito", "Logan", "Xylo", "Quanto"
        ]
        
        # Engine types
        self.engine_types = [
            "1.2L Turbo Petrol", "1.5L Diesel", "2.0L Diesel", "2.2L Diesel",
            "1.5L Petrol", "1.6L Petrol", "2.5L Diesel", "1.2L Petrol"
        ]
        
        # Part categories with realistic subcategories
        self.part_categories = {
            "Engine System": [
                "Engine Block", "Pistons", "Valves", "Camshaft", "Crankshaft",
                "Oil Pump", "Water Pump", "Timing Belt", "Spark Plugs", "Injectors"
            ],
            "Brake System": [
                "Brake Pads", "Brake Discs", "Brake Drums", "Brake Calipers",
                "Master Cylinder", "Brake Lines", "Brake Fluid", "ABS Sensors"
            ],
            "Suspension System": [
                "Shock Absorbers", "Springs", "Struts", "Control Arms",
                "Ball Joints", "Bushings", "Stabilizer Links"
            ],
            "Electrical System": [
                "Alternator", "Starter Motor", "Battery", "Wiring Harness",
                "ECU", "Sensors", "Relays", "Fuses", "LED Lights"
            ],
            "Transmission": [
                "Clutch Disc", "Pressure Plate", "Flywheel", "Transmission Oil",
                "Gear Box", "Drive Shaft", "CV Joints"
            ],
            "Body & Interior": [
                "Door Handles", "Mirrors", "Seats", "Dashboard", "Bumpers",
                "Headlights", "Tail Lights", "Interior Trim"
            ],
            "Cooling System": [
                "Radiator", "Cooling Fan", "Thermostat", "Coolant Hoses",
                "Expansion Tank", "Intercooler"
            ],
            "Fuel System": [
                "Fuel Pump", "Fuel Filter", "Fuel Tank", "Fuel Lines",
                "Fuel Injectors", "Throttle Body"
            ]
        }
        
        # Suppliers (realistic Indian automotive suppliers)
        self.suppliers = [
            "Mahindra Genuine Parts", "Bosch India", "Tata AutoComp", "Motherson Sumi",
            "Bharat Forge", "Amtek Auto", "Sundram Fasteners", "TVS Motor",
            "Ashok Leyland", "Force Motors", "Bajaj Auto", "Hero MotoCorp",
            "Maruti Suzuki", "Hyundai Motors", "Lucas TVS", "Valeo India"
        ]
        
        # Materials
        self.materials = [
            "Steel", "Aluminum", "Cast Iron", "Plastic", "Rubber", "Copper",
            "Brass", "Stainless Steel", "Carbon Fiber", "Ceramic", "Composite"
        ]
        
        # Quality grades
        self.quality_grades = ["Premium", "Standard", "Economy", "OEM", "Aftermarket"]
        
        # Certification standards
        self.certifications = [
            "ISO 9001", "TS 16949", "ISO 14001", "OHSAS 18001",
            "ARAI Certified", "BIS Standard", "Euro 6", "BS VI"
        ]
    
    def _generate_technical_specs(self, category: str, subcategory: str) -> TechnicalSpecification:
        """Generate realistic technical specifications based on part type"""
        
        # Base dimensions vary by category
        if category == "Engine System":
            length = round(random.uniform(50, 500), 1)
            width = round(random.uniform(30, 300), 1)
            height = round(random.uniform(20, 200), 1)
            weight = round(random.uniform(0.1, 50), 2)
        elif category == "Brake System":
            length = round(random.uniform(100, 350), 1)
            width = round(random.uniform(80, 150), 1)
            height = round(random.uniform(10, 80), 1)
            weight = round(random.uniform(0.5, 15), 2)
        else:
            length = round(random.uniform(20, 600), 1)
            width = round(random.uniform(15, 400), 1)
            height = round(random.uniform(5, 300), 1)
            weight = round(random.uniform(0.05, 100), 2)
        
        return TechnicalSpecification(
            length_mm=length,
            width_mm=width,
            height_mm=height,
            weight_kg=weight,
            material=random.choice(self.materials),
            operating_temp_min=random.randint(-40, 0),
            operating_temp_max=random.randint(80, 400),
            pressure_rating_bar=round(random.uniform(1, 10), 1) if random.random() > 0.7 else None,
            voltage_rating=f"{random.choice([12, 24, 48])}V" if random.random() > 0.8 else None,
            current_rating_amp=round(random.uniform(1, 50), 1) if random.random() > 0.8 else None
        )
    
    def _generate_compatibility(self) -> CompatibilityInfo:
        """Generate realistic vehicle compatibility"""
        
        num_models = random.randint(1, 5)
        models = random.sample(self.vehicle_models, min(num_models, len(self.vehicle_models)))
        
        num_engines = random.randint(1, 3)
        engines = random.sample(self.engine_types, min(num_engines, len(self.engine_types)))
        
        start_year = random.randint(2010, 2020)
        end_year = random.randint(start_year, 2024)
        
        trim_levels = ["Base", "W4", "W6", "W8", "W10", "W12"]
        selected_trims = random.sample(trim_levels, random.randint(1, 4))
        
        regions = ["India", "Export", "SAARC", "Middle East", "Africa"]
        selected_regions = random.sample(regions, random.randint(1, 3))
        
        return CompatibilityInfo(
            vehicle_models=models,
            engine_types=engines,
            year_range=f"{start_year}-{end_year}",
            trim_levels=selected_trims,
            region_compatibility=selected_regions
        )
    
    def _generate_supply_chain(self) -> SupplyChainData:
        """Generate realistic supply chain data"""
        
        primary = random.choice(self.suppliers)
        alternates = random.sample([s for s in self.suppliers if s != primary], random.randint(1, 3))
        
        return SupplyChainData(
            primary_supplier=primary,
            alternate_suppliers=alternates,
            lead_time_days=random.randint(7, 90),
            minimum_order_qty=random.choice([50, 100, 200, 500, 1000]),
            current_stock=random.randint(0, 5000),
            reorder_point=random.randint(100, 1000),
            max_stock_level=random.randint(1000, 10000),
            supplier_rating=round(random.uniform(3.0, 5.0), 1),
            country_of_origin=random.choice(["India", "China", "Germany", "Japan", "South Korea"])
        )
    
    def _generate_quality_metrics(self) -> QualityMetrics:
        """Generate realistic quality metrics"""
        
        return QualityMetrics(
            defect_rate_ppm=random.randint(1, 100),
            warranty_months=random.choice([6, 12, 24, 36, 48]),
            mtbf_hours=random.randint(5000, 100000) if random.random() > 0.5 else None,
            return_rate_percent=round(random.uniform(0.1, 5.0), 1),
            customer_rating=round(random.uniform(3.5, 5.0), 1),
            quality_grade=random.choice(self.quality_grades),
            certification_standards=random.sample(self.certifications, random.randint(1, 4))
        )
    
    def _generate_environmental_data(self) -> EnvironmentalData:
        """Generate environmental and sustainability data"""
        
        eco_ratings = ["A+", "A", "B+", "B", "C+", "C"]
        hazardous = ["Lead", "Mercury", "Cadmium", "Chromium VI", "None"]
        env_certs = ["RoHS", "WEEE", "ISO 14001", "Green Building", "Energy Star"]
        
        return EnvironmentalData(
            recyclable_percentage=random.randint(40, 95),
            eco_friendly_rating=random.choice(eco_ratings),
            carbon_footprint_kg=round(random.uniform(0.1, 50), 2),
            hazardous_materials=random.sample(hazardous, random.randint(0, 2)),
            environmental_certifications=random.sample(env_certs, random.randint(0, 3))
        )
    
    def _generate_visual_assets(self, part_id: str, category: str) -> VisualAssets:
        """Generate visual asset paths"""
        
        category_clean = category.lower().replace(" ", "_")
        
        return VisualAssets(
            primary_image=f"images/{category_clean}/{part_id}_main.jpg",
            technical_drawings=[
                f"technical_drawings/{category_clean}/{part_id}_tech.pdf",
                f"technical_drawings/{category_clean}/{part_id}_dimensions.pdf"
            ],
            installation_guide=f"documentation/{category_clean}/{part_id}_install.pdf",
            maintenance_manual=f"documentation/{category_clean}/{part_id}_maintenance.pdf",
            exploded_view=f"images/{category_clean}/{part_id}_exploded.jpg"
        )
    
    def generate_single_part(self, category: str = None) -> AutomotivePart:
        """Generate a single automotive part with all attributes"""
        
        try:
            # Select category and subcategory
            if not category:
                category = random.choice(list(self.part_categories.keys()))
            subcategory = random.choice(self.part_categories[category])
            
            # Generate unique part ID
            part_id = f"MP-{datetime.now().year}-{str(uuid.uuid4())[:8].upper()}"
            
            # Generate part name
            manufacturer = random.choice(self.suppliers)
            name = f"{subcategory} - {random.choice(['Premium', 'Standard', 'Heavy Duty', 'Performance'])}"
            
            # Generate OEM and aftermarket part numbers
            oem_number = f"{manufacturer[:3].upper()}-{random.randint(10000, 99999)}"
            aftermarket_numbers = [
                f"AM-{random.randint(10000, 99999)}" for _ in range(random.randint(0, 3))
            ]
            
            # Generate pricing
            base_cost = random.uniform(100, 10000)
            cost_price = round(base_cost, 2)
            retail_price = round(base_cost * random.uniform(1.5, 3.0), 2)
            discount = random.randint(0, 30)
            
            # Generate additional attributes
            part = AutomotivePart(
                part_id=part_id,
                name=name,
                category=category,
                subcategory=subcategory,
                manufacturer=manufacturer,
                oem_part_number=oem_number,
                aftermarket_numbers=aftermarket_numbers,
                technical_specs=self._generate_technical_specs(category, subcategory),
                compatibility=self._generate_compatibility(),
                supply_chain=self._generate_supply_chain(),
                quality=self._generate_quality_metrics(),
                environmental=self._generate_environmental_data(),
                visual_assets=self._generate_visual_assets(part_id, category),
                cost_price=cost_price,
                retail_price=retail_price,
                discount_percentage=discount,
                installation_time_minutes=random.randint(15, 480),
                service_interval_km=random.choice([10000, 15000, 20000, 30000, None]),
                replacement_frequency_months=random.choice([6, 12, 24, 36, 48, None]),
                performance_impact=random.choice(["High", "Medium", "Low"]),
                criticality_level=random.choice(["Critical", "Important", "Standard", "Optional"]),
                seasonal_demand=random.choice(["High", "Medium", "Low", "Constant"]),
                market_availability=random.choice(["Readily Available", "Limited", "Made to Order"]),
                innovation_score=random.randint(1, 10),
                technology_generation=random.choice(["Gen 1", "Gen 2", "Gen 3", "Gen 4", "Latest"]),
                export_potential=random.choice(["High", "Medium", "Low", "Domestic Only"])
            )
            
            return part
            
        except Exception as e:
            logger.error(f"Error generating part: {str(e)}")
            raise ProductionError(f"Failed to generate automotive part: {str(e)}")
    
    def generate_dataset(self, num_parts: int = 200000, batch_size: int = 1000) -> None:
        """Generate complete dataset with specified number of parts"""
        
        logger.info(f"Starting generation of {num_parts} automotive parts...")
        
        try:
            total_batches = (num_parts + batch_size - 1) // batch_size
            
            for batch_num in range(total_batches):
                batch_start = batch_num * batch_size
                batch_end = min(batch_start + batch_size, num_parts)
                batch_size_actual = batch_end - batch_start
                
                logger.info(f"Generating batch {batch_num + 1}/{total_batches} ({batch_size_actual} parts)")
                
                # Generate batch
                batch_parts = []
                for i in range(batch_size_actual):
                    try:
                        part = self.generate_single_part()
                        batch_parts.append(asdict(part))
                    except Exception as e:
                        logger.warning(f"Skipping part {i} due to error: {str(e)}")
                        continue
                
                # Save batch to file
                batch_filename = self.output_dir / "datasets" / f"automotive_parts_batch_{batch_num + 1:04d}.jsonl"
                with open(batch_filename, 'w', encoding='utf-8') as f:
                    for part in batch_parts:
                        f.write(json.dumps(part, ensure_ascii=False) + '\n')
                
                logger.info(f"Saved batch {batch_num + 1} with {len(batch_parts)} parts to {batch_filename}")
            
            # Generate summary statistics
            self._generate_summary_stats(num_parts)
            
            logger.info(f"Dataset generation completed successfully. Total parts: {num_parts}")
            
        except Exception as e:
            logger.error(f"Dataset generation failed: {str(e)}")
            raise ProductionError(f"Failed to generate dataset: {str(e)}")
    
    def _generate_summary_stats(self, total_parts: int) -> None:
        """Generate summary statistics for the dataset"""
        
        try:
            summary = {
                "dataset_info": {
                    "total_parts": total_parts,
                    "generation_date": datetime.now().isoformat(),
                    "version": "1.0",
                    "format": "JSONL"
                },
                "categories": list(self.part_categories.keys()),
                "total_attributes_per_part": "50+",
                "suppliers": len(self.suppliers),
                "vehicle_models": len(self.vehicle_models),
                "quality_standards": self.certifications
            }
            
            summary_file = self.output_dir / "dataset_summary.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Summary statistics saved to {summary_file}")
            
        except Exception as e:
            logger.warning(f"Failed to generate summary stats: {str(e)}")

class ProductionError(Exception):
    """Custom exception for production errors"""
    pass

def main():
    """Main function to generate production dataset"""
    
    try:
        # Initialize generator
        generator = ProductionDatasetGenerator()
        
        # Generate dataset (start with smaller number for testing)
        test_size = 1000  # Change to 200000 for full dataset
        generator.generate_dataset(num_parts=test_size, batch_size=100)
        
        print(f"\n✅ Successfully generated {test_size} automotive parts!")
        print(f"📁 Output directory: {generator.output_dir}")
        print("📊 Check dataset_summary.json for statistics")
        
    except ProductionError as e:
        logger.error(f"Production error: {str(e)}")
        print(f"❌ Production error: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
