#!/usr/bin/env python3
"""
HashID CLI Interface - Main entry point
"""

import argparse
import sys
import os
import time
import json
import csv
from datetime import datetime
from typing import List, Dict, Any

from ..core.analyzer import HashTokenAnalyzer


def persistent_mode(quick_mode=False, verbose=True):
    """Run in persistent mode for continuous hash/token analysis."""
    session_history = []
    analysis_count = 0
    
    if not quick_mode:
        print_banner()
    
    print("\n" + "="*60)
    print("PERSISTENT HASH/TOKEN ANALYZER - v2.0")
    print("="*60)
    print("Enter hash/token followed by ENTER to analyze.")
    print("Commands: 'help', 'history', 'clear', 'stats', 'quit'")
    print("Tip: Use Ctrl+C or 'quit' to exit\n")
    
    start_time = time.time()
    
    while True:
        try:
            # Enhanced prompt with analysis count
            prompt = f"[{analysis_count}] hash/token > "
            user_input = input(prompt).strip()
            
            # Handle empty input
            if not user_input:
                continue
                
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print(f"\nSession Statistics:")
                print(f"  Total analyses: {analysis_count}")
                print(f"  Session time: {time.time() - start_time:.1f} seconds")
                print("Goodbye!")
                break
                
            elif user_input.lower() == 'help':
                print("\nAvailable Commands:")
                print("  <hash/token>     - Analyze the provided hash or token")
                print("  help            - Show this help message")
                print("  history         - Show analysis history")
                print("  clear           - Clear the screen")
                print("  stats           - Show session statistics")
                print("  quit/exit/q     - Exit the program")
                print("\nFeatures:")
                print("  - Supports all hash formats (MD5, SHA, NTLM, etc.)")
                print("  - JWT token analysis")
                print("  - Cryptocurrency addresses")
                print("  - Online hash lookups")
                print("  - Automatic encoding detection\n")
                continue
                
            elif user_input.lower() == 'history':
                if not session_history:
                    print("No analysis history available.\n")
                else:
                    print("\nAnalysis History:")
                    for i, (timestamp, input_hash, detected) in enumerate(session_history[-10:], 1):
                        short_hash = input_hash[:30] + "..." if len(input_hash) > 30 else input_hash
                        formats = detected[:2] if detected else ['Unknown']
                        print(f"  {i}. [{timestamp}] {short_hash} -> {', '.join(formats)}")
                    if len(session_history) > 10:
                        print(f"  ... ({len(session_history) - 10} more entries)")
                    print()
                continue
                
            elif user_input.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                print("Screen cleared. Session continues...\n")
                continue
                
            elif user_input.lower() == 'stats':
                print(f"\nSession Statistics:")
                print(f"  Total analyses: {analysis_count}")
                print(f"  Session time: {time.time() - start_time:.1f} seconds")
                print(f"  History entries: {len(session_history)}")
                
                if session_history:
                    format_counts = {}
                    for _, _, formats in session_history:
                        for fmt in formats:
                            format_counts[fmt] = format_counts.get(fmt, 0) + 1
                    
                    if format_counts:
                        print("  Most common formats:")
                        for fmt, count in sorted(format_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                            print(f"    {fmt}: {count}")
                print()
                continue
            
            # Analyze the input
            analysis_count += 1
            print(f"\n{'='*50}")
            print(f"Analysis #{analysis_count}: {user_input[:30]}{'...' if len(user_input) > 30 else ''}")
            print('='*50)
            
            analyzer = HashTokenAnalyzer(user_input, verbose=verbose)
            
            if quick_mode:
                analyzer.identify_hash_formats()
                analyzer._calculate_entropy()
            else:
                analyzer.comprehensive_analysis()
            
            # Store in history
            timestamp = datetime.now().strftime('%H:%M:%S')
            detected_formats = analyzer.results.get('detected_formats', [])
            session_history.append((timestamp, user_input, detected_formats))
            
            # Quick result summary for persistent mode
            if detected_formats:
                print(f"\n[QUICK SUMMARY] Detected: {', '.join(detected_formats[:3])}{'...' if len(detected_formats) > 3 else ''}")
            
            if analyzer.results.get('cracking_attempts'):
                print("[CRITICAL] Password/plaintext found in cracking attempts!")
                
            print(f"\n{'='*50}\n")
            
        except KeyboardInterrupt:
            print(f"\n\nSession Statistics:")
            print(f"  Total analyses: {analysis_count}")
            print(f"  Session time: {time.time() - start_time:.1f} seconds")
            print("\nGoodbye!")
            break
        except Exception as e:
            # Handle cases where user_input might not be defined
            input_display = user_input[:30] + '...' if 'user_input' in locals() and len(user_input) > 30 else (user_input if 'user_input' in locals() else 'input')
            print(f"Error analyzing '{input_display}': {e}\n")


def interactive_mode():
    """Run in interactive mode for multiple analyses."""
    print("Interactive Hash/Token Analyzer")
    print("Enter 'quit' or 'exit' to stop, 'help' for commands\n")
    
    while True:
        try:
            user_input = input("Enter hash/token to analyze: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            elif user_input.lower() == 'help':
                print("Commands:")
                print("  <hash/token> - Analyze the input")
                print("  help - Show this help")
                print("  quit/exit/q - Exit the program")
                continue
            elif not user_input:
                continue
                
            print(f"\n{'='*60}")
            analyzer = HashTokenAnalyzer(user_input)
            analyzer.comprehensive_analysis()
            print('='*60)
            
            # Ask if user wants to export results
            export = input("\nExport results? (json/csv/txt/n): ").strip().lower()
            if export in ['json', 'csv', 'txt']:
                filename = export_results(analyzer.results, export)
                if filename:
                    print(f"Results saved to {filename}")
                    
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def analyze_from_file(filepath: str) -> List[Dict[str, Any]]:
    """Analyze multiple hashes/tokens from a file."""
    results = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    print(f"\n{'='*50}")
                    print(f"Analyzing line {line_num}: {line[:50]}{'...' if len(line) > 50 else ''}")
                    print('='*50)
                    
                    analyzer = HashTokenAnalyzer(line)
                    analyzer.comprehensive_analysis()
                    results.append({
                        'line': line_num,
                        'input': line,
                        'results': analyzer.results
                    })
        return results
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return []


def export_results(results: Dict[str, Any], format_type: str = 'json', filename: str = None) -> str:
    """Export analysis results to file."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if not filename:
        filename = f"hash_analysis_{timestamp}.{format_type}"
        
    try:
        if format_type == 'json':
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
                
        elif format_type == 'csv':
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Category', 'Subcategory', 'Value'])
                
                def write_nested(data, category=''):
                    for key, value in data.items():
                        if isinstance(value, dict):
                            write_nested(value, f"{category}.{key}" if category else key)
                        elif isinstance(value, list):
                            writer.writerow([category, key, '; '.join(map(str, value))])
                        else:
                            writer.writerow([category, key, str(value)])
                            
                write_nested(results)
                
        elif format_type == 'txt':
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Hash/Token Analysis Report\n")
                f.write(f"Generated: {datetime.now().isoformat()}\n")
                f.write(f"Target: {results.get('original_input', 'N/A')}\n")
                f.write(f"{'='*50}\n\n")
                
                for category, data in results.items():
                    f.write(f"{category.upper()}:\n")
                    if isinstance(data, dict):
                        for key, value in data.items():
                            f.write(f"  {key}: {value}\n")
                    elif isinstance(data, list):
                        for item in data:
                            f.write(f"  - {item}\n")
                    else:
                        f.write(f"  {data}\n")
                    f.write("\n")
                    
        print(f"Results exported to: {filename}")
        return filename
        
    except Exception as e:
        print(f"Export failed: {e}")
        return ""


def print_banner():
    """Print professional banner."""
    banner = r'''
   #########################################################################
   #     __  __                     __           ______    _____           #
   #    /\ \/\ \                   /\ \         /\__  _\  /\  _ `\         #
   #    \ \ \_\ \     __      ____ \ \ \___     \/_/\ \/  \ \ \/\ \        #
   #     \ \  _  \  /'__`\   / ,__\ \ \  _ `\      \ \ \   \ \ \ \ \       #
   #      \ \ \ \ \/\ \_\ \_/\__, `\ \ \ \ \ \      \_\ \__ \ \ \_\ \      #
   #       \ \_\ \_\ \___ \_\/\____/  \ \_\ \_\     /\_____\ \ \____/      #
   #        \/_/\/_/\/__/\/_/\/___/    \/_/\/_/     \/_____/  \/___/  v2.0 #
   #                                                             by xp     #
   #                                  Hash Identifier                      #
   #########################################################################
    '''
    print(banner)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Hash and Token Analyzer v2.0",
        epilog="Examples:\n"
               "  hashid 5d41402abc4b2a76b9719d911017c592\n"
               "  hashid eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYWRtaW4ifQ.abc123\n"
               "  hashid --file hashes.txt\n"
               "  hashid --interactive\n"
               "  hashid --persistent\n"
               "  hashid -p --quick\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'target', 
        nargs='?', 
        help='Hash, token, or encoded data to analyze'
    )
    parser.add_argument(
        '--file', '-f',
        help='Analyze hashes/tokens from a file (one per line)'
    )
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--persistent', '-p',
        action='store_true',
        help='Run in persistent mode (keeps running for multiple analyses)'
    )
    parser.add_argument(
        '--export', '-e',
        choices=['json', 'csv', 'txt'],
        help='Export results to file'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output filename (default: auto-generated)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress verbose output'
    )
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Skip time-intensive operations (brute force, online lookups)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='HashID Analyzer v2.0'
    )
    
    args = parser.parse_args()
    
    # Handle different modes
    if args.persistent:
        persistent_mode(quick_mode=args.quick, verbose=not args.quiet)
        return
        
    if args.interactive:
        interactive_mode()
        return
        
    if args.file:
        results = analyze_from_file(args.file)
        if args.export and results:
            # Export combined results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = args.output or f"batch_analysis_{timestamp}.{args.export}"
            
            try:
                if args.export == 'json':
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
                print(f"Batch results exported to: {filename}")
            except Exception as e:
                print(f"Export failed: {e}")
        return
        
    if not args.target:
        parser.print_help()
        return
    
    # Check if user wants persistent mode after single analysis
    if args.persistent:
        # Analyze the provided hash first, then enter persistent mode
        if not args.quiet:
            print_banner()
        print(f"\nAnalyzing provided hash: {args.target[:50]}{'...' if len(args.target) > 50 else ''}")
        print("="*60)
        
        analyzer = HashTokenAnalyzer(args.target, verbose=not args.quiet)
        if args.quick:
            analyzer.identify_hash_formats()
            analyzer._calculate_entropy()
        else:
            analyzer.comprehensive_analysis()
        
        print("\nEntering persistent mode for additional analyses...")
        time.sleep(1)
        persistent_mode(quick_mode=args.quick, verbose=not args.quiet)
        return
        
    # Single analysis mode
    if not args.quiet:
        print_banner()
    else:
        print(f"HashID Analyzer v2.0 - Target: {args.target[:50]}{'...' if len(args.target) > 50 else ''}")
    
    analyzer = HashTokenAnalyzer(args.target, verbose=not args.quiet)
    
    if args.quick:
        analyzer.identify_hash_formats()
        analyzer._calculate_entropy()
    else:
        analyzer.comprehensive_analysis()
    
    if args.export:
        filename = export_results(analyzer.results, args.export, args.output)
        
    if not args.quiet:
        print("\nAnalysis complete! Use --export to save detailed results.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)