import pandas as pd
import os
from typing import Optional, Tuple

def load_historical_population_data() -> Optional[pd.DataFrame]:
    """
    'population.csv' dosyasını yükler, temizler ve analiz için hazırlar.

    Returns:
        pd.DataFrame: 'Year' ve 'Population' sütunlarını içeren temizlenmiş DataFrame.
                      Dosya bulunamazsa veya işlenemezse None döner.
    """
    file_path = os.path.join(os.path.dirname(__file__), '..', 'datasets', 'population.csv')
    
    if not os.path.exists(file_path):
        print(f"Veri seti dosyası bulunamadı: {file_path}")
        return None
        
    try:
        df = pd.read_csv(file_path)
        
        # Sadece gerekli sütunları al ve yeniden adlandır
        # 'Average' sütunu farklı kaynakların ortalaması olduğu için en mantıklısı
        df_clean = df[['Year', 'Average']].copy()
        df_clean.rename(columns={'Average': 'Population'}, inplace=True)
        
        # Eksik verileri kaldır
        df_clean.dropna(inplace=True)
        
        # Veri tiplerini ayarla
        df_clean['Year'] = df_clean['Year'].astype(int)
        df_clean['Population'] = df_clean['Population'].astype(float) * 1_000_000 # Milyon olarak ölçekle
        
        print(f"{len(df_clean)} adet geçerli tarihsel popülasyon verisi yüklendi.")
        return df_clean
        
    except Exception as e:
        print(f"Veri seti işlenirken bir hata oluştu: {e}")
        return None

if __name__ == '__main__':
    # Test için
    data = load_historical_population_data()
    if data is not None:
        print("\n--- Veri Seti Önizlemesi ---")
        print(data.head())
        print("\n--- Veri Seti Bilgisi ---")
        data.info()
        
        # Basit bir görselleştirme (eğer matplotlib kuruluysa)
        try:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(12, 6))
            plt.plot(data['Year'], data['Population'])
            plt.title('Tarihsel Dünya Nüfusu')
            plt.xlabel('Yıl')
            plt.ylabel('Nüfus (Milyon)')
            plt.grid(True)
            plt.show()
        except ImportError:
            print("\nGörselleştirme için matplotlib kütüphanesi gerekli.") 