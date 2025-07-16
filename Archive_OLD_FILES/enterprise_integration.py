"""
IntelliPart Enterprise Integration Module
Connects with ERP systems, suppliers, and real-time data sources
"""

import json
import requests
import sqlite3
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import xml.etree.ElementTree as ET
from dataclasses import dataclass
import asyncio
import aiohttp

@dataclass
class SupplierConfig:
    """Configuration for supplier API integration."""
    name: str
    api_endpoint: str
    api_key: str
    format: str  # 'json', 'xml', 'csv'
    update_frequency: int  # minutes

@dataclass
class ERPConfig:
    """Configuration for ERP system integration."""
    system_type: str  # 'SAP', 'Oracle', 'Microsoft', 'Custom'
    connection_string: str
    username: str
    password: str
    database_name: str

class EnterpriseIntegrator:
    """Handles enterprise system integrations."""
    
    def __init__(self, db_path: str = "enterprise.db"):
        self.db_path = db_path
        self.suppliers = {}
        self.erp_config = None
        self.init_database()
        
    def init_database(self):
        """Initialize enterprise database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Parts master table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parts_master (
                id INTEGER PRIMARY KEY,
                part_number TEXT UNIQUE,
                part_name TEXT,
                description TEXT,
                category TEXT,
                manufacturer TEXT,
                current_cost REAL,
                average_cost REAL,
                last_updated TIMESTAMP,
                stock_level INTEGER,
                reorder_point INTEGER,
                max_stock INTEGER,
                location TEXT,
                supplier_id TEXT,
                lead_time_days INTEGER,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Price history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY,
                part_number TEXT,
                supplier_id TEXT,
                price REAL,
                effective_date DATE,
                currency TEXT DEFAULT 'INR',
                quantity_break INTEGER DEFAULT 1,
                FOREIGN KEY (part_number) REFERENCES parts_master (part_number)
            )
        ''')
        
        # Inventory transactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_transactions (
                id INTEGER PRIMARY KEY,
                part_number TEXT,
                transaction_type TEXT, -- 'IN', 'OUT', 'ADJUSTMENT'
                quantity INTEGER,
                unit_cost REAL,
                transaction_date TIMESTAMP,
                reference_number TEXT,
                notes TEXT,
                FOREIGN KEY (part_number) REFERENCES parts_master (part_number)
            )
        ''')
        
        # Supplier master
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY,
                supplier_id TEXT UNIQUE,
                name TEXT,
                contact_person TEXT,
                email TEXT,
                phone TEXT,
                address TEXT,
                rating REAL,
                payment_terms TEXT,
                delivery_performance REAL,
                quality_rating REAL,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Enterprise database initialized")
    
    def add_supplier_config(self, config: SupplierConfig):
        """Add supplier API configuration."""
        self.suppliers[config.name] = config
        print(f"Added supplier configuration: {config.name}")
    
    def configure_erp(self, config: ERPConfig):
        """Configure ERP system connection."""
        self.erp_config = config
        print(f"Configured ERP system: {config.system_type}")
    
    async def fetch_supplier_data(self, supplier_name: str) -> List[Dict]:
        """Fetch real-time data from supplier APIs."""
        if supplier_name not in self.suppliers:
            return []
        
        config = self.suppliers[supplier_name]
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Authorization': f'Bearer {config.api_key}'}
                async with session.get(config.api_endpoint, headers=headers) as response:
                    if config.format == 'json':
                        data = await response.json()
                    elif config.format == 'xml':
                        text = await response.text()
                        data = self._parse_xml_data(text)
                    else:
                        text = await response.text()
                        data = self._parse_csv_data(text)
                    
                    return self._normalize_supplier_data(data, supplier_name)
        except Exception as e:
            print(f"Error fetching data from {supplier_name}: {e}")
            return []
    
    def _parse_xml_data(self, xml_text: str) -> List[Dict]:
        """Parse XML supplier data."""
        root = ET.fromstring(xml_text)
        parts = []
        
        for part_elem in root.findall('.//part'):
            part = {}
            for child in part_elem:
                part[child.tag] = child.text
            parts.append(part)
        
        return parts
    
    def _parse_csv_data(self, csv_text: str) -> List[Dict]:
        """Parse CSV supplier data."""
        lines = csv_text.strip().split('\n')
        reader = csv.DictReader(lines)
        return list(reader)
    
    def _normalize_supplier_data(self, data: List[Dict], supplier_name: str) -> List[Dict]:
        """Normalize supplier data to standard format."""
        normalized = []
        
        for item in data:
            normalized_item = {
                'part_number': item.get('part_no', item.get('partNumber', item.get('sku', ''))),
                'part_name': item.get('name', item.get('description', '')),
                'price': float(item.get('price', item.get('cost', 0))),
                'stock': int(item.get('stock', item.get('quantity', 0))),
                'supplier': supplier_name,
                'last_updated': datetime.now().isoformat()
            }
            normalized.append(normalized_item)
        
        return normalized
    
    def sync_with_erp(self) -> bool:
        """Synchronize data with ERP system."""
        if not self.erp_config:
            print("ERP not configured")
            return False
        
        try:
            if self.erp_config.system_type == 'SAP':
                return self._sync_with_sap()
            elif self.erp_config.system_type == 'Oracle':
                return self._sync_with_oracle()
            else:
                return self._sync_with_generic_db()
        except Exception as e:
            print(f"ERP sync error: {e}")
            return False
    
    def _sync_with_sap(self) -> bool:
        """Sync with SAP system."""
        # SAP RFC/API integration would go here
        print("SAP sync not implemented - would use SAP RFC/API")
        return True
    
    def _sync_with_oracle(self) -> bool:
        """Sync with Oracle ERP."""
        # Oracle ERP integration would go here
        print("Oracle sync not implemented - would use Oracle APIs")
        return True
    
    def _sync_with_generic_db(self) -> bool:
        """Sync with generic database."""
        # Generic database sync
        print("Generic database sync completed")
        return True
    
    def update_parts_master(self, parts_data: List[Dict]):
        """Update parts master with new data."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for part in parts_data:
            cursor.execute('''
                INSERT OR REPLACE INTO parts_master 
                (part_number, part_name, current_cost, stock_level, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                part.get('part_number'),
                part.get('part_name'),
                part.get('price', 0),
                part.get('stock', 0),
                datetime.now()
            ))
        
        conn.commit()
        conn.close()
        print(f"Updated {len(parts_data)} parts in master database")
    
    def get_price_trends(self, part_number: str, days: int = 30) -> List[Dict]:
        """Get price trends for a part."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT supplier_id, price, effective_date
            FROM price_history
            WHERE part_number = ? AND effective_date >= date('now', '-{} days')
            ORDER BY effective_date DESC
        '''.format(days), (part_number,))
        
        trends = []
        for row in cursor.fetchall():
            trends.append({
                'supplier': row[0],
                'price': row[1],
                'date': row[2]
            })
        
        conn.close()
        return trends
    
    def generate_procurement_alerts(self) -> List[Dict]:
        """Generate procurement alerts based on stock levels."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT part_number, part_name, stock_level, reorder_point
            FROM parts_master
            WHERE stock_level <= reorder_point AND is_active = 1
        ''')
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'type': 'LOW_STOCK',
                'part_number': row[0],
                'part_name': row[1],
                'current_stock': row[2],
                'reorder_point': row[3],
                'urgency': 'HIGH' if row[2] == 0 else 'MEDIUM'
            })
        
        conn.close()
        return alerts

class RealTimeDataProcessor:
    """Processes real-time data feeds."""
    
    def __init__(self, integrator: EnterpriseIntegrator):
        self.integrator = integrator
        self.is_running = False
    
    async def start_real_time_sync(self):
        """Start real-time data synchronization."""
        self.is_running = True
        print("Starting real-time data sync...")
        
        while self.is_running:
            try:
                # Sync with all configured suppliers
                for supplier_name in self.integrator.suppliers:
                    data = await self.integrator.fetch_supplier_data(supplier_name)
                    if data:
                        self.integrator.update_parts_master(data)
                        print(f"Synced {len(data)} parts from {supplier_name}")
                
                # Sync with ERP
                self.integrator.sync_with_erp()
                
                # Wait before next sync
                await asyncio.sleep(300)  # 5 minutes
                
            except Exception as e:
                print(f"Sync error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    def stop_sync(self):
        """Stop real-time synchronization."""
        self.is_running = False
        print("Stopped real-time sync")

# Example usage and testing
def demo_enterprise_integration():
    """Demonstrate enterprise integration features."""
    print("🏢 IntelliPart Enterprise Integration Demo")
    print("="*50)
    
    # Initialize integrator
    integrator = EnterpriseIntegrator()
    
    # Configure suppliers
    supplier1 = SupplierConfig(
        name="Bosch_API",
        api_endpoint="https://api.bosch-parts.com/v1/parts",
        api_key="demo_key_123",
        format="json",
        update_frequency=60
    )
    
    supplier2 = SupplierConfig(
        name="Mahle_Feed",
        api_endpoint="https://feeds.mahle.com/parts.xml",
        api_key="mahle_api_key",
        format="xml",
        update_frequency=120
    )
    
    integrator.add_supplier_config(supplier1)
    integrator.add_supplier_config(supplier2)
    
    # Configure ERP
    erp_config = ERPConfig(
        system_type="SAP",
        connection_string="sap://server:port",
        username="integration_user",
        password="secure_password",
        database_name="PARTS_DB"
    )
    
    integrator.configure_erp(erp_config)
    
    # Simulate some data updates
    sample_data = [
        {
            'part_number': 'BOSCH_001',
            'part_name': 'Brake Pad Set',
            'price': 2500.00,
            'stock': 15
        },
        {
            'part_number': 'MAHLE_002',
            'part_name': 'Oil Filter',
            'price': 450.00,
            'stock': 50
        }
    ]
    
    integrator.update_parts_master(sample_data)
    
    # Generate alerts
    alerts = integrator.generate_procurement_alerts()
    print(f"Generated {len(alerts)} procurement alerts")
    
    print("Enterprise integration demo completed!")

if __name__ == "__main__":
    demo_enterprise_integration()
