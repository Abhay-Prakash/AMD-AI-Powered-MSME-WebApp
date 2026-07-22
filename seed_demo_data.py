import asyncio
import argparse
from datetime import date, datetime, timedelta, UTC
import random
from uuid import uuid4
from decimal import Decimal

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.ca_profile import CAProfile, VerificationStatus
from app.models.firm import Firm
from app.models.firm_membership import FirmMembership
from app.models.user import User
from app.models.client import Client
from app.models.match import Match
from app.models.application import Application
from app.models.invoice import Invoice
from app.models.notification import Notification
from app.services.user_service import _ph


# Deterministic Data
SECTORS = ["Textile", "Renewables", "Food Processing", "Electronics", "Healthcare", "Chemical", "Dairy", "Agro Processing", "Packaging", "IT Services"]

COMPANY_NAMES = {
    "Textile": ["WeaveCraft Innovations", "SilkRoute Threads", "Bharat Textiles"],
    "Renewables": ["Aarav Solar Tech", "Vayu Green Energy", "Sunlit Power Corp"],
    "Food Processing": ["Nandini Agro Processors", "TasteOfIndia Foods", "SpicyBite Snacks"],
    "Electronics": ["CircuitWorks India", "Neon Devices", "ElectroTech Solutions"],
    "Healthcare": ["MediCare Instruments", "LifeGuard Pharma", "Pulse Diagnostics"],
    "Chemical": ["NeoChem Industries", "Bharat Polymers", "Crystal Chemicals"],
    "Dairy": ["WhiteGold Dairy", "PureMilk Producers", "Kisan Dairy Farms"],
    "Agro Processing": ["GreenHarvest Mills", "AgriGrow Solutions", "Kisan Cereals"],
    "Packaging": ["SafePack Solutions", "EcoWrap Industries", "Prime Packaging"],
    "IT Services": ["CodeCrafters India", "TechVision Labs", "CloudScale Systems"]
}

OWNER_FIRST_NAMES = ["Rajesh", "Suresh", "Amit", "Vikram", "Sneha", "Priya", "Neha", "Anita", "Karan", "Rahul"]
OWNER_LAST_NAMES = ["Kumar", "Sharma", "Singh", "Gupta", "Patel", "Reddy", "Nair", "Iyer", "Deshmukh", "Joshi"]

SCHEMES = {
    "Textile": ["Technology Upgradation Fund", "ZED", "Interest Subvention"],
    "Renewables": ["PMEGP", "Technology Centre Scheme", "ZED"],
    "Food Processing": ["PMFME", "PMEGP", "CGTMSE"],
    "Electronics": ["SPECS", "Design Clinic", "Digital MSME"],
    "Healthcare": ["CGTMSE", "Technology Upgradation", "ZED"],
    "Chemical": ["Lean Manufacturing", "ZED", "CGTMSE"],
    "Dairy": ["Dairy Entrepreneurship Development Scheme", "PMFME", "PMEGP"],
    "Agro Processing": ["PMEGP", "PMFME", "Interest Subvention"],
    "Packaging": ["ZED", "CLCSS", "Lean Manufacturing"],
    "IT Services": ["Digital MSME", "CGTMSE", "PMEGP"]
}

STATUS_CHAIN = ["suggested", "under_review", "approved", "drafted", "submitted", "sanctioned", "disbursed"]

def generate_gst(state_code="27", pan="ABCDE1234F"):
    return f"{state_code}{pan}1Z5"

def generate_udyam():
    return f"UDYAM-MH-19-{random.randint(1000000, 9999999)}"

async def clear_data(session: AsyncSession):
    print("Clearing existing demo data...")
    await session.execute(delete(Notification))
    await session.execute(delete(Invoice))
    await session.execute(delete(Application))
    await session.execute(delete(Match))
    await session.execute(delete(Client))
    await session.commit()
    print("Demo data cleared.")

async def seed_demo_data(reset=False):
    """
    Idempotent seed script to populate a development database with a
    realistic demo Firm, CA, Clients, Matches, Applications, Invoices, and Notifications.
    """
    random.seed(42)  # Deterministic randomness
    
    async with AsyncSessionLocal() as session:
        if reset:
            await clear_data(session)

        # 1. Create a User for the CA
        stmt = select(User).where(User.email == "demo_ca@subsidydesk.com")
        result = await session.execute(stmt)
        ca_user = result.scalar_one_or_none()

        if not ca_user:
            print("Creating Demo CA User...")
            ca_user = User(
                email="demo_ca@subsidydesk.com",
                hashed_password=_ph.hash("password123")
            )
            session.add(ca_user)
            await session.commit()
            await session.refresh(ca_user)
        else:
            print("Demo CA User already exists.")

        # 2. Create the CA Profile
        stmt = select(CAProfile).where(CAProfile.user_id == ca_user.id)
        result = await session.execute(stmt)
        ca_profile = result.scalar_one_or_none()

        if not ca_profile:
            print("Creating Demo CA Profile...")
            ca_profile = CAProfile(
                user_id=ca_user.id,
                full_name="Rajesh Kumar",
                membership_number="MBR123456",
                designation="Senior Partner",
                years_of_experience=15,
                verification_status=VerificationStatus.VERIFIED.value
            )
            session.add(ca_profile)
            await session.commit()
            await session.refresh(ca_profile)

        # 3. Create the Firm
        stmt = select(Firm).where(Firm.registration_number == "FIRM987654")
        result = await session.execute(stmt)
        firm = result.scalar_one_or_none()

        if not firm:
            print("Creating Demo Firm...")
            firm = Firm(
                firm_name="Kumar & Associates",
                registration_number="FIRM987654",
                firm_type="LLP",
                city="Mumbai",
                established_year=2010
            )
            session.add(firm)
            await session.commit()
            await session.refresh(firm)

        # 4. Create the Firm Membership
        stmt = select(FirmMembership).where(
            FirmMembership.ca_profile_id == ca_profile.id,
            FirmMembership.firm_id == firm.id
        )
        result = await session.execute(stmt)
        membership = result.scalar_one_or_none()

        if not membership:
            print("Creating Firm Membership...")
            membership = FirmMembership(
                ca_profile_id=ca_profile.id,
                firm_id=firm.id,
                role="partner",
                is_primary=True,
                joined_at=date(2010, 1, 1)
            )
            session.add(membership)
            await session.commit()

        # 5. Create Clients
        stmt = select(Client).where(Client.company_name == "Aarav Solar Tech")
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            print("Demo Clients already exist. Use --reset to start fresh.")
            return

        print("Generating 30 Clients...")
        clients = []
        for sector, companies in COMPANY_NAMES.items():
            for company_name in companies:
                owner = f"{random.choice(OWNER_FIRST_NAMES)} {random.choice(OWNER_LAST_NAMES)}"
                pan = f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))}{random.randint(1000,9999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
                turnover = Decimal(random.randint(10, 500)) * Decimal("100000") # 10L to 5Cr
                client = Client(
                    ca_profile_id=ca_profile.id,
                    company_name=company_name,
                    owner_name=owner,
                    sector=sector,
                    state=random.choice(["Maharashtra", "Gujarat", "Karnataka", "Tamil Nadu", "Delhi"]),
                    district="Metro",
                    address="123 Industrial Area",
                    gst_number=generate_gst("27", pan),
                    pan_number=pan,
                    udyam_number=generate_udyam(),
                    enterprise_class="Micro" if turnover < Decimal("50000000") else "Small",
                    turnover=turnover,
                    email=f"contact@{company_name.lower().replace(' ', '')}.com",
                    phone=f"98{random.randint(10000000, 99999999)}"
                )
                clients.append(client)
                session.add(client)
        
        await session.commit()
        for c in clients:
            await session.refresh(c)

        print("Generating Eligibility Matches (~75)...")
        matches = []
        for client in clients:
            num_matches = random.randint(1, 4)
            available_schemes = SCHEMES.get(client.sector, ["PMEGP", "CGTMSE"])
            for _ in range(num_matches):
                scheme = random.choice(available_schemes)
                status = random.choice(STATUS_CHAIN)
                
                benefit_amount = Decimal(random.randint(5, 50)) * Decimal("100000") # 5L to 50L
                
                match = Match(
                    client_id=client.id,
                    scheme=scheme,
                    confidence=random.choice(["high", "medium"]),
                    status=status,
                    reason=f"{client.company_name} meets the criteria for {scheme} based on their {client.sector} classification and {client.enterprise_class} status.",
                    benefit=benefit_amount,
                    citation=f"Notification No. {random.randint(100, 999)}/{datetime.now().year}",
                    clause_ref=f"Section {random.randint(1, 10)}({random.choice('abcde')})",
                    issuing_body="Ministry of MSME",
                    last_verified=datetime.now(UTC).strftime("%Y-%m-%d"),
                )
                matches.append(match)
                session.add(match)

        await session.commit()
        for m in matches:
            await session.refresh(m)

        print("Generating Applications & Invoices...")
        applications = []
        invoices = []
        notifications = []
        for match in matches:
            if match.status in ["drafted", "submitted", "sanctioned", "disbursed"]:
                app = Application(
                    match_id=match.id,
                    draft_content={"executive_summary": "Auto-generated draft for submission."}
                )
                applications.append(app)
                session.add(app)
                
                if match.status in ["sanctioned", "disbursed"]:
                    invoice = Invoice(
                        application_id=match.id,
                        invoice_number=f"INV-{datetime.now().year}-{random.randint(1000, 9999)}",
                        invoice_status="generated",
                        payment_status="paid" if match.status == "disbursed" else random.choice(["pending", "overdue"]),
                        success_fee_percentage=Decimal("2.50"),
                        success_fee_amount=match.benefit * Decimal("0.025"),
                        generated_at=(datetime.now(UTC) - timedelta(days=random.randint(1, 30))).isoformat(),
                        payment_due_date=(datetime.now(UTC) + timedelta(days=15)).isoformat()
                    )
                    invoices.append(invoice)
                    session.add(invoice)

        print("Generating Notifications...")
        for i in range(100):
            notif = Notification(
                title=random.choice(["Match Found", "Draft Ready", "Payment Due", "Inspection Scheduled", "Scheme Updated"]),
                message="This is a system generated notification.",
                notification_type="alert",
                priority=random.choice(["normal", "high"]),
                is_read=random.choice([True, False])
            )
            notifications.append(notif)
            session.add(notif)

        await session.commit()

        print("\nSeed completed successfully!")
        print(f"Total Clients: {len(clients)}")
        print(f"Total Matches: {len(matches)}")
        print(f"Total Applications: {len(applications)}")
        print(f"Total Invoices: {len(invoices)}")
        print(f"Total Notifications: {len(notifications)}")
        print("Test CA Login: demo_ca@subsidydesk.com / password123")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the database with demo data.")
    parser.add_argument("--reset", action="store_true", help="Clear existing demo data before seeding.")
    args = parser.parse_args()
    asyncio.run(seed_demo_data(reset=args.reset))
