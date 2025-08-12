import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List

# Constants
VAT_RATE = 0.19  # 19% VAT rate
BASE_PATH = "../DataEngineeringChallenge/DataEngineeringChallenge/src/"

def load_asset_data() -> Dict:
    #Load asset data including technical and contract information
    asset_data = {}
    
    # Load technical data to get installed capacities and types
    tech_data_path = os.path.join(BASE_PATH, "vpp/technical_data")
    if os.path.exists(tech_data_path):
        for filename in os.listdir(tech_data_path):
            if filename.endswith('.json'):
                with open(os.path.join(tech_data_path, filename), 'r') as f:
                    data = json.load(f)
                    for asset in data.get('assets', []):
                        asset_id = asset.get('asset_id')
                        if asset_id:
                            asset_type = 'wind' if 'WND' in asset_id else 'solar'
                            tech_attrs = asset.get('technical_attributes', {})
                            asset_data[asset_id] = {
                                'type': asset_type,
                                'capacity': tech_attrs.get('capacity_kw', 0),
                                'price': 45.0 if asset_type == 'wind' else 50.0,  # Default prices
                                'fee': 2.0 if asset_type == 'wind' else 2.5  # Default fees
                            }
    
    # Load contract data for pricing and fees
    contract_path = os.path.join(BASE_PATH, "vpp/contract_data")
    if os.path.exists(contract_path):
        for file in os.listdir(contract_path):
            if file.endswith('.json'):
                with open(os.path.join(contract_path, file)) as f:
                    for record in json.load(f):
                        asset_id = record.get('asset_id')
                        if asset_id in asset_data:
                            asset_data[asset_id].update({
                                'price': record.get('price', asset_data[asset_id]['price']),
                                'fee': record.get('fee', asset_data[asset_id]['fee'])
                            })
    
    return asset_data

def load_production_data() -> pd.DataFrame:
    # Load production data from Task 2
    try:
        df = pd.read_csv("../Task2/output/asset_best_of_infeed.csv")
        df['delivery_start'] = pd.to_datetime(df['delivery_start'])
        return df
    except Exception as e:
        print(f"Error loading production data: {e}")
        return pd.DataFrame()

def load_redispatch_data() -> pd.DataFrame:
    redispatch_path = os.path.join(BASE_PATH, "distribution_system_operator/redispatch")
    dfs = []
    
    if os.path.exists(redispatch_path):
        for file in os.listdir(redispatch_path):
            if file.endswith('.json'):
                with open(os.path.join(redispatch_path, file)) as f:
                    data = json.load(f)
                    dfs.append(pd.DataFrame(data))
    
    if dfs:
        df = pd.concat(dfs)
        df['delivery_start'] = pd.to_datetime(df['delivery_start'])
        return df
    return pd.DataFrame()

def calculate_invoice(asset_id: str, production_data: pd.DataFrame, 
                     asset_data: Dict, redispatch_data: pd.DataFrame) -> Dict:

    # Filter data for this asset
    asset_prod = production_data[production_data['asset_id'] == asset_id]
    asset_info = asset_data[asset_id]
    
    # Calculate base payout
    total_production_mwh = asset_prod['best_of_infeed_kw'].sum() / 1000  # Convert to MWh
    base_payout = total_production_mwh * asset_info['price']
    
    # Calculate fees
    fees = total_production_mwh * asset_info['fee']
    
    # Calculate redispatch compensation
    redispatch_payout = 0
    if not redispatch_data.empty:
        asset_redispatch = redispatch_data[redispatch_data['asset_id'] == asset_id]
        for _, row in asset_redispatch.iterrows():
            forecast = asset_prod[asset_prod['delivery_start'] == row['delivery_start']]['forecast_kw'].iloc[0]
            redispatch_payout += (forecast / 1000) * row['compensation_price']
    
    # Calculate totals with VAT
    total_net = base_payout - fees + redispatch_payout
    total_vat = total_net * VAT_RATE
    
    return {
        'asset_id': asset_id,
        'invoice_date': datetime.now().strftime('%Y-%m-%d'),
        'production_mwh': round(total_production_mwh, 2),
        'base_payout': round(base_payout, 2),
        'fees': round(fees, 2),
        'redispatch_payout': round(redispatch_payout, 2),
        'total_net': round(total_net, 2),
        'vat': round(total_vat, 2),
        'total_gross': round(total_net + total_vat, 2)
    }

def generate_all_invoices() -> List[Dict]:
    print("Loading data...")
    asset_data = load_asset_data()
    production_data = load_production_data()
    redispatch_data = load_redispatch_data()
    
    print(f"Generating invoices for {len(asset_data)} assets...")
    invoices = []
    for asset_id in asset_data:
        try:
            invoice = calculate_invoice(asset_id, production_data, asset_data, redispatch_data)
            invoices.append(invoice)
            print(f"Generated invoice for {asset_id}")
        except Exception as e:
            print(f"Error generating invoice for {asset_id}: {e}")
    
    return invoices

def save_invoices(invoices: List[Dict]):
    os.makedirs("output", exist_ok=True)
    
    # Save as JSON
    with open("output/invoices.json", 'w') as f:
        json.dump(invoices, f, indent=2)
    
    # Save as CSV
    pd.DataFrame(invoices).to_csv("output/invoices.csv", index=False)
    
    print(f"Saved {len(invoices)} invoices to output/")

def main():
    # Generate and save invoices
    invoices = generate_all_invoices()
    save_invoices(invoices)
    
    df = pd.DataFrame(invoices)
    print(df)

if __name__ == "__main__":
    main()
