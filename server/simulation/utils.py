from typing import Any

def deep_convert_to_native_types(data: Any) -> Any:
    """
    İç içe geçmiş bir veri yapısındaki tüm NumPy/CuPy sayısal tiplerini
    ve NaN/inf değerlerini JSON serileştirmesiyle uyumlu hale getirir.
    """
    import numpy as np
    import math

    if isinstance(data, dict):
        return {k: deep_convert_to_native_types(v) for k, v in data.items()}
    if isinstance(data, list):
        return [deep_convert_to_native_types(i) for i in data]
    
    # Check for numpy types
    if isinstance(data, (np.integer, np.floating, np.bool_)):
        return data.item()
    
    # Check for NaN/inf in standard Python float
    if isinstance(data, float) and (math.isnan(data) or math.isinf(data)):
        return 0.0  # veya None, duruma göre
        
    return data 