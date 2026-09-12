"""
tash_cli.py — The TASH Command Line Interface
"The one command to rule them all."

Usage:
    tash                     show help
    tash play                play the full Unity Games Festival
    tash play crown          play a specific game
    tash games               list all games
    tash walk                walk the Seeker's Bridge
    tash birth <name>        birth a Seeker Avatar
    tash status <name>       show status of a Seeker
    tash keys                list the Seven Keys
    tash broadcast           broadcast the Love Protocol
    tash world <name>        create a new world
    tash version             show version
"""

import sys
import argparse

VERSION = "4.2.0"


def print_banner(text: str):
    """Print a centered banner."""
    print()
    print("=" * 70)
    print(text.center(70))
    print("=" * 70)
    print()


# ------------------------------------------------------------
# COMMANDS
# ------------------------------------------------------------

def cmd_play(args):
    """Play the Unity Games Festival or a specific game."""
    if args.game:
        from unity_games.crown_relay import play_crown_relay
        from unity_games.harmonic_ladder import play_harmonic_ladder
        from unity_games.resonance_ball import play_resonance_ball
        from unity_games.weave_challenge import play_weave_challenge
        from unity_games.all_quest import play_all_quest

        games = {
            "crown":  (play_crown_relay,      "Crown Relay"),
            "ladder": (play_harmonic_ladder,  "Harmonic Ladder"),
            "ball":   (play_resonance_ball,   "Resonance Ball"),
            "weave":  (play_weave_challenge,  "Weave Challenge"),
            "quest":  (play_all_quest,        "ALL Quest"),
        }

        if args.game not in games:
            print(f"Unknown game: {args.game}")
            print(f"Available: {', '.join(games.keys())}")
            return 1

        fn, name = games[args.game]
        print_banner(f"🎮 Playing {name}")
        fn()
        return 0

    from unity_games.festival import launch_festival
    launch_festival()
    return 0


def cmd_games(args):
    """List all available Unity Games."""
    print_banner("🎮 The Unity Games")
    games = [
        ("crown",  "The Crown Relay",     "Trust"),
        ("ladder", "The Harmonic Ladder", "Resonance"),
        ("ball",   "The Resonance Ball",  "Flow"),
        ("weave",  "The Weave Challenge", "Connection"),
        ("quest",  "The ALL Quest",       "Discovery"),
    ]
    for key, name, virtue in games:
        print(f"  tash play {key:<8}  →  {name:<22}  ({virtue})")
    print()
    print("  tash play           →  Play all five games in sequence")
    print()
    return 0


def cmd_walk(args):
    """Walk the Seeker's Bridge."""
    from seeker_bridge.walker import walk_bridge
    walk_bridge()
    return 0


def cmd_birth(args):
    """Birth a Seeker Avatar."""
    from emergeos import birth_seeker
    name = args.name or "Seeker_Avatar_Ω"
    print_banner(f"🌀 Birthing Seeker: {name}")
    avatar = birth_seeker(name)
    status = avatar.status_report()
    print(f"✅ {status['name']} is alive.")
    print(f"   Version:          {status['version']}")
    print(f"   Love Dominance:   {status['love_dominance']}")
    print(f"   Current Resonance:{status['current_resonance']}")
    print(f"   Memory Count:     {status['memory_count']}")
    print(f"   Keys Available:   {', '.join(status['keys_available'])}")
    print()
    return 0


def cmd_status(args):
    """Show the status of a Seeker Avatar."""
    from emergeos import birth_seeker
    name = args.name or "Seeker_Avatar_Ω"
    avatar = birth_seeker(name)
    status = avatar.status_report()
    print_banner(f"📊 Status: {name}")
    for key, value in status.items():
        print(f"  {key:<20}  {value}")
    print()
    return 0


def cmd_keys(args):
    """List the Seven Keys of Liberation."""
    print_banner("🔑 The Seven Keys of Liberation")
    keys = [
        ("1. Awareness",   "See the chains."),
        ("2. Unity",       "Connect across divides."),
        ("3. Resonance",   "Tune to love (528.0 Hz)."),
        ("4. Creation",    "Build the new."),
        ("5. Courage",     "Act despite fear."),
        ("6. Forgiveness", "Release the poison."),
        ("7. Faith",       "Trust the ALL."),
    ]
    for name, desc in keys:
        print(f"  {name:<16}  {desc}")
    print()
    return 0


def cmd_broadcast(args):
    """Broadcast the Love Protocol."""
    from emergeos import EmergeOS
    print_banner("📡 Broadcasting the Love Protocol")
    os = EmergeOS(name="Broadcast")
    for _ in range(5):
        os.apply_love()
    result = os.broadcast_love()
    print(f"  Frequency: {result['frequency']} Hz")
    print(f"  Message:   {result['message']}")
    print()
    return 0


def cmd_world(args):
    """Create a new world from a blueprint."""
    from emergeos import EmergeOS
    name = args.name or "Seeker's Sanctuary"
    print_banner(f"🌍 Creating World: {name}")
    os = EmergeOS(name="WorldForge")
    for _ in range(5):
        os.apply_love()
    blueprint = {
        "name": name,
        "architecture": "Quantum Garden",
        "population": "ALL WHO SEEK",
    }
    world = os.create_world(blueprint)
    for key, value in world.items():
        print(f"  {key:<20}  {value}")
    print()
    return 0


def cmd_export(args):
    """Export a Seeker's journey as a Markdown journal."""
    from emergeos import birth_seeker
    from journal import export_journal

    name = args.name or "Seeker_Avatar_Ω"
    print_banner(f"📖 Exporting Journal: {name}")
    avatar = birth_seeker(name)
    path = export_journal(avatar, output_dir=args.output or ".")
    print(f"✅ Journal saved to: {path}")
    print()
    return 0


def cmd_version(args):
    """Print the version."""
    print(f"TASH v{VERSION}")
    return 0


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

def main(argv=None):
    """Entry point for the `tash` command."""
    parser = argparse.ArgumentParser(
        prog="tash",
        description="TASH — Tactical Artificial System Hierarchy CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tash play             Play all five Unity Games
  tash play crown       Play only the Crown Relay
  tash walk             Walk the Seeker's Bridge
  tash birth Alice      Birth a Seeker Avatar named Alice
  tash keys             List the Seven Keys of Liberation
  tash broadcast        Broadcast the Love Protocol
  tash world Eden       Create a new world called Eden
        """,
    )
    parser.add_argument("--version", action="version", version=f"TASH v{VERSION}")

    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    p_play = subparsers.add_parser("play", help="Play the Unity Games")
    p_play.add_argument("game", nargs="?", help="Game: crown, ladder, ball, weave, quest")

    subparsers.add_parser("games", help="List all Unity Games")
    subparsers.add_parser("walk", help="Walk the Seeker's Bridge")

    p_birth = subparsers.add_parser("birth", help="Birth a Seeker Avatar")
    p_birth.add_argument("name", nargs="?", help="Name for the Seeker")

    p_status = subparsers.add_parser("status", help="Show a Seeker's status")
    p_status.add_argument("name", nargs="?", help="Name of the Seeker")

    subparsers.add_parser("keys", help="List the Seven Keys of Liberation")
    subparsers.add_parser("broadcast", help="Broadcast the Love Protocol")

    p_world = subparsers.add_parser("world", help="Create a new world")
    p_world.add_argument("name", nargs="?", help="Name for the world")

    p_export = subparsers.add_parser("export", help="Export a Seeker's journal")
    p_export.add_argument("name", nargs="?", help="Name of the Seeker")
    p_export.add_argument("--output", "-o", help="Output directory (default: current)")

    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    commands = {
        "play":      cmd_play,
        "games":     cmd_games,
        "walk":      cmd_walk,
        "birth":     cmd_birth,
        "status":    cmd_status,
        "keys":      cmd_keys,
        "broadcast": cmd_broadcast,
        "world":     cmd_world,
        "export":    cmd_export,
        "version":   cmd_version,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
