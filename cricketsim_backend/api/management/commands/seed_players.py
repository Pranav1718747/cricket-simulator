from django.core.management.base import BaseCommand
from api.models import Player, PlayerMatchup
import random

class Command(BaseCommand):
    help = 'Seeds exactly the 108 user-defined players categorized into 1-5 star tiers'

    def handle(self, *args, **kwargs):
        
        # Helper configuration to autogenerate realistic stats based on Tier + Role
        def generate_stats_for_tier(name, role, stars):
            # Base logic defaults
            bat_avg, sr = 0.0, 0.0
            bowl_avg, econ = 0.0, 0.0
            
            # V2 RPG Attributes
            batting_power = 50
            batting_consistency = 50
            spin_skill = 50
            pace_skill = 50
            
            powerplay_skill = 50
            middle_overs_skill = 50
            death_bowling_skill = 50
            fielding_skill = 50
            
            tactical_role = 'Standard'
            bowling_style = 'None'
            is_spinner = False
            
            # Helper to set batting attributes
            def set_bat(pwr, con, spin, pace):
                return (random.randint(pwr-5, pwr+5), random.randint(con-5, con+5), 
                        random.randint(spin-5, spin+5), random.randint(pace-5, pace+5))
            
            # Helper to set bowling attributes
            def set_bowl(pp, mid, death):
                return (random.randint(pp-5, pp+5), random.randint(mid-5, mid+5), random.randint(death-5, death+5))
            
            # 5 Star
            if stars == 5:
                fielding_skill = random.randint(85, 95)
                if role == 'Batsman' or role == 'Wicketkeeper':
                    bat_avg, sr = random.uniform(35.0, 48.0), random.uniform(145.0, 175.0)
                    batting_power, batting_consistency, spin_skill, pace_skill = set_bat(92, 95, 90, 92)
                    tactical_role = random.choice(['Anchor', 'Power Hitter', 'Finisher'])
                elif role == 'All-rounder':
                    bat_avg, sr = random.uniform(25.0, 32.0), random.uniform(150.0, 170.0)
                    bowl_avg, econ = random.uniform(22.0, 26.0), random.uniform(7.0, 8.2)
                    batting_power, batting_consistency, spin_skill, pace_skill = set_bat(88, 85, 82, 85)
                    powerplay_skill, middle_overs_skill, death_bowling_skill = set_bowl(85, 88, 85)
                    bowling_style = random.choice(['All-Round Pacer', 'All-Round Spinner'])
                    tactical_role = 'Finisher'
                else: # Bowler
                    bat_avg, sr = random.uniform(5.0, 12.0), random.uniform(80.0, 110.0)
                    bowl_avg, econ = random.uniform(18.0, 22.0), random.uniform(6.5, 7.5)
                    batting_power, batting_consistency, spin_skill, pace_skill = set_bat(30, 20, 25, 25)
                    powerplay_skill, middle_overs_skill, death_bowling_skill = set_bowl(92, 95, 95)
                    bowling_style = random.choice(['Swing Specialist', 'Death Specialist', 'Spinner'])
            
            # 4 Star
            elif stars == 4:
                fielding_skill = random.randint(75, 85)
                if role == 'Batsman' or role == 'Wicketkeeper':
                    bat_avg, sr = random.uniform(30.0, 38.0), random.uniform(138.0, 155.0)
                    batting_power, batting_consistency, spin_skill, pace_skill = set_bat(85, 85, 82, 84)
                    tactical_role = random.choice(['Anchor', 'Power Hitter', 'Standard'])
                elif role == 'All-rounder':
                    bat_avg, sr = random.uniform(22.0, 28.0), random.uniform(140.0, 160.0)
                    bowl_avg, econ = random.uniform(25.0, 29.0), random.uniform(7.5, 8.6)
                    batting_power, batting_consistency, spin_skill, pace_skill = set_bat(82, 78, 75, 80)
                    powerplay_skill, middle_overs_skill, death_bowling_skill = set_bowl(80, 82, 78)
                    bowling_style = random.choice(['All-Round Pacer', 'All-Round Spinner'])
                    tactical_role = 'Standard'
                else: 
                    bat_avg, sr = random.uniform(5.0, 10.0), random.uniform(70.0, 95.0)
                    bowl_avg, econ = random.uniform(22.0, 26.0), random.uniform(7.2, 8.2)
                    batting_power, batting_consistency, spin_skill, pace_skill = set_bat(25, 15, 20, 20)
                    powerplay_skill, middle_overs_skill, death_bowling_skill = set_bowl(85, 88, 88)
                    bowling_style = random.choice(['Swing Specialist', 'Death Specialist', 'Spinner'])
                    
            # 3 Star
            elif stars == 3:
                fielding_skill = random.randint(65, 75)
                if role == 'Batsman' or role == 'Wicketkeeper':
                    bat_avg, sr = random.uniform(25.0, 32.0), random.uniform(128.0, 142.0)
                    batting_power, batting_consistency, spin_skill, pace_skill = set_bat(75, 78, 75, 75)
                    tactical_role = 'Standard'
                elif role == 'All-rounder':
                    bat_avg, sr = random.uniform(18.0, 24.0), random.uniform(130.0, 145.0)
                    bowl_avg, econ = random.uniform(28.0, 34.0), random.uniform(8.0, 9.2)
                    batting_power, batting_consistency, spin_skill, pace_skill = set_bat(72, 68, 65, 70)
                    powerplay_skill, middle_overs_skill, death_bowling_skill = set_bowl(70, 75, 68)
                    bowling_style = random.choice(['All-Round Pacer', 'All-Round Spinner'])
                else: 
                    bat_avg, sr = random.uniform(4.0, 9.0), random.uniform(60.0, 85.0)
                    bowl_avg, econ = random.uniform(25.0, 30.0), random.uniform(7.8, 8.8)
                    batting_power, batting_consistency, spin_skill, pace_skill = set_bat(20, 10, 15, 15)
                    powerplay_skill, middle_overs_skill, death_bowling_skill = set_bowl(78, 80, 75)
                    bowling_style = random.choice(['Swing Specialist', 'Death Specialist', 'Spinner'])
                    
            # 2 Star
            elif stars == 2:
                fielding_skill = random.randint(55, 65)
                if role == 'Batsman' or role == 'Wicketkeeper':
                    bat_avg, sr = random.uniform(18.0, 25.0), random.uniform(115.0, 130.0)
                    batting_power, batting_consistency, spin_skill, pace_skill = set_bat(65, 68, 65, 65)
                elif role == 'All-rounder':
                    bat_avg, sr = random.uniform(12.0, 18.0), random.uniform(120.0, 135.0)
                    bowl_avg, econ = random.uniform(32.0, 40.0), random.uniform(9.0, 10.5)
                    batting_power, batting_consistency, spin_skill, pace_skill = set_bat(60, 55, 50, 60)
                    powerplay_skill, middle_overs_skill, death_bowling_skill = set_bowl(60, 65, 55)
                    bowling_style = random.choice(['All-Round Pacer', 'All-Round Spinner'])
                else: 
                    bat_avg, sr = random.uniform(2.0, 7.0), random.uniform(50.0, 75.0)
                    bowl_avg, econ = random.uniform(29.0, 38.0), random.uniform(8.5, 9.8)
                    batting_power, batting_consistency, spin_skill, pace_skill = set_bat(15, 8, 10, 10)
                    powerplay_skill, middle_overs_skill, death_bowling_skill = set_bowl(68, 70, 65)
                    bowling_style = random.choice(['All-Round Pacer', 'Spinner', 'Swing Specialist'])

            # 1 Star
            else: 
                fielding_skill = random.randint(45, 55)
                if role == 'Batsman' or role == 'Wicketkeeper':
                    bat_avg, sr = random.uniform(12.0, 20.0), random.uniform(105.0, 120.0)
                    batting_power, batting_consistency, spin_skill, pace_skill = set_bat(55, 55, 50, 55)
                elif role == 'All-rounder':
                    bat_avg, sr = random.uniform(8.0, 15.0), random.uniform(105.0, 125.0)
                    bowl_avg, econ = random.uniform(35.0, 50.0), random.uniform(9.5, 11.5)
                    batting_power, batting_consistency, spin_skill, pace_skill = set_bat(50, 45, 40, 50)
                    powerplay_skill, middle_overs_skill, death_bowling_skill = set_bowl(50, 55, 45)
                    bowling_style = random.choice(['All-Round Pacer', 'All-Round Spinner'])
                else: 
                    bat_avg, sr = random.uniform(1.0, 5.0), random.uniform(40.0, 60.0)
                    bowl_avg, econ = random.uniform(35.0, 48.0), random.uniform(9.5, 11.0)
                    batting_power, batting_consistency, spin_skill, pace_skill = set_bat(10, 5, 5, 5)
                    powerplay_skill, middle_overs_skill, death_bowling_skill = set_bowl(55, 60, 50)
                    bowling_style = random.choice(['All-Round Pacer', 'Spinner'])


            # EXACT USER REQUIRED BOWLING STYLES
            exact_map = {
                'AB de Villiers': 'None',
                'Andre Russell': 'All-Round Pacer',
                'Chris Gayle': 'None',
                'Dale Steyn': 'Swing Specialist',
                'David Warner': 'None',
                'Dwayne Bravo': 'Death Specialist',
                'Jasprit Bumrah': 'Death Specialist',
                'Jos Buttler': 'None',
                'Kieron Pollard': 'None',
                'Lasith Malinga': 'Death Specialist',
                'MS Dhoni': 'None',
                'Rashid Khan': 'All-Round Spinner',
                'Rohit Sharma': 'None',
                'Sai Sudharsan': 'None',
                'Sunil Narine': 'All-Round Spinner',
                'Suresh Raina': 'None',
                'Suryakumar Yadav': 'None',
                'Trent Boult': 'Swing Specialist',
                'Virat Kohli': 'None',
                'Yuvraj Singh': 'All-Round Spinner',
                'Faf du Plessis': 'None',
                'Glenn Maxwell': 'All-Round Spinner',
                'Hardik Pandya': 'Death Specialist',
                'Heinrich Klaasen': 'None',
                'Irfan Pathan': 'Swing Specialist',
                'Jofra Archer': 'Swing Specialist',
                'KL Rahul': 'None',
                'Kagiso Rabada': 'Death Specialist',
                'Kuldeep Yadav': 'Spinner',
                'Matheesha Pathirana': 'Death Specialist',
                'Mitchell Starc': 'Death Specialist',
                'Mohammed Shami': 'Swing Specialist',
                'Nicholas Pooran': 'None',
                'Pat Cummins': 'Swing Specialist',
                'Ravichandran Ashwin': 'All-Round Spinner',
                'Ravindra Jadeja': 'All-Round Spinner',
                'Rishabh Pant': 'None',
                'Ruturaj Gaikwad': 'None',
                'Sanju Samson': 'None',
                'Shubman Gill': 'None',
                'Travis Head': 'None',
                'Yashasvi Jaiswal': 'None',
                'Yuzvendra Chahal': 'Spinner',
                'Amit Mishra': 'Spinner',
                'Arshdeep Singh': 'Death Specialist',
                'Axar Patel': 'All-Round Pacer',
                'Bhuvneshwar Kumar': 'Swing Specialist',
                'Cameron Green': 'All-Round Pacer',
                'David Miller': 'None',
                'Devon Conway': 'None',
                'Ishan Kishan': 'None',
                'Jonny Bairstow': 'None',
                'Liam Livingstone': 'All-Round Pacer',
                'Marcus Stoinis': 'All-Round Pacer',
                'Mayank Yadav': 'Death Specialist',
                'Moeen Ali': 'All-Round Spinner',
                'Mohammed Siraj': 'Swing Specialist',
                'Quinton de Kock': 'None',
                'Rajat Patidar': 'None',
                'Ravi Bishnoi': 'Spinner',
                'Rinku Singh': 'None',
                'Robin Uthappa': 'None',
                'Sam Curran': 'Swing Specialist',
                'Shakib Al Hasan': 'All-Round Spinner',
                'Shreyas Iyer': 'None',
                'Tilak Varma': 'None',
                'Tim David': 'None',
                'Tristan Stubbs': 'None',
                'Varun Chakravarthy': 'Spinner',
                'Will Jacks': 'All-Round Spinner',
                'Yusuf Pathan': 'All-Round Pacer',
                'Abhishek Sharma': 'Spinner',
                'Aiden Markram': 'None',
                'Ashutosh Sharma': 'None',
                'Avesh Khan': 'Swing Specialist',
                'Chris Woakes': 'All-Round Pacer',
                'Deepak Chahar': 'Swing Specialist',
                'Dewald Brevis': 'None',
                'Glenn Phillips': 'None',
                'Harshal Patel': 'Death Specialist',
                'Harshit Rana': 'Swing Specialist',
                'Keshav Maharaj': 'Spinner',
                'Marco Jansen': 'All-Round Pacer',
                'Matt Henry': 'Swing Specialist',
                'Mitchell Marsh': 'All-Round Pacer',
                'Mohammad Nabi': 'All-Round Spinner',
                'Mohit Sharma': 'Death Specialist',
                'Mukesh Kumar': 'Swing Specialist',
                'Mustafizur Rahman': 'Death Specialist',
                'Mujeeb Ur Rahman': 'Spinner',
                'Nitish Rana': 'Swing Specialist',
                'Pathum Nissanka': 'None',
                'Phil Salt': 'None',
                'Rahul Chahar': 'Spinner',
                'Rahul Tewatia': 'All-Round Pacer',
                'Rahul Tripathi': 'None',
                'Riyan Parag': 'All-Round Pacer',
                'Rovman Powell': 'None',
                'Shashank Singh': 'None',
                'Shimron Hetmyer': 'None',
                'Shivam Dube': 'All-Round Pacer',
                'T Natarajan': 'Death Specialist',
                'Venkatesh Iyer': 'All-Round Pacer',
                'Washington Sundar': 'All-Round Spinner',
                'Wriddhiman Saha': 'None',
                'Jacob Bethell': 'All-Round Spinner',
                'Abdul Samad': 'None',
                'Ajinkya Rahane': 'None',
                'Akeal Hosein': 'All-Round Spinner',
                'Ambati Rayudu': 'None',
                'Ayush Badoni': 'None',
                'Azmatullah Omarzai': 'All-Round Pacer',
                'Ben Stokes': 'All-Round Pacer',
                'Chris Jordan': 'All-Round Pacer',
                'Dasun Shanaka': 'All-Round Pacer',
                'Deepak Hooda': 'All-Round Pacer',
                'Dinesh Karthik': 'None',
                'Gudakesh Motie': 'Swing Specialist',
                'Harry Brook': 'None',
                'Ishant Sharma': 'Swing Specialist',
                'Jacob Bethell': 'All-Round Pacer',
                'Jason Holder': 'All-Round Pacer',
                'Jimmy Neesham': 'All-Round Pacer',
                'Jitesh Sharma': 'None',
                'Khaleel Ahmed': 'Swing Specialist',
                'Krunal Pandya': 'All-Round Pacer',
                'Lalit Yadav': 'All-Round Pacer',
                'Lungi Ngidi': 'Death Specialist',
                'Mark Wood': 'Death Specialist',
                'Mayank Agarwal': 'None',
                'Michael Bracewell': 'All-Round Spinner',
                'Mohsin Khan': 'Swing Specialist',
                'Naveen-ul-Haq': 'Swing Specialist',
                'Nehal Wadhera': 'None',
                'Nitish Kumar Reddy': 'All-Round Pacer',
                'Noor Ahmad': 'Spinner',
                'Parthiv Patel': 'None',
                'Prabhsimran Singh': 'None',
                'Prithvi Shaw': 'None',
                'Rahmanullah Gurbaz': 'None',
                'Shikhar Dhawan': 'None',
                'Tom Latham': 'None',
                'Tymal Mills': 'Death Specialist',
                'Umran Malik': 'Death Specialist',
                'Wanindu Hasaranga': 'All-Round Spinner',
                'Shahrukh Khan': 'None',
                'Harpreet Brar': 'All-Round Spinner',
                'Abinav Manohar': 'None',
                'Abishek Porel': 'None',
                'Adam Zampa': 'Spinner',
                'Aman Khan': 'All-Round Spinner',
                'Angkrish Raghuvanshi': 'None',
                'Anshul Kamboj': 'Swing Specialist',
                'Atharva Taide': 'None',
                'Dhruv Jurel': 'None',
                'Fazalhaq Farooqi': 'Swing Specialist',
                'Kwena Maphaka': 'Swing Specialist',
                'Luke Wood': 'Death Specialist',
                'Maheesh Theekshana': 'Spinner',
                'Mahipal Lomror': 'None',
                'Mitchell Santner': 'All-Round Spinner',
                'Nathan Ellis': 'Death Specialist',
                'Piyush Chawla': 'Spinner',
                'Reece Topley': 'Spinner',
                'Romario Shepherd': 'All-Round Pacer',
                'Shahbaz Ahmed': 'All-Round Pacer',
                'Shardul Thakur': 'Swing Specialist',
                'Sheldon Cottrell': 'Death Specialist',
                'Tom Curran': 'All-Round Pacer',
                'Akash Madhwal': 'Spinner',
                'Anmolpreet Singh': 'None',
                'Anuj Rawat': 'None',
                'Chetan Sakariya': 'Swing Specialist',
                'Corbin Bosch': 'All-Round Pacer',
                'Jayant Yadav': 'All-Round Spinner',
                'Karn Sharma': 'Spinner',
                'Kartikeya Singh': 'Swing Specialist',
                'Kuldeep Sen': 'Swing Specialist',
                'Manimaran Siddharth': 'Spinner',
                'Murugan Ashwin': 'Swing Specialist',
                'Naman Dhir': 'All-Round Spinner',
                'Simarjeet Singh': 'Spinner',
                'Suyash Prabhudessai': 'None',
                'Suyash Sharma': 'Swing Specialist',
                'Tushar Deshpande': 'Swing Specialist',
                'Vishnu Vinod': 'None',
                'Vyshak Vijaykumar': 'Swing Specialist',
                'Yash Dhull': 'None',
                'Arshad Khan': 'Swing Specialist',
                'Swapnil Singh': 'All-Round Spinner',
                'Alzarri Joseph': 'Death Specialist',
                'Arjun Tendulkar': 'All-Round Spinner',
                'Ayush Mhatre': 'None',
                'Jaydev Unadkat': 'Spinner',
                'Josh Hazlewood': 'Swing Specialist',
                'Lockie Ferguson': 'Death Specialist',
                'Obed McCoy': 'Swing Specialist',
                'Prasidh Krishna': 'Swing Specialist',
                'Sandeep Sharma': 'Swing Specialist',
                'Umesh Yadav': 'Death Specialist',
                'Vaibhav Suryavanshi': 'None',
                'Daniel Sams': 'All-Round Pacer',
                'KS Bharat': 'None',
                'Kamlesh Nagarkoti': 'Swing Specialist',
                'Pranshu Arya': 'None',
                'Riley Meredith': 'Swing Specialist',
                'Sameer Rizvi': 'None',
                'Sarfaraz Khan': 'None',
                'Shivam Mavi': 'Spinner',
                'Priyansh Arya': 'None',
                'Finn Allen': 'None',
                'Tim Seifert': 'None'
            }
            if name in exact_map and exact_map[name] != 'None':
                bowling_style = exact_map[name]
            elif exact_map.get(name) == 'None':
                bowling_style = 'None'

            # Set explicit tactical roles for specific famous players
            if name in ['Virat Kohli', 'KL Rahul', 'Faf du Plessis', 'Kane Williamson', 'Shikhar Dhawan']:
                tactical_role = 'Anchor'
            elif name in ['Andre Russell', 'MS Dhoni', 'David Miller', 'Tim David', 'Shimron Hetmyer', 'Tristan Stubbs', 'Ashutosh Sharma', 'Shashank Singh', 'Suresh Raina', 'Kieron Pollard', 'Dasun Shanaka', 'Corbin Bosch']:
                tactical_role = 'Finisher'
            elif name in ['Suryakumar Yadav', 'Travis Head', 'Heinrich Klaasen', 'Nicholas Pooran', 'Jake Fraser-McGurk']:
                tactical_role = 'Power Hitter'

            is_spinner = bowling_style in ['Spinner', 'All-Round Spinner']

            matches = random.randint(20, 180)
            # Classify All-rounders
            if role == 'All-rounder':
                # Explicit overrides for Bowling All-rounders
                if name in [
                    'Rashid Khan', 'Sunil Narine', 'Wanindu Hasaranga', 
                    'Dwayne Bravo', 'Krunal Pandya', 'Marco Jansen', 'Mitchell Santner'
                ]:
                    role = 'Bowling All-rounder'
                else:
                    bat_score = (bat_avg / 20.0) + (sr / 120.0)
                    bowl_score = (30.0 / bowl_avg if bowl_avg > 0 else 0) + (9.0 / econ if econ > 0 else 0)
                    if bat_score > bowl_score:
                        role = 'Batting All-rounder'
                    else:
                        role = 'Bowling All-rounder'

            # MS Dhoni Special Power Boost
            if name == 'MS Dhoni':
                batting_power = 98 
                batting_consistency = 95
                tactical_role = 'Finisher'

            if name == 'Jacob Bethell':
                role = 'Batting All-rounder'

            return {
                'name': name,
                'country': 'India', # Simplified for speed, could expand later
                'role': role,
                'tactical_role': tactical_role,
                'bowling_style': bowling_style,
                'star_rating': float(stars), # Exact 1 to 5
                
                # V2 Stats
                'batting_power': max(0, min(100, batting_power)),
                'batting_consistency': max(0, min(100, batting_consistency)),
                'spin_skill': max(0, min(100, spin_skill)),
                'pace_skill': max(0, min(100, pace_skill)),
                
                'powerplay_skill': max(0, min(100, powerplay_skill)),
                'middle_overs_skill': max(0, min(100, middle_overs_skill)),
                'death_bowling_skill': max(0, min(100, death_bowling_skill)),
                'is_spinner': is_spinner,
                
                'fielding_skill': max(0, min(100, fielding_skill)),
                
                # Real-world display stats
                'batting_avg': round(bat_avg, 1),
                'strike_rate': round(sr, 1),
                'bowling_avg': round(bowl_avg, 1),
                'economy': round(econ, 1),
                'ipl_matches': matches,
                'ipl_runs': int(matches * bat_avg * 0.8),
                'ipl_batting_avg': round(bat_avg, 2),
                'ipl_strike_rate': round(sr, 2),
                'ipl_wickets': int(matches * (1.2 if bowling_style != 'None' else 0)),
                'ipl_bowling_avg': round(bowl_avg, 2),
                'ipl_economy': round(econ, 2),
                'form_rating': round(random.uniform(5.5, 9.5), 1)
            }


        # 1. THE USER DEFINED LISTS
        roster = []

        # ==========================================
        # ⭐⭐⭐⭐⭐ 5 STAR
        # ==========================================
        r_5 = [
            ('Virat Kohli', 'Batsman'), ('Jos Buttler', 'Wicketkeeper'), ('KL Rahul', 'Wicketkeeper'), 
            ('AB de Villiers', 'Batsman'), ('David Warner', 'Batsman'), ('Suryakumar Yadav', 'Batsman'), 
            ('Andre Russell', 'All-rounder'), ('Rashid Khan', 'All-rounder'), ('Sunil Narine', 'All-rounder'), 
            ('Ruturaj Gaikwad', 'Batsman'), ('Yashasvi Jaiswal', 'Batsman'), ('Shubman Gill', 'Batsman'), 
            ('Heinrich Klaasen', 'Wicketkeeper'), ('Nicholas Pooran', 'Wicketkeeper'), 
            ('Glenn Maxwell', 'All-rounder'), ('Faf du Plessis', 'Batsman'),
            ('Rohit Sharma', 'Batsman'), ('Kane Williamson', 'Batsman'), ('Pat Cummins', 'Bowler'),
            ('Jofra Archer', 'Bowler'), ('Kagiso Rabada', 'Bowler'), ('Mitchell Starc', 'Bowler'),
            ('David Miller', 'Batsman'), ('Rahul Dravid', 'Batsman'),
            ('Sai Sudharsan', 'Batsman'), ('Jasprit Bumrah', 'Bowler'), ('MS Dhoni', 'Batsman'),
            ('Chris Gayle', 'Batsman'), ('Hardik Pandya', 'All-rounder'),
            ('Axar Patel', 'All-rounder'), ('Trent Boult', 'Bowler'), ('Kuldeep Yadav', 'Bowler'),
            ('Varun Chakravarthy', 'Bowler'), ('Josh Hazlewood', 'Bowler'), ('Suresh Raina', 'Batsman'),
            ('Lasith Malinga', 'Bowler'), ('Kieron Pollard', 'Batsman')
        ]
        for name, role in r_5:
            roster.append(generate_stats_for_tier(name, role, 5))

        # ==========================================
        # ⭐⭐⭐⭐ 4 STAR
        # ==========================================
        r_4 = [
            ('Rishabh Pant', 'Wicketkeeper'), ('Sanju Samson', 'Wicketkeeper'), 
            ('Cameron Green', 'All-rounder'), ('Marcus Stoinis', 'All-rounder'), ('Moeen Ali', 'All-rounder'), 
            ('Ravindra Jadeja', 'All-rounder'), ('Sam Curran', 'All-rounder'), 
            ('Devon Conway', 'Batsman'), ('Rinku Singh', 'Batsman'), ('Ishan Kishan', 'Wicketkeeper'), 
            ('Quinton de Kock', 'Wicketkeeper'), ('Tilak Varma', 'Batsman'), ('Rahul Tripathi', 'Batsman'), 
            ('Shimron Hetmyer', 'Batsman'), ('Tim David', 'Batsman'), ('Liam Livingstone', 'All-rounder'),
            ('Rahul Chahar', 'Bowler'), ('Shivam Dube', 'All-rounder'), ('Abdul Samad', 'Batsman'),
            ('Krunal Pandya', 'All-rounder'), ('Wanindu Hasaranga', 'All-rounder'), ('Dwayne Bravo', 'All-rounder'),
            ('Ambati Rayudu', 'Batsman'), ('Tymal Mills', 'Bowler'), ('Mark Wood', 'Bowler'), 
            ('Matheesha Pathirana', 'Bowler'), ('Deepak Chahar', 'Bowler'), ('Dewald Brevis', 'Batsman'),
            ('Rajat Patidar', 'Batsman'), ('Will Jacks', 'All-rounder'), ('Venkatesh Iyer', 'All-rounder'),
            ('Nitish Rana', 'All-rounder'), ('Abhishek Sharma', 'All-rounder'), ('Marco Jansen', 'All-rounder'),
            ('Bhuvneshwar Kumar', 'Bowler'), ('Glenn Phillips', 'Wicketkeeper'), ('Tristan Stubbs', 'Wicketkeeper'),
            ('Yuzvendra Chahal', 'Bowler'), ('Riyan Parag', 'All-rounder'), ('Jitesh Sharma', 'Wicketkeeper'),
            ('Prabhsimran Singh', 'Wicketkeeper'), ('Arshdeep Singh', 'Bowler'), ('Rahul Tewatia', 'All-rounder'),
            ('Noor Ahmad', 'Bowler'), ('Ravi Bishnoi', 'Bowler'), ('Naveen-ul-Haq', 'Bowler'), ('Ayush Badoni', 'Batsman'),
            ('Mohsin Khan', 'Bowler'), ('Mohammed Siraj', 'Bowler'), ('Ben Stokes', 'All-rounder'),
            ('Mohammed Shami', 'Bowler'), ('T Natarajan', 'Bowler'), ('Harshal Patel', 'Bowler'),
            ('Harshit Rana', 'Bowler'), ('Travis Head', 'Batsman'), ('Aiden Markram', 'Batsman'),
            ('Shreyas Iyer', 'Batsman'), ('Heinrich Klaasen', 'Wicketkeeper'), ('Dale Steyn', 'Bowler'),
            ('Lungi Ngidi', 'Bowler'), ('Yuvraj Singh', 'All-rounder'), ('Shakib Al Hasan', 'All-rounder'),
            ('Ravichandran Ashwin', 'All-rounder'), ('Dinesh Karthik', 'Wicketkeeper'), 
            ('Robin Uthappa', 'Wicketkeeper')
        ]
        for name, role in r_4:
            stars = 3.5 if name == 'Robin Uthappa' else (3.5 if name == 'Lungi Ngidi' else 4)
            roster.append(generate_stats_for_tier(name, role, stars))

        # ==========================================
        # ⭐⭐⭐ 3 STAR GOOD & BOWLERS
        # ==========================================
        r_3 = [
            ('Shikhar Dhawan', 'Batsman'), ('Mayank Agarwal', 'Batsman'), ('Ajinkya Rahane', 'Batsman'), 
            ('Deepak Hooda', 'All-rounder'), ('Washington Sundar', 'All-rounder'), ('Mitchell Marsh', 'All-rounder'), 
            ('Abishek Porel', 'Wicketkeeper'), ('Anrich Nortje', 'Bowler'), 
            ('Avesh Khan', 'Bowler'), ('Shardul Thakur', 'Bowler'), ('Nathan Ellis', 'Bowler'), 
            ('Adam Zampa', 'Bowler'), ('Kartikeya Singh', 'Bowler'), ('Murugan Ashwin', 'Bowler'), 
            ('Suyash Sharma', 'Bowler'), ('Manimaran Siddharth', 'Bowler'), ('Kuldeep Sen', 'Bowler'), 
            ('Akash Madhwal', 'Bowler'), ('Tushar Deshpande', 'Bowler'), ('Simarjeet Singh', 'Bowler'), 
            ('Chetan Sakariya', 'Bowler'), ('Maheesh Theekshana', 'Bowler'), ('Mitchell Santner', 'All-rounder'),
            ('Vishnu Vinod', 'Wicketkeeper'), ('Kumar Kartikeya', 'Bowler'), ('Piyush Chawla', 'Bowler'),
            ('Luke Wood', 'Bowler'), ('Romario Shepherd', 'All-rounder'), ('Anuj Rawat', 'Wicketkeeper'),
            ('Suyash Prabhudessai', 'Batsman'), ('Karn Sharma', 'Bowler'), ('Vyshak Vijaykumar', 'Bowler'),
            ('Mayank Markande', 'Bowler'), ('Fazalhaq Farooqi', 'Bowler'), ('Khaleel Ahmed', 'Bowler'),
            ('Mukesh Kumar', 'Bowler'), ('Navdeep Saini', 'Bowler'), ('Donovan Ferreira', 'Wicketkeeper'),
            ('Harpreet Brar', 'All-rounder'), ('Vidwath Kaverappa', 'Bowler'), ('Mohit Sharma', 'Bowler'),
            ('Yash Dayal', 'Bowler'), ('Darshan Nalkande', 'Bowler'), ('Spencer Johnson', 'Bowler'),
            ('Shahrukh Khan', 'Batsman'), ('Yash Thakur', 'Bowler'), ('Arshin Kulkarni', 'All-rounder'),
            ('Ashton Turner', 'Batsman'), ('David Willey', 'All-rounder'), ('Prasidh Krishna', 'Bowler'),
            ('Jacob Bethell', 'All-rounder'), ('Nehal Wadhera', 'Batsman'), ('Ashutosh Sharma', 'Batsman'),
            ('Prithvi Shaw', 'Batsman'), ('Angkrish Raghuvanshi', 'Batsman'), ('Jonny Bairstow', 'Wicketkeeper'),
            ('Vaibhav Suryavanshi', 'Batsman'), ('Ayush Mhatre', 'Batsman'), ('Shashank Singh', 'Batsman'),
            ('Mayank Yadav', 'Bowler'), ('Umran Malik', 'Bowler'), ('Ishant Sharma', 'Bowler'),
            ('Matt Henry', 'Bowler'), ('Mujeeb Ur Rahman', 'Bowler'), ('Amit Mishra', 'Bowler'),
            ('Azmatullah Omarzai', 'All-rounder'), ('Michael Bracewell', 'All-rounder'),
            ('Jimmy Neesham', 'All-rounder'), ('Dasun Shanaka', 'All-rounder'),
            ('Mohammad Nabi', 'All-rounder'), ('Chris Woakes', 'All-rounder'),
            ('Nitish Kumar Reddy', 'All-rounder'), ('Wriddhiman Saha', 'Wicketkeeper'),
            ('Dhruv Jurel', 'Wicketkeeper'), ('Phil Salt', 'Wicketkeeper'),
            ('Parthiv Patel', 'Wicketkeeper'), ('Finn Allen', 'Wicketkeeper'),
            ('Tim Seifert', 'Wicketkeeper')
        ]
        for name, role in r_3:
            roster.append(generate_stats_for_tier(name, role, 3))

        # ==========================================
        # ⭐⭐ 2 STAR BOWLERS/SQUAD
        # ==========================================
        r_2 = [
            ('Umesh Yadav', 'Bowler'), ('Mustafizur Rahman', 'Bowler'), 
            ('Alzarri Joseph', 'Bowler'), ('Lockie Ferguson', 'Bowler'), 
            ('Obed McCoy', 'Bowler'), ('Jaydev Unadkat', 'Bowler'), ('Sandeep Sharma', 'Bowler'), 
            ('Kulwant Khejroliya', 'Bowler'), ('KM Asif', 'Bowler'), ('Arshad Khan', 'All-rounder'),
            ('Rishi Dhawan', 'All-rounder'), ('Yudhvir Singh', 'Bowler'), ('Akash Singh', 'Bowler'), 
            ('Raj Angad Bawa', 'All-rounder'), ('Rovman Powell', 'Batsman'), ('Matthew Short', 'All-rounder'), 
            ('Ben Cutting', 'All-rounder'), ('Nathan Coulter-Nile', 'Bowler'), ('Aman Khan', 'All-rounder'),
            ('Swapnil Singh', 'All-rounder'), ('Arjun Tendulkar', 'All-rounder'), ('Hrithik Shokeen', 'All-rounder'), 
            ('Raghav Goyal', 'Bowler'), ('Jagadeesha Suchith', 'All-rounder'), ('Ripal Patel', 'All-rounder'), 
            ('Rasikh Salam', 'Bowler'), ('Shams Mulani', 'All-rounder'), ('Kartik Tyagi', 'Bowler'),
            ('Rajvardhan Hangargekar', 'All-rounder'), ('Mukesh Choudhary', 'Bowler'), ('Prashant Solanki', 'Bowler'),
            ('Ajay Mandal', 'All-rounder'), ('Naman Dhir', 'All-rounder'), ('Pravin Dubey', 'All-rounder'),
            ('Sumit Kumar', 'All-rounder'), ('Kunal Rathore', 'Wicketkeeper'), ('Tanush Kotian', 'All-rounder'),
            ('Rahmanullah Gurbaz', 'Wicketkeeper'), ('Tom Latham', 'Wicketkeeper'), ('Pathum Nissanka', 'Wicketkeeper'),
            ('Priyansh Arya', 'Batsman'), ('Anshul Kamboj', 'Bowler'), ('Keshav Maharaj', 'Bowler'),
            ('Akeal Hosein', 'All-rounder'), ('Jayant Yadav', 'All-rounder'), ('Tom Curran', 'All-rounder'),
            ('Corbin Bosch', 'All-rounder'), ('Chris Jordan', 'All-rounder')
        ]
        for name, role in r_2:
            roster.append(generate_stats_for_tier(name, role, 2))

        # ==========================================
        # ⭐ 1 STAR BENCH/UTILITY
        # ==========================================
        r_1 = [
            ('Sameer Rizvi', 'Batsman'), ('KS Bharat', 'Wicketkeeper'), ('Priyam Garg', 'Batsman'), 
            ('Sarfaraz Khan', 'Batsman'), ('Manish Pandey', 'Batsman'), ('Karun Nair', 'Batsman'),
            ('Jason Holder', 'All-rounder'), ('Odean Smith', 'All-rounder'), ('Daniel Sams', 'All-rounder'), 
            ('Fabian Allen', 'All-rounder'), ('Shivam Mavi', 'Bowler'), ('Kamlesh Nagarkoti', 'Bowler'), 
            ('Riley Meredith', 'Bowler'), ('Yash Dhull', 'Batsman')
        ]
        for name, role in r_1:
            roster.append(generate_stats_for_tier(name, role, 1))

        # Ensure absolute uniqueness across the combined roster (Highest star rating wins)
        unique_roster = {}
        for player in roster:
            name = player['name']
            if name not in unique_roster:
                unique_roster[name] = player
            else:
                if player['star_rating'] > unique_roster[name]['star_rating']:
                    unique_roster[name] = player
        
        roster = list(unique_roster.values())

        # --- SEED EXECUTION ---
        Player.objects.all().delete()
        PlayerMatchup.objects.all().delete()
        
        self.stdout.write(f'We are wiping the database and inserting the {len(roster)} exact user requested players...')

        for data in roster:
            Player.objects.create(**data)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully imported exactly {len(roster)} curated players from the 5-star tiers.'))
