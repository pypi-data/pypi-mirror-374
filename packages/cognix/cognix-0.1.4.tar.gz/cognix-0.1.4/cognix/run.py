"""
Run Command for Cognix - Specification Compliant
Handles code execution according to exact requirements

This module should be placed at: cognix/run.py (not in commands subdirectory)
"""

import subprocess
import time
import os
import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class SimpleTestRunner:
    """Simple test runner for v0.1.4"""
    
    def find_test_files(self, target_file: str) -> List[str]:
        """Find test files for the target file"""
        target_path = Path(target_file)
        base_name = target_path.stem
        
        patterns = [
            f"test_{base_name}.py",
            f"tests/test_{base_name}.py", 
            f"{base_name}_test.py",
        ]
        
        found = []
        for pattern in patterns:
            if os.path.exists(pattern):
                found.append(pattern)
        return found
    
    def run_pytest(self, test_file: str) -> Dict[str, Any]:
        """Run pytest and return results"""
        try:
            result = subprocess.run(
                ['python', '-m', 'pytest', test_file, '-v'],
                capture_output=True, text=True, timeout=30
            )
            return {
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {'exit_code': -1, 'stdout': '', 'stderr': str(e)}
    
    def parse_pytest_output(self, stdout: str) -> Dict[str, Any]:
        """Parse pytest output for clean display"""
        passed = failed = 0
        test_results = []
        seen_tests = set()  # 重複防止
        
        for line in stdout.split('\n'):
            if '::' in line and ('PASSED' in line or 'FAILED' in line):
                parts = line.split('::')
                if len(parts) >= 2:
                    test_name = parts[1].split()[0]
                    if test_name not in seen_tests:  # 重複チェック
                        seen_tests.add(test_name)
                        status = 'passed' if 'PASSED' in line else 'failed'
                        test_results.append({'name': test_name, 'status': status})
                        
                        if status == 'passed':
                            passed += 1
                        else:
                            failed += 1
        
        return {'passed': passed, 'failed': failed, 'test_results': test_results}


class RunCommand:
    """Run command implementation"""
    
    def __init__(self, cognix_cli):
        """Initialize run command"""
        self.cli = cognix_cli
        self.history = []
    
    def execute(self, args: List[str]):
        """Execute run command according to specification"""
        if not args:
            print("Usage: /run <file> [--args 'arguments'] [--watch] [--test] [--profile]")
            print("\nOptions:")
            print("  --args    Arguments to pass to the script")
            print("  --watch   Watch file for changes and re-run")
            print("  --test    Run with pytest for testing")
            print("  --profile Show execution time and performance")
            return
        
        file_path = args[0]
        script_args = []
        watch_mode = False
        test_mode = False
        profile_mode = False
        
        # Parse arguments
        i = 1
        while i < len(args):
            if args[i] == '--args' and i + 1 < len(args):
                script_args = args[i + 1].split()
                i += 2
            elif args[i] == '--watch':
                watch_mode = True
                i += 1
            elif args[i] == '--test':
                test_mode = True
                i += 1
            elif args[i] == '--profile':
                profile_mode = True
                i += 1
            else:
                i += 1
        
        # Basic file validation
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            print(f"File not found: {file_path}")
            return
        
        # Execute based on mode
        if watch_mode:
            self._execute_watch_mode(file_path_obj, script_args, profile_mode)
        elif test_mode:
            self._execute_test_mode(file_path_obj, profile_mode)
        else:
            self._execute_normal_mode(file_path_obj, script_args, profile_mode)
    
    def _execute_normal_mode(self, file_path: Path, script_args: List[str], profile_mode: bool):
        """Normal execution mode"""
        language = self._get_language(file_path)
        
        if profile_mode and language == 'python':
            self._run_with_profile(file_path, script_args)
            return
        
        executor = self._get_executor(language)
        
        if not executor:
            print(f"No executor available for {language} files")
            return
        
        command = executor + [str(file_path)] + script_args
        
        print(f"Executing: {file_path.name}")
        if script_args:
            print(f"Arguments: {' '.join(script_args)}")
        
        self._run_command(command, file_path.parent, profile_mode)
    
    def _execute_test_mode(self, file_path: Path, profile_mode: bool):
        """Test mode with file detection and clean output"""
        test_runner = SimpleTestRunner()
        test_files = test_runner.find_test_files(str(file_path))
        
        print(f"Tests for {file_path.name}")
        print("─" * 20)
        
        if not test_files:
            print("No test files found")
            print(f"Expected: test_{file_path.stem}.py or tests/test_{file_path.stem}.py")
            return
        
        print(f"Found: {', '.join(test_files)}")
        print()
        
        # Run first test file
        results = test_runner.run_pytest(test_files[0])
        parsed = test_runner.parse_pytest_output(results['stdout'])
        
        print("Results:")
        for test in parsed['test_results']:
            icon = "✅" if test['status'] == 'passed' else "❌"
            print(f"{icon} {test['name']}")
        
        print()
        total = parsed['passed'] + parsed['failed']
        if total > 0:
            print(f"Summary: {parsed['passed']} passed, {parsed['failed']} failed")
        
        self._save_to_history(['pytest'] + test_files, results['exit_code'], 0)
    
    def _execute_watch_mode(self, file_path: Path, script_args: List[str], profile_mode: bool):
        """Watch mode - simple file monitoring without external dependencies"""
        print(f"Watching {file_path.name} for changes... (Ctrl+C to stop)")
        print("Note: This is a basic polling implementation")
        
        last_modified = file_path.stat().st_mtime
        
        # Initial execution
        if profile_mode:
            self._run_with_profile(file_path, script_args)
        else:
            language = self._get_language(file_path)
            executor = self._get_executor(language)
            if executor:
                command = executor + [str(file_path)] + script_args
                self._run_command(command, file_path.parent, False)
        
        try:
            while True:
                time.sleep(1)  # Check every second
                
                if not file_path.exists():
                    print(f"File {file_path.name} was deleted. Stopping watch.")
                    break
                
                current_modified = file_path.stat().st_mtime
                if current_modified > last_modified:
                    last_modified = current_modified
                    print(f"\nFile changed: {file_path.name}")
                    print("Re-executing...")
                    
                    if profile_mode:
                        self._run_with_profile(file_path, script_args)
                    else:
                        language = self._get_language(file_path)
                        executor = self._get_executor(language)
                        if executor:
                            command = executor + [str(file_path)] + script_args
                            self._run_command(command, file_path.parent, False)
                    
                    print(f"\nWatching {file_path.name} for changes... (Ctrl+C to stop)")
                    
        except KeyboardInterrupt:
            print("\nStopped watching")
    
    def _run_with_profile(self, file_path: Path, script_args: List[str]):
        """Profile execution with cProfile and detailed analysis"""
        import cProfile
        import pstats
        import io
        import tempfile
        
        print(f"🔍 Profiling: {file_path.name}")
        print("\nRunning with profiler...")
        
        try:
            # Create temporary file for profile data
            with tempfile.NamedTemporaryFile(suffix='.prof', delete=False) as tmp:
                temp_path = tmp.name
            
            # Build command for cProfile
            command = ['python', '-m', 'cProfile', '-o', temp_path, str(file_path)] + script_args
            start_time = time.time()
            
            # Run with profiler
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(file_path.parent)
            )
            
            total_time = time.time() - start_time
            
            # Display normal output first
            if result.stdout.strip():
                print(result.stdout)
            
            if result.stderr.strip():
                print("Error output:", result.stderr)
            
            # Parse and display profile results
            try:
                stats = pstats.Stats(temp_path)
                stats.sort_stats('cumulative')
                
                print("\n📊 Performance Report:")
                print("━" * 20)
                print(f"⏱️  Total time: {total_time:.2f}s")
                print("🔥 Top functions:")
                
                # Get stats data directly instead of using print_stats
                stats_data = stats.stats
                sorted_stats = sorted(stats_data.items(), key=lambda x: x[1][3], reverse=True)
                
                count = 0
                for (filename, lineno, func_name), (cc, nc, tt, ct, callers) in sorted_stats[:5]:
                    if ct < 0.001:  # Skip negligible times
                        continue
                    
                    # Clean up function name for display
                    if func_name == '<module>':
                        display_name = '<module>'
                    elif 'built-in method' in func_name:
                        display_name = func_name.replace('built-in method ', '')
                    else:
                        display_name = func_name
                    
                    percentage = (ct / total_time * 100) if total_time > 0 else 0
                    print(f"  {count + 1}. {display_name:<20} {ct:.1f}s ({percentage:.0f}%)")
                    count += 1
                
                if count > 0:
                    print(f"\n💡 Top function consumes most execution time")
                
            except Exception as e:
                print(f"Profile analysis failed: {e}")
                # Fallback: show basic timing info
                print(f"\n📊 Basic Profile:")
                print(f"⏱️  Total execution time: {total_time:.2f}s")
                
            # Save to history
            self._save_to_history(
                ['python', '-m', 'cProfile'] + [str(file_path)] + script_args,
                result.returncode,
                total_time
            )
            
        except subprocess.TimeoutExpired:
            print("Profiling timed out (>30s)")
        except Exception as e:
            print(f"Profiling error: {e}")
        finally:
            # Clean up temporary file
            try:
                import os
                if 'temp_path' in locals():
                    os.unlink(temp_path)
            except:
                pass
    
    def _run_command(self, command: List[str], working_dir: Path, profile_mode: bool):
        """Execute command and display results"""
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(working_dir)
            )
            
            duration = time.time() - start_time
            
            # Display results
            if result.returncode == 0:
                print(f"Success ({duration*1000:.0f}ms)")
                if result.stdout.strip():
                    print("\nOutput:")
                    print(result.stdout)
            else:
                print(f"Failed (exit code: {result.returncode})")
                if result.stderr.strip():
                    print("\nError:")
                    print(result.stderr)
            
            # Profile info
            if profile_mode:
                print(f"\nProfile:")
                print(f"  Command: {' '.join(command)}")
                print(f"  Duration: {duration*1000:.0f}ms")
                print(f"  Exit code: {result.returncode}")
                print(f"  Working dir: {working_dir}")
            
            # Save to history
            self._save_to_history(command, result.returncode, duration)
            
        except subprocess.TimeoutExpired:
            print("Execution timed out (>30s)")
        except Exception as e:
            print(f"Execution error: {e}")
    
    def _get_language(self, file_path: Path) -> str:
        """Get language from file extension"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.go': 'go',
            '.rs': 'rust',
            '.java': 'java'
        }
        return ext_map.get(file_path.suffix.lower(), 'python')
    
    def _get_executor(self, language: str) -> List[str]:
        """Get executor command for language"""
        executors = {
            'python': ['python', '-u'],
            'javascript': ['node'],
            'typescript': ['npx', 'ts-node'],
            'go': ['go', 'run']
        }
        return executors.get(language, ['python', '-u'])
    
    def _save_to_history(self, command: List[str], exit_code: int, duration: float):
        """Save execution to history"""
        entry = {
            'command': ' '.join(command),
            'exit_code': exit_code,
            'duration': duration,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'success': exit_code == 0
        }
        
        self.history.append(entry)
        if len(self.history) > 20:
            self.history = self.history[-20:]
    
    def show_history(self, limit: int = 10):
        """Show execution history"""
        if not self.history:
            print("No execution history")
            return
        
        print(f"Recent executions (last {min(limit, len(self.history))}):")
        
        for i, entry in enumerate(self.history[-limit:], 1):
            status = "✅" if entry['success'] else "❌"
            cmd = entry['command']
            if len(cmd) > 50:
                cmd = cmd[:47] + "..."
            
            print(f"{i:2d}. {status} {cmd}")
            print(f"    {entry['timestamp']} - {entry['duration']*1000:.0f}ms - exit {entry['exit_code']}")