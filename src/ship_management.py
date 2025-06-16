import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class Ship:
    def __init__(self, ship_id: str, name: str, capacity: float, speed: float, 
                 fuel_consumption: float, ship_type: str = "Container"):
        self.ship_id = ship_id
        self.name = name
        self.capacity = capacity  # TEU
        self.speed = speed  # ノット
        self.fuel_consumption = fuel_consumption  # L/hour
        self.ship_type = ship_type
        self.current_location = None
        self.status = "Available"  # Available, In Transit, Loading, Unloading
        self.cargo = 0
        self.route_history = []

    def to_dict(self) -> Dict:
        return {
            'ship_id': self.ship_id,
            'name': self.name,
            'capacity': self.capacity,
            'speed': self.speed,
            'fuel_consumption': self.fuel_consumption,
            'ship_type': self.ship_type,
            'current_location': self.current_location,
            'status': self.status,
            'cargo': self.cargo
        }

class ShipManager:
    def __init__(self):
        self.ships = {}
        
    def add_ship(self, ship: Ship) -> bool:
        """船舶を追加"""
        if ship.ship_id in self.ships:
            return False
        self.ships[ship.ship_id] = ship
        return True
    
    def remove_ship(self, ship_id: str) -> bool:
        """船舶を削除"""
        if ship_id in self.ships:
            del self.ships[ship_id]
            return True
        return False
    
    def get_ship(self, ship_id: str) -> Optional[Ship]:
        """船舶を取得"""
        return self.ships.get(ship_id)
    
    def get_all_ships(self) -> List[Ship]:
        """全船舶を取得"""
        return list(self.ships.values())
    
    def get_ships_by_status(self, status: str) -> List[Ship]:
        """ステータス別に船舶を取得"""
        return [ship for ship in self.ships.values() if ship.status == status]
    
    def update_ship_status(self, ship_id: str, status: str) -> bool:
        """船舶ステータスを更新"""
        if ship_id in self.ships:
            self.ships[ship_id].status = status
            return True
        return False
    
    def to_dataframe(self) -> pd.DataFrame:
        """DataFrame形式で出力"""
        data = [ship.to_dict() for ship in self.ships.values()]
        return pd.DataFrame(data)
    
    def from_dataframe(self, df: pd.DataFrame):
        """DataFrameから船舶データを読み込み"""
        self.ships = {}
        for _, row in df.iterrows():
            ship = Ship(
                ship_id=str(row['ship_id']),
                name=str(row['name']),
                capacity=float(row['capacity']),
                speed=float(row['speed']),
                fuel_consumption=float(row['fuel_consumption']),
                ship_type=str(row.get('ship_type', 'Container'))
            )
            self.ships[ship.ship_id] = ship
    
    def export_to_csv(self, filename: str):
        """CSVファイルにエクスポート"""
        df = self.to_dataframe()
        df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    def import_from_csv(self, filename: str):
        """CSVファイルからインポート"""
        df = pd.read_csv(filename)
        self.from_dataframe(df)
