import os
import time
import asyncio
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime
import statistics


@dataclass
class BenchmarkResult:
    """压测结果"""
    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    duration_seconds: float
    requests_per_second: float
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    avg_memory_mb: float
    peak_memory_mb: float
    avg_cpu_percent: float
    peak_cpu_percent: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class StressTestRunner:
    """性能压测运行器"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[BenchmarkResult] = []

    def _measure_request(self, func: Callable, *args, **kwargs) -> tuple:
        """测量单个请求的性能"""
        latencies = []
        start_time = time.time()
        success = 0
        failed = 0

        try:
            result = func(*args, **kwargs)
            success = 1
            latency = (time.time() - start_time) * 1000
            latencies.append(latency)
            return result, latency, success, failed
        except Exception as e:
            failed = 1
            latency = (time.time() - start_time) * 1000
            latencies.append(latency)
            return None, latency, success, failed

    def benchmark_endpoint(
        self,
        name: str,
        request_func: Callable,
        num_requests: int = 100,
        concurrency: int = 10,
        warmup_requests: int = 10
    ) -> BenchmarkResult:
        """压测单个接口"""
        print(f"\n{'='*60}")
        print(f"Benchmarking: {name}")
        print(f"Requests: {num_requests}, Concurrency: {concurrency}")
        print(f"{'='*60}")

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024

        print(f"Warmup: {warmup_requests} requests...")
        for _ in range(warmup_requests):
            try:
                request_func()
            except:
                pass

        print(f"Running benchmark...")
        latencies = []
        success_count = 0
        fail_count = 0

        start_time = time.time()

        def make_request():
            req_start = time.time()
            try:
                request_func()
                latencies.append((time.time() - req_start) * 1000)
                return 1, 0
            except Exception as e:
                latencies.append((time.time() - req_start) * 1000)
                return 0, 1

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            for future in futures:
                s, f = future.result()
                success_count += s
                fail_count += f

        duration = time.time() - start_time

        final_memory = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent(interval=0.1)

        if latencies:
            latencies.sort()
            p50_idx = int(len(latencies) * 0.50)
            p95_idx = int(len(latencies) * 0.95)
            p99_idx = int(len(latencies) * 0.99)

            result = BenchmarkResult(
                endpoint=name,
                total_requests=num_requests,
                successful_requests=success_count,
                failed_requests=fail_count,
                duration_seconds=duration,
                requests_per_second=num_requests / duration,
                avg_latency_ms=statistics.mean(latencies),
                min_latency_ms=min(latencies),
                max_latency_ms=max(latencies),
                p50_latency_ms=latencies[p50_idx] if p50_idx < len(latencies) else 0,
                p95_latency_ms=latencies[p95_idx] if p95_idx < len(latencies) else 0,
                p99_latency_ms=latencies[p99_idx] if p99_idx < len(latencies) else 0,
                avg_memory_mb=final_memory,
                peak_memory_mb=final_memory,
                avg_cpu_percent=cpu_percent,
                peak_cpu_percent=cpu_percent
            )
        else:
            result = BenchmarkResult(
                endpoint=name,
                total_requests=num_requests,
                successful_requests=0,
                failed_requests=num_requests,
                duration_seconds=duration,
                requests_per_second=0,
                avg_latency_ms=0,
                min_latency_ms=0,
                max_latency_ms=0,
                p50_latency_ms=0,
                p95_latency_ms=0,
                p99_latency_ms=0,
                avg_memory_mb=final_memory,
                peak_memory_mb=final_memory,
                avg_cpu_percent=cpu_percent,
                peak_cpu_percent=cpu_percent
            )

        self.results.append(result)
        self._print_result(result)
        return result

    def _print_result(self, result: BenchmarkResult):
        """打印压测结果"""
        print(f"\n{'='*60}")
        print(f"Benchmark Results: {result.endpoint}")
        print(f"{'='*60}")
        print(f"Total Requests:      {result.total_requests}")
        print(f"Successful:           {result.successful_requests}")
        print(f"Failed:               {result.failed_requests}")
        print(f"Duration:             {result.duration_seconds:.2f}s")
        print(f"RPS:                  {result.requests_per_second:.2f}")
        print(f"Avg Latency:          {result.avg_latency_ms:.2f}ms")
        print(f"Min/Max Latency:      {result.min_latency_ms:.2f}ms / {result.max_latency_ms:.2f}ms")
        print(f"P50/P95/P99:          {result.p50_latency_ms:.2f}ms / {result.p95_latency_ms:.2f}ms / {result.p99_latency_ms:.2f}ms")
        print(f"Memory:               {result.avg_memory_mb:.2f}MB")
        print(f"CPU:                  {result.avg_cpu_percent:.2f}%")
        print(f"{'='*60}\n")

    def export_results(self, output_path: str = None) -> str:
        """导出结果到 JSON"""
        if output_path is None:
            output_path = f"data/runs/benchmark_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        import json
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "results": [
                {
                    "endpoint": r.endpoint,
                    "total_requests": r.total_requests,
                    "successful_requests": r.successful_requests,
                    "failed_requests": r.failed_requests,
                    "duration_seconds": r.duration_seconds,
                    "requests_per_second": r.requests_per_second,
                    "avg_latency_ms": r.avg_latency_ms,
                    "min_latency_ms": r.min_latency_ms,
                    "max_latency_ms": r.max_latency_ms,
                    "p50_latency_ms": r.p50_latency_ms,
                    "p95_latency_ms": r.p95_latency_ms,
                    "p99_latency_ms": r.p99_latency_ms,
                    "avg_memory_mb": r.avg_memory_mb,
                    "peak_memory_mb": r.peak_memory_mb,
                    "avg_cpu_percent": r.avg_cpu_percent,
                    "peak_cpu_percent": r.peak_cpu_percent,
                }
                for r in self.results
            ]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Benchmark results exported to: {output_path}")
        return output_path


def get_stress_test_runner(base_url: str = "http://localhost:8000") -> StressTestRunner:
    """获取压测运行器实例"""
    return StressTestRunner(base_url)


if __name__ == "__main__":
    import requests

    runner = get_stress_test_runner()

    def test_health():
        requests.get(f"{runner.base_url}/health")

    def test_chat():
        requests.post(
            f"{runner.base_url}/chat",
            json={"message": "hello", "stream": False}
        )

    runner.benchmark_endpoint("/health", test_health, num_requests=50, concurrency=5)
    runner.benchmark_endpoint("/chat", test_chat, num_requests=50, concurrency=5)

    runner.export_results()
