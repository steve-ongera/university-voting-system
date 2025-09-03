import os
import sys
import django
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
import random
from datetime import datetime, timedelta


from voting.models import (
    Faculty, Department, Programme, Student, Party, Position, 
    Candidate, Delegate, Election, DelegateVote, MainVote, 
    VoteAuditLog, ElectionResult
)

fake = Faker()

# Kenyan names data
KENYAN_FIRST_NAMES = [
    # Male names
    'Abdirahman', 'Abdirizak', 'Abdullahi', 'Achieng', 'Adan', 'Aggrey', 'Ahmed', 'Akello', 
    'Akoth', 'Amos', 'Andrew', 'Anthony', 'Antony', 'Atieno', 'Augustine', 'Ayub', 'Baraka', 
    'Benjamin', 'Bernard', 'Brian', 'Caleb', 'Calvin', 'Charles', 'Chris', 'Christopher', 
    'Clement', 'Collins', 'Daniel', 'David', 'Dennis', 'Derrick', 'Duncan', 'Edwin', 'Emmanuel', 
    'Eric', 'Evans', 'Felix', 'Francis', 'Franklin', 'Fred', 'Frederick', 'Geoffrey', 'George', 
    'Gilbert', 'Harrison', 'Henry', 'Ian', 'Isaac', 'Jackson', 'Jacob', 'James', 'Japheth', 
    'Jason', 'Javan', 'Jefferson', 'Job', 'Joel', 'John', 'Jonathan', 'Joseph', 'Joshua', 
    'Julius', 'Kennedy', 'Kevin', 'Kiprotich', 'Lewis', 'Lucas', 'Mark', 'Martin', 'Mathew', 
    'Maurice', 'Michael', 'Moses', 'Nicholas', 'Ochieng', 'Odhiambo', 'Oduya', 'Oliver', 
    'Ongeri', 'Ouko', 'Owen', 'Pascal', 'Patrick', 'Paul', 'Peter', 'Philip', 'Richard', 
    'Robert', 'Samson', 'Samuel', 'Simon', 'Stephen', 'Steve', 'Thomas', 'Timothy', 'Vincent', 
    'Wesley', 'William',
    
    # Female names
    'Abigail', 'Agnes', 'Alice', 'Ann', 'Anne', 'Beatrice', 'Beryl', 'Brenda', 'Caroline', 
    'Catherine', 'Charity', 'Christine', 'Claire', 'Consolata', 'Diana', 'Doris', 'Dorothy', 
    'Edith', 'Elizabeth', 'Esther', 'Eunice', 'Faith', 'Florence', 'Grace', 'Hannah', 'Helen', 
    'Jane', 'Janet', 'Jennifer', 'Joan', 'Joyce', 'Judith', 'Julia', 'June', 'Khadijah', 
    'Linda', 'Lucy', 'Lydia', 'Margaret', 'Maria', 'Mary', 'Mercy', 'Monica', 'Nancy', 
    'Naomi', 'Nyokabi', 'Patricia', 'Peris', 'Phanice', 'Purity', 'Rachel', 'Rebecca', 
    'Rose', 'Ruth', 'Sally', 'Sarah', 'Scholastica', 'Susan', 'Tabitha', 'Teresia', 
    'Violet', 'Wanjiku', 'Wanjiru', 'Winnie'
]

KENYAN_LAST_NAMES = [
    'Abdi', 'Abudo', 'Achola', 'Achieng', 'Adhiambo', 'Aduol', 'Agola', 'Akinyi', 'Akoth', 
    'Amolo', 'Andika', 'Anyango', 'Apiyo', 'Aringo', 'Asena', 'Asiago', 'Atamba', 'Atieno', 
    'Awino', 'Ayodo', 'Bett', 'Chebet', 'Chelimo', 'Cheruiyot', 'Chesire', 'Choge', 'Gacheru', 
    'Gachoya', 'Gakinya', 'Gathogo', 'Gathumbi', 'Gatonye', 'Gitau', 'Githinji', 'Githongo', 
    'Gitonga', 'Gituku', 'Hassan', 'Hussein', 'Irungu', 'Kabiru', 'Kadhenge', 'Kagema', 
    'Kairu', 'Kamande', 'Kamau', 'Kamenju', 'Kanyi', 'Kapkatet', 'Kariuki', 'Karobia', 
    'Karuga', 'Karuri', 'Karwirwa', 'Kathure', 'Kaunda', 'Keter', 'Khaemba', 'Kibe', 
    'Kibiru', 'Kihara', 'Kiiru', 'Kimani', 'Kimathi', 'Kimeto', 'Kimeu', 'Kimotho', 
    'Kimumbi', 'Kinoti', 'Kiprotich', 'Kiragu', 'Kirika', 'Kirui', 'Koech', 'Korir', 
    'Lagat', 'Limo', 'Lukoye', 'Macharia', 'Maingi', 'Makena', 'Maloba', 'Mambo', 
    'Manyara', 'Maranga', 'Masaba', 'Masinde', 'Matano', 'Matere', 'Mbaabu', 'Mbatha', 
    'Mbugua', 'Mburu', 'Miano', 'Muchiri', 'Mugambi', 'Mugo', 'Muhoro', 'Muigai', 
    'Muiruri', 'Muite', 'Mujuni', 'Mukiri', 'Munyua', 'Murage', 'Mureithi', 'Muriithi', 
    'Muriuki', 'Muriungi', 'Musa', 'Musau', 'Musyoka', 'Mutai', 'Mutinda', 'Mutua', 
    'Mwacharo', 'Mwai', 'Mwangi', 'Mwaniki', 'Mwanza', 'Mwaura', 'Ndegwa', 'Nderi', 
    'Ndirangu', 'Ndunda', 'Ngugi', 'Ngumo', 'Njagi', 'Njenga', 'Njeru', 'Njoroge', 
    'Njuguna', 'Nthiga', 'Nyaga', 'Nyambura', 'Nyandoro', 'Nyangau', 'Nyong', 'Ochola', 
    'Ochieng', 'Odhiambo', 'Odongo', 'Ogola', 'Ogutu', 'Ojwang', 'Okello', 'Okoth', 
    'Oloo', 'Omolo', 'Ongeri', 'Onyancha', 'Otieno', 'Ouko', 'Owino', 'Oyaro', 'Rioba', 
    'Rotich', 'Ruto', 'Sagini', 'Saina', 'Sang', 'Tanui', 'Tarus', 'Thuo', 'Too', 
    'Wachira', 'Wafula', 'Waiguru', 'Wainaina', 'Waiganjo', 'Wairimu', 'Wairua', 'Waiyaki', 
    'Wakaba', 'Wambua', 'Wamukoya', 'Wanjala', 'Wanjiku', 'Wanjiru', 'Warega', 'Waweru'
]

class Command(BaseCommand):
    help = 'Seed the database with sample data for the voting app'

    def add_arguments(self, parser):
        parser.add_argument(
            '--students',
            type=int,
            default=300,
            help='Number of students to create (default: 300)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()
        
        self.stdout.write('Starting data seeding...')
        
        # Create faculties and departments
        faculties_data = self.create_faculties()
        departments_data = self.create_departments(faculties_data)
        programmes_data = self.create_programmes(departments_data)
        
        # Create students
        students = self.create_students(programmes_data, options['students'])
        
        # Create parties
        parties = self.create_parties()
        
        # Create positions
        positions = self.create_positions()
        
        # Create election
        election = self.create_election()
        
        # Create delegates
        delegates = self.create_delegates(students, parties, departments_data)
        
        # Create candidates
        candidates = self.create_candidates(students, parties, positions)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully seeded database with:\n'
                f'- {len(faculties_data)} faculties\n'
                f'- {len(departments_data)} departments\n'
                f'- {len(programmes_data)} programmes\n'
                f'- {len(students)} students\n'
                f'- {len(parties)} parties\n'
                f'- {len(positions)} positions\n'
                f'- {len(delegates)} delegates\n'
                f'- {len(candidates)} candidates\n'
                f'- 1 election'
            )
        )

    def clear_data(self):
        """Clear existing data"""
        models_to_clear = [
            VoteAuditLog, ElectionResult, MainVote, DelegateVote,
            Delegate, Candidate, Election, Position, Party,
            Student, Programme, Department, Faculty
        ]
        
        for model in models_to_clear:
            model.objects.all().delete()
        
        self.stdout.write('Existing data cleared.')

    def create_faculties(self):
        """Create sample faculties"""
        faculties_data = [
            ('Faculty of Science and Technology', 'FST'),
            ('Faculty of Business and Economics', 'FBE'),
            ('Faculty of Education', 'FED'),
            ('Faculty of Law', 'LAW'),
            ('Faculty of Medicine and Health Sciences', 'FMHS'),
            ('Faculty of Arts and Social Sciences', 'FASS'),
            ('Faculty of Engineering', 'ENG'),
            ('Faculty of Agriculture', 'AGR'),
        ]
        
        faculties = []
        for name, code in faculties_data:
            faculty, created = Faculty.objects.get_or_create(
                name=name,
                defaults={'code': code}
            )
            faculties.append(faculty)
        
        return faculties

    def create_departments(self, faculties):
        """Create departments for each faculty"""
        departments_mapping = {
            'Faculty of Science and Technology': [
                ('Computer Science', 'CS'),
                ('Mathematics', 'MATH'),
                ('Physics', 'PHYS'),
                ('Chemistry', 'CHEM'),
                ('Biology', 'BIO'),
                ('Statistics', 'STAT'),
            ],
            'Faculty of Business and Economics': [
                ('Business Administration', 'BA'),
                ('Economics', 'ECON'),
                ('Accounting', 'ACC'),
                ('Finance', 'FIN'),
                ('Marketing', 'MKT'),
            ],
            'Faculty of Education': [
                ('Educational Psychology', 'EDPS'),
                ('Curriculum Studies', 'CURR'),
                ('Educational Management', 'EDMG'),
                ('Early Childhood Education', 'ECE'),
            ],
            'Faculty of Law': [
                ('Public Law', 'PUB'),
                ('Private Law', 'PRI'),
                ('Commercial Law', 'COM'),
            ],
            'Faculty of Medicine and Health Sciences': [
                ('Medicine', 'MED'),
                ('Nursing', 'NUR'),
                ('Public Health', 'PH'),
                ('Pharmacy', 'PHAR'),
            ],
            'Faculty of Arts and Social Sciences': [
                ('English Literature', 'ENG'),
                ('History', 'HIST'),
                ('Philosophy', 'PHIL'),
                ('Sociology', 'SOC'),
                ('Political Science', 'POL'),
            ],
            'Faculty of Engineering': [
                ('Civil Engineering', 'CE'),
                ('Mechanical Engineering', 'ME'),
                ('Electrical Engineering', 'EE'),
                ('Chemical Engineering', 'CHE'),
            ],
            'Faculty of Agriculture': [
                ('Crop Science', 'CROP'),
                ('Animal Science', 'ANIM'),
                ('Agricultural Economics', 'AGECON'),
            ],
        }
        
        departments = []
        for faculty in faculties:
            if faculty.name in departments_mapping:
                for dept_name, dept_code in departments_mapping[faculty.name]:
                    department, created = Department.objects.get_or_create(
                        name=dept_name,
                        faculty=faculty,
                        defaults={'code': dept_code}
                    )
                    departments.append(department)
        
        return departments

    def create_programmes(self, departments):
        """Create programmes for each department"""
        programmes = []
        
        for department in departments:
            # Create 2-3 programmes per department
            prog_names = [
                f"Bachelor of {department.name}",
                f"Master of {department.name}",
            ]
            
            if random.choice([True, False]):  # 50% chance for PhD
                prog_names.append(f"PhD in {department.name}")
            
            for i, prog_name in enumerate(prog_names):
                prog_code = f"{department.code}{i+1:02d}"
                programme, created = Programme.objects.get_or_create(
                    name=prog_name,
                    department=department,
                    defaults={'code': prog_code}
                )
                programmes.append(programme)
        
        return programmes

    def create_students(self, programmes, num_students):
        """Create students with Kenyan names"""
        students = []
        used_reg_numbers = set()
        
        for i in range(num_students):
            # Generate unique registration number
            while True:
                # Format: SC211/0530/2022 (Faculty Code + Department + Sequential/Year)
                year = random.choice([2020, 2021, 2022, 2023, 2024])
                dept_code = random.choice(['SC', 'BA', 'ED', 'LW', 'MD', 'AS', 'EN', 'AG'])
                sequential = random.randint(100, 999)
                student_num = random.randint(1000, 9999)
                reg_number = f"{dept_code}{sequential}/{student_num:04d}/{year}"
                
                if reg_number not in used_reg_numbers:
                    used_reg_numbers.add(reg_number)
                    break
            
            # Generate birth certificate number
            birth_cert = f"{random.randint(10000000, 99999999)}"
            
            # Select random Kenyan names
            first_name = random.choice(KENYAN_FIRST_NAMES)
            last_name = random.choice(KENYAN_LAST_NAMES)
            
            # Generate email
            email = f"{first_name.lower()}.{last_name.lower()}@student.university.ac.ke"
            
            # Generate phone number (Kenyan format)
            phone_prefixes = ['0701', '0702', '0703', '0704', '0705', '0706', '0707', '0708', '0709',
                            '0710', '0711', '0712', '0713', '0714', '0715', '0716', '0717', '0718', '0719',
                            '0720', '0721', '0722', '0723', '0724', '0725', '0726', '0727', '0728', '0729']
            phone = f"{random.choice(phone_prefixes)}{random.randint(100000, 999999)}"
            
            # Select random programme and year
            programme = random.choice(programmes)
            year_of_study = random.randint(1, 4)
            
            student = Student(
                registration_number=reg_number,
                birth_certificate_number=birth_cert,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone,
                programme=programme,
                year_of_study=year_of_study,
                is_active=True,
                date_joined=fake.date_time_between(start_date='-2y', end_date='now', tzinfo=timezone.get_current_timezone())
            )
            
            # Set password to birth certificate number
            student.set_password(birth_cert)
            student.save()
            students.append(student)
            
            if (i + 1) % 50 == 0:
                self.stdout.write(f'Created {i + 1} students...')
        
        return students

    def create_parties(self):
        """Create political parties"""
        parties_data = [
            ('Students Democratic Party', 'SDP', 'Fighting for student rights and democracy', '#FF0000'),
            ('Progressive Students Alliance', 'PSA', 'Progressive policies for modern students', '#00FF00'),
            ('United Students Movement', 'USM', 'Unity and strength in diversity', '#0000FF'),
            ('Students Liberation Front', 'SLF', 'Liberation through education and empowerment', '#FFFF00'),
            ('Independent Students Coalition', 'ISC', 'Independent voices for independent minds', '#FF00FF'),
            ('Revolutionary Students Party', 'RSP', 'Revolutionary change for better tomorrow', '#00FFFF'),
        ]
        
        parties = []
        for name, acronym, description, color in parties_data:
            party, created = Party.objects.get_or_create(
                name=name,
                defaults={
                    'acronym': acronym,
                    'description': description,
                    'color_code': color,
                    'is_active': True
                }
            )
            parties.append(party)
        
        return parties

    def create_positions(self):
        """Create positions"""
        positions_data = [
            ('president', 'Student body president', 1),
            ('vice_president', 'Student body vice president', 2),
            ('secretary_general', 'Secretary general of student body', 3),
            ('treasurer', 'Student body treasurer', 4),
            ('sports_minister', 'Sports and recreation minister', 5),
            ('entertainment_minister', 'Entertainment and culture minister', 6),
            ('education_minister', 'Education and academic affairs minister', 7),
            ('accommodation_minister', 'Accommodation and welfare minister', 8),
        ]
        
        positions = []
        for name, description, order in positions_data:
            position, created = Position.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    'order': order
                }
            )
            positions.append(position)
        
        return positions

    def create_election(self):
        """Create an active election"""
        now = timezone.now()
        
        election, created = Election.objects.get_or_create(
            name="Student Government Elections 2024",
            defaults={
                'description': 'Annual student government elections',
                'current_phase': 'registration',
                'delegate_voting_start': now + timedelta(days=7),
                'delegate_voting_end': now + timedelta(days=10),
                'main_voting_start': now + timedelta(days=14),
                'main_voting_end': now + timedelta(days=17),
                'is_active': True
            }
        )
        
        return election

    def create_delegates(self, students, parties, departments):
        """Create delegates - max 2 per party per department"""
        delegates = []
        
        for party in parties:
            party_delegates_count = 0
            
            for department in departments:
                if party_delegates_count >= 15:  # Max 15 delegates per party
                    break
                
                # Get students from this department
                dept_students = [s for s in students if s.programme.department == department]
                
                if len(dept_students) < 2:
                    continue
                
                # Select 1-2 students as delegates for this party in this department
                num_delegates = min(random.randint(1, 2), len(dept_students), 15 - party_delegates_count)
                selected_students = random.sample(dept_students, num_delegates)
                
                for student in selected_students:
                    # Check if student is already a delegate
                    if not hasattr(student, 'delegate_profile'):
                        delegate = Delegate.objects.create(
                            student=student,
                            party=party,
                            department=department,
                            is_approved=random.choice([True, True, True, False])  # 75% approved
                        )
                        delegates.append(delegate)
                        party_delegates_count += 1
                        
                        if party_delegates_count >= 15:
                            break
        
        return delegates

    def create_candidates(self, students, parties, positions):
        """Create candidates - one per position per party"""
        candidates = []
        
        for party in parties:
            for position in positions:
                # Find a suitable student for this position
                available_students = [s for s in students if not hasattr(s, 'candidacies') or s.candidacies.count() == 0]
                
                if available_students:
                    student = random.choice(available_students)
                    manifesto = f"As your {position.get_name_display()}, I pledge to bring positive change to our university. My vision includes improved student welfare, better facilities, and stronger representation of student interests."
                    
                    candidate = Candidate.objects.create(
                        student=student,
                        party=party,
                        position=position,
                        manifesto=manifesto,
                        is_approved=random.choice([True, True, True, False])  # 75% approved
                    )
                    candidates.append(candidate)
        
        return candidates


if __name__ == '__main__':
    # You can also run this script directly
    import sys
    from django.core.management import execute_from_command_line
    
    # Add the command to Django
    execute_from_command_line(['manage.py', 'seed_data'])