#!/usr/bin/env python3
"""
Configuration Update Utility for AI Trading Assistant
Safely updates configuration values without shell injection issues
"""

import argparse
import configparser
import sys
import os
from pathlib import Path

def update_config(config_file, section, key, value):
    """Safely update a configuration value"""
    try:
        config = configparser.ConfigParser()
        
        # Read existing config if it exists
        if os.path.exists(config_file):
            config.read(config_file)
        
        # Ensure section exists
        if section not in config:
            config.add_section(section)
        
        # Update value
        config[section][key] = value
        
        # Write back to file
        with open(config_file, 'w') as f:
            config.write(f)
        
        print(f"✓ Updated [{section}] {key}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating config: {e}")
        return False

def update_multiple_config(config_file, updates):
    """Update multiple configuration values at once"""
    try:
        config = configparser.ConfigParser()
        
        # Read existing config if it exists
        if os.path.exists(config_file):
            config.read(config_file)
        
        # Apply all updates
        for section, key, value in updates:
            if section not in config:
                config.add_section(section)
            config[section][key] = value
        
        # Write back to file
        with open(config_file, 'w') as f:
            config.write(f)
        
        print(f"✓ Updated {len(updates)} configuration values")
        return True
        
    except Exception as e:
        print(f"❌ Error updating config: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Update AI Trading Assistant configuration')
    parser.add_argument('config_file', help='Path to configuration file')
    parser.add_argument('--section', required=True, help='Configuration section')
    parser.add_argument('--key', required=True, help='Configuration key')
    parser.add_argument('--value', required=True, help='Configuration value')
    parser.add_argument('--batch', help='Batch update from file (format: section,key,value per line)')
    
    args = parser.parse_args()
    
    if args.batch:
        # Batch update mode
        updates = []
        try:
            with open(args.batch, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split(',', 2)
                        if len(parts) == 3:
                            updates.append((parts[0].strip(), parts[1].strip(), parts[2].strip()))
            
            if updates:
                success = update_multiple_config(args.config_file, updates)
                sys.exit(0 if success else 1)
            else:
                print("No valid updates found in batch file")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Error reading batch file: {e}")
            sys.exit(1)
    else:
        # Single update mode
        success = update_config(args.config_file, args.section, args.key, args.value)
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()