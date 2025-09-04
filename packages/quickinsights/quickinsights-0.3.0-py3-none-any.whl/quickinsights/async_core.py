"""
Async-First Architecture for QuickInsights

Provides async/await support for all core operations, enabling
concurrent processing and better performance for I/O operations.
"""

import asyncio
import aiofiles
import aiohttp
import pandas as pd
import numpy as np
from typing import Any, Dict, List, Optional, Union, Callable, Awaitable
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
import time
from dataclasses import dataclass
from enum import Enum

from .error_handling import QuickInsightsError, PerformanceError
from .advanced_config import get_advanced_config_manager

logger = logging.getLogger(__name__)


class AsyncOperationType(Enum):
    """Types of async operations"""
    ANALYSIS = "analysis"
    VISUALIZATION = "visualization"
    DATA_LOADING = "data_loading"
    DATA_SAVING = "data_saving"
    MODEL_TRAINING = "model_training"
    MODEL_PREDICTION = "model_prediction"
    CUSTOM = "custom"


@dataclass
class AsyncTask:
    """Async task information"""
    task_id: str
    operation_type: AsyncOperationType
    function: Callable
    args: tuple
    kwargs: dict
    priority: int = 0
    created_at: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Any = None
    error: Optional[Exception] = None


class AsyncTaskManager:
    """Manages async tasks with priority and resource management"""
    
    def __init__(self, max_concurrent_tasks: int = 10):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.tasks: Dict[str, AsyncTask] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_queue: List[AsyncTask] = []
        self.completed_tasks: Dict[str, AsyncTask] = {}
        self.lock = asyncio.Lock()
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_tasks)
        
    async def submit_task(
        self,
        task_id: str,
        operation_type: AsyncOperationType,
        function: Callable,
        *args,
        priority: int = 0,
        **kwargs
    ) -> str:
        """Submit an async task"""
        async with self.lock:
            task = AsyncTask(
                task_id=task_id,
                operation_type=operation_type,
                function=function,
                args=args,
                kwargs=kwargs,
                priority=priority,
                created_at=time.time()
            )
            
            self.tasks[task_id] = task
            self.task_queue.append(task)
            
            # Sort by priority (higher priority first)
            self.task_queue.sort(key=lambda t: t.priority, reverse=True)
            
            # Start task if we have capacity
            await self._start_next_task()
            
            return task_id
    
    async def _start_next_task(self):
        """Start the next task in queue if capacity allows"""
        if len(self.running_tasks) >= self.max_concurrent_tasks:
            return
        
        if not self.task_queue:
            return
        
        task = self.task_queue.pop(0)
        task.started_at = time.time()
        
        # Create asyncio task
        asyncio_task = asyncio.create_task(self._execute_task(task))
        self.running_tasks[task.task_id] = asyncio_task
        
        # Add done callback
        asyncio_task.add_done_callback(lambda t: self._task_completed_sync(task.task_id, t))
    
    async def _execute_task(self, task: AsyncTask) -> Any:
        """Execute a task"""
        try:
            # Check if function is async
            if asyncio.iscoroutinefunction(task.function):
                result = await task.function(*task.args, **task.kwargs)
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    task.function,
                    *task.args,
                    **task.kwargs
                )
            
            task.result = result
            task.completed_at = time.time()
            
            return result
            
        except Exception as e:
            task.error = e
            task.completed_at = time.time()
            logger.error(f"Task {task.task_id} failed: {e}")
            raise
    
    def _task_completed_sync(self, task_id: str, asyncio_task: asyncio.Task):
        """Handle task completion (sync callback)"""
        # Schedule async completion handler
        asyncio.create_task(self._task_completed(task_id, asyncio_task))
    
    async def _task_completed(self, task_id: str, asyncio_task: asyncio.Task):
        """Handle task completion"""
        async with self.lock:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            
            if task_id in self.tasks:
                task = self.tasks[task_id]
                # Update task with result or error
                try:
                    task.result = asyncio_task.result()
                except Exception as e:
                    task.error = e
                task.completed_at = time.time()
                
                self.completed_tasks[task_id] = task
                del self.tasks[task_id]
            
            # Start next task
            await self._start_next_task()
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Wait for a specific task to complete"""
        if task_id in self.running_tasks:
            try:
                return await asyncio.wait_for(self.running_tasks[task_id], timeout=timeout)
            except asyncio.TimeoutError:
                raise QuickInsightsError(f"Task {task_id} timed out after {timeout} seconds")
        
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            if task.error:
                raise task.error
            return task.result
        
        raise QuickInsightsError(f"Task {task_id} not found")
    
    async def wait_for_all_tasks(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Wait for all tasks to complete"""
        if not self.running_tasks:
            return {}
        
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*self.running_tasks.values(), return_exceptions=True),
                timeout=timeout
            )
            
            return dict(zip(self.running_tasks.keys(), results))
            
        except asyncio.TimeoutError:
            raise QuickInsightsError(f"Tasks timed out after {timeout} seconds")
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            return {
                "status": "queued",
                "created_at": task.created_at,
                "priority": task.priority
            }
        
        if task_id in self.running_tasks:
            task = self.tasks.get(task_id)
            if task:
                return {
                    "status": "running",
                    "created_at": task.created_at,
                    "started_at": task.started_at,
                    "priority": task.priority
                }
        
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return {
                "status": "completed" if not task.error else "failed",
                "created_at": task.created_at,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "error": str(task.error) if task.error else None
            }
        
        return None
    
    def get_all_tasks_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all tasks"""
        status = {}
        
        for task_id in self.tasks:
            status[task_id] = self.get_task_status(task_id)
        
        for task_id in self.running_tasks:
            status[task_id] = self.get_task_status(task_id)
        
        for task_id in self.completed_tasks:
            status[task_id] = self.get_task_status(task_id)
        
        return status
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        async with self.lock:
            if task_id in self.running_tasks:
                self.running_tasks[task_id].cancel()
                del self.running_tasks[task_id]
                return True
            
            if task_id in self.tasks:
                self.tasks[task_id].error = QuickInsightsError(f"Task {task_id} was cancelled")
                self.completed_tasks[task_id] = self.tasks[task_id]
                del self.tasks[task_id]
                return True
            
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        # Cancel all running tasks
        for task in self.running_tasks.values():
            task.cancel()
        
        # Wait for cancellation
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
        
        # Shutdown executor
        self.executor.shutdown(wait=True)


class AsyncDataLoader:
    """Async data loading utilities"""
    
    @staticmethod
    async def load_csv(file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load CSV file asynchronously"""
        loop = asyncio.get_event_loop()
        
        def _load_csv():
            return pd.read_csv(file_path, **kwargs)
        
        return await loop.run_in_executor(None, _load_csv)
    
    @staticmethod
    async def load_excel(file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load Excel file asynchronously"""
        loop = asyncio.get_event_loop()
        
        def _load_excel():
            return pd.read_excel(file_path, **kwargs)
        
        return await loop.run_in_executor(None, _load_excel)
    
    @staticmethod
    async def load_json(file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load JSON file asynchronously"""
        loop = asyncio.get_event_loop()
        
        def _load_json():
            return pd.read_json(file_path, **kwargs)
        
        return await loop.run_in_executor(None, _load_json)
    
    @staticmethod
    async def load_parquet(file_path: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load Parquet file asynchronously"""
        loop = asyncio.get_event_loop()
        
        def _load_parquet():
            return pd.read_parquet(file_path, **kwargs)
        
        return await loop.run_in_executor(None, _load_parquet)
    
    @staticmethod
    async def load_from_url(url: str, **kwargs) -> pd.DataFrame:
        """Load data from URL asynchronously"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    
                    # Determine format from URL or content
                    if url.endswith('.csv'):
                        return await AsyncDataLoader.load_csv_from_bytes(content, **kwargs)
                    elif url.endswith('.json'):
                        return await AsyncDataLoader.load_json_from_bytes(content, **kwargs)
                    else:
                        raise QuickInsightsError(f"Unsupported URL format: {url}")
                else:
                    raise QuickInsightsError(f"Failed to load data from URL: {response.status}")
    
    @staticmethod
    async def load_csv_from_bytes(content: bytes, **kwargs) -> pd.DataFrame:
        """Load CSV from bytes"""
        import io
        
        loop = asyncio.get_event_loop()
        
        def _load_csv():
            return pd.read_csv(io.BytesIO(content), **kwargs)
        
        return await loop.run_in_executor(None, _load_csv)
    
    @staticmethod
    async def load_json_from_bytes(content: bytes, **kwargs) -> pd.DataFrame:
        """Load JSON from bytes"""
        import io
        
        loop = asyncio.get_event_loop()
        
        def _load_json():
            return pd.read_json(io.BytesIO(content), **kwargs)
        
        return await loop.run_in_executor(None, _load_json)


class AsyncDataSaver:
    """Async data saving utilities"""
    
    @staticmethod
    async def save_csv(df: pd.DataFrame, file_path: Union[str, Path], **kwargs) -> None:
        """Save DataFrame to CSV asynchronously"""
        loop = asyncio.get_event_loop()
        
        def _save_csv():
            df.to_csv(file_path, index=False, **kwargs)
        
        await loop.run_in_executor(None, _save_csv)
    
    @staticmethod
    async def save_excel(df: pd.DataFrame, file_path: Union[str, Path], **kwargs) -> None:
        """Save DataFrame to Excel asynchronously"""
        loop = asyncio.get_event_loop()
        
        def _save_excel():
            df.to_excel(file_path, **kwargs)
        
        await loop.run_in_executor(None, _save_excel)
    
    @staticmethod
    async def save_json(df: pd.DataFrame, file_path: Union[str, Path], **kwargs) -> None:
        """Save DataFrame to JSON asynchronously"""
        loop = asyncio.get_event_loop()
        
        def _save_json():
            df.to_json(file_path, **kwargs)
        
        await loop.run_in_executor(None, _save_json)
    
    @staticmethod
    async def save_parquet(df: pd.DataFrame, file_path: Union[str, Path], **kwargs) -> None:
        """Save DataFrame to Parquet asynchronously"""
        loop = asyncio.get_event_loop()
        
        def _save_parquet():
            df.to_parquet(file_path, **kwargs)
        
        await loop.run_in_executor(None, _save_parquet)


class AsyncAnalyzer:
    """Async data analysis operations"""
    
    def __init__(self, task_manager: AsyncTaskManager):
        self.task_manager = task_manager
    
    async def analyze_async(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Async data analysis"""
        loop = asyncio.get_event_loop()
        
        def _analyze():
            # Import here to avoid circular imports
            from .analysis.basic_analysis import analyze
            return analyze(df, **kwargs)
        
        return await loop.run_in_executor(None, _analyze)
    
    async def analyze_numeric_async(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Async numeric analysis"""
        loop = asyncio.get_event_loop()
        
        def _analyze_numeric():
            from .analysis.basic_analysis import analyze_numeric
            return analyze_numeric(df, **kwargs)
        
        return await loop.run_in_executor(None, _analyze_numeric)
    
    async def analyze_categorical_async(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Async categorical analysis"""
        loop = asyncio.get_event_loop()
        
        def _analyze_categorical():
            from .analysis.basic_analysis import analyze_categorical
            return analyze_categorical(df, **kwargs)
        
        return await loop.run_in_executor(None, _analyze_categorical)
    
    async def analyze_multiple_datasets(
        self,
        datasets: List[pd.DataFrame],
        analysis_type: str = "full",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Analyze multiple datasets concurrently"""
        tasks = []
        
        for i, df in enumerate(datasets):
            if analysis_type == "full":
                task_id = await self.task_manager.submit_task(
                    f"analyze_{i}",
                    AsyncOperationType.ANALYSIS,
                    self.analyze_async,
                    df,
                    **kwargs
                )
            elif analysis_type == "numeric":
                task_id = await self.task_manager.submit_task(
                    f"analyze_numeric_{i}",
                    AsyncOperationType.ANALYSIS,
                    self.analyze_numeric_async,
                    df,
                    **kwargs
                )
            elif analysis_type == "categorical":
                task_id = await self.task_manager.submit_task(
                    f"analyze_categorical_{i}",
                    AsyncOperationType.ANALYSIS,
                    self.analyze_categorical_async,
                    df,
                    **kwargs
                )
            else:
                raise QuickInsightsError(f"Unsupported analysis type: {analysis_type}")
            
            tasks.append(task_id)
        
        # Wait for all tasks to complete
        results = []
        for task_id in tasks:
            result = await self.task_manager.wait_for_task(task_id)
            results.append(result)
        
        return results


class AsyncVisualizer:
    """Async visualization operations"""
    
    def __init__(self, task_manager: AsyncTaskManager):
        self.task_manager = task_manager
    
    async def create_visualization_async(
        self,
        data: Any,
        chart_type: str,
        **kwargs
    ) -> Any:
        """Create visualization asynchronously"""
        loop = asyncio.get_event_loop()
        
        def _create_visualization():
            # Import here to avoid circular imports
            from .visualization.charts import create_chart
            return create_chart(data, chart_type, **kwargs)
        
        return await loop.run_in_executor(None, _create_visualization)
    
    async def create_multiple_visualizations(
        self,
        data_list: List[Any],
        chart_types: List[str],
        **kwargs
    ) -> List[Any]:
        """Create multiple visualizations concurrently"""
        tasks = []
        
        for i, (data, chart_type) in enumerate(zip(data_list, chart_types)):
            task_id = await self.task_manager.submit_task(
                f"visualization_{i}",
                AsyncOperationType.VISUALIZATION,
                self.create_visualization_async,
                data,
                chart_type,
                **kwargs
            )
            tasks.append(task_id)
        
        # Wait for all tasks to complete
        results = []
        for task_id in tasks:
            result = await self.task_manager.wait_for_task(task_id)
            results.append(result)
        
        return results


class AsyncQuickInsights:
    """Main async interface for QuickInsights"""
    
    def __init__(self, max_concurrent_tasks: int = 10):
        self.task_manager = AsyncTaskManager(max_concurrent_tasks)
        self.data_loader = AsyncDataLoader()
        self.data_saver = AsyncDataSaver()
        self.analyzer = AsyncAnalyzer(self.task_manager)
        self.visualizer = AsyncVisualizer(self.task_manager)
    
    async def load_data(self, source: Union[str, Path], **kwargs) -> pd.DataFrame:
        """Load data from various sources asynchronously"""
        source = Path(source)
        
        if source.suffix.lower() == '.csv':
            return await self.data_loader.load_csv(source, **kwargs)
        elif source.suffix.lower() in ['.xlsx', '.xls']:
            return await self.data_loader.load_excel(source, **kwargs)
        elif source.suffix.lower() == '.json':
            return await self.data_loader.load_json(source, **kwargs)
        elif source.suffix.lower() == '.parquet':
            return await self.data_loader.load_parquet(source, **kwargs)
        elif str(source).startswith('http'):
            return await self.data_loader.load_from_url(str(source), **kwargs)
        else:
            raise QuickInsightsError(f"Unsupported file format: {source.suffix}")
    
    async def save_data(
        self,
        df: pd.DataFrame,
        file_path: Union[str, Path],
        **kwargs
    ) -> None:
        """Save data to various formats asynchronously"""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.csv':
            await self.data_saver.save_csv(df, file_path, **kwargs)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            await self.data_saver.save_excel(df, file_path, **kwargs)
        elif file_path.suffix.lower() == '.json':
            await self.data_saver.save_json(df, file_path, **kwargs)
        elif file_path.suffix.lower() == '.parquet':
            await self.data_saver.save_parquet(df, file_path, **kwargs)
        else:
            raise QuickInsightsError(f"Unsupported file format: {file_path.suffix}")
    
    async def analyze(self, df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Analyze data asynchronously"""
        return await self.analyzer.analyze_async(df, **kwargs)
    
    async def analyze_multiple(
        self,
        datasets: List[pd.DataFrame],
        analysis_type: str = "full",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Analyze multiple datasets concurrently"""
        return await self.analyzer.analyze_multiple_datasets(
            datasets, analysis_type, **kwargs
        )
    
    async def visualize(
        self,
        data: Any,
        chart_type: str,
        **kwargs
    ) -> Any:
        """Create visualization asynchronously"""
        return await self.visualizer.create_visualization_async(
            data, chart_type, **kwargs
        )
    
    async def visualize_multiple(
        self,
        data_list: List[Any],
        chart_types: List[str],
        **kwargs
    ) -> List[Any]:
        """Create multiple visualizations concurrently"""
        return await self.visualizer.create_multiple_visualizations(
            data_list, chart_types, **kwargs
        )
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        return self.task_manager.get_task_status(task_id)
    
    async def get_all_tasks_status(self) -> Dict[str, Dict[str, Any]]:
        """Get all tasks status"""
        return self.task_manager.get_all_tasks_status()
    
    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Wait for a specific task to complete"""
        return await self.task_manager.wait_for_task(task_id, timeout)
    
    async def wait_for_all_tasks(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Wait for all tasks to complete"""
        return await self.task_manager.wait_for_all_tasks(timeout)
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a task"""
        return await self.task_manager.cancel_task(task_id)
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.task_manager.cleanup()


# Global async instance
_async_quickinsights: Optional[AsyncQuickInsights] = None


def get_async_quickinsights() -> AsyncQuickInsights:
    """Get the global async QuickInsights instance"""
    global _async_quickinsights
    if _async_quickinsights is None:
        config = get_advanced_config_manager()
        max_tasks = config.get("performance.max_concurrent_tasks", 10)
        _async_quickinsights = AsyncQuickInsights(max_tasks)
    return _async_quickinsights


async def analyze_async(df: pd.DataFrame, **kwargs) -> Dict[str, Any]:
    """Async analyze function"""
    return await get_async_quickinsights().analyze(df, **kwargs)


async def load_data_async(source: Union[str, Path], **kwargs) -> pd.DataFrame:
    """Async data loading function"""
    return await get_async_quickinsights().load_data(source, **kwargs)


async def save_data_async(
    df: pd.DataFrame,
    file_path: Union[str, Path],
    **kwargs
) -> None:
    """Async data saving function"""
    await get_async_quickinsights().save_data(df, file_path, **kwargs)
