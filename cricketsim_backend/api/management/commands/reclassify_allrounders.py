from django.core.management.base import BaseCommand
from api.models import Player

class Command(BaseCommand):
    help = 'Re-classifies all-rounders as Batting All-rounder or Bowling All-rounder based on current stats'

    def handle(self, *args, **kwargs):
        all_rounders = Player.objects.filter(role__icontains='All-rounder')
        count = 0
        
        for p in all_rounders:
            # We treat All-rounder, Batting All-rounder, and Bowling All-rounder the same for recalculation
            # in case their stats have changed.
            
            bat_avg = p.batting_avg
            sr = p.strike_rate
            bowl_avg = p.bowling_avg
            econ = p.economy
            
            # Use the same formula as defined in the plan
            bat_score = (bat_avg / 20.0) + (sr / 120.0)
            bowl_score = (30.0 / bowl_avg if bowl_avg > 0 else 0) + (9.0 / econ if econ > 0 else 0)
            
            new_role = 'Batting All-rounder' if bat_score > bowl_score else 'Bowling All-rounder'
            
            if p.role != new_role:
                old_role = p.role
                p.role = new_role
                p.save()
                self.stdout.write(f"Updated {p.name}: {old_role} -> {new_role}")
                count += 1
        
        self.stdout.write(self.style.SUCCESS(f"Successfully re-classified {count} all-rounders."))
