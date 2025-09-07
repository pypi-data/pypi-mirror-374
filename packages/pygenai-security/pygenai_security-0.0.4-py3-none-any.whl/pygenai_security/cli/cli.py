"""
Command Line Interface for PyGenAI Security Framework
Enterprise-ready CLI with comprehensive commands and beautiful output.
"""

import click
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
import time
from datetime import datetime

from ..core.security_scanner import PyGenAIScanner, ScanMode
from ..core.config_manager import ConfigManager
from ..core.exceptions import PyGenAISecurityError, ScanError, ConfigurationError
from ..utils.logger import setup_logging, get_logger
from ..utils.report_generator import ReportGenerator

logger = get_logger(__name__)


@click.group()
@click.version_option(version='1.0.0', prog_name='PyGenAI Security Framework')
@click.option('--config', '-c', type=click.Path(exists=True), help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--quiet', '-q', is_flag=True, help='Suppress non-error output')
@click.pass_context
def cli(ctx, config, verbose, quiet):
    """
    PyGenAI Security Framework - Comprehensive Python and GenAI Security Scanner
    
    A powerful security scanner for Python applications with specialized GenAI/LLM
    vulnerability detection, enterprise features, and VS Code integration.
    
    Repository: https://github.com/RiteshGenAI/pygenai-security
    """
    ctx.ensure_object(dict)
    
    # Setup logging
    if verbose:
        log_level = 'DEBUG'
    elif quiet:
        log_level = 'ERROR'
    else:
        log_level = 'INFO'
    
    setup_logging(level=log_level, log_file='pygenai_security.log')
    
    # Load configuration
    try:
        if config:
            config_manager = ConfigManager(config)
        else:
            config_manager = ConfigManager()
        
        ctx.obj['config'] = config_manager
        
    except ConfigurationError as e:
        click.echo(f"❌ Configuration Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--mode', '-m', 
              type=click.Choice(['fast', 'standard', 'thorough', 'compliance', 'genai_focus']),
              default='standard', 
              help='Scanning mode')
@click.option('--format', '-f', 
              type=click.Choice(['json', 'html', 'csv', 'text']),
              default='text',
              help='Output format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--include', multiple=True, help='File patterns to include')
@click.option('--exclude', multiple=True, help='File patterns to exclude')
@click.option('--severity', '-s',
              type=click.Choice(['info', 'low', 'medium', 'high', 'critical']),
              help='Minimum severity level')
@click.option('--genai-only', is_flag=True, help='Only scan for GenAI vulnerabilities')
@click.option('--no-progress', is_flag=True, help='Disable progress bar')
@click.pass_context
def scan(ctx, path, mode, format, output, include, exclude, severity, genai_only, no_progress):
    """
    Scan directory or file for security vulnerabilities
    
    Examples:
        pygenai scan /path/to/project
        pygenai scan . --mode thorough --format html --output report.html
        pygenai scan src/ --genai-only --severity high
    """
    config_manager = ctx.obj['config']
    
    try:
        # Update configuration based on CLI options
        if severity:
            config_manager.set('filtering.min_threat_level', severity)
        
        if genai_only:
            config_manager.set('scanners.enabled', ['genai_security'])
        
        # Initialize scanner
        scanner = PyGenAIScanner(config_manager)
        
        # Setup progress callback
        progress_callback = None if no_progress else create_progress_callback()
        
        # Start scan
        click.echo(f"🚀 Starting {mode} scan of: {path}")
        click.echo(f"📊 Scanner: PyGenAI Security Framework v1.0.0")
        
        start_time = time.time()
        
        # Execute scan
        results = scanner.scan_directory(
            path,
            scan_mode=ScanMode(mode),
            include_patterns=list(include) if include else None,
            exclude_patterns=list(exclude) if exclude else None,
            progress_callback=progress_callback
        )
        
        scan_duration = time.time() - start_time
        
        # Display results
        display_scan_results(results, format, output, scan_duration)
        
        # Exit with appropriate code
        exit_code = get_exit_code(results)
        sys.exit(exit_code)
        
    except (ScanError, PyGenAISecurityError) as e:
        click.echo(f"❌ Scan Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Unexpected Error: {e}", err=True)
        if ctx.obj.get('verbose'):
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--format', '-f', 
              type=click.Choice(['json', 'text']),
              default='text',
              help='Output format')
@click.pass_context
def scan_file(ctx, file_path, format):
    """
    Scan a single file for vulnerabilities
    
    Example:
        pygenai scan-file app.py --format json
    """
    config_manager = ctx.obj['config']
    
    try:
        scanner = PyGenAIScanner(config_manager)
        
        click.echo(f"🔍 Scanning file: {file_path}")
        
        vulnerabilities = scanner.scan_file(file_path)
        
        if format == 'json':
            output = json.dumps([v.to_dict() for v in vulnerabilities], indent=2)
            click.echo(output)
        else:
            display_file_scan_results(vulnerabilities, file_path)
        
    except Exception as e:
        click.echo(f"❌ Error scanning file: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--enterprise', is_flag=True, help='Show enterprise features status')
@click.pass_context
def status(ctx, enterprise):
    """Show scanner status and configuration"""
    config_manager = ctx.obj['config']
    
    try:
        scanner = PyGenAIScanner(config_manager)
        status_info = scanner.get_scan_status()
        scanner_info = scanner.get_scanner_info()
        
        # Display status
        click.echo("📊 PyGenAI Security Framework Status")
        click.echo("=" * 40)
        
        click.echo(f"Scanner ID: {status_info['scanner_id']}")
        click.echo(f"Version: {scanner_info['scanner_metadata']['version']}")
        click.echo(f"Uptime: {status_info['uptime']:.1f} seconds")
        click.echo(f"License Valid: {'✅' if status_info['license_valid'] else '❌'}")
        
        click.echo("\n🔧 Configuration:")
        click.echo(f"  Max Workers: {status_info['configuration_status']['max_workers']}")
        click.echo(f"  Scan Timeout: {status_info['configuration_status']['scan_timeout']}s")
        click.echo(f"  File Size Limit: {status_info['configuration_status']['file_size_limit_mb']:.1f}MB")
        
        click.echo("\n🔍 Available Scanners:")
        for scanner_name in status_info['available_scanners']:
            click.echo(f"  ✅ {scanner_name}")
        
        if enterprise and status_info['enterprise_enabled']:
            click.echo("\n🏢 Enterprise Features:")
            enterprise_config = config_manager.get_enterprise_config()
            click.echo(f"  License Status: {'✅ Valid' if status_info['license_valid'] else '❌ Invalid'}")
            click.echo(f"  Compliance Frameworks: {len(enterprise_config.get('compliance_frameworks', []))}")
            click.echo(f"  Advanced Analytics: {'✅' if enterprise_config.get('advanced_analytics') else '❌'}")
        
        click.echo("\n🎯 Capabilities:")
        capabilities = scanner_info['capabilities']
        for capability, enabled in capabilities.items():
            status_icon = "✅" if enabled else "❌"
            capability_name = capability.replace('_', ' ').title()
            click.echo(f"  {status_icon} {capability_name}")
        
    except Exception as e:
        click.echo(f"❌ Error getting status: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--reset', is_flag=True, help='Reset to default configuration')
@click.option('--show', is_flag=True, help='Show current configuration')
@click.option('--set', 'set_values', multiple=True, help='Set configuration value (key=value)')
@click.pass_context
def config(ctx, reset, show, set_values):
    """
    Manage configuration settings
    
    Examples:
        pygenai config --show
        pygenai config --set scanners.enabled=traditional_python,genai_security
        pygenai config --reset
    """
    config_manager = ctx.obj['config']
    
    try:
        if reset:
            config_manager.reset_to_defaults()
            click.echo("✅ Configuration reset to defaults")
        
        if set_values:
            for set_value in set_values:
                try:
                    key, value = set_value.split('=', 1)
                    
                    # Parse value (simple parsing for common types)
                    if value.lower() in ['true', 'false']:
                        value = value.lower() == 'true'
                    elif value.isdigit():
                        value = int(value)
                    elif ',' in value:
                        value = [v.strip() for v in value.split(',')]
                    
                    config_manager.set(key, value)
                    click.echo(f"✅ Set {key} = {value}")
                    
                except ValueError:
                    click.echo(f"❌ Invalid format for --set: {set_value} (use key=value)", err=True)
        
        if show:
            config_summary = config_manager.get_config_summary()
            
            click.echo("⚙️ Configuration Summary")
            click.echo("=" * 30)
            
            click.echo(f"Config File: {config_summary.get('config_file', 'Default')}")
            click.echo(f"Enabled Scanners: {', '.join(config_summary['enabled_scanners'])}")
            click.echo(f"Enterprise Enabled: {'✅' if config_summary['enterprise_enabled'] else '❌'}")
            
            click.echo("\n🔧 Performance:")
            perf = config_summary['performance']
            click.echo(f"  Max Workers: {perf['max_workers']}")
            click.echo(f"  Parallel Scanning: {'✅' if perf['parallel_scanning'] else '❌'}")
            click.echo(f"  File Size Limit: {perf['file_size_limit_mb']}MB")
            
            click.echo("\n🔍 Filtering:")
            filtering = config_summary['filtering']
            click.echo(f"  Min Threat Level: {filtering['min_threat_level']}")
            click.echo(f"  Confidence Threshold: {filtering['confidence_threshold']}")
            
            click.echo("\n🔌 Integrations:")
            integrations = config_summary['integrations']
            for integration, enabled in integrations.items():
                status_icon = "✅" if enabled else "❌"
                click.echo(f"  {status_icon} {integration.replace('_', ' ').title()}")
    
    except Exception as e:
        click.echo(f"❌ Configuration error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--format', '-f',
              type=click.Choice(['html', 'pdf', 'csv', 'json']),
              default='html',
              help='Report format')
@click.option('--template', type=click.Path(exists=True), help='Custom report template')
@click.pass_context
def generate_report(ctx, input_file, output_file, format, template):
    """
    Generate formatted report from scan results
    
    Example:
        pygenai generate-report results.json report.html --format html
    """
    try:
        # Load scan results
        with open(input_file, 'r') as f:
            results = json.load(f)
        
        # Initialize report generator
        config_manager = ctx.obj['config']
        report_generator = ReportGenerator(config_manager)
        
        # Generate report
        click.echo(f"📄 Generating {format.upper()} report...")
        
        if template:
            report_generator.generate_report_with_template(results, output_file, template)
        else:
            report_generator.generate_report(results, output_file, format)
        
        click.echo(f"✅ Report generated: {output_file}")
        
    except Exception as e:
        click.echo(f"❌ Report generation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def version(ctx):
    """Show version information"""
    click.echo("PyGenAI Security Framework")
    click.echo("Version: 1.0.0")
    click.echo("Author: RiteshGenAI")
    click.echo("Repository: https://github.com/RiteshGenAI/pygenai-security")
    click.echo("License: MIT")


def create_progress_callback():
    """Create progress callback for CLI"""
    def progress_callback(progress_data):
        percentage = progress_data.get('progress_percentage', 0)
        current_scanner = progress_data.get('current_scanner', '')
        processed_files = progress_data.get('processed_files', 0)
        total_files = progress_data.get('total_files', 0)
        
        # Simple progress indicator
        bar_length = 40
        filled_length = int(bar_length * percentage / 100)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        click.echo(f"\r[{bar}] {percentage:.1f}% - {current_scanner} - {processed_files}/{total_files} files", nl=False)
    
    return progress_callback


def display_scan_results(results: Dict[str, Any], format: str, output: Optional[str], scan_duration: float):
    """Display scan results in specified format"""
    
    if format == 'json':
        output_content = json.dumps(results, indent=2, default=str)
        
        if output:
            with open(output, 'w') as f:
                f.write(output_content)
            click.echo(f"\n✅ JSON results saved to: {output}")
        else:
            click.echo(output_content)
    
    elif format in ['html', 'csv']:
        if not output:
            click.echo(f"❌ Output file required for {format} format", err=True)
            sys.exit(1)
        
        try:
            report_generator = ReportGenerator()
            report_generator.generate_report(results, output, format)
            click.echo(f"\n✅ {format.upper()} report saved to: {output}")
        except Exception as e:
            click.echo(f"❌ Failed to generate {format} report: {e}", err=True)
            sys.exit(1)
    
    else:  # text format
        display_text_results(results, scan_duration)
        
        if output:
            # Save text results to file
            with open(output, 'w') as f:
                # Redirect stdout temporarily to capture output
                import contextlib
                import io
                
                text_output = io.StringIO()
                with contextlib.redirect_stdout(text_output):
                    display_text_results(results, scan_duration)
                
                f.write(text_output.getvalue())
            click.echo(f"\n✅ Text results saved to: {output}")


def display_text_results(results: Dict[str, Any], scan_duration: float):
    """Display results in human-readable text format"""
    
    summary = results.get('summary', {})
    security_metrics = results.get('security_metrics', {})
    vulnerabilities = results.get('vulnerabilities', [])
    
    click.echo("\n" + "=" * 60)
    click.echo("🎯 PYGENAI SECURITY SCAN RESULTS")
    click.echo("=" * 60)
    
    # Summary
    click.echo(f"📊 Scan Summary:")
    click.echo(f"   Duration: {scan_duration:.2f} seconds")
    click.echo(f"   Files Scanned: {summary.get('files_scanned', 0)}")
    click.echo(f"   Total Vulnerabilities: {summary.get('total_vulnerabilities', 0)}")
    click.echo(f"   Scanners Used: {', '.join(summary.get('scanners_executed', []))}")
    
    # Threat level breakdown
    if security_metrics.get('by_threat_level'):
        click.echo(f"\n🚨 By Threat Level:")
        threat_levels = security_metrics['by_threat_level']
        for level, count in threat_levels.items():
            if count > 0:
                icon = get_threat_level_icon(level)
                click.echo(f"   {icon} {level.title()}: {count}")
    
    # Category breakdown
    if security_metrics.get('by_category'):
        click.echo(f"\n🔍 By Category:")
        categories = security_metrics['by_category']
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                category_name = category.replace('_', ' ').title()
                click.echo(f"   • {category_name}: {count}")
    
    # Risk analysis
    risk_analysis = results.get('risk_analysis', {})
    if risk_analysis:
        click.echo(f"\n⚠️ Risk Analysis:")
        click.echo(f"   Overall Risk Level: {risk_analysis.get('risk_level', 'unknown').upper()}")
        click.echo(f"   Risk Score: {risk_analysis.get('risk_score', 0):.1f}")
    
    # Top vulnerabilities
    if vulnerabilities:
        click.echo(f"\n🔍 Top Vulnerabilities:")
        top_vulns = sorted(vulnerabilities, key=lambda v: v.get('threat_level_numeric', 0), reverse=True)[:5]
        
        for i, vuln in enumerate(top_vulns, 1):
            threat_level = vuln.get('threat_level', 'unknown')
            icon = get_threat_level_icon(threat_level)
            
            click.echo(f"   {i}. {icon} {vuln.get('title', 'Unknown')}")
            click.echo(f"      File: {vuln.get('file_path', '')}:{vuln.get('line_number', 0)}")
            click.echo(f"      Category: {vuln.get('category_display', '')}")
    
    # Recommendations
    recommendations = results.get('recommendations', [])
    if recommendations:
        click.echo(f"\n💡 Recommendations:")
        for i, rec in enumerate(recommendations[:5], 1):
            click.echo(f"   {i}. {rec}")
    
    # Enterprise features
    enterprise_features = results.get('enterprise_features', {})
    if enterprise_features.get('enabled'):
        click.echo(f"\n🏢 Enterprise Features Active")
        click.echo(f"   License Valid: {'✅' if enterprise_features.get('license_valid') else '❌'}")
        click.echo(f"   Compliance Reporting: {'✅' if enterprise_features.get('compliance_reporting') else '❌'}")


def display_file_scan_results(vulnerabilities: list, file_path: str):
    """Display single file scan results"""
    
    click.echo(f"\n📁 File: {file_path}")
    click.echo(f"🔍 Vulnerabilities Found: {len(vulnerabilities)}")
    
    if not vulnerabilities:
        click.echo("✅ No security vulnerabilities detected!")
        return
    
    click.echo("\n" + "-" * 50)
    
    for i, vuln in enumerate(vulnerabilities, 1):
        threat_level = vuln.threat_level.name.lower()
        icon = get_threat_level_icon(threat_level)
        
        click.echo(f"{i}. {icon} {vuln.title}")
        click.echo(f"   Line {vuln.line_number}: {vuln.description}")
        click.echo(f"   Category: {vuln.category.display_name}")
        click.echo(f"   Confidence: {vuln.confidence:.2f}")
        
        if vuln.remediation:
            click.echo(f"   💡 Remediation: {vuln.remediation}")
        
        click.echo()


def get_threat_level_icon(threat_level: str) -> str:
    """Get icon for threat level"""
    icons = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢',
        'info': '🔵'
    }
    return icons.get(threat_level.lower(), '⚪')


def get_exit_code(results: Dict[str, Any]) -> int:
    """Get appropriate exit code based on scan results"""
    summary = results.get('summary', {})
    security_metrics = results.get('security_metrics', {})
    
    # Check for scan errors
    if summary.get('scan_errors'):
        return 2  # Scan errors
    
    # Check threat levels
    threat_levels = security_metrics.get('by_threat_level', {})
    
    if threat_levels.get('critical', 0) > 0:
        return 3  # Critical vulnerabilities found
    elif threat_levels.get('high', 0) > 0:
        return 1  # High vulnerabilities found
    elif summary.get('total_vulnerabilities', 0) > 0:
        return 0  # Other vulnerabilities found, but not critical/high
    else:
        return 0  # No vulnerabilities found


if __name__ == '__main__':
    cli()
