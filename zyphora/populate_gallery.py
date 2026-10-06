import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zyphora.settings')
django.setup()

from projects.models import Project, ProjectMedia
from users.models import CustomUser

def populate_gallery():
    project = Project.objects.filter(title__icontains="Completed Project Lead").first()
    if not project:
        print("Completed project not found. Did you run the previous script?")
        return
    
    engineer = CustomUser.objects.filter(username="eng_test").first()

    images_to_add = [
        ("before.png", "before_photo", "Site before installation"),
        ("after.png", "after_photo", "Finished solar setup"),
        ("on-grid.jpg", "installation_photo", "Panel mounting process")
    ]

    static_images_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')

    for img_name, category, caption in images_to_add:
        src_path = os.path.join(static_images_dir, img_name)
        if os.path.exists(src_path):
            with open(src_path, 'rb') as f:
                pm = ProjectMedia(
                    project=project,
                    uploaded_by=engineer,
                    category=category,
                    caption=caption
                )
                pm.file.save(img_name, File(f), save=True)
                print(f"Added {img_name} to gallery!")
        else:
            print(f"File not found: {src_path}")

if __name__ == "__main__":
    populate_gallery()
