import time
import json
import os
from ..simulation.world_v12 import ProductionWorld

# Benchmark Ayarları
BENCHMARK_DURATION_SECONDS = 300  # 5 dakika
INITIAL_POPULATION = 100
WORLD_WIDTH = 1600
WORLD_HEIGHT = 1200
OUTPUT_DIR = "server/benchmarks"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_benchmark():
    """
    Simülasyonu belirli bir süre çalıştırır ve performans metriklerini kaydeder.
    """
    print("Benchmark senaryosu başlatılıyor...")
    print(f"Süre: {BENCHMARK_DURATION_SECONDS} saniye")
    print(f"Popülasyon: {INITIAL_POPULATION} ajan")

    # Simülasyon dünyasını oluştur
    world = ProductionWorld(
        width=WORLD_WIDTH,
        height=WORLD_HEIGHT,
        initial_population=INITIAL_POPULATION
    )

    start_time = time.time()
    end_time = start_time + BENCHMARK_DURATION_SECONDS
    last_update = start_time

    print("Simülasyon döngüsü başladı.")
    while time.time() < end_time:
        now = time.time()
        delta_time = now - last_update
        world.update(delta_time=delta_time)
        last_update = now
        # CPU'yu %100 kilitlememek için çok kısa bir bekleme
        time.sleep(0.001)

    print("Benchmark tamamlandı.")

    # Sonuçları topla
    final_stats = world.get_statistics()
    avg_metrics = world.perf_monitor.get_average_metrics()
    perf_history = world.perf_monitor.get_history()

    benchmark_results = {
        "benchmark_settings": {
            "duration_seconds": BENCHMARK_DURATION_SECONDS,
            "initial_population": INITIAL_POPULATION,
            "world_width": WORLD_WIDTH,
            "world_height": WORLD_HEIGHT,
        },
        "performance_summary": {
            "average_cpu_percent": avg_metrics.get("avg_cpu_percent"),
            "average_memory_mb": avg_metrics.get("avg_memory_mb"),
            "total_ticks": world.ticks,
            "total_generations": world.generation,
        },
        "final_world_stats": {
            "population_size": final_stats.get("population_size"),
            "genetic_summary": final_stats.get("genetic_summary"),
        },
        "performance_history": perf_history
    }

    # Sonuçları JSON dosyasına yaz
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f"benchmark_results_{timestamp}.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(benchmark_results, f, indent=4, ensure_ascii=False)

    print(f"Benchmark sonuçları kaydedildi: {output_path}")

if __name__ == "__main__":
    run_benchmark() 