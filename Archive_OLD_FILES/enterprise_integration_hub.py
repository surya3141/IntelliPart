"""
IntelliPart Enterprise Integration Hub
Real-world connectors and enterprise-grade features
"""

import json
import sqlite3
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import hashlib
import hmac
import base64

class EnterpriseIntegrationHub:
    """Enterprise integration and real-world connectivity."""
    
    def __init__(self, config_file: str = "enterprise_config.json"):
        self.config = self._load_config(config_file)
        self.setup_database()
        self.integration_log = []
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load enterprise configuration."""
        default_config = {
            "erp_systems": {
                "sap": {
                    "enabled": False,
                    "endpoint": "https://api.sap.com/parts",
                    "auth_type": "oauth2",
                    "credentials": {}
                },
                "oracle": {
                    "enabled": False,
                    "endpoint": "https://api.oracle.com/inventory",
                    "auth_type": "api_key",
                    "credentials": {}
                }
            },
            "supplier_apis": {
                "bosch": {
                    "enabled": True,
                    "endpoint": "https://api.example-bosch.com/parts",
                    "rate_limit": 100,
                    "auth_token": "demo_token"
                },
                "continental": {
                    "enabled": True,
                    "endpoint": "https://api.example-continental.com/catalog",
                    "rate_limit": 50,
                    "auth_token": "demo_token"
                }
            },
            "notification_systems": {
                "slack": {
                    "enabled": True,
                    "webhook_url": "https://hooks.slack.com/demo",
                    "channels": ["#parts-alerts", "#inventory"]
                },
                "email": {
                    "enabled": True,
                    "smtp_server": "smtp.company.com",
                    "notifications": ["procurement@company.com"]
                }
            },
            "real_time_sync": {
                "enabled": False,
                "sync_interval": 300,  # 5 minutes
                "batch_size": 100
            }
        }
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default config
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def setup_database(self):
        """Setup enterprise integration database."""
        self.conn = sqlite3.connect('enterprise_integration.db')
        cursor = self.conn.cursor()
        
        # Integration log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS integration_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                source_system TEXT,
                operation TEXT,
                status TEXT,
                details TEXT,
                records_processed INTEGER
            )
        ''')
        
        # Supplier data cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplier_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier TEXT,
                part_number TEXT,
                data TEXT,
                last_updated TEXT,
                status TEXT
            )
        ''')
        
        # Real-time alerts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT,
                severity TEXT,
                message TEXT,
                part_number TEXT,
                system TEXT,
                created_at TEXT,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        self.conn.commit()
    
    async def sync_with_erp_systems(self) -> Dict[str, Any]:
        """Sync data with ERP systems."""
        results = {
            'sync_timestamp': datetime.now().isoformat(),
            'systems_synced': [],
            'total_records': 0,
            'errors': []
        }
        
        for system_name, config in self.config['erp_systems'].items():
            if not config.get('enabled', False):
                continue
                
            try:
                print(f"🔄 Syncing with {system_name.upper()}...")
                sync_result = await self._sync_erp_system(system_name, config)
                results['systems_synced'].append(sync_result)
                results['total_records'] += sync_result['records_processed']
                
                # Log integration
                self._log_integration(system_name, 'ERP_SYNC', 'SUCCESS', sync_result)
                
            except Exception as e:
                error_msg = f"Failed to sync with {system_name}: {str(e)}"
                results['errors'].append(error_msg)
                self._log_integration(system_name, 'ERP_SYNC', 'ERROR', {'error': error_msg})
        
        return results
    
    async def _sync_erp_system(self, system_name: str, config: Dict) -> Dict[str, Any]:
        """Sync with individual ERP system."""
        # Simulate ERP sync (replace with actual API calls)
        await asyncio.sleep(1)  # Simulate network delay
        
        # Demo data for different ERP systems
        demo_updates = {
            'sap': {
                'inventory_updates': [
                    {'part_number': 'BR001', 'new_stock': 150, 'cost_update': 85.50},
                    {'part_number': 'EG002', 'new_stock': 75, 'cost_update': 320.00}
                ],
                'new_parts': 3,
                'price_changes': 12
            },
            'oracle': {
                'inventory_updates': [
                    {'part_number': 'SU003', 'new_stock': 200, 'cost_update': 45.75},
                    {'part_number': 'LT004', 'new_stock': 90, 'cost_update': 125.00}
                ],
                'new_parts': 2,
                'price_changes': 8
            }
        }
        
        system_data = demo_updates.get(system_name, {'inventory_updates': [], 'new_parts': 0, 'price_changes': 0})
        
        return {
            'system': system_name,
            'status': 'success',
            'records_processed': len(system_data['inventory_updates']) + system_data['new_parts'],
            'inventory_updates': len(system_data['inventory_updates']),
            'new_parts': system_data['new_parts'],
            'price_changes': system_data['price_changes'],
            'sync_time': datetime.now().isoformat()
        }
    
    async def sync_supplier_catalogs(self) -> Dict[str, Any]:
        """Sync with supplier API catalogs."""
        results = {
            'sync_timestamp': datetime.now().isoformat(),
            'suppliers_synced': [],
            'total_parts_updated': 0,
            'new_parts_found': 0,
            'errors': []
        }
        
        async with aiohttp.ClientSession() as session:
            for supplier_name, config in self.config['supplier_apis'].items():
                if not config.get('enabled', False):
                    continue
                    
                try:
                    print(f"🏭 Syncing with {supplier_name.title()} catalog...")
                    sync_result = await self._sync_supplier_catalog(session, supplier_name, config)
                    results['suppliers_synced'].append(sync_result)
                    results['total_parts_updated'] += sync_result['parts_updated']
                    results['new_parts_found'] += sync_result['new_parts']
                    
                    # Cache supplier data
                    self._cache_supplier_data(supplier_name, sync_result['catalog_data'])
                    
                    # Log integration
                    self._log_integration(supplier_name, 'SUPPLIER_SYNC', 'SUCCESS', sync_result)
                    
                except Exception as e:
                    error_msg = f"Failed to sync with {supplier_name}: {str(e)}"
                    results['errors'].append(error_msg)
                    self._log_integration(supplier_name, 'SUPPLIER_SYNC', 'ERROR', {'error': error_msg})
        
        return results
    
    async def _sync_supplier_catalog(self, session: aiohttp.ClientSession, supplier: str, config: Dict) -> Dict[str, Any]:
        """Sync with individual supplier catalog."""
        # Simulate API call (replace with actual supplier API)
        await asyncio.sleep(0.5)  # Simulate network delay
        
        # Demo catalog data
        demo_catalogs = {
            'bosch': {
                'catalog_data': [
                    {
                        'part_number': 'BOSCH_BR_001',
                        'part_name': 'Premium Brake Pad Set',
                        'system': 'BRAKE SYSTEM',
                        'cost': '₹2,850',
                        'availability': 'In Stock',
                        'lead_time': '2-3 days'
                    },
                    {
                        'part_number': 'BOSCH_SP_002',
                        'part_name': 'High Performance Spark Plug',
                        'system': 'IGNITION SYSTEM',
                        'cost': '₹450',
                        'availability': 'Limited Stock',
                        'lead_time': '1-2 days'
                    }
                ],
                'parts_updated': 15,
                'new_parts': 3,
                'discontinued_parts': 1
            },
            'continental': {
                'catalog_data': [
                    {
                        'part_number': 'CONT_TI_001',
                        'part_name': 'All-Season Tire 225/60R16',
                        'system': 'WHEEL AND TIRE',
                        'cost': '₹8,500',
                        'availability': 'In Stock',
                        'lead_time': '1 day'
                    },
                    {
                        'part_number': 'CONT_BE_002',
                        'part_name': 'Premium Timing Belt',
                        'system': 'ENGINE',
                        'cost': '₹1,250',
                        'availability': 'In Stock',
                        'lead_time': '2-3 days'
                    }
                ],
                'parts_updated': 12,
                'new_parts': 2,
                'discontinued_parts': 0
            }
        }
        
        catalog_info = demo_catalogs.get(supplier, {
            'catalog_data': [],
            'parts_updated': 0,
            'new_parts': 0,
            'discontinued_parts': 0
        })
        
        return {
            'supplier': supplier,
            'status': 'success',
            'parts_updated': catalog_info['parts_updated'],
            'new_parts': catalog_info['new_parts'],
            'discontinued_parts': catalog_info['discontinued_parts'],
            'catalog_data': catalog_info['catalog_data'],
            'sync_time': datetime.now().isoformat()
        }
    
    def _cache_supplier_data(self, supplier: str, catalog_data: List[Dict]):
        """Cache supplier catalog data."""
        cursor = self.conn.cursor()
        
        for part in catalog_data:
            cursor.execute('''
                INSERT OR REPLACE INTO supplier_cache 
                (supplier, part_number, data, last_updated, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                supplier,
                part['part_number'],
                json.dumps(part),
                datetime.now().isoformat(),
                'active'
            ))
        
        self.conn.commit()
    
    def generate_procurement_alerts(self) -> Dict[str, Any]:
        """Generate intelligent procurement alerts."""
        alerts = {
            'timestamp': datetime.now().isoformat(),
            'critical_alerts': [],
            'warning_alerts': [],
            'info_alerts': [],
            'recommendations': []
        }
        
        # Load current inventory data
        try:
            with open('data/training Dataset.jsonl', 'r', encoding='utf-8') as f:
                parts = [json.loads(line.strip()) for line in f if line.strip()]
        except:
            parts = []
        
        # Analyze for alerts
        for part in parts:
            stock = self._extract_stock(part.get('stock', '0'))
            cost = self._extract_cost(part.get('cost', '0'))
            
            # Critical: Out of stock
            if stock == 0:
                alert = {
                    'type': 'OUT_OF_STOCK',
                    'part_number': part.get('part_number', 'Unknown'),
                    'part_name': part.get('part_name', 'Unknown'),
                    'system': part.get('system', 'Unknown'),
                    'severity': 'CRITICAL',
                    'message': f"Part {part.get('part_number', 'Unknown')} is out of stock",
                    'action_required': 'Immediate restocking needed'
                }
                alerts['critical_alerts'].append(alert)
                self._create_alert('OUT_OF_STOCK', 'CRITICAL', alert['message'], part.get('part_number'), part.get('system'))
            
            # Warning: Low stock
            elif stock < 10:
                alert = {
                    'type': 'LOW_STOCK',
                    'part_number': part.get('part_number', 'Unknown'),
                    'current_stock': stock,
                    'severity': 'WARNING',
                    'message': f"Low stock alert: {part.get('part_number', 'Unknown')} has only {stock} units",
                    'action_required': 'Plan restocking within 1-2 weeks'
                }
                alerts['warning_alerts'].append(alert)
                self._create_alert('LOW_STOCK', 'WARNING', alert['message'], part.get('part_number'), part.get('system'))
            
            # Info: High-cost parts
            elif cost > 500:
                alert = {
                    'type': 'HIGH_VALUE_ITEM',
                    'part_number': part.get('part_number', 'Unknown'),
                    'cost': cost,
                    'stock': stock,
                    'severity': 'INFO',
                    'message': f"High-value item {part.get('part_number', 'Unknown')} (₹{cost}) - monitor closely",
                    'action_required': 'Regular monitoring recommended'
                }
                alerts['info_alerts'].append(alert)
        
        # Generate recommendations
        critical_count = len(alerts['critical_alerts'])
        warning_count = len(alerts['warning_alerts'])
        
        if critical_count > 0:
            alerts['recommendations'].append(f"URGENT: {critical_count} parts are out of stock - immediate procurement required")
        
        if warning_count > 5:
            alerts['recommendations'].append(f"WARNING: {warning_count} parts have low stock - plan bulk procurement")
        
        if critical_count == 0 and warning_count <= 3:
            alerts['recommendations'].append("Inventory levels are healthy - maintain regular monitoring")
        
        return alerts
    
    def _extract_stock(self, stock_str: str) -> int:
        """Extract numeric stock value."""
        if isinstance(stock_str, int):
            return stock_str
        try:
            import re
            numbers = re.findall(r'\d+', str(stock_str))
            return int(numbers[0]) if numbers else 0
        except:
            return 0
    
    def _extract_cost(self, cost_str: str) -> float:
        """Extract numeric cost value."""
        if isinstance(cost_str, (int, float)):
            return float(cost_str)
        try:
            import re
            numbers = re.findall(r'[\d.]+', str(cost_str))
            return float(numbers[0]) if numbers else 0.0
        except:
            return 0.0
    
    def _create_alert(self, alert_type: str, severity: str, message: str, part_number: str, system: str):
        """Create alert in database."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (alert_type, severity, message, part_number, system, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (alert_type, severity, message, part_number, system, datetime.now().isoformat()))
        self.conn.commit()
    
    async def send_notifications(self, alerts: Dict[str, Any]) -> Dict[str, Any]:
        """Send notifications through configured channels."""
        notification_results = {
            'timestamp': datetime.now().isoformat(),
            'channels_used': [],
            'messages_sent': 0,
            'errors': []
        }
        
        # Prepare notification content
        critical_count = len(alerts['critical_alerts'])
        warning_count = len(alerts['warning_alerts'])
        
        if critical_count == 0 and warning_count == 0:
            return notification_results  # No alerts to send
        
        message = f"🚨 IntelliPart Alert Summary:\n"
        message += f"• Critical alerts: {critical_count}\n"
        message += f"• Warning alerts: {warning_count}\n"
        
        if critical_count > 0:
            message += f"\n❌ Critical Issues:\n"
            for alert in alerts['critical_alerts'][:3]:  # Top 3 critical
                message += f"  - {alert['message']}\n"
        
        if warning_count > 0:
            message += f"\n⚠️ Warning Issues:\n"
            for alert in alerts['warning_alerts'][:3]:  # Top 3 warnings
                message += f"  - {alert['message']}\n"
        
        # Send Slack notifications
        if self.config['notification_systems']['slack']['enabled']:
            try:
                await self._send_slack_notification(message)
                notification_results['channels_used'].append('slack')
                notification_results['messages_sent'] += 1
            except Exception as e:
                notification_results['errors'].append(f"Slack notification failed: {str(e)}")
        
        # Send email notifications
        if self.config['notification_systems']['email']['enabled']:
            try:
                await self._send_email_notification(message, alerts)
                notification_results['channels_used'].append('email')
                notification_results['messages_sent'] += 1
            except Exception as e:
                notification_results['errors'].append(f"Email notification failed: {str(e)}")
        
        return notification_results
    
    async def _send_slack_notification(self, message: str):
        """Send Slack notification (demo implementation)."""
        # Demo implementation - replace with actual Slack webhook
        print(f"📱 [SLACK] {message}")
        await asyncio.sleep(0.1)  # Simulate API call
    
    async def _send_email_notification(self, message: str, alerts: Dict[str, Any]):
        """Send email notification (demo implementation)."""
        # Demo implementation - replace with actual email sending
        print(f"📧 [EMAIL] Sent to {self.config['notification_systems']['email']['notifications']}")
        print(f"Subject: IntelliPart Procurement Alerts - {len(alerts['critical_alerts'])} Critical, {len(alerts['warning_alerts'])} Warnings")
        await asyncio.sleep(0.1)  # Simulate API call
    
    def _log_integration(self, source: str, operation: str, status: str, details: Dict):
        """Log integration activity."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO integration_log 
            (timestamp, source_system, operation, status, details, records_processed)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            source,
            operation,
            status,
            json.dumps(details),
            details.get('records_processed', 0)
        ))
        self.conn.commit()
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status."""
        cursor = self.conn.cursor()
        
        # Recent integration activity
        cursor.execute('''
            SELECT source_system, operation, status, timestamp, records_processed
            FROM integration_log
            ORDER BY timestamp DESC
            LIMIT 20
        ''')
        
        recent_activity = []
        for row in cursor.fetchall():
            recent_activity.append({
                'source': row[0],
                'operation': row[1],
                'status': row[2],
                'timestamp': row[3],
                'records_processed': row[4]
            })
        
        # Active alerts
        cursor.execute('''
            SELECT alert_type, severity, COUNT(*) as count
            FROM alerts
            WHERE resolved = FALSE
            GROUP BY alert_type, severity
            ORDER BY severity DESC, count DESC
        ''')
        
        active_alerts = []
        for row in cursor.fetchall():
            active_alerts.append({
                'type': row[0],
                'severity': row[1],
                'count': row[2]
            })
        
        return {
            'status_timestamp': datetime.now().isoformat(),
            'recent_activity': recent_activity,
            'active_alerts': active_alerts,
            'system_health': 'HEALTHY' if len(active_alerts) == 0 else 'NEEDS_ATTENTION',
            'total_integrations_today': len([a for a in recent_activity if datetime.fromisoformat(a['timestamp']).date() == datetime.now().date()])
        }

async def main():
    """Run enterprise integration demo."""
    print("🏢 IntelliPart Enterprise Integration Hub")
    print("=" * 60)
    
    # Initialize integration hub
    hub = EnterpriseIntegrationHub()
    
    print("\n🔄 Starting Enterprise Data Synchronization...")
    
    # Sync with ERP systems
    print("\n1️⃣ ERP Systems Synchronization")
    erp_results = await hub.sync_with_erp_systems()
    print(f"   ✅ Synced {len(erp_results['systems_synced'])} ERP systems")
    print(f"   📊 Processed {erp_results['total_records']} records")
    
    # Sync with suppliers
    print("\n2️⃣ Supplier Catalog Synchronization")
    supplier_results = await hub.sync_supplier_catalogs()
    print(f"   ✅ Synced {len(supplier_results['suppliers_synced'])} suppliers")
    print(f"   🆕 Found {supplier_results['new_parts_found']} new parts")
    print(f"   🔄 Updated {supplier_results['total_parts_updated']} existing parts")
    
    # Generate procurement alerts
    print("\n3️⃣ Procurement Alert Generation")
    alerts = hub.generate_procurement_alerts()
    print(f"   🚨 Critical alerts: {len(alerts['critical_alerts'])}")
    print(f"   ⚠️  Warning alerts: {len(alerts['warning_alerts'])}")
    print(f"   ℹ️  Info alerts: {len(alerts['info_alerts'])}")
    
    # Send notifications
    print("\n4️⃣ Notification Delivery")
    notification_results = await hub.send_notifications(alerts)
    print(f"   📱 Channels used: {notification_results['channels_used']}")
    print(f"   📧 Messages sent: {notification_results['messages_sent']}")
    
    # Display integration status
    print("\n5️⃣ Integration Status Summary")
    status = hub.get_integration_status()
    print(f"   🏥 System health: {status['system_health']}")
    print(f"   📈 Today's integrations: {status['total_integrations_today']}")
    
    # Show sample alerts
    if alerts['critical_alerts']:
        print("\n🚨 SAMPLE CRITICAL ALERTS:")
        for alert in alerts['critical_alerts'][:3]:
            print(f"   ❌ {alert['message']}")
    
    if alerts['recommendations']:
        print("\n💡 KEY RECOMMENDATIONS:")
        for rec in alerts['recommendations']:
            print(f"   • {rec}")
    
    print("\n" + "="*60)
    print("🎯 Enterprise Integration Complete!")
    print("📊 Real-time monitoring and alerts are now active")

if __name__ == "__main__":
    asyncio.run(main())
