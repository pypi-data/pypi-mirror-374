import logging
import pprint
from django.core.management.base import BaseCommand
from django.conf import settings
from allianceauth.eveonline.models import EveCorporationInfo, EveCharacter
from allianceauth.services.hooks import ServicesHook


logger = logging.getLogger(__name__)
class Command(BaseCommand):
    help = 'Test discord numbers'
    def handle(self, *args, **options):
        SERVICE_DB = {
            "mumble":"mumble",
            "smf":"smf",
            "discord":"discord",
            "discorse":"discourse",
            "Wiki JS":"wikijs",
            "ips4":"ips4",
            "openfire":"openfire",
            "phpbb3":"phpbb3",
            "teamspeak3":"teamspeak3",
        }
        corporation_id=1115572377
        linked_chars = EveCharacter.objects.filter(corporation_id=corporation_id)
        linked_chars = linked_chars | EveCharacter.objects.filter(
            character_ownership__user__profile__main_character__corporation_id=corporation_id)  # add all alts for characters in corp
        services = [svc.name for svc in ServicesHook.get_services()]
        #for char in linked_chars:
        #    print(f"Character: {char.character_name} ({char.character_id})")
        #    print(vars(char))
        print(f"Services: {services}")
        linked_chars = linked_chars.select_related('character_ownership',
            'character_ownership__user__profile__main_character') \
            .prefetch_related('character_ownership__user__character_ownerships')
        #for char in linked_chars:
        #    print(f"Character: {char.character_name} ({char.character_id})")
        #    #print(vars(char))
        #    print(vars(char.character_ownership))
        #    print()
        skiped_services = []
        for service in services:
            if service in SERVICE_DB:
                linked_chars = linked_chars.select_related("character_ownership__user__{}".format(SERVICE_DB[service]))
        
        #for char in linked_chars:
        #    print(f"Character: {char.character_name} ({char.character_id})")
        #    print(vars(char))
        #    #print(vars(char.character_ownership))
        #    print()

        members = [] # member list
        orphans = [] # orphan list
        alt_count = 0 #
        total_mains = 0
        total_alts = 0
        total_dicord = 0
        total_mumble = 0 
        services_count = {} # for the stats
        for service in services:
            services_count[service] = 0 # prefill
        mains = {} # main list
        temp_ids = [] # filter out linked vs unreg'd
        """ for char in linked_chars:
            main = char.character_ownership.user.profile.main_character # main from profile
            if main is not None: 
                if main.corporation_id == corporation_id: # iis this char in corp
                    if main.character_id not in mains: # add array
                        mains[main.character_id] = {
                            'main':main,
                            'alts':[], 
                            'services':{}
                            }
                        for service in services:
                            mains[main.character_id]['services'][service] = False # pre fill
                    if char.character_id == main.character_id:
                        for service in services:
                            try:
                                if hasattr(char.character_ownership.user, SERVICE_DB[service]):
                                    mains[main.character_id]['services'][service] = True
                                    if mains[main.character_id]['services']["discord"]:
                                        total_dicord += 1
                                        print(f"Discord: {main.character_name} ({main.character_id})")
                                    if mains[main.character_id]['services']["mumble"]:
                                        total_mumble += 1
                                        print(f"Mumble: {main.character_name} ({main.character_id})") 
                                    services_count[service] += 1
                            except Exception as e:
                                print(e)

                    mains[main.character_id]['alts'].append(char) #add to alt listing
                    if char.character_id != main.character_id:
                        alt_count += 1
                    print(f"Total Alts: {alt_count}") """
        for char in linked_chars:
            main = char.character_ownership.user.profile.main_character
            print(main)
            if main is not None:
                if main.corporation_id == corporation_id and char.character_id == main.character_id:
                    total_mains += 1
                    if hasattr(char.character_ownership.user, "discord"):
                        total_dicord += 1
                    if hasattr(char.character_ownership.user, "mumble"):
                        total_mumble += 1
                        
        #pprint.pp(mains)
        #total_mains = len(mains)
        print(f"Total Mains: {total_mains}")
        print(f"Total Discord: {total_dicord}")
        print(f"Total Mumble: {total_mumble}")
        #print(f"Total Alts: {alt_count}")
