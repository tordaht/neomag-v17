import pandas as pd
from scipy.stats import ttest_ind
from typing import Dict, Any, Tuple, List
import numpy as np

# Celery entegrasyonu için eklendi
from server.celery_app import celery_app

# Yeni eklenenler
from .dataset_loader import load_historical_population_data
try:
    from dtw import dtw
    DTW_AVAILABLE = True
except ImportError:
    DTW_AVAILABLE = False


def compare_populations_ttest(
    pop1_data: pd.DataFrame, 
    pop2_data: pd.DataFrame, 
    feature: str
) -> Tuple[float, float]:
    """
    İki popülasyonun belirli bir özelliğini (feature) kullanarak 
    bağımsız iki örneklem t-testi gerçekleştirir.

    Args:
        pop1_data (pd.DataFrame): Birinci popülasyonun verileri.
        pop2_data (pd.DataFrame): İkinci popülasyonun verileri.
        feature (str): Karşılaştırılacak olan sütun adı (örn: 'genes_speed').

    Returns:
        Tuple[float, float]: t-istatistiği ve p-değeri.
    """
    # Veri setlerinden ilgili özelliği çıkar
    sample1 = pop1_data[feature].dropna()
    sample2 = pop2_data[feature].dropna()
    
    if len(sample1) < 2 or len(sample2) < 2:
        # Test için yeterli veri yoksa
        return (float('nan'), float('nan'))
        
    # Bağımsız iki örneklem t-testi
    t_statistic, p_value = ttest_ind(sample1, sample2, equal_var=False)
    # Sonuçların float olduğundan emin ol (scipy bazen numpy.float64 döndürebilir)
    t_statistic = float(t_statistic)
    p_value = float(p_value)
    return t_statistic, p_value

def compare_trends_dtw(sim_population_trend: List[float], historical_population_trend: List[float]) -> Dict[str, Any]:
    """
    Simülasyonun popülasyon trendi ile tarihsel veri trendini
    Dinamik Zaman Bükme (DTW) kullanarak karşılaştırır.

    Args:
        sim_population_trend (List[float]): Simülasyonun jenerasyonlara göre popülasyon sayıları.
        historical_population_trend (List[float]): Tarihsel popülasyon verisi.

    Returns:
        Dict[str, Any]: DTW analiz sonucunu içeren bir sözlük.
    """
    if not DTW_AVAILABLE:
        return {"error": "DTW kütüphanesi kurulu değil. Lütfen 'pip install dtw-python' ile kurun."}

    if not sim_population_trend or not historical_population_trend:
        return {"error": "Analiz için yeterli popülasyon trend verisi yok."}

    # Verileri normalize et (0-1 arasına ölçekle)
    sim_norm = (np.array(sim_population_trend) - np.min(sim_population_trend)) / (np.max(sim_population_trend) - np.min(sim_population_trend))
    hist_norm = (np.array(historical_population_trend) - np.min(historical_population_trend)) / (np.max(historical_population_trend) - np.min(historical_population_trend))

    # DTW analizini çalıştır
    alignment = dtw(sim_norm, hist_norm, keep_internals=True)

    return {
        "dtw_distance": alignment.distance,
        "normalized_distance": alignment.normalizedDistance,
        "message": f"İki popülasyon trendi arasındaki normalize edilmiş DTW mesafesi {alignment.normalizedDistance:.4f}. Düşük değerler daha yüksek benzerlik anlamına gelir."
    }


@celery_app.task(name="tasks.run_full_analysis")
def run_full_analysis(
    simulation_data_json: str, 
    real_world_data_json: str
) -> Dict[str, Any]:
    """
    Simülasyon verisi ile gerçek dünya verisi arasında tam bir 
    karşılaştırmalı istatistiksel analiz yürütür.
    Bu fonksiyon bir Celery görevi olarak çalışır. Veriler JSON formatında alınır.

    Args:
        simulation_data_json (str): Simülasyon ajanlarının verilerini içeren JSON string.
        real_world_data_json (str): Karşılaştırılacak gerçek dünya verisini içeren JSON string.

    Returns:
        Dict[str, Any]: Analiz sonuçlarını içeren bir rapor.
    """
    # JSON string'lerinden DataFrame'e dönüşüm
    simulation_data = pd.read_json(simulation_data_json, orient='split')
    real_world_data = pd.read_json(real_world_data_json, orient='split')
    
    analysis_report = {
        'comparison_summary': {},
        'significant_differences': []
    }
    
    features_to_compare = [
        'genes_speed', 
        'genes_energy_efficiency', 
        'genes_detection_range',
        'genes_aggression'
    ]
    
    for feature in features_to_compare:
        if feature not in simulation_data.columns or feature not in real_world_data.columns:
            continue
            
        t_stat, p_value = compare_populations_ttest(simulation_data, real_world_data, feature)
        
        analysis_report['comparison_summary'][feature] = {
            'sim_mean': simulation_data[feature].mean(),
            'real_mean': real_world_data[feature].mean(),
            't_statistic': t_stat,
            'p_value': p_value
        }
        
        # p < 0.05 ise, fark istatistiksel olarak anlamlıdır
        if p_value < 0.05:
            analysis_report['significant_differences'].append({
                'feature': feature,
                'p_value': p_value,
                'message': f"Simülasyon ve gerçek dünya verisi arasında '{feature}' özelliği için istatistiksel olarak anlamlı bir fark bulundu."
            })
            
    return analysis_report 