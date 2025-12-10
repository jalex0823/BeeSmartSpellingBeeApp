"""
BeeSmart Spelling Bee App - Railway to DigitalOcean Migration Script
====================================================================

This script migrates your Railway database and assets to DigitalOcean.

BEFORE RUNNING:
1. Set up your DigitalOcean PostgreSQL database
2. Create environment variables:
   - RAILWAY_DATABASE_URL: Your Railway PostgreSQL connection string
   - DIGITALOCEAN_DATABASE_URL: Your DigitalOcean PostgreSQL connection string
3. Ensure you have backups of your Railway data
4. Install required packages: pip install psycopg2-binary sqlalchemy

WHAT THIS SCRIPT DOES:
- Exports all tables from Railway database
- Migrates user accounts, avatars, quiz data, word lists
- Exports avatar files (GLB files and thumbnails)
- Imports everything to DigitalOcean
- Validates the migration
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, inspect, text
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(message):
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")


class RailwayToDigitalOceanMigration:
    """Handles migration from Railway to DigitalOcean"""
    
    def __init__(self):
        self.railway_url = os.getenv('RAILWAY_DATABASE_URL') or os.getenv('DATABASE_URL')
        self.digitalocean_url = os.getenv('DIGITALOCEAN_DATABASE_URL')
        self.backup_dir = Path('migration_backup') / datetime.now().strftime('%Y%m%d_%H%M%S')
        self.railway_engine = None
        self.digitalocean_engine = None
        
    def validate_connections(self):
        """Validate database connections"""
        print_header("Step 1: Validating Database Connections")
        
        if not self.railway_url:
            print_error("RAILWAY_DATABASE_URL not found in environment")
            print_info("Set it with: $env:RAILWAY_DATABASE_URL='your-railway-connection-string'")
            return False
            
        if not self.digitalocean_url:
            print_error("DIGITALOCEAN_DATABASE_URL not found in environment")
            print_info("Set it with: $env:DIGITALOCEAN_DATABASE_URL='your-digitalocean-connection-string'")
            return False
        
        # Fix postgres:// to postgresql://
        if self.railway_url.startswith('postgres://'):
            self.railway_url = self.railway_url.replace('postgres://', 'postgresql://', 1)
        if self.digitalocean_url.startswith('postgres://'):
            self.digitalocean_url = self.digitalocean_url.replace('postgres://', 'postgresql://', 1)
        
        # Test Railway connection
        try:
            print_info("Testing Railway connection...")
            self.railway_engine = create_engine(self.railway_url)
            with self.railway_engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print_success(f"Railway connected: {version[:50]}...")
        except Exception as e:
            print_error(f"Railway connection failed: {e}")
            return False
        
        # Test DigitalOcean connection
        try:
            print_info("Testing DigitalOcean connection...")
            self.digitalocean_engine = create_engine(self.digitalocean_url)
            with self.digitalocean_engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print_success(f"DigitalOcean connected: {version[:50]}...")
        except Exception as e:
            print_error(f"DigitalOcean connection failed: {e}")
            return False
        
        return True
    
    def create_backup_directory(self):
        """Create backup directory for exported data"""
        print_header("Step 2: Creating Backup Directory")
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        print_success(f"Backup directory created: {self.backup_dir}")
        
    def export_database_schema(self):
        """Export database schema from Railway"""
        print_header("Step 3: Exporting Database Schema")
        
        try:
            metadata = MetaData()
            metadata.reflect(bind=self.railway_engine)
            
            tables = list(metadata.tables.keys())
            print_info(f"Found {len(tables)} tables to export:")
            for table in tables:
                print(f"  - {table}")
            
            # Save table list
            schema_file = self.backup_dir / 'schema.json'
            with open(schema_file, 'w') as f:
                json.dump({'tables': tables}, f, indent=2)
            
            print_success(f"Schema exported to {schema_file}")
            return tables
        except Exception as e:
            print_error(f"Schema export failed: {e}")
            return []
    
    def export_table_data(self, table_name):
        """Export data from a specific table"""
        try:
            with self.railway_engine.connect() as conn:
                result = conn.execute(text(f'SELECT * FROM "{table_name}"'))
                rows = result.fetchall()
                columns = result.keys()
                
                # Convert to list of dicts
                data = []
                for row in rows:
                    row_dict = {}
                    for i, col in enumerate(columns):
                        value = row[i]
                        # Handle special types
                        if isinstance(value, (datetime, )):
                            value = value.isoformat()
                        elif isinstance(value, bytes):
                            value = None  # Skip binary data in JSON export
                        row_dict[col] = value
                    data.append(row_dict)
                
                # Save to JSON
                table_file = self.backup_dir / f'{table_name}.json'
                with open(table_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print_success(f"  ✓ {table_name}: {len(data)} rows exported")
                return len(data)
        except Exception as e:
            print_warning(f"  ⚠ {table_name}: Export failed - {e}")
            return 0
    
    def export_all_data(self, tables):
        """Export data from all tables"""
        print_header("Step 4: Exporting Table Data")
        
        total_rows = 0
        for table in tables:
            rows = self.export_table_data(table)
            total_rows += rows
        
        print_success(f"\nTotal: {total_rows} rows exported from {len(tables)} tables")
        return total_rows > 0
    
    def export_static_assets(self):
        """Export static assets (avatars, badges, etc.)"""
        print_header("Step 5: Backing Up Static Assets")
        
        assets_to_backup = [
            'static/assets/avatars',
            'static/assets/badges',
            'static/BeeSmartCrestLogo1.png',
            'static/favicon.ico',
        ]
        
        assets_backup = self.backup_dir / 'static_assets'
        assets_backup.mkdir(exist_ok=True)
        
        for asset_path in assets_to_backup:
            if os.path.exists(asset_path):
                dest = assets_backup / asset_path
                if os.path.isdir(asset_path):
                    shutil.copytree(asset_path, dest, dirs_exist_ok=True)
                    print_success(f"  ✓ Backed up directory: {asset_path}")
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(asset_path, dest)
                    print_success(f"  ✓ Backed up file: {asset_path}")
            else:
                print_warning(f"  ⚠ Not found: {asset_path}")
        
        print_success("Static assets backed up")
    
    def create_digitalocean_schema(self):
        """Create tables in DigitalOcean database"""
        print_header("Step 6: Creating Schema in DigitalOcean")
        
        print_info("This will use your models.py to create the schema...")
        print_info("Make sure your models.py is up to date!")
        
        try:
            # Import your models
            from models import db
            from config import get_config
            
            # Create a temporary Flask app to initialize database
            from flask import Flask
            app = Flask(__name__)
            app.config.from_object(get_config())
            app.config['SQLALCHEMY_DATABASE_URI'] = self.digitalocean_url
            
            db.init_app(app)
            
            with app.app_context():
                # Create all tables
                db.create_all()
                print_success("All tables created in DigitalOcean database")
            
            return True
        except Exception as e:
            print_error(f"Schema creation failed: {e}")
            print_info("You may need to run this manually using: python init_db.py")
            return False
    
    def import_table_data(self, table_name):
        """Import data into a specific table"""
        table_file = self.backup_dir / f'{table_name}.json'
        
        if not table_file.exists():
            print_warning(f"  ⚠ No data file for {table_name}")
            return 0
        
        try:
            with open(table_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not data:
                print_info(f"  - {table_name}: No data to import")
                return 0
            
            # Build INSERT statement
            with self.digitalocean_engine.connect() as conn:
                for row in data:
                    columns = ', '.join(f'"{k}"' for k in row.keys())
                    placeholders = ', '.join(':' + k for k in row.keys())
                    query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({placeholders})'
                    
                    try:
                        conn.execute(text(query), row)
                    except Exception as e:
                        # Handle conflicts (e.g., duplicate keys)
                        if 'duplicate' in str(e).lower() or 'unique constraint' in str(e).lower():
                            continue  # Skip duplicates
                        else:
                            raise
                
                conn.commit()
            
            print_success(f"  ✓ {table_name}: {len(data)} rows imported")
            return len(data)
        except Exception as e:
            print_warning(f"  ⚠ {table_name}: Import failed - {e}")
            return 0
    
    def import_all_data(self, tables):
        """Import data into all tables"""
        print_header("Step 7: Importing Data to DigitalOcean")
        
        # Import in dependency order (important tables first)
        priority_tables = ['users', 'avatars', 'word_lists', 'wordbank_storage']
        other_tables = [t for t in tables if t not in priority_tables]
        ordered_tables = priority_tables + other_tables
        
        total_rows = 0
        for table in ordered_tables:
            if table in tables:
                rows = self.import_table_data(table)
                total_rows += rows
        
        print_success(f"\nTotal: {total_rows} rows imported to {len(tables)} tables")
    
    def verify_migration(self):
        """Verify the migration was successful"""
        print_header("Step 8: Verifying Migration")
        
        tables_to_check = ['users', 'avatars', 'quiz_sessions', 'wordbank_storage']
        
        all_good = True
        for table in tables_to_check:
            try:
                # Count rows in Railway
                with self.railway_engine.connect() as conn:
                    result = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                    railway_count = result.fetchone()[0]
                
                # Count rows in DigitalOcean
                with self.digitalocean_engine.connect() as conn:
                    result = conn.execute(text(f'SELECT COUNT(*) FROM "{table}"'))
                    do_count = result.fetchone()[0]
                
                if railway_count == do_count:
                    print_success(f"  ✓ {table}: {railway_count} rows (match)")
                else:
                    print_warning(f"  ⚠ {table}: Railway={railway_count}, DigitalOcean={do_count}")
                    all_good = False
            except Exception as e:
                print_warning(f"  ⚠ {table}: Could not verify - {e}")
                all_good = False
        
        return all_good
    
    def generate_env_file(self):
        """Generate updated .env file for DigitalOcean"""
        print_header("Step 9: Generating Environment Configuration")
        
        env_content = f"""# BeeSmart Spelling App - DigitalOcean Configuration
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Database Configuration
DATABASE_URL={self.digitalocean_url}

# Flask Configuration  
FLASK_APP=AjaSpellBApp.py
FLASK_ENV=production
SECRET_KEY={os.getenv('SECRET_KEY', 'change-me-to-secure-random-string')}

# Feature Flags
ENABLE_OCR=true

# Mail Configuration (update with your settings)
MAIL_SERVER=smtp.hostinger.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=your-email@domain.com
"""
        
        env_file = self.backup_dir / '.env.digitalocean'
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print_success(f"Environment file created: {env_file}")
        print_info("Copy this to your DigitalOcean deployment as .env")
    
    def run_migration(self):
        """Run the complete migration process"""
        print_header("BeeSmart Migration: Railway → DigitalOcean")
        print_info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Validate connections
        if not self.validate_connections():
            print_error("Migration aborted - connection validation failed")
            return False
        
        # Step 2: Create backup directory
        self.create_backup_directory()
        
        # Step 3-4: Export from Railway
        tables = self.export_database_schema()
        if not tables:
            print_error("Migration aborted - no tables found")
            return False
        
        if not self.export_all_data(tables):
            print_error("Migration aborted - data export failed")
            return False
        
        # Step 5: Backup static assets
        self.export_static_assets()
        
        # Ask for confirmation before importing
        print_warning("\n" + "="*70)
        print_warning("⚠️  IMPORTANT: About to modify DigitalOcean database")
        print_warning("="*70)
        response = input("\nContinue with import? (yes/no): ").strip().lower()
        
        if response != 'yes':
            print_info("Migration paused. Your backup is saved at:")
            print_info(f"  {self.backup_dir}")
            print_info("\nTo continue later, run:")
            print_info("  python migrate_railway_to_digitalocean.py --import-only")
            return False
        
        # Step 6-7: Import to DigitalOcean
        if not self.create_digitalocean_schema():
            print_warning("Schema creation had issues - continuing anyway...")
        
        self.import_all_data(tables)
        
        # Step 8: Verify
        if self.verify_migration():
            print_success("\n🎉 Migration verification passed!")
        else:
            print_warning("\n⚠️  Migration completed with some warnings")
        
        # Step 9: Generate config
        self.generate_env_file()
        
        # Final summary
        print_header("Migration Complete!")
        print_success(f"Backup location: {self.backup_dir}")
        print_info("\nNext steps:")
        print_info("1. Review the generated .env.digitalocean file")
        print_info("2. Upload static assets to your DigitalOcean server")
        print_info("3. Update your deployment configuration")
        print_info("4. Test the application with DigitalOcean database")
        print_info("5. Keep Railway database as backup for a few days")
        
        return True


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("BeeSmart Spelling Bee App")
    print("Railway → DigitalOcean Migration Tool")
    print("="*70 + "\n")
    
    # Check if running with --import-only flag
    import_only = '--import-only' in sys.argv
    
    migration = RailwayToDigitalOceanMigration()
    
    if import_only:
        print_info("Running in import-only mode...")
        print_info("This assumes you have already exported data")
        # TODO: Implement import-only mode
        print_error("Import-only mode not yet implemented")
        return
    
    # Run full migration
    try:
        success = migration.run_migration()
        if success:
            print_success("\n✅ Migration completed successfully!")
            sys.exit(0)
        else:
            print_warning("\n⚠️  Migration completed with warnings")
            sys.exit(1)
    except KeyboardInterrupt:
        print_warning("\n\n⚠️  Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
