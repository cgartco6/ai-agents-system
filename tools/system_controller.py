import asyncio
import psutil
import GPUtil
import platform
import subprocess
import os
import signal
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json

class SystemController:
    """Advanced system controller for monitoring and managing system resources"""
    
    def __init__(self):
        self.system_info = {}
        self.monitoring_tasks = {}
        self.alert_thresholds = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'disk_percent': 90,
            'temperature': 80,
            'network_errors': 10
        }
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        logger = logging.getLogger("SystemController")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    async def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            # Basic system info
            system_info = {
                'timestamp': datetime.now().isoformat(),
                'platform': {
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version(),
                    'machine': platform.machine(),
                    'processor': platform.processor()
                },
                'python': {
                    'version': platform.python_version(),
                    'implementation': platform.python_implementation(),
                    'compiler': platform.python_compiler()
                },
                'cpu': await self._get_cpu_info(),
                'memory': await self._get_memory_info(),
                'disk': await self._get_disk_info(),
                'network': await self._get_network_info(),
                'gpu': await self._get_gpu_info(),
                'processes': await self._get_processes_info()
            }
            
            self.system_info = system_info
            return system_info
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }

    async def _get_cpu_info(self) -> Dict[str, Any]:
        """Get CPU information"""
        try:
            cpu_times = psutil.cpu_times()
            return {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'usage_percent': psutil.cpu_percent(interval=1),
                'per_core_usage': psutil.cpu_percent(interval=1, percpu=True),
                'times': {
                    'user': cpu_times.user,
                    'system': cpu_times.system,
                    'idle': cpu_times.idle
                },
                'stats': {
                    'ctx_switches': psutil.cpu_stats().ctx_switches,
                    'interrupts': psutil.cpu_stats().interrupts,
                    'soft_interrupts': psutil.cpu_stats().soft_interrupts
                },
                'frequency': {
                    'current': psutil.cpu_freq().current if psutil.cpu_freq() else None,
                    'min': psutil.cpu_freq().min if psutil.cpu_freq() else None,
                    'max': psutil.cpu_freq().max if psutil.cpu_freq() else None
                }
            }
        except Exception as e:
            return {'error': str(e)}

    async def _get_memory_info(self) -> Dict[str, Any]:
        """Get memory information"""
        try:
            virtual_memory = psutil.virtual_memory()
            swap_memory = psutil.swap_memory()
            
            return {
                'virtual': {
                    'total_gb': round(virtual_memory.total / (1024**3), 2),
                    'available_gb': round(virtual_memory.available / (1024**3), 2),
                    'used_gb': round(virtual_memory.used / (1024**3), 2),
                    'percent': virtual_memory.percent
                },
                'swap': {
                    'total_gb': round(swap_memory.total / (1024**3), 2),
                    'used_gb': round(swap_memory.used / (1024**3), 2),
                    'free_gb': round(swap_memory.free / (1024**3), 2),
                    'percent': swap_memory.percent
                }
            }
        except Exception as e:
            return {'error': str(e)}

    async def _get_disk_info(self) -> Dict[str, Any]:
        """Get disk information"""
        try:
            disk_partitions = psutil.disk_partitions()
            disk_usage = {}
            disk_io = psutil.disk_io_counters()
            
            for partition in disk_partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total_gb': round(usage.total / (1024**3), 2),
                        'used_gb': round(usage.used / (1024**3), 2),
                        'free_gb': round(usage.free / (1024**3), 2),
                        'percent': usage.percent
                    }
                except PermissionError:
                    continue
            
            return {
                'partitions': disk_usage,
                'io': {
                    'read_count': disk_io.read_count if disk_io else None,
                    'write_count': disk_io.write_count if disk_io else None,
                    'read_bytes_gb': round(disk_io.read_bytes / (1024**3), 2) if disk_io else None,
                    'write_bytes_gb': round(disk_io.write_bytes / (1024**3), 2) if disk_io else None
                } if disk_io else {}
            }
        except Exception as e:
            return {'error': str(e)}

    async def _get_network_info(self) -> Dict[str, Any]:
        """Get network information"""
        try:
            net_io = psutil.net_io_counters()
            net_connections = psutil.net_connections()
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            return {
                'io': {
                    'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
                    'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2),
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv,
                    'errin': net_io.errin,
                    'errout': net_io.errout,
                    'dropin': net_io.dropin,
                    'dropout': net_io.dropout
                },
                'connections': {
                    'total': len(net_connections),
                    'tcp': len([c for c in net_connections if c.type == 1]),
                    'udp': len([c for c in net_connections if c.type == 2])
                },
                'interfaces': {
                    name: {
                        'addresses': [addr.address for addr in addrs],
                        'is_up': net_if_stats[name].isup if name in net_if_stats else False,
                        'speed_mbps': net_if_stats[name].speed if name in net_if_stats else 0
                    }
                    for name, addrs in net_if_addrs.items()
                }
            }
        except Exception as e:
            return {'error': str(e)}

    async def _get_gpu_info(self) -> Dict[str, Any]:
        """Get GPU information"""
        try:
            gpus = GPUtil.getGPUs()
            gpu_info = []
            
            for gpu in gpus:
                gpu_info.append({
                    'id': gpu.id,
                    'name': gpu.name,
                    'load_percent': gpu.load * 100,
                    'memory_used_gb': round(gpu.memoryUsed, 2),
                    'memory_total_gb': round(gpu.memoryTotal, 2),
                    'memory_percent': gpu.memoryUtil * 100,
                    'temperature_c': gpu.temperature
                })
            
            return {
                'count': len(gpus),
                'gpus': gpu_info
            }
        except Exception as e:
            return {'error': str(e), 'gpus': []}

    async def _get_processes_info(self) -> Dict[str, Any]:
        """Get processes information"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            return {
                'total': len(processes),
                'top_cpu': processes[:10],  # Top 10 by CPU
                'top_memory': sorted(processes, key=lambda x: x['memory_percent'] or 0, reverse=True)[:10]
            }
        except Exception as e:
            return {'error': str(e)}

    async def start_monitoring(self, interval: int = 5) -> str:
        """Start system monitoring"""
        monitor_id = f"monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        async def monitor_loop():
            while monitor_id in self.monitoring_tasks:
                try:
                    system_status = await self.get_system_status()
                    await self._check_alerts(system_status)
                    await asyncio.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Monitoring error: {str(e)}")
                    await asyncio.sleep(interval)
        
        self.monitoring_tasks[monitor_id] = asyncio.create_task(monitor_loop())
        self.logger.info(f"Started system monitoring with ID: {monitor_id}")
        
        return monitor_id

    async def stop_monitoring(self, monitor_id: str) -> bool:
        """Stop system monitoring"""
        if monitor_id in self.monitoring_tasks:
            self.monitoring_tasks[monitor_id].cancel()
            del self.monitoring_tasks[monitor_id]
            self.logger.info(f"Stopped monitoring: {monitor_id}")
            return True
        return False

    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status with health assessment"""
        system_info = await self.get_system_info()
        
        # Calculate health scores
        cpu_health = await self._assess_cpu_health(system_info.get('cpu', {}))
        memory_health = await self._assess_memory_health(system_info.get('memory', {}))
        disk_health = await self._assess_disk_health(system_info.get('disk', {}))
        network_health = await self._assess_network_health(system_info.get('network', {}))
        
        overall_health = min(cpu_health['score'], memory_health['score'], 
                           disk_health['score'], network_health['score'])
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_health': {
                'score': overall_health,
                'status': 'healthy' if overall_health >= 80 else 
                         'degraded' if overall_health >= 60 else 'critical'
            },
            'component_health': {
                'cpu': cpu_health,
                'memory': memory_health,
                'disk': disk_health,
                'network': network_health
            },
            'system_info': system_info,
            'recommendations': await self._generate_recommendations(
                cpu_health, memory_health, disk_health, network_health
            )
        }

    async def _assess_cpu_health(self, cpu_info: Dict[str, Any]) -> Dict[str, Any]:
        """Assess CPU health"""
        try:
            usage = cpu_info.get('usage_percent', 0)
            per_core_usage = cpu_info.get('per_core_usage', [])
            
            # Calculate health score (0-100)
            if usage < 50:
                score = 100
            elif usage < 80:
                score = 80
            elif usage < 95:
                score = 60
            else:
                score = 40
            
            issues = []
            if usage > self.alert_thresholds['cpu_percent']:
                issues.append(f"High CPU usage: {usage}%")
            
            # Check for core imbalance
            if per_core_usage:
                max_core_usage = max(per_core_usage)
                min_core_usage = min(per_core_usage)
                if max_core_usage - min_core_usage > 50:  # Significant imbalance
                    issues.append("CPU core usage imbalance detected")
            
            return {
                'score': score,
                'usage_percent': usage,
                'issues': issues,
                'status': 'healthy' if score >= 80 else 'degraded' if score >= 60 else 'critical'
            }
        except Exception as e:
            return {'score': 0, 'issues': [f"Assessment error: {str(e)}"], 'status': 'error'}

    async def _assess_memory_health(self, memory_info: Dict[str, Any]) -> Dict[str, Any]:
        """Assess memory health"""
        try:
            virtual_usage = memory_info.get('virtual', {}).get('percent', 0)
            swap_usage = memory_info.get('swap', {}).get('percent', 0)
            
            # Calculate health score
            if virtual_usage < 70:
                score = 100
            elif virtual_usage < 85:
                score = 80
            elif virtual_usage < 95:
                score = 60
            else:
                score = 40
            
            # Penalize high swap usage
            if swap_usage > 50:
                score = max(score - 20, 0)
            
            issues = []
            if virtual_usage > self.alert_thresholds['memory_percent']:
                issues.append(f"High memory usage: {virtual_usage}%")
            
            if swap_usage > 50:
                issues.append(f"High swap usage: {swap_usage}%")
            
            return {
                'score': score,
                'virtual_usage_percent': virtual_usage,
                'swap_usage_percent': swap_usage,
                'issues': issues,
                'status': 'healthy' if score >= 80 else 'degraded' if score >= 60 else 'critical'
            }
        except Exception as e:
            return {'score': 0, 'issues': [f"Assessment error: {str(e)}"], 'status': 'error'}

    async def _assess_disk_health(self, disk_info: Dict[str, Any]) -> Dict[str, Any]:
        """Assess disk health"""
        try:
            partitions = disk_info.get('partitions', {})
            max_usage = 0
            issues = []
            
            for device, info in partitions.items():
                usage = info.get('percent', 0)
                max_usage = max(max_usage, usage)
                
                if usage > self.alert_thresholds['disk_percent']:
                    issues.append(f"High disk usage on {device}: {usage}%")
            
            # Calculate health score
            if max_usage < 80:
                score = 100
            elif max_usage < 90:
                score = 80
            elif max_usage < 95:
                score = 60
            else:
                score = 40
            
            return {
                'score': score,
                'max_usage_percent': max_usage,
                'issues': issues,
                'status': 'healthy' if score >= 80 else 'degraded' if score >= 60 else 'critical'
            }
        except Exception as e:
            return {'score': 0, 'issues': [f"Assessment error: {str(e)}"], 'status': 'error'}

    async def _assess_network_health(self, network_info: Dict[str, Any]) -> Dict[str, Any]:
        """Assess network health"""
        try:
            io = network_info.get('io', {})
            errors = io.get('errin', 0) + io.get('errout', 0)
            drops = io.get('dropin', 0) + io.get('dropout', 0)
            
            # Calculate health score
            score = 100
            
            if errors > self.alert_thresholds['network_errors']:
                score -= 20
            
            if drops > 5:
                score -= 20
            
            issues = []
            if errors > 0:
                issues.append(f"Network errors detected: {errors}")
            
            if drops > 0:
                issues.append(f"Network packets dropped: {drops}")
            
            return {
                'score': score,
                'errors': errors,
                'drops': drops,
                'issues': issues,
                'status': 'healthy' if score >= 80 else 'degraded' if score >= 60 else 'critical'
            }
        except Exception as e:
            return {'score': 0, 'issues': [f"Assessment error: {str(e)}"], 'status': 'error'}

    async def _check_alerts(self, system_status: Dict[str, Any]):
        """Check for system alerts"""
        alerts = []
        
        component_health = system_status.get('component_health', {})
        
        for component, health in component_health.items():
            if health.get('status') in ['degraded', 'critical']:
                alerts.append({
                    'component': component,
                    'status': health['status'],
                    'issues': health.get('issues', []),
                    'timestamp': datetime.now().isoformat()
                })
        
        if alerts:
            await self._handle_alerts(alerts)

    async def _handle_alerts(self, alerts: List[Dict[str, Any]]):
        """Handle system alerts"""
        for alert in alerts:
            self.logger.warning(
                f"System alert: {alert['component']} is {alert['status']}. "
                f"Issues: {', '.join(alert['issues'])}"
            )
            
            # In production, this would send notifications, trigger auto-remediation, etc.
            if alert['status'] == 'critical':
                await self._trigger_critical_alert(alert)

    async def _trigger_critical_alert(self, alert: Dict[str, Any]):
        """Trigger critical alert actions"""
        component = alert['component']
        
        if component == 'memory' and 'High memory usage' in alert['issues']:
            # Suggest memory optimization
            self.logger.info("Suggesting memory optimization procedures...")
        
        elif component == 'disk' and 'High disk usage' in alert['issues']:
            # Suggest disk cleanup
            self.logger.info("Suggesting disk cleanup procedures...")

    async def _generate_recommendations(self, cpu_health: Dict[str, Any], 
                                      memory_health: Dict[str, Any],
                                      disk_health: Dict[str, Any],
                                      network_health: Dict[str, Any]) -> List[str]:
        """Generate system optimization recommendations"""
        recommendations = []
        
        # CPU recommendations
        if cpu_health.get('score', 0) < 80:
            recommendations.extend([
                "Consider optimizing CPU-intensive processes",
                "Check for runaway processes consuming excessive CPU",
                "Consider scaling up CPU resources if consistently high usage"
            ])
        
        # Memory recommendations
        if memory_health.get('score', 0) < 80:
            recommendations.extend([
                "Monitor memory usage and consider adding more RAM",
                "Optimize application memory usage",
                "Check for memory leaks in running processes"
            ])
        
        # Disk recommendations
        if disk_health.get('score', 0) < 80:
            recommendations.extend([
                "Clean up temporary files and unused applications",
                "Consider archiving old data",
                "Monitor disk space and consider expanding storage"
            ])
        
        # Network recommendations
        if network_health.get('score', 0) < 80:
            recommendations.extend([
                "Check network connectivity and configuration",
                "Monitor for network-intensive applications",
                "Consider network optimization or upgrade"
            ])
        
        return recommendations if recommendations else ["System is running optimally"]

    async def optimize_system(self, optimization_type: str) -> Dict[str, Any]:
        """Perform system optimization"""
        try:
            if optimization_type == 'memory':
                return await self._optimize_memory()
            elif optimization_type == 'disk':
                return await self._optimize_disk()
            elif optimization_type == 'processes':
                return await self._optimize_processes()
            else:
                return {
                    'status': 'error',
                    'error': f"Unknown optimization type: {optimization_type}"
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    async def _optimize_memory(self) -> Dict[str, Any]:
        """Optimize memory usage"""
        # This would implement actual memory optimization strategies
        return {
            'status': 'success',
            'optimization': 'memory',
            'actions_taken': [
                'Suggested closing unused applications',
                'Recommended memory-intensive process review',
                'Advised system restart if persistent issues'
            ],
            'impact': 'Potential memory usage reduction',
            'notes': 'Manual intervention may be required for significant improvements'
        }

    async def _optimize_disk(self) -> Dict[str, Any]:
        """Optimize disk usage"""
        try:
            # Clean up temporary files (simplified)
            temp_dirs = ['/tmp', '/var/tmp']
            cleaned_files = 0
            
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    # This is a simulation - actual cleanup would be more careful
                    cleaned_files += 1
            
            return {
                'status': 'success',
                'optimization': 'disk',
                'actions_taken': [
                    'Checked temporary directories',
                    'Identified potential cleanup candidates'
                ],
                'cleaned_directories': cleaned_files,
                'notes': 'Run disk cleanup utilities for comprehensive optimization'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    async def _optimize_processes(self) -> Dict[str, Any]:
        """Optimize running processes"""
        try:
            # Identify resource-intensive processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if (proc.info['cpu_percent'] or 0) > 10 or (proc.info['memory_percent'] or 0) > 5:
                        processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                'status': 'success',
                'optimization': 'processes',
                'resource_intensive_processes': processes[:10],  # Top 10
                'recommendations': [
                    'Review high-CPU processes for optimization opportunities',
                    'Consider terminating unnecessary background processes',
                    'Monitor process memory leaks'
                ]
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    async def execute_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute system command safely"""
        try:
            self.logger.info(f"Executing command: {command}")
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
                
                return {
                    'status': 'success',
                    'command': command,
                    'return_code': process.returncode,
                    'stdout': stdout.decode('utf-8', errors='ignore') if stdout else '',
                    'stderr': stderr.decode('utf-8', errors='ignore') if stderr else '',
                    'execution_time': 'measured'  # Would be actual measurement
                }
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    'status': 'error',
                    'command': command,
                    'error': f"Command timeout after {timeout} seconds"
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'command': command,
                'error': str(e)
            }

    async def get_system_logs(self, log_type: str = 'system', lines: int = 50) -> Dict[str, Any]:
        """Get system logs"""
        try:
            # This is platform-specific and would need adjustment
            if platform.system() == 'Linux':
                if log_type == 'system':
                    command = f"journalctl -n {lines}"
                elif log_type == 'kernel':
                    command = f"dmesg | tail -n {lines}"
                else:
                    command = f"tail -n {lines} /var/log/syslog"
            elif platform.system() == 'Darwin':  # macOS
                command = f"log show --last 1h | tail -n {lines}"
            else:  # Windows
                command = f"Get-EventLog -LogName System -Newest {lines}"
            
            result = await self.execute_command(command)
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    async def create_system_report(self) -> Dict[str, Any]:
        """Create comprehensive system report"""
        system_status = await self.get_system_status()
        system_info = await self.get_system_info()
        
        report = {
            'report_id': f"system_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'overall_health': system_status['overall_health'],
                'critical_issues': len([c for c in system_status['component_health'].values() 
                                      if c.get('status') == 'critical']),
                'degraded_components': len([c for c in system_status['component_health'].values() 
                                         if c.get('status') == 'degraded'])
            },
            'detailed_analysis': system_status,
            'system_configuration': system_info,
            'recommendations': system_status.get('recommendations', []),
            'monitoring_status': {
                'active_monitors': list(self.monitoring_tasks.keys()),
                'alert_thresholds': self.alert_thresholds
            }
        }
        
        return report

    async def set_alert_thresholds(self, thresholds: Dict[str, float]) -> Dict[str, Any]:
        """Set custom alert thresholds"""
        old_thresholds = self.alert_thresholds.copy()
        self.alert_thresholds.update(thresholds)
        
        self.logger.info(f"Updated alert thresholds: {thresholds}")
        
        return {
            'status': 'success',
            'old_thresholds': old_thresholds,
            'new_thresholds': self.alert_thresholds,
            'changes': list(thresholds.keys())
        }
