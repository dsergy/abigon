from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Sets up the default site'

    def handle(self, *args, **kwargs):
        # Update the default site
        site = Site.objects.get_or_create(id=1)[0]
        site.domain = '192.168.1.107:8000'
        site.name = 'MVP'
        site.save()
        
        self.stdout.write(self.style.SUCCESS('Successfully set up site configuration')) 