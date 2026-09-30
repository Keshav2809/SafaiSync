import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","safaisync.settings")
import django
django.setup()
from django.contrib.auth.models import User
from core.models import Profile, AwarenessPost

admin, created = User.objects.get_or_create(username="admin", defaults={"email":"admin@safaisync.local","is_staff":True,"is_superuser":True})
admin.set_password("Admin@123")
admin.is_staff=True
admin.is_superuser=True
admin.save()
Profile.objects.update_or_create(user=admin, defaults={"role":"admin"})

citizen, created = User.objects.get_or_create(username="citizen", defaults={"email":"citizen@safaisync.local"})
citizen.set_password("Citizen@123")
citizen.save()
Profile.objects.update_or_create(user=citizen, defaults={"phone":"9000000001","address":"Kanpur, Uttar Pradesh","role":"citizen"})

collector, created = User.objects.get_or_create(username="collector", defaults={"email":"collector@safaisync.local"})
collector.set_password("Collector@123")
collector.is_staff=False
collector.is_superuser=False
collector.save()
Profile.objects.update_or_create(user=collector, defaults={"phone":"9000000002","address":"Kanpur, Uttar Pradesh","role":"collector"})

if not AwarenessPost.objects.exists():
    AwarenessPost.objects.create(title="Segregate Waste at Source", content="Keep wet, dry and hazardous waste separate to make collection and recycling more effective.", category="Segregation", created_by=admin)
    AwarenessPost.objects.create(title="Keep Public Places Clean", content="Use designated bins and report overflowing bins or illegal dumping through SafaiSync.", category="Cleanliness", created_by=admin)
    AwarenessPost.objects.create(title="Reduce Single-Use Plastic", content="Prefer reusable bags and containers and dispose of plastic responsibly.", category="Sustainability", created_by=admin)

print("Demo data created.")
print("Admin: admin / Admin@123")
print("Citizen: citizen / Citizen@123")
print("Collector: collector / Collector@123")
