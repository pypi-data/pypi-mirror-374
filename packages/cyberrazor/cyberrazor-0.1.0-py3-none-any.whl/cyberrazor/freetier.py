import os
import sys
import time
import hashlib
import platform
import socket
import psutil
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import deque
import logging
import shutil
import subprocess
import threading
import requests
import json

logger: logging.Logger


def print_banner():
	banner = """
 \033[34m██████╗██╗   ██╗██████╗ ███████╗██████╗     ██████╗  █████╗ ███████╗ ██████╗ ██████╗ 
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗    ██╔══██╗██╔══██╗╚══███╔╝██╔═══██╗██╔══██╗
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝    ██████╔╝███████║  ███╔╝ ██║   ██║██████╔╝
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗    ██╔══██╗██╔══██║ ███╔╝  ██║   ██║██╔══██╗
╚██████╗   ██║   ██████╔╝███████╗██║  ██║    ██║  ██║██║  ██║███████╗╚██████╔╝██║  ██║
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝
\033[0m"""
	print(banner)
	print("="*88)
	print("Welcome to Cyber Razor - Advanced Security Agent v2.0")
	print("Real-time Threat Detection & AI Analysis")
	print("="*88)
	print()


class Config:
	LOGGING_ENABLED = True
	LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
	LOG_FORMAT = os.getenv("LOG_FORMAT", "table")
	LOG_FILE = os.path.join(os.path.expanduser("~"), ".cyberrazor", "freetier.log")
	SCAN_PATHS = [os.path.expanduser("~/Downloads"), os.path.expanduser("~/Desktop")]
	EXTENSIONS = ['.exe', '.dll', '.py', '.sh', '.pdf', '.doc', '.docx', '.apk', '.jar', '.bat', '.ps1']
	NETWORK_ANALYSIS_ENABLED = os.getenv("NETWORK_ANALYSIS_ENABLED", "true").lower() == "true"
	NETWORK_ANALYSIS_DURATION = int(os.getenv("NETWORK_ANALYSIS_DURATION", "30"))
	CIA_AUDITS_ENABLED = os.getenv("CIA_AUDITS_ENABLED", "true").lower() == "true"
	WAZUH_MANAGER = os.getenv("WAZUH_MANAGER", "10.0.0.2")
	WAZUH_API_USER = os.getenv("WAZUH_API_USER", "wazuh-wui")
	WAZUH_API_PASSWORD = os.getenv("WAZUH_API_PASSWORD", "123")
	WAZUH_AGENT_NAME = os.getenv("WAZUH_AGENT_NAME", "agent-1")
	WAZUH_AGENT_IP = os.getenv("WAZUH_AGENT_IP", "192.168.10.130")
	WAZUH_MASTER_IP = os.getenv("WAZUH_MASTER_IP", "192.168.10.128")


class TableFormatter(logging.Formatter):
	def __init__(self):
		super().__init__()
		self.max_width = 80

	def format(self, record):
		timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
		level = record.levelname
		message = record.getMessage()
		if len(message) > self.max_width - 20:
			message = message[:self.max_width - 23] + "..."
		colors = {'DEBUG': '\033[36m', 'INFO': '\033[32m', 'WARNING': '\033[33m', 'ERROR': '\033[31m', 'CRITICAL': '\033[35m'}
		reset = '\033[0m'
		color = colors.get(level, '')
		formatted = f"{color}│ {timestamp} │ {level:8} │ {message:<{self.max_width-20}} │{reset}"
		if hasattr(record, 'extra_data') and record.extra_data:
			extra_lines = []
			for key, value in record.extra_data.items():
				if key not in ['timestamp', 'level', 'message', 'module', 'function', 'line']:
					if isinstance(value, dict):
						for sub_key, sub_value in value.items():
							extra_lines.append(f"{color}│         │          │   {sub_key}: {sub_value}")
					else:
						extra_lines.append(f"{color}│         │          │   {key}: {value}")
			if extra_lines:
				formatted += "\n" + "\n".join(extra_lines)
		return formatted


class PrettyConsoleHandler(logging.StreamHandler):
	def __init__(self, format_type="table"):
		super().__init__(sys.stdout)
		self.format_type = format_type
		self.table_footer_printed = False
		if format_type == "table":
			self.setFormatter(TableFormatter())
			print("\033[1m┌──────────┬──────────┬────────────────────────────────────────────────────────────────────────────┐")
			print("│ Time     │ Level    │ Message                                                                    │")
			print("├──────────┼──────────┼────────────────────────────────────────────────────────────────────────────┤\033[0m")
		else:
			self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

	def close(self):
		if self.format_type == "table" and not self.table_footer_printed:
			print("\033[1m└──────────┴──────────┴────────────────────────────────────────────────────────────────────────────┘\033[0m")
			self.table_footer_printed = True
		super().close()


def setup_logging(silent=False, format_type=None):
	os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True)
	if format_type is None:
		format_type = Config.LOG_FORMAT
	file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
	file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
	handlers = [file_handler]
	if not silent:
		console_handler = PrettyConsoleHandler(format_type)
		handlers.append(console_handler)
	logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL), format='%(asctime)s - %(levelname)s - %(message)s', handlers=handlers)
	return logging.getLogger(__name__)


def hash_file(file_path: str) -> Optional[str]:
	try:
		sha256_hash = hashlib.sha256()
		with open(file_path, "rb") as f:
			for chunk in iter(lambda: f.read(4096), b""):
				sha256_hash.update(chunk)
		return sha256_hash.hexdigest()
	except Exception as e:
		logger.error(f"Error hashing file {file_path}: {e}")
		return None


def get_file_metadata(file_path: str) -> Dict[str, Any]:
	try:
		stat = os.stat(file_path)
		return {
			"size": stat.st_size,
			"created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
			"modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
			"accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
			"permissions": oct(stat.st_mode)[-3:],
			"owner": stat.st_uid if hasattr(stat, 'st_uid') else None
		}
	except Exception as e:
		logger.error(f"Error getting metadata for {file_path}: {e}")
		return {}


def detect_source(file_path: str) -> str:
	path_lower = file_path.lower()
	if any(usb_path in path_lower for usb_path in ['/media/', 'd:/', 'e:/', 'f:/', 'g:/']):
		return "USB"
	elif any(download_path in path_lower for download_path in ['/downloads', '/download', 'downloads']):
		return "Download"
	elif any(desktop_path in path_lower for desktop_path in ['/desktop', 'desktop']):
		return "Desktop"
	elif any(temp_path in path_lower for temp_path in ['/tmp', '/temp', 'temp']):
		return "Temporary"
	else:
		return "System"


def handle_threat_response(file_path: str, ai_result: Dict[str, Any], file_metadata: Dict[str, Any], source: str) -> str:
	print(f"\n🚨 THREAT DETECTED: {os.path.basename(file_path)}")
	print(f"   Verdict: {ai_result.get('verdict', 'Unknown')}")
	print(f"   Confidence: {ai_result.get('confidence', 'Unknown')}")
	print(f"   Severity: {ai_result.get('severity', 'Unknown')}")
	print(f"   Reason: {ai_result.get('reason', 'No reason provided')}")
	print(f"   Source: {source}")
	print(f"   File Size: {file_metadata.get('size', 0)} bytes")
	while True:
		print("\nSelect action:")
		print("1. ✅ Allow (Mark as safe)")
		print("2. 🗑️  Remove (Delete file)")
		print("3. 🚫 Quarantine (Move to quarantine)")
		print("4. 📊 More Details")
		choice = input("\nEnter choice (1-4): ").strip()
		if choice == "1":
			logger.info(f"✅ User allowed file: {file_path}")
			return "allowed"
		elif choice == "2":
			try:
				os.remove(file_path)
				logger.info(f"🗑️  User removed file: {file_path}")
				return "removed"
			except Exception as e:
				logger.error(f"Error removing file {file_path}: {e}")
				print(f"❌ Error removing file: {e}")
				return "error"
		elif choice == "3":
			try:
				quarantine_dir = os.path.join(os.path.expanduser("~"), ".cyberrazor", "quarantine")
				os.makedirs(quarantine_dir, exist_ok=True)
				filename = os.path.basename(file_path)
				quarantine_path = os.path.join(quarantine_dir, f"{int(time.time())}_{filename}")
				shutil.move(file_path, quarantine_path)
				logger.info(f"🚫 User quarantined file: {file_path} -> {quarantine_path}")
				return "quarantined"
			except Exception as e:
				logger.error(f"Error quarantining file {file_path}: {e}")
				print(f"❌ Error quarantining file: {e}")
				return "error"
		elif choice == "4":
			print(f"\n📊 Detailed Information:")
			print(f"   Full Path: {file_path}")
			print(f"   Hash: {file_metadata.get('hash', 'Unknown')}")
			print(f"   Created: {file_metadata.get('created', 'Unknown')}")
			print(f"   Modified: {file_metadata.get('modified', 'Unknown')}")
			print(f"   Permissions: {file_metadata.get('permissions', 'Unknown')}")
			print(f"   Threat Type: {ai_result.get('threat_type', 'Unknown')}")
		else:
			print("❌ Invalid choice. Please select 1-4.")


def scan_files(force_scan: bool = False, custom_path: str = None, hash_only: bool = False) -> None:
	if custom_path:
		scan_paths = [custom_path]
		scan_description = f"Custom path: {custom_path}"
	else:
		scan_paths = Config.SCAN_PATHS
		scan_description = f"Free Tier Scan: Downloads and Desktop"
	scan_mode = "Hash-Only" if hash_only else "Basic Hash Check"
	logger.info(f"🔍 Starting file scan...", extra={"extra_data": {
		"event_type": "File Scan",
		"entity_path": custom_path if custom_path else "Downloads and Desktop",
		"detection_method": scan_mode,
		"remarks": f"{scan_description} for {len(Config.EXTENSIONS)} file types"
	}})
	scanned_count = 0
	threat_count = 0
	for root_path in scan_paths:
		if not os.path.exists(root_path):
			continue
		for root, _, files in os.walk(root_path):
			for file in files:
				if any(file.lower().endswith(ext) for ext in Config.EXTENSIONS):
					file_path = os.path.join(root, file)
					scanned_count += 1
					file_hash = hash_file(file_path)
					if file_hash:
						logger.info(f"Scanning {file_path} ({file_hash[:10]}...)")
						if file_path.lower().endswith('.exe'):
							threat_count += 1
							file_metadata = get_file_metadata(file_path)
							file_metadata['hash'] = file_hash
							source = detect_source(file_path)
							ai_result = {
								"verdict": "Suspicious",
								"confidence": "Medium",
								"reason": "Executable file detected. Manual review recommended in Free Tier.",
								"threat_type": "unknown",
								"severity": "low"
							}
							handle_threat_response(file_path, ai_result, file_metadata, source)
	logger.info(f"Scan complete. Scanned {scanned_count} files, found {threat_count} potential threats.")


class UsageManager:
	def __init__(self):
		self.usage_file = os.path.join(os.path.expanduser("~"), ".cyberrazor", "usage.json")
		self.usage_data = self._load_usage_data()
	def _load_usage_data(self):
		if not os.path.exists(self.usage_file):
			return {"first_use_date": None, "daily_usage": {}}
		try:
			with open(self.usage_file, "r") as f:
				return json.load(f)
		except (IOError, json.JSONDecodeError):
			return {"first_use_date": None, "daily_usage": {}}
	def _save_usage_data(self):
		os.makedirs(os.path.dirname(self.usage_file), exist_ok=True)
		with open(self.usage_file, "w") as f:
			json.dump(self.usage_data, f)
	def check_usage(self):
		today = datetime.now().strftime("%Y-%m-%d")
		if self.usage_data["first_use_date"] is None:
			self.usage_data["first_use_date"] = today
			self.usage_data["daily_usage"][today] = 0
		first_use_date = datetime.strptime(self.usage_data["first_use_date"], "%Y-%m-%d")
		if (datetime.now() - first_use_date).days > 7:
			logger.warning("Your 7-day trial has expired. Please upgrade to Pro.")
			return False
		daily_limit = 5
		if self.usage_data["daily_usage"].get(today, 0) >= daily_limit:
			logger.warning(f"You have reached your daily limit of {daily_limit} scans.")
			return False
		return True
	def record_usage(self):
		today = datetime.now().strftime("%Y-%m-%d")
		self.usage_data["daily_usage"][today] = self.usage_data["daily_usage"].get(today, 0) + 1
		self._save_usage_data()


class NetworkAnalyzer:
	def __init__(self):
		self.capture_running = False
		self.well_known_ports = {20: "FTP", 21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 3306: "MySQL", 5432: "PostgreSQL", 27017: "MongoDB"}
	def start_fallback_monitoring(self):
		try:
			logger.info("🔍 Starting basic network monitoring")
			self.capture_running = True
			self.start_time = time.time()
			monitor_thread = threading.Thread(target=self._fallback_monitor_loop, daemon=True)
			monitor_thread.start()
			logger.info(f"Network monitoring will run for {Config.NETWORK_ANALYSIS_DURATION} seconds.")
			time.sleep(Config.NETWORK_ANALYSIS_DURATION)
			self.capture_running = False
			logger.info("Network monitoring finished.")
			return True
		except Exception as e:
			logger.error(f"Error starting fallback monitoring: {e}")
			return False
	def _fallback_monitor_loop(self):
		try:
			while self.capture_running:
				self._check_active_connections()
				time.sleep(5)
		except Exception as e:
			logger.error(f"Error in fallback monitoring: {e}")
	def _check_active_connections(self):
		try:
			if os.name == 'nt':
				result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, timeout=10)
				if result.returncode == 0:
					self._analyze_netstat_output(result.stdout)
			else:
				result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True, timeout=10)
				if result.returncode == 0:
					self._analyze_netstat_output(result.stdout)
		except Exception as e:
			logger.debug(f"Error checking active connections: {e}")
	def _analyze_netstat_output(self, output):
		try:
			lines = output.strip().split('\n')
			logger.info("Active Network Connections:")
			for line in lines:
				if 'LISTENING' not in line and 'ESTABLISHED' not in line:
					continue
				parts = line.strip().split()
				if len(parts) < 4:
					continue
				proto, local_addr, foreign_addr, state = parts[0], parts[1], parts[2], parts[3]
				try:
					local_ip, local_port_str = local_addr.rsplit(':', 1)
					local_port = int(local_port_str)
					foreign_ip, foreign_port_str = foreign_addr.rsplit(':', 1)
					foreign_port = int(foreign_port_str)
				except ValueError:
					continue
				port_desc = self.well_known_ports.get(local_port) or self.well_known_ports.get(foreign_port)
				log_message = f"  {proto} | {local_addr} -> {foreign_addr} | {state}"
				if port_desc:
					log_message += f" ({port_desc})"
				logger.info(log_message)
				if state == 'ESTABLISHED' and not foreign_ip.startswith('127.0.0.1') and not foreign_ip.startswith('::1') and foreign_ip != "0.0.0.0":
					if foreign_port > 1024 and foreign_port not in self.well_known_ports:
						self.handle_network_threat(proto, local_addr, foreign_addr)
		except Exception as e:
			logger.debug(f"Error analyzing netstat output: {e}")
	def handle_network_threat(self, proto, local_addr, foreign_addr):
		print(f"\n🚨 SUSPICIOUS NETWORK CONNECTION DETECTED:")
		print(f"   Protocol: {proto}")
		print(f"   Connection: {local_addr} -> {foreign_addr}")
		print(f"   Reason: Connection to a non-standard high port.")
		while True:
			print("\nSelect action:")
			print("1. ✅ Allow (Mark as safe)")
			print("2. 🚫 Log as suspicious")
			choice = input("\nEnter choice (1-2): ").strip()
			if choice == "1":
				logger.info(f"✅ User allowed connection: {local_addr} -> {foreign_addr}")
				break
			elif choice == "2":
				logger.warning(f"🚫 User logged suspicious connection: {local_addr} -> {foreign_addr}")
				break
			else:
				print("❌ Invalid choice. Please select 1-2.")


class CIAAuditor:
	def __init__(self):
		self.audit_results = {"confidentiality": {"score": 0, "findings": []}, "integrity": {"score": 0, "findings": []}, "availability": {"score": 0, "findings": []}}
	def run_full_audit(self):
		pc_name = socket.gethostname()
		logger.info(f"🔒 Starting Limited CIA Security Audit on {pc_name}...")
		self._check_confidentiality()
		self._check_integrity()
		self._check_availability()
		overall_score = self.calculate_overall_score()
		logger.info("--- CIA Audit Report ---")
		logger.info(f"Computer: {pc_name}")
		logger.info(f"Overall Score: {overall_score}/100")
		logger.info("------------------------")
		logger.info(f"Confidentiality Score: {self.audit_results['confidentiality']['score']}/100")
		logger.info("  Basis for score:")
		for finding in self.audit_results['confidentiality']['findings']:
			logger.info(f"    - {finding}")
		logger.info(f"Integrity Score: {self.audit_results['integrity']['score']}/100")
		logger.info("  Basis for score:")
		for finding in self.audit_results['integrity']['findings']:
			logger.info(f"    - {finding}")
		logger.info(f"Availability Score: {self.audit_results['availability']['score']}/100")
		logger.info("  Basis for score:")
		for finding in self.audit_results['availability']['findings']:
			logger.info(f"    - {finding}")
		logger.info("--- End of Report ---")
		logger.info("✅ Limited CIA Audit completed.")
		logger.info("Upgrade to Pro for detailed findings and recommendations.")
	def calculate_overall_score(self) -> int:
		conf_score = self.audit_results["confidentiality"].get("score", 0)
		int_score = self.audit_results["integrity"].get("score", 0)
		avail_score = self.audit_results["availability"].get("score", 0)
		return (conf_score + int_score + avail_score) // 3
	def _check_confidentiality(self):
		score = 100
		findings = []
		try:
			if os.name == 'nt':
				result = subprocess.run(['netsh', 'advfirewall', 'show', 'allprofiles', 'state'], capture_output=True, text=True, timeout=10)
				if "State                              ON" in result.stdout:
					findings.append("Firewall is active.")
				else:
					score -= 40
					findings.append("Firewall is inactive or not configured.")
		except Exception as e:
			findings.append(f"Could not check firewall status: {e}")
			score -= 10
		sensitive_extensions = ['.pem', '.key', '.pkcs12', '.p12', '.pfx', '.asc', '.env']
		home_dir = os.path.expanduser("~")
		scan_dirs = [os.path.join(home_dir, ".ssh"), os.path.join(home_dir, "Downloads"), os.path.join(home_dir, "Desktop"), os.path.join(home_dir, "Documents"), os.path.join(home_dir, ".aws"), os.path.join(home_dir, ".config"), os.path.join(home_dir, ".gnupg")]
		findings.append(f"Scanned directories: {', '.join([d.replace(home_dir, '~') for d in scan_dirs])}")
		found_sensitive_files = False
		for s_dir in scan_dirs:
			if not os.path.isdir(s_dir):
				continue
			for root, _, files in os.walk(s_dir):
				for file in files:
					if any(file.lower().endswith(ext) for ext in sensitive_extensions):
						findings.append(f"Potential sensitive file found: {os.path.join(root, file)}")
						if not found_sensitive_files:
							score -= 25
							found_sensitive_files = True
		if not found_sensitive_files:
			findings.append("No sensitive files found in high-risk directories.")
		self.audit_results["confidentiality"]["score"] = score
		self.audit_results["confidentiality"]["findings"] = findings
	def _check_integrity(self):
		score = 100
		findings = []
		try:
			if os.name == 'nt':
				result = subprocess.run(['wmic', '/namespace:\\root\\SecurityCenter2', 'path', 'AntiVirusProduct', 'get', 'displayName'], capture_output=True, text=True, timeout=10)
				if result.stdout.strip() and "displayName" in result.stdout:
					findings.append("Antivirus software detected.")
				else:
					score -= 50
					findings.append("No antivirus software detected.")
		except Exception as e:
			findings.append(f"Could not check for antivirus software: {e}")
			score -= 10
		self.audit_results["integrity"]["score"] = score
		self.audit_results["integrity"]["findings"] = findings
	def _check_availability(self):
		score = 100
		findings = []
		try:
			total, used, free = shutil.disk_usage("/")
			free_percent = (free / total) * 100
			findings.append(f"Disk space: {free_percent:.2f}% free.")
			if free_percent < 15:
				score -= 30
				findings.append("Low disk space warning.")
		except Exception as e:
			findings.append(f"Could not check disk space: {e}")
			score -= 10
		try:
			cpu_usage = psutil.cpu_percent(interval=1)
			mem_usage = psutil.virtual_memory().percent
			findings.append(f"CPU usage: {cpu_usage}%, Memory usage: {mem_usage}%")
			if cpu_usage > 90:
				score -= 25
				findings.append("High CPU usage detected.")
			if mem_usage > 90:
				score -= 25
				findings.append("High memory usage detected.")
		except Exception as e:
			findings.append(f"Could not check CPU/Memory usage: {e}")
			score -= 10
		self.audit_results["availability"]["score"] = max(0, score)
		self.audit_results["availability"]["findings"] = findings


class FIM_Monitor:
	def __init__(self, directories_to_watch, alert_manager):
		self.directories_to_watch = directories_to_watch
		self.alert_manager = alert_manager
		self.baseline = {}
		self.monitoring = False
		self.monitor_thread = None
	def _create_baseline(self):
		logger.info("Creating FIM baseline...")
		baseline = {}
		for directory in self.directories_to_watch:
			if not os.path.isdir(directory):
				continue
			for root, _, files in os.walk(directory):
				for file in files:
					try:
						file_path = os.path.join(root, file)
						baseline[file_path] = hash_file(file_path)
					except Exception as e:
						logger.debug(f"Could not baseline file {file_path}: {e}")
		logger.info("FIM baseline created.")
		return baseline
	def start(self):
		if self.monitoring:
			logger.info("Real-time monitoring is already running.")
			return
		self.baseline = self._create_baseline()
		self.monitoring = True
		self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
		self.monitor_thread.start()
		logger.info("Real-time file monitoring started.")
	def stop(self):
		if not self.monitoring:
			return
		self.monitoring = False
		if self.monitor_thread:
			self.monitor_thread.join()
		logger.info("Real-time file monitoring stopped.")
	def _monitor_loop(self):
		while self.monitoring:
			time.sleep(10)
			try:
				current_state = {}
				for directory in self.directories_to_watch:
					if not os.path.isdir(directory):
						continue
					for root, _, files in os.walk(directory):
						for file in files:
							try:
								file_path = os.path.join(root, file)
								current_state[file_path] = hash_file(file_path)
							except Exception as e:
								logger.debug(f"Could not hash file {file_path}: {e}")
				for file_path, old_hash in self.baseline.items():
					if file_path not in current_state:
						self._generate_alert("File removed", file_path)
					elif current_state.get(file_path) != old_hash:
						self._generate_alert("File modified", file_path)
				for file_path in current_state:
					if file_path not in self.baseline:
						self._generate_alert("File added", file_path)
				self.baseline = current_state
			except Exception as e:
				logger.error(f"Error in FIM loop: {e}")
	def _generate_alert(self, event_type, file_path):
		alert_data = {"timestamp": datetime.now().isoformat(), "agent": {"name": Config.WAZUH_AGENT_NAME}, "manager": {"ip": "local"}, "rule": {"id": 550, "description": f"File Integrity Monitoring: {event_type}: {file_path}"}, "file": {"path": file_path}, "severity": "medium", "source": "FIM"}
		self.alert_manager.process_alert(alert_data)


class LocalAlertManager:
	def __init__(self):
		self.alerts_file = os.path.join(os.path.expanduser("~"), ".cyberrazor", "local_alerts.json")
		self.alerts = self._load_alerts()
	def _load_alerts(self):
		if not os.path.exists(self.alerts_file):
			return []
		try:
			with open(self.alerts_file, "r") as f:
				return json.load(f)
		except (IOError, json.JSONDecodeError):
			return []
	def _save_alerts(self):
		os.makedirs(os.path.dirname(self.alerts_file), exist_ok=True)
		with open(self.alerts_file, "w") as f:
			json.dump(self.alerts, f, indent=4)
	def process_alert(self, alert_data):
		logger.info("Processing alert locally...")
		priority = self._get_priority(alert_data.get("severity"))
		recommendation = self._get_recommendation(alert_data.get("rule", {}).get("id"))
		processed_alert = {"timestamp": datetime.now().isoformat(), "status": "processed_locally", "priority": priority, "recommendation": recommendation, "original_alert": alert_data}
		self.alerts.append(processed_alert)
		self._save_alerts()
		logger.info("✅ Alert has been processed and stored locally.")
	def _get_priority(self, severity):
		if severity == "high":
			return "High"
		elif severity == "medium":
			return "Medium"
		else:
			return "Low"
	def _get_recommendation(self, rule_id):
		if rule_id == 100001:
			return "This is a test alert. No action is required."
		else:
			return "Review the alert details and investigate the source of the activity."
	def display_alerts(self):
		if not self.alerts:
			logger.info("No local alerts found.")
			return
		logger.info("--- Local Alerts ---")
		for alert in self.alerts:
			print(f"Timestamp: {alert['timestamp']}")
			print(f"Priority: {alert['priority']}")
			print(f"Recommendation: {alert['recommendation']}")
			print(f"Details: {alert['original_alert']['rule']['description']}")
			print("--------------------")


class WazuhClient:
	def __init__(self, api_url: str, username: str, password: str, local_alert_manager: LocalAlertManager):
		self.api_url = api_url
		self.auth = (username, password)
		self.local_alert_manager = local_alert_manager
	def send_alert(self, data: Dict[str, Any]) -> bool:
		headers = {'Content-Type': 'application/json'}
		try:
			response = requests.post(f"{self.api_url}/alerts", auth=self.auth, json=data, headers=headers, verify=False, timeout=5)
			response.raise_for_status()
			logger.info("✅ Threat sent to Wazuh Manager")
			return True
		except requests.exceptions.RequestException:
			self.local_alert_manager.process_alert(data)
			return False


def alert_wazuh(file_path: str, ai_result: Dict[str, Any], file_metadata: Dict[str, Any], source: str, local_alert_manager: LocalAlertManager) -> None:
	wazuh_client = WazuhClient(api_url=f"https://{Config.WAZUH_MANAGER}:55000", username=Config.WAZUH_API_USER, password=Config.WAZUH_API_PASSWORD, local_alert_manager=local_alert_manager)
	alert_data = {"timestamp": datetime.now().isoformat(), "agent": {"name": Config.WAZUH_AGENT_NAME, "ip": Config.WAZUH_AGENT_IP}, "manager": {"ip": Config.WAZUH_MASTER_IP}, "rule": {"id": 100001, "description": ai_result.get("reason", "Threat detected")}, "file": {"path": file_path, "hash": file_metadata.get("hash", ""), "size": file_metadata.get("size", 0)}, "severity": ai_result.get("severity", "medium"), "source": source}
	wazuh_client.send_alert(alert_data)


def run_cli():
	global logger
	if sys.stdout.encoding != 'utf-8':
		try:
			sys.stdout.reconfigure(encoding='utf-8')
			sys.stderr.reconfigure(encoding='utf-8')
		except (TypeError, AttributeError):
			import codecs
			sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
			sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)
	print_banner()
	logger = setup_logging()
	logger.info("Freetier agent started.")
	usage_manager = UsageManager()
	local_alert_manager = LocalAlertManager()
	home_dir = os.path.expanduser("~")
	fim_dirs = [os.path.join(home_dir, "Downloads"), os.path.join(home_dir, "Desktop")]
	fim_monitor = FIM_Monitor(fim_dirs, local_alert_manager)
	try:
		while True:
			print("\nCyberRazor Free Tier Menu:")
			print("1. Run File Scan")
			print("2. Run Network Monitoring")
			print("3. Run Limited CIA Audit")
			print("4. Send Test Wazuh Alert")
			print("5. View Local Alerts")
			print("6. Start Real-time Monitoring")
			print("7. Stop Real-time Monitoring")
			print("8. Exit")
			choice = input("Enter your choice (1-8): ").strip()
			if choice == '1':
				scan_files(force_scan=True)
			elif choice == '2':
				if Config.NETWORK_ANALYSIS_ENABLED:
					if usage_manager.check_usage():
						net_analyzer = NetworkAnalyzer()
						if net_analyzer.start_fallback_monitoring():
							usage_manager.record_usage()
				else:
					logger.info("Network analysis is disabled in the configuration.")
			elif choice == '3':
				if Config.CIA_AUDITS_ENABLED:
					auditor = CIAAuditor()
					auditor.run_full_audit()
				else:
					logger.info("CIA audits are disabled in the configuration.")
			elif choice == '4':
				logger.info("Sending test alert to Wazuh...")
				test_file_path = "/tmp/test-file.exe"
				test_ai_result = {"verdict": "Suspicious", "confidence": "High", "reason": "This is a test alert from the CyberRazor Free Tier agent.", "threat_type": "test", "severity": "high"}
				test_file_metadata = {"hash": "d41d8cd98f00b204e9800998ecf8427e", "size": 0}
				alert_wazuh(test_file_path, test_ai_result, test_file_metadata, "test-source", local_alert_manager)
			elif choice == '5':
				local_alert_manager.display_alerts()
			elif choice == '6':
				fim_monitor.start()
			elif choice == '7':
				fim_monitor.stop()
			elif choice == '8':
				logger.info("Exiting Freetier agent.")
				break
			else:
				print("Invalid choice. Please enter a number between 1 and 8.")
	finally:
		fim_monitor.stop()
		logger.info("Freetier agent finished.")
	return 0
