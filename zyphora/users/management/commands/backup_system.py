import os
import zipfile
import shutil
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Create automated backup of database and media files, and apply retention policy'

    def add_arguments(self, parser):
        parser.add_argument(
            '--retention-days',
            type=int,
            default=7,
            help='Number of days to keep old backups (default: 7)'
        )

    def handle(self, *args, **options):
        retention_days = options['retention_days']
        
        # 1. Setup backup directory
        base_dir = settings.BASE_DIR
        backup_dir = os.path.join(base_dir, 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_{timestamp}.zip"
        backup_filepath = os.path.join(backup_dir, backup_filename)
        
        # 2. Gather files to backup
        db_path = os.path.join(base_dir, 'db.sqlite3')
        media_dir = getattr(settings, 'MEDIA_ROOT', os.path.join(base_dir, 'media'))
        
        self.stdout.write(f"Starting backup process: {backup_filename}")
        
        # 3. Create zip file
        with zipfile.ZipFile(backup_filepath, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
            # Backup Database
            if os.path.exists(db_path):
                backup_zip.write(db_path, arcname='db.sqlite3')
                self.stdout.write("-> Added database to backup")
            else:
                self.stdout.write(self.style.WARNING("-> Database db.sqlite3 not found!"))

            # Backup Media Files
            if os.path.exists(media_dir):
                for root, dirs, files in os.walk(media_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Avoid adding empty directories or unnecessary files if needed
                        arcname = os.path.relpath(file_path, base_dir)
                        backup_zip.write(file_path, arcname=arcname)
                self.stdout.write("-> Added media files to backup")
            else:
                self.stdout.write(self.style.WARNING("-> Media directory not found!"))
                
        self.stdout.write(self.style.SUCCESS(f"Successfully created backup: {backup_filepath}"))
        
        # 4. Retention Policy (Delete old backups)
        self.stdout.write(f"Applying retention policy: Deleting backups older than {retention_days} days...")
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        deleted_count = 0
        for filename in os.listdir(backup_dir):
            if filename.startswith("backup_") and filename.endswith(".zip"):
                filepath = os.path.join(backup_dir, filename)
                # Get file modification time
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_mtime < cutoff_date:
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                        self.stdout.write(f"-> Deleted old backup: {filename}")
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Failed to delete {filename}: {e}"))
                        
        self.stdout.write(self.style.SUCCESS(f"Retention policy applied. Deleted {deleted_count} old backups."))
