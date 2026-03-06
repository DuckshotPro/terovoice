#!/usr/bin/env python3
"""
Onboard a new client in 60 seconds.
Creates client config, sets up SIP routing, generates dashboard.
"""
import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.router import ClientRouter
from config.settings import settings


def onboard_client():
    """Interactive client onboarding."""
    print("\n🚀 AI Receptionist - Client Onboarding\n")

    # Get client info
    name = input("Client name (e.g., Dr Mike Dentistry): ").strip()
    if not name:
        print("❌ Name required")
        return

    phone = input("Phone number (E.164 format, e.g., +12025551234): ").strip()
    if not phone:
        print("❌ Phone number required")
        return

    profession = input(
        "Profession (dentist/plumber/mechanic/locksmith/photographer/realtor/tattoo/inspector/massage): "
    ).strip()
    if not profession:
        profession = "dentist"

    voice_id = input("Voice ID (or press Enter for default): ").strip()
    if not voice_id:
        voice_id = "af_sarah"  # Default Cartesia voice

    # Initialize router
    router = ClientRouter(settings.clients_db_path)

    # Add client
    success = router.add_client(
        name=name,
        phone_numbers=[phone],
        profession=profession,
        voice_id=voice_id,
        dashboard_url=f"https://{name.lower().replace(' ', '-')}.yourdomain.com",
    )

    if success:
        print(f"\n✅ Client onboarded successfully!")
        print(f"   Name: {name}")
        print(f"   Phone: {phone}")
        print(f"   Profession: {profession}")
        print(f"   Voice ID: {voice_id}")
        print(f"\n📊 Dashboard: https://{name.lower().replace(' ', '-')}.yourdomain.com")
        print(f"💰 Billing: $499/month starting now")
        print(f"\n🔗 Next steps:")
        print(f"   1. Configure SIP trunk in LiveKit for {phone}")
        print(f"   2. Clone voice using Cartesia API")
        print(f"   3. Send dashboard link to client")
    else:
        print("❌ Failed to onboard client")


if __name__ == "__main__":
    onboard_client()
