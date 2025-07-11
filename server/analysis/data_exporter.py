import json
import os
from datetime import datetime
from typing import Dict, Any, List
import pandas as pd
from pathlib import Path

class ScientificDataExporter:
    """
    Simülasyon verilerini çeşitli formatlarda (CSV, JSON, Excel) dışa aktarmak
    için merkezi bir sınıftır.
    """
    def __init__(self, output_dir: str = "server/exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def load_snapshot_data_for_gen(self, session_id: str, generation: int) -> pd.DataFrame:
        """Belirtilen jenerasyon için snapshot verisini yükler."""
        snapshot_dir = Path("server/sim_snapshots") / session_id
        gen_str = f"{generation:04d}"
        
        try:
            target_file = next(snapshot_dir.glob(f"gen_{gen_str}_*.json"))
        except StopIteration:
            raise FileNotFoundError(f"Jenerasyon {generation} için snapshot dosyası bulunamadı.")
            
        with open(target_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        agents_data = data.get('agents', [])
        return pd.json_normalize(agents_data, sep='_')

    def export_simulation_data(
        self,
        world_data: Dict[str, Any],
        metrics_history: List[Dict[str, Any]],
        format_type: str = "all"
    ) -> List[str]:
        """Simülasyon verilerini belirtilen formatlarda dışa aktarır."""
        session_id = world_data.get('metadata', {}).get('session_id', 'unknown')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        agents_data = world_data.get('agents', [])
        
        exported_files = []

        if format_type in ["xlsx", "all"]:
            excel_path = self._export_excel(session_id, timestamp, agents_data, metrics_history, world_data.get('metadata', {}))
            exported_files.append(excel_path)
        
        if format_type in ["csv", "all"]:
            csv_paths = self._export_csv(session_id, timestamp, agents_data)
            exported_files.extend(csv_paths)
        
        if format_type in ["json", "all"]:
            json_path = self._export_json(world_data, session_id, timestamp)
            exported_files.append(json_path)
        
        return exported_files
    
    def _export_excel(self, session_id, timestamp, agents_data, metrics_data, metadata) -> str:
        """Verileri Excel dosyasına yazar."""
        excel_path = self.output_dir / f"neomag_analysis_{session_id}_{timestamp}.xlsx"
        with pd.ExcelWriter(str(excel_path), engine='openpyxl') as writer:
            if agents_data:
                pd.DataFrame(agents_data).to_excel(writer, sheet_name='Agents', index=False)
            if metrics_data:
                pd.DataFrame(metrics_data).to_excel(writer, sheet_name='Metrics', index=False)
            if metadata:
                pd.DataFrame([metadata]).to_excel(writer, sheet_name='Metadata', index=False)
        return str(excel_path)

    def _export_csv(self, session_id, timestamp, agents_data) -> List[str]:
        """Ajan verilerini CSV'ye aktarır."""
        if not agents_data:
            return []
        
        csv_path = self.output_dir / f"neomag_data_{session_id}_{timestamp}_agents.csv"
        pd.DataFrame(agents_data).to_csv(csv_path, index=False, encoding='utf-8')
        return [str(csv_path)]

    def _export_json(self, world_data: dict, session_id: str, timestamp: str) -> str:
        """Dünya verisini JSON olarak kaydeder."""
        json_path = self.output_dir / f"neomag_snapshot_{session_id}_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(world_data, f, indent=4)
        return str(json_path)