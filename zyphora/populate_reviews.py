import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zyphora.settings')
django.setup()

from crm.models import Review

def populate_reviews():
    reviews = [
        {
            "name": "Ramesh Gupta",
            "email": "ramesh@example.com",
            "location": "New Delhi",
            "rating": 5,
            "review": "Excellent service and very professional installation team. The 5kW system is working perfectly and my electricity bill has significantly reduced!"
        },
        {
            "name": "Anjali Sharma",
            "email": "anjali.s@example.com",
            "location": "Gurugram",
            "rating": 4,
            "review": "Good experience overall. The sales team was very helpful in explaining the subsidy process. Installation took a day longer than expected, but the quality of work is great."
        },
        {
            "name": "Vikram Singh",
            "email": "vikram.singh@example.com",
            "location": "Noida",
            "rating": 5,
            "review": "Highly recommend them! They handled everything from site survey to net-metering. The KSEB approval was smooth and fast. Great job."
        },
        {
            "name": "Sunita Verma",
            "email": "sunitav@example.com",
            "location": "Faridabad",
            "rating": 5,
            "review": "We opted for the Leakproof Solar Roof, and it looks beautiful on our house. The team was very polite and cleaned up everything after installation."
        },
        {
            "name": "Amit Patel",
            "email": "amit.patel@example.com",
            "location": "Ghaziabad",
            "rating": 3,
            "review": "The solar panels are generating good power, but the initial communication regarding the delivery date was a bit confusing. Overall satisfactory."
        }
    ]

    for rev in reviews:
        Review.objects.get_or_create(
            email=rev['email'],
            defaults={
                'name': rev['name'],
                'location': rev['location'],
                'rating': rev['rating'],
                'review': rev['review']
            }
        )
    print(f"Successfully added {len(reviews)} reviews!")

if __name__ == "__main__":
    populate_reviews()
