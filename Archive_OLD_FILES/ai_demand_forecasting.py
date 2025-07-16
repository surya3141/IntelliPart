"""
IntelliPart AI Demand Forecasting & Predictive Analytics
Uses machine learning to predict parts demand and optimize inventory
"""

import json
import sqlite3
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import pickle
import os

# Optional ML imports - graceful degradation
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

class DemandForecaster:
    """AI-powered demand forecasting for auto parts."""
    
    def __init__(self, data_path: str = "demand_data.db"):
        self.data_path = data_path
        self.models = {}
        self.features = [
            'day_of_week', 'month', 'quarter', 'is_weekend',
            'avg_demand_7d', 'avg_demand_30d', 'trend_7d',
            'seasonality_factor', 'price_change_pct'
        ]
        self.init_database()
        
    def init_database(self):
        """Initialize demand forecasting database."""
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        
        # Historical demand data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS demand_history (
                id INTEGER PRIMARY KEY,
                part_number TEXT,
                date DATE,
                demand_quantity INTEGER,
                price REAL,
                stock_level INTEGER,
                lead_time INTEGER,
                supplier TEXT,
                season TEXT,
                day_of_week INTEGER,
                is_holiday BOOLEAN DEFAULT 0
            )
        ''')
        
        # Forecast results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS demand_forecasts (
                id INTEGER PRIMARY KEY,
                part_number TEXT,
                forecast_date DATE,
                predicted_demand REAL,
                confidence_interval_low REAL,
                confidence_interval_high REAL,
                model_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Model performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY,
                part_number TEXT,
                model_type TEXT,
                mae REAL,
                mse REAL,
                accuracy_score REAL,
                training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_synthetic_demand_data(self, part_numbers: List[str], days: int = 365):
        """Generate realistic synthetic demand data for testing."""
        import random
        
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute('DELETE FROM demand_history')
        
        base_date = datetime.now() - timedelta(days=days)
        
        for part_number in part_numbers:
            # Each part has different demand characteristics
            base_demand = random.randint(5, 50)
            seasonality = random.uniform(0.5, 2.0)
            trend = random.uniform(-0.1, 0.1)
            volatility = random.uniform(0.1, 0.5)
            
            for day in range(days):
                current_date = base_date + timedelta(days=day)
                
                # Calculate demand with multiple factors
                seasonal_factor = 1 + seasonality * np.sin(2 * np.pi * day / 365)
                trend_factor = 1 + trend * (day / 365)
                weekend_factor = 0.7 if current_date.weekday() >= 5 else 1.0
                random_factor = 1 + random.uniform(-volatility, volatility)
                
                demand = max(0, int(base_demand * seasonal_factor * trend_factor * 
                                   weekend_factor * random_factor))
                
                # Simulate price and stock
                base_price = random.uniform(100, 5000)
                price_variation = random.uniform(0.9, 1.1)
                price = base_price * price_variation
                
                stock_level = random.randint(0, 100)
                lead_time = random.randint(1, 14)
                
                cursor.execute('''
                    INSERT INTO demand_history 
                    (part_number, date, demand_quantity, price, stock_level, 
                     lead_time, supplier, day_of_week)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    part_number,
                    current_date.date(),
                    demand,
                    price,
                    stock_level,
                    lead_time,
                    f'Supplier_{random.randint(1, 5)}',
                    current_date.weekday()
                ))
        
        conn.commit()
        conn.close()
        print(f"Generated {days} days of demand data for {len(part_numbers)} parts")
    
    def extract_features(self, part_number: str) -> List[Tuple]:
        """Extract features for machine learning model."""
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT date, demand_quantity, price, day_of_week
            FROM demand_history
            WHERE part_number = ?
            ORDER BY date
        ''', (part_number,))
        
        data = cursor.fetchall()
        conn.close()
        
        if len(data) < 30:  # Need minimum data for meaningful features
            return []
        
        features = []
        for i in range(7, len(data)):  # Start from day 7 to have rolling averages
            date_str, demand, price, dow = data[i]
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Recent demand data for rolling averages
            recent_7d = [row[1] for row in data[i-7:i]]
            recent_30d = [row[1] for row in data[max(0, i-30):i]]
            
            # Calculate features
            feature_row = [
                dow,  # day_of_week
                date_obj.month,  # month
                (date_obj.month - 1) // 3 + 1,  # quarter
                1 if dow >= 5 else 0,  # is_weekend
                np.mean(recent_7d),  # avg_demand_7d
                np.mean(recent_30d),  # avg_demand_30d
                recent_7d[-1] - recent_7d[0],  # trend_7d
                1 + 0.3 * np.sin(2 * np.pi * date_obj.timetuple().tm_yday / 365),  # seasonality_factor
                0 if i == 0 else (price - data[i-1][2]) / data[i-1][2]  # price_change_pct
            ]
            
            features.append((feature_row, demand))
        
        return features
    
    def train_model(self, part_number: str) -> bool:
        """Train demand forecasting model for a specific part."""
        if not HAS_SKLEARN:
            print("scikit-learn not available - using simple statistical model")
            return self._train_statistical_model(part_number)
        
        feature_data = self.extract_features(part_number)
        if len(feature_data) < 50:
            print(f"Insufficient data for {part_number}")
            return False
        
        # Prepare training data
        X = np.array([row[0] for row in feature_data])
        y = np.array([row[1] for row in feature_data])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train multiple models and select best
        models = {
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
            'LinearRegression': LinearRegression()
        }
        
        best_model = None
        best_score = float('inf')
        best_name = None
        
        for name, model in models.items():
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)
            mae = mean_absolute_error(y_test, predictions)
            
            if mae < best_score:
                best_score = mae
                best_model = model
                best_name = name
        
        # Save model
        model_path = f"models/{part_number}_{best_name}.pkl"
        os.makedirs("models", exist_ok=True)
        with open(model_path, 'wb') as f:
            pickle.dump(best_model, f)
        
        # Save performance metrics
        self._save_model_performance(part_number, best_name, best_score)
        
        self.models[part_number] = {
            'model': best_model,
            'type': best_name,
            'mae': best_score
        }
        
        print(f"Trained {best_name} model for {part_number} (MAE: {best_score:.2f})")
        return True
    
    def _train_statistical_model(self, part_number: str) -> bool:
        """Train simple statistical model when ML libraries aren't available."""
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT demand_quantity FROM demand_history
            WHERE part_number = ?
            ORDER BY date DESC
            LIMIT 30
        ''', (part_number,))
        
        recent_demands = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if len(recent_demands) < 10:
            return False
        
        # Simple statistical model: weighted average with trend
        weights = np.linspace(0.1, 1.0, len(recent_demands))
        avg_demand = np.average(recent_demands, weights=weights)
        
        # Calculate trend
        if len(recent_demands) >= 7:
            recent_avg = np.mean(recent_demands[:7])
            older_avg = np.mean(recent_demands[7:14]) if len(recent_demands) >= 14 else recent_avg
            trend = recent_avg - older_avg
        else:
            trend = 0
        
        self.models[part_number] = {
            'model': 'statistical',
            'avg_demand': avg_demand,
            'trend': trend,
            'type': 'StatisticalAverage'
        }
        
        print(f"Trained statistical model for {part_number}")
        return True
    
    def predict_demand(self, part_number: str, days_ahead: int = 7) -> List[Dict]:
        """Predict demand for specified number of days ahead."""
        if part_number not in self.models:
            if not self.train_model(part_number):
                return []
        
        model_info = self.models[part_number]
        predictions = []
        
        if model_info['type'] == 'StatisticalAverage':
            # Simple statistical prediction
            base_demand = model_info['avg_demand']
            trend = model_info['trend']
            
            for day in range(1, days_ahead + 1):
                predicted = max(0, base_demand + trend * day)
                predictions.append({
                    'date': (datetime.now() + timedelta(days=day)).date(),
                    'predicted_demand': round(predicted, 2),
                    'confidence_low': round(predicted * 0.8, 2),
                    'confidence_high': round(predicted * 1.2, 2)
                })
        
        elif HAS_SKLEARN:
            # ML-based prediction
            model = model_info['model']
            
            for day in range(1, days_ahead + 1):
                future_date = datetime.now() + timedelta(days=day)
                
                # Create features for future date (simplified)
                features = [
                    future_date.weekday(),  # day_of_week
                    future_date.month,  # month
                    (future_date.month - 1) // 3 + 1,  # quarter
                    1 if future_date.weekday() >= 5 else 0,  # is_weekend
                    model_info.get('avg_demand', 10),  # avg_demand_7d (approximate)
                    model_info.get('avg_demand', 10),  # avg_demand_30d (approximate)
                    0,  # trend_7d (approximate)
                    1 + 0.3 * np.sin(2 * np.pi * future_date.timetuple().tm_yday / 365),  # seasonality
                    0  # price_change_pct (assume no change)
                ]
                
                predicted = model.predict([features])[0]
                mae = model_info.get('mae', predicted * 0.2)
                
                predictions.append({
                    'date': future_date.date(),
                    'predicted_demand': round(max(0, predicted), 2),
                    'confidence_low': round(max(0, predicted - mae), 2),
                    'confidence_high': round(predicted + mae, 2)
                })
        
        # Save predictions to database
        self._save_predictions(part_number, predictions, model_info['type'])
        
        return predictions
    
    def _save_predictions(self, part_number: str, predictions: List[Dict], model_type: str):
        """Save predictions to database."""
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        
        for pred in predictions:
            cursor.execute('''
                INSERT OR REPLACE INTO demand_forecasts
                (part_number, forecast_date, predicted_demand, 
                 confidence_interval_low, confidence_interval_high, model_used)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                part_number,
                pred['date'],
                pred['predicted_demand'],
                pred['confidence_low'],
                pred['confidence_high'],
                model_type
            ))
        
        conn.commit()
        conn.close()
    
    def _save_model_performance(self, part_number: str, model_type: str, mae: float):
        """Save model performance metrics."""
        conn = sqlite3.connect(self.data_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO model_performance
            (part_number, model_type, mae, accuracy_score)
            VALUES (?, ?, ?, ?)
        ''', (part_number, model_type, mae, 100 - mae))
        
        conn.commit()
        conn.close()
    
    def generate_inventory_recommendations(self, part_number: str) -> Dict[str, Any]:
        """Generate inventory management recommendations."""
        predictions = self.predict_demand(part_number, days_ahead=30)
        
        if not predictions:
            return {}
        
        total_predicted = sum(p['predicted_demand'] for p in predictions)
        max_daily = max(p['predicted_demand'] for p in predictions)
        avg_daily = total_predicted / len(predictions)
        
        # Calculate safety stock (covers 95% of demand variability)
        confidence_range = [p['confidence_high'] - p['predicted_demand'] for p in predictions]
        safety_stock = np.percentile(confidence_range, 95) * 7  # 7 days coverage
        
        return {
            'part_number': part_number,
            'next_30_days_demand': round(total_predicted, 0),
            'average_daily_demand': round(avg_daily, 2),
            'peak_daily_demand': round(max_daily, 2),
            'recommended_safety_stock': round(safety_stock, 0),
            'recommended_reorder_point': round(avg_daily * 7 + safety_stock, 0),  # 7 days lead time
            'recommended_max_stock': round(avg_daily * 30 + safety_stock, 0),  # 30 days supply
            'forecast_confidence': 'HIGH' if len(predictions) >= 7 else 'MEDIUM'
        }
    
    def get_demand_analytics(self, part_numbers: List[str]) -> Dict[str, Any]:
        """Get comprehensive demand analytics."""
        analytics = {
            'total_parts_analyzed': len(part_numbers),
            'successful_forecasts': 0,
            'total_predicted_demand': 0,
            'high_demand_parts': [],
            'slow_moving_parts': [],
            'recommendation_summary': {
                'total_safety_stock_needed': 0,
                'total_investment_required': 0,
                'parts_needing_restocking': 0
            }
        }
        
        for part_number in part_numbers:
            try:
                recommendations = self.generate_inventory_recommendations(part_number)
                if recommendations:
                    analytics['successful_forecasts'] += 1
                    analytics['total_predicted_demand'] += recommendations['next_30_days_demand']
                    
                    # Categorize parts
                    if recommendations['average_daily_demand'] > 5:
                        analytics['high_demand_parts'].append({
                            'part_number': part_number,
                            'daily_demand': recommendations['average_daily_demand']
                        })
                    elif recommendations['average_daily_demand'] < 1:
                        analytics['slow_moving_parts'].append({
                            'part_number': part_number,
                            'daily_demand': recommendations['average_daily_demand']
                        })
            except Exception as e:
                print(f"Error analyzing {part_number}: {e}")
        
        return analytics

def demo_demand_forecasting():
    """Demonstrate demand forecasting capabilities."""
    print("🤖 IntelliPart AI Demand Forecasting Demo")
    print("="*50)
    
    forecaster = DemandForecaster()
    
    # Sample part numbers
    sample_parts = [
        'BRAKE_PAD_001', 'OIL_FILTER_002', 'HEADLIGHT_003',
        'WIPER_BLADE_004', 'AIR_FILTER_005'
    ]
    
    print("Generating synthetic demand data...")
    forecaster.generate_synthetic_demand_data(sample_parts, days=180)
    
    print("\nTraining forecasting models...")
    for part in sample_parts:
        forecaster.train_model(part)
    
    print("\nGenerating forecasts...")
    for part in sample_parts[:3]:  # Demo first 3 parts
        print(f"\n📈 Forecast for {part}:")
        predictions = forecaster.predict_demand(part, days_ahead=7)
        
        for pred in predictions:
            print(f"  {pred['date']}: {pred['predicted_demand']:.1f} units "
                  f"(range: {pred['confidence_low']:.1f} - {pred['confidence_high']:.1f})")
        
        recommendations = forecaster.generate_inventory_recommendations(part)
        print(f"  💡 Recommended safety stock: {recommendations['recommended_safety_stock']:.0f} units")
        print(f"  💡 Reorder point: {recommendations['recommended_reorder_point']:.0f} units")
    
    print("\n📊 Overall Analytics:")
    analytics = forecaster.get_demand_analytics(sample_parts)
    print(f"  Total predicted demand (30 days): {analytics['total_predicted_demand']:.0f} units")
    print(f"  High-demand parts: {len(analytics['high_demand_parts'])}")
    print(f"  Slow-moving parts: {len(analytics['slow_moving_parts'])}")
    
    print("\nDemand forecasting demo completed!")

if __name__ == "__main__":
    demo_demand_forecasting()
