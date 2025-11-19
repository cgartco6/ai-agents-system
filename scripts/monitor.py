#!/usr/bin/env python3
"""
Advanced AI System - System Monitor
Real-time monitoring and dashboard for the AI system
"""

import asyncio
import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.system_controller import SystemController
from tasks.task_executor import TaskExecutor

class SystemMonitor:
    """Comprehensive system monitor for the AI system"""
    
    def __init__(self):
        self.system_controller = SystemController()
        self.monitoring_data = []
        self.alert_history = []
        self.is_monitoring = False
        
    async def start_comprehensive_monitoring(self):
        """Start comprehensive system monitoring"""
        self.is_monitoring = True
        
        print("🚀 Starting Comprehensive System Monitoring...")
        print("=" * 80)
        
        # Start monitoring tasks
        monitoring_tasks = [
            self._monitor_system_health(),
            self._monitor_agent_performance(),
            self._monitor_task_execution(),
            self._monitor_memory_usage(),
            self._monitor_network_activity(),
            self._display_dashboard()
        ]
        
        try:
            await asyncio.gather(*monitoring_tasks)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
        finally:
            self.is_monitoring = False
    
    async def _monitor_system_health(self):
        """Monitor overall system health"""
        while self.is_monitoring:
            try:
                system_status = await self.system_controller.get_system_status()
                self.monitoring_data.append({
                    'timestamp': time.time(),
                    'type': 'system_health',
                    'data': system_status
                })
                
                # Check for critical alerts
                if system_status['overall_health']['status'] in ['degraded', 'critical']:
                    alert = {
                        'timestamp': time.time(),
                        'level': system_status['overall_health']['status'],
                        'component': 'system',
                        'message': f"System health {system_status['overall_health']['status']}",
                        'details': system_status
                    }
                    self.alert_history.append(alert)
                    self._handle_alert(alert)
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"❌ System health monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _monitor_agent_performance(self):
        """Monitor AI agent performance"""
        while self.is_monitoring:
            try:
                # This would integrate with actual agent monitoring
                agent_data = {
                    'timestamp': time.time(),
                    'type': 'agent_performance',
                    'data': {
                        'active_agents': 12,  # Example data
                        'average_success_rate': 85.5,
                        'total_tasks_processed': 1500
                    }
                }
                self.monitoring_data.append(agent_data)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"❌ Agent monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _monitor_task_execution(self):
        """Monitor task execution system"""
        while self.is_monitoring:
            try:
                # This would integrate with actual task system monitoring
                task_data = {
                    'timestamp': time.time(),
                    'type': 'task_execution',
                    'data': {
                        'pending_tasks': 5,
                        'active_tasks': 3,
                        'completed_tasks': 45,
                        'success_rate': 92.0
                    }
                }
                self.monitoring_data.append(task_data)
                
                await asyncio.sleep(15)  # Check every 15 seconds
                
            except Exception as e:
                print(f"❌ Task monitoring error: {e}")
                await asyncio.sleep(15)
    
    async def _monitor_memory_usage(self):
        """Monitor memory and storage usage"""
        while self.is_monitoring:
            try:
                system_info = await self.system_controller.get_system_info()
                memory_info = system_info.get('memory', {})
                
                memory_data = {
                    'timestamp': time.time(),
                    'type': 'memory_usage',
                    'data': {
                        'ram_usage_percent': memory_info.get('virtual', {}).get('percent', 0),
                        'swap_usage_percent': memory_info.get('swap', {}).get('percent', 0),
                        'disk_usage_percent': max(
                            partition.get('percent', 0) 
                            for partition in system_info.get('disk', {}).get('partitions', {}).values()
                        ) if system_info.get('disk', {}).get('partitions') else 0
                    }
                }
                self.monitoring_data.append(memory_data)
                
                # Check memory thresholds
                if memory_data['data']['ram_usage_percent'] > 85:
                    alert = {
                        'timestamp': time.time(),
                        'level': 'warning',
                        'component': 'memory',
                        'message': f"High memory usage: {memory_data['data']['ram_usage_percent']}%",
                        'details': memory_data
                    }
                    self.alert_history.append(alert)
                    self._handle_alert(alert)
                
                await asyncio.sleep(20)  # Check every 20 seconds
                
            except Exception as e:
                print(f"❌ Memory monitoring error: {e}")
                await asyncio.sleep(20)
    
    async def _monitor_network_activity(self):
        """Monitor network activity"""
        while self.is_monitoring:
            try:
                system_info = await self.system_controller.get_system_info()
                network_info = system_info.get('network', {})
                
                network_data = {
                    'timestamp': time.time(),
                    'type': 'network_activity',
                    'data': {
                        'bytes_sent_mb': network_info.get('io', {}).get('bytes_sent_mb', 0),
                        'bytes_recv_mb': network_info.get('io', {}).get('bytes_recv_mb', 0),
                        'connections': network_info.get('connections', {}).get('total', 0),
                        'errors': network_info.get('io', {}).get('errin', 0) + network_info.get('io', {}).get('errout', 0)
                    }
                }
                self.monitoring_data.append(network_data)
                
                await asyncio.sleep(25)  # Check every 25 seconds
                
            except Exception as e:
                print(f"❌ Network monitoring error: {e}")
                await asyncio.sleep(25)
    
    async def _display_dashboard(self):
        """Display real-time monitoring dashboard"""
        while self.is_monitoring:
            try:
                # Clear screen (works on most terminals)
                os.system('cls' if os.name == 'nt' else 'clear')
                
                print("🤖 ADVANCED AI SYSTEM - REAL-TIME MONITOR")
                print("=" * 80)
                
                # Get latest monitoring data
                latest_data = self._get_latest_monitoring_data()
                
                # Display system health
                self._display_system_health(latest_data.get('system_health'))
                
                # Display resource usage
                self._display_resource_usage(latest_data.get('memory_usage'))
                
                # Display performance metrics
                self._display_performance_metrics(latest_data.get('agent_performance'), latest_data.get('task_execution'))
                
                # Display network activity
                self._display_network_activity(latest_data.get('network_activity'))
                
                # Display alerts
                self._display_alerts()
                
                # Display recommendations
                self._display_recommendations(latest_data)
                
                print("\n" + "=" * 80)
                print("🔄 Auto-refreshing every 5 seconds... (Ctrl+C to stop)")
                
                await asyncio.sleep(5)
                
            except Exception as e:
                print(f"❌ Dashboard error: {e}")
                await asyncio.sleep(5)
    
    def _get_latest_monitoring_data(self) -> Dict[str, Any]:
        """Get latest monitoring data for each type"""
        latest_data = {}
        
        for data_type in ['system_health', 'agent_performance', 'task_execution', 'memory_usage', 'network_activity']:
            relevant_data = [d for d in self.monitoring_data if d['type'] == data_type]
            if relevant_data:
                latest_data[data_type] = relevant_data[-1]['data']
        
        return latest_data
    
    def _display_system_health(self, health_data: Optional[Dict[str, Any]]):
        """Display system health information"""
        print("\n📊 SYSTEM HEALTH")
        print("-" * 40)
        
        if health_data:
            overall_health = health_data.get('overall_health', {})
            component_health = health_data.get('component_health', {})
            
            # Overall health with color coding
            score = overall_health.get('score', 0)
            status = overall_health.get('status', 'unknown')
            
            if status == 'healthy':
                health_color = '🟢'
            elif status == 'degraded':
                health_color = '🟡'
            else:
                health_color = '🔴'
            
            print(f"{health_color} Overall Health: {score}% ({status})")
            
            # Component health
            for component, health in component_health.items():
                comp_score = health.get('score', 0)
                comp_status = health.get('status', 'unknown')
                
                if comp_status == 'healthy':
                    comp_color = '🟢'
                elif comp_status == 'degraded':
                    comp_color = '🟡'
                else:
                    comp_color = '🔴'
                
                print(f"   {comp_color} {component.title()}: {comp_score}%")
        else:
            print("❌ No health data available")
    
    def _display_resource_usage(self, memory_data: Optional[Dict[str, Any]]):
        """Display resource usage information"""
        print("\n💾 RESOURCE USAGE")
        print("-" * 40)
        
        if memory_data:
            ram_usage = memory_data.get('ram_usage_percent', 0)
            swap_usage = memory_data.get('swap_usage_percent', 0)
            disk_usage = memory_data.get('disk_usage_percent', 0)
            
            # RAM usage with progress bar
            ram_bar = self._create_progress_bar(ram_usage)
            print(f"🖥️  RAM:    {ram_bar} {ram_usage:.1f}%")
            
            # Swap usage
            swap_bar = self._create_progress_bar(swap_usage)
            print(f"💫 Swap:   {swap_bar} {swap_usage:.1f}%")
            
            # Disk usage
            disk_bar = self._create_progress_bar(disk_usage)
            print(f"💾 Disk:   {disk_bar} {disk_usage:.1f}%")
        else:
            print("❌ No resource data available")
    
    def _display_performance_metrics(self, agent_data: Optional[Dict[str, Any]], task_data: Optional[Dict[str, Any]]):
        """Display performance metrics"""
        print("\n⚡ PERFORMANCE METRICS")
        print("-" * 40)
        
        # Agent performance
        if agent_data:
            active_agents = agent_data.get('active_agents', 0)
            success_rate = agent_data.get('average_success_rate', 0)
            total_tasks = agent_data.get('total_tasks_processed', 0)
            
            print(f"🤖 Active Agents: {active_agents}")
            print(f"📈 Success Rate:  {success_rate:.1f}%")
            print(f"📊 Tasks Processed: {total_tasks}")
        else:
            print("🤖 Agents: No data")
        
        # Task execution
        if task_data:
            pending_tasks = task_data.get('pending_tasks', 0)
            active_tasks = task_data.get('active_tasks', 0)
            task_success_rate = task_data.get('success_rate', 0)
            
            print(f"📋 Pending Tasks: {pending_tasks}")
            print(f"🔄 Active Tasks:  {active_tasks}")
            print(f"🎯 Task Success:  {task_success_rate:.1f}%")
        else:
            print("📋 Tasks: No data")
    
    def _display_network_activity(self, network_data: Optional[Dict[str, Any]]):
        """Display network activity"""
        print("\n🌐 NETWORK ACTIVITY")
        print("-" * 40)
        
        if network_data:
            sent_mb = network_data.get('bytes_sent_mb', 0)
            recv_mb = network_data.get('bytes_recv_mb', 0)
            connections = network_data.get('connections', 0)
            errors = network_data.get('errors', 0)
            
            print(f"📤 Sent: {sent_mb:.1f} MB")
            print(f"📥 Received: {recv_mb:.1f} MB")
            print(f"🔗 Connections: {connections}")
            print(f"❌ Errors: {errors}")
        else:
            print("❌ No network data available")
    
    def _display_alerts(self):
        """Display recent alerts"""
        print("\n🚨 RECENT ALERTS")
        print("-" * 40)
        
        recent_alerts = self.alert_history[-5:]  # Last 5 alerts
        
        if recent_alerts:
            for alert in recent_alerts:
                timestamp = time.strftime('%H:%M:%S', time.localtime(alert['timestamp']))
                level = alert['level']
                message = alert['message']
                
                if level == 'critical':
                    alert_icon = '🔴'
                elif level == 'warning':
                    alert_icon = '🟡'
                else:
                    alert_icon = '🟢'
                
                print(f"{alert_icon} [{timestamp}] {message}")
        else:
            print("✅ No recent alerts")
    
    def _display_recommendations(self, monitoring_data: Dict[str, Any]):
        """Display system recommendations"""
        print("\n💡 RECOMMENDATIONS")
        print("-" * 40)
        
        recommendations = []
        
        # Check memory usage
        memory_data = monitoring_data.get('memory_usage', {})
        if memory_data.get('ram_usage_percent', 0) > 80:
            recommendations.append("💾 Consider optimizing memory usage or adding more RAM")
        
        # Check system health
        health_data = monitoring_data.get('system_health', {})
        if health_data.get('overall_health', {}).get('score', 100) < 70:
            recommendations.append("🔄 System performance degraded - review component health")
        
        # Check task success rate
        task_data = monitoring_data.get('task_execution', {})
        if task_data.get('success_rate', 100) < 85:
            recommendations.append("🎯 Task success rate low - review agent performance")
        
        if recommendations:
            for rec in recommendations[:3]:  # Show top 3 recommendations
                print(f"• {rec}")
        else:
            print("✅ System running optimally")
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """Create a visual progress bar"""
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        return bar
    
    def _handle_alert(self, alert: Dict[str, Any]):
        """Handle system alerts"""
        # In production, this would send notifications, trigger actions, etc.
        print(f"🚨 ALERT: {alert['message']}")
    
    async def generate_monitoring_report(self, duration_hours: int = 1) -> Dict[str, Any]:
        """Generate a comprehensive monitoring report"""
        print(f"📈 Generating monitoring report for last {duration_hours} hour(s)...")
        
        # Filter data for the specified duration
        cutoff_time = time.time() - (duration_hours * 3600)
        relevant_data = [d for d in self.monitoring_data if d['timestamp'] >= cutoff_time]
        
        # Generate report
        report = {
            'report_id': f"monitoring_report_{int(time.time())}",
            'generated_at': time.time(),
            'duration_hours': duration_hours,
            'summary': await self._generate_report_summary(relevant_data),
            'alerts': self.alert_history[-20:],  # Last 20 alerts
            'recommendations': await self._generate_report_recommendations(relevant_data),
            'raw_data_sample': relevant_data[:10]  # Sample of raw data
        }
        
        return report
    
    async def _generate_report_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate report summary from monitoring data"""
        system_health_data = [d for d in data if d['type'] == 'system_health']
        agent_data = [d for d in data if d['type'] == 'agent_performance']
        task_data = [d for d in data if d['type'] == 'task_execution']
        
        summary = {
            'data_points': len(data),
            'average_system_health': self._calculate_average_health(system_health_data),
            'agent_performance': self._calculate_average_performance(agent_data),
            'task_metrics': self._calculate_task_metrics(task_data),
            'alert_count': len([a for a in self.alert_history if a['timestamp'] >= data[0]['timestamp'] if data else time.time()])
        }
        
        return summary
    
    def _calculate_average_health(self, health_data: List[Dict[str, Any]]) -> float:
        """Calculate average system health"""
        if not health_data:
            return 0.0
        
        total_health = sum(d['data']['overall_health']['score'] for d in health_data)
        return total_health / len(health_data)
    
    def _calculate_average_performance(self, agent_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate average agent performance"""
        if not agent_data:
            return {'success_rate': 0, 'active_agents': 0}
        
        success_rates = [d['data']['average_success_rate'] for d in agent_data]
        active_agents = [d['data']['active_agents'] for d in agent_data]
        
        return {
            'success_rate': sum(success_rates) / len(success_rates),
            'active_agents': sum(active_agents) / len(active_agents)
        }
    
    def _calculate_task_metrics(self, task_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate task execution metrics"""
        if not task_data:
            return {'success_rate': 0, 'average_pending': 0}
        
        success_rates = [d['data']['success_rate'] for d in task_data]
        pending_tasks = [d['data']['pending_tasks'] for d in task_data]
        
        return {
            'success_rate': sum(success_rates) / len(success_rates),
            'average_pending': sum(pending_tasks) / len(pending_tasks)
        }
    
    async def _generate_report_recommendations(self, data: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on monitoring data"""
        recommendations = []
        
        # Analyze system health trends
        health_data = [d for d in data if d['type'] == 'system_health']
        if health_data:
            recent_health = health_data[-1]['data']['overall_health']['score']
            if recent_health < 70:
                recommendations.append("Immediate attention needed for system health degradation")
        
        # Analyze memory usage
        memory_data = [d for d in data if d['type'] == 'memory_usage']
        if memory_data:
            avg_ram_usage = sum(d['data']['ram_usage_percent'] for d in memory_data) / len(memory_data)
            if avg_ram_usage > 75:
                recommendations.append("Consider memory optimization or capacity increase")
        
        # Analyze alerts
        if len(self.alert_history) > 10:
            recommendations.append("High alert frequency - review system stability")
        
        return recommendations if recommendations else ["System operating within normal parameters"]

async def main():
    """Main entry point for the system monitor"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced AI System Monitor')
    parser.add_argument('--report', action='store_true', help='Generate monitoring report')
    parser.add_argument('--duration', type=int, default=1, help='Report duration in hours')
    parser.add_argument('--export', type=str, help='Export report to file')
    
    args = parser.parse_args()
    
    monitor = SystemMonitor()
    
    try:
        if args.report:
            # Generate and display report
            report = await monitor.generate_monitoring_report(args.duration)
            
            print("\n" + "=" * 80)
            print("📊 MONITORING REPORT")
            print("=" * 80)
            
            print(f"Report ID: {report['report_id']}")
            print(f"Duration: {report['duration_hours']} hour(s)")
            print(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(report['generated_at']))}")
            
            print("\nSUMMARY:")
            summary = report['summary']
            print(f"  • Data Points: {summary['data_points']}")
            print(f"  • Average System Health: {summary['average_system_health']:.1f}%")
            print(f"  • Agent Success Rate: {summary['agent_performance']['success_rate']:.1f}%")
            print(f"  • Task Success Rate: {summary['task_metrics']['success_rate']:.1f}%")
            print(f"  • Alerts: {summary['alert_count']}")
            
            print("\nRECOMMENDATIONS:")
            for rec in report['recommendations']:
                print(f"  • {rec}")
            
            # Export report if requested
            if args.export:
                with open(args.export, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                print(f"\n✅ Report exported to: {args.export}")
                
        else:
            # Start real-time monitoring
            await monitor.start_comprehensive_monitoring()
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")
    except Exception as e:
        print(f"❌ Monitor error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
