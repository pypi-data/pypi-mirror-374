"""VibeQ CLI - Enterprise command-line interface"""

import argparse
import sys
import json


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="vibeq",
        description="VibeQ - AI-powered plain-English browser automation"
    )
    parser.add_argument("--version", action="version", version="VibeQ 1.0.0")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run interactive demo")
    demo_parser.add_argument("--headless", action="store_true", help="Run demo in headless mode")
    
    # Examples command
    examples_parser = subparsers.add_parser("examples", help="Show example scripts")
    examples_parser.add_argument("--copy", help="Copy example to current directory")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup guide for new users")
    
    # Run command
    run_parser = subparsers.add_parser("run", help="Execute a plain-English command")
    run_parser.add_argument("text", nargs="+", help="Command to execute")
    run_parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    run_parser.add_argument("--enterprise", action="store_true", help="Enable enterprise mode")
    run_parser.add_argument("--ai-provider", choices=["openai", "anthropic", "grok", "auto"], 
                           default="auto", help="AI provider to use")
    
    # Health check
    health_parser = subparsers.add_parser("health", help="Get test suite health report")
    health_parser.add_argument("--days", type=int, default=7, help="Days to analyze")
    
    # Analytics
    analytics_parser = subparsers.add_parser("analytics", help="Get analytics report")
    analytics_parser.add_argument("--type", choices=["intelligence", "healing", "governance"], 
                                 default="intelligence", help="Type of analytics")
    
    # Configuration
    config_parser = subparsers.add_parser("configure", help="Configure VibeQ settings")
    config_parser.add_argument("--ai-mode", choices=["training", "production", "offline", "audit"],
                              help="Set AI operation mode")
    config_parser.add_argument("--max-ai-calls", type=int, help="Max AI calls per session")
    
    # CSV automation
    csv_parser = subparsers.add_parser("csv", help="Run CSV automation")
    csv_parser.add_argument("file", help="CSV file to process")
    csv_parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "demo":
            run_demo_command(args)
        elif args.command == "examples":
            show_examples_command(args)
        elif args.command == "setup":
            show_setup_command(args)
        elif args.command == "run":
            run_command(args)
        elif args.command == "health":
            show_health(args)
        elif args.command == "analytics":
            show_analytics(args)
        elif args.command == "configure":
            configure_vibeq(args)
        elif args.command == "csv":
            run_csv_automation(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def run_command(args):
    """Execute a single plain-English command."""
    from . import VibeQ
    
    command_text = " ".join(args.text)
    print(f"🚀 Executing: {command_text}")
    
    vq = VibeQ(
        headless=args.headless,
        enterprise_mode=args.enterprise,
        ai_provider=args.ai_provider
    )
    
    try:
        vq.start()
        success = vq.do(command_text)
        print(f"{'✅' if success else '❌'} Result: {'Success' if success else 'Failed'}")
        
        if args.enterprise:
            stats = vq.get_intelligence_stats()
            print(f"📊 Intelligence: {stats.get('hit_rate', 'N/A')} cache hit rate")
    finally:
        vq.close()


def show_health(args):
    """Show test suite health report."""
    from . import VibeQ
    
    print("📊 VibeQ Health Report")
    vq = VibeQ(enterprise_mode=True)
    health = vq.get_suite_health_report(days=args.days)
    
    print(f"📈 Test Suite Health Report ({health['period']})")
    print(f"   Success Rate: {health['summary']['success_rate']}")
    print(f"   Healing Rate: {health['summary']['healing_rate']}")
    print(f"   Total Executions: {health['summary']['total_test_executions']}")
    
    if health['recommendations']:
        print("\n💡 Recommendations:")
        for rec in health['recommendations']:
            print(f"   - {rec}")


def show_analytics(args):
    """Show enterprise analytics."""
    from . import VibeQ
    
    print("📈 VibeQ Analytics")
    vq = VibeQ(enterprise_mode=True)
    
    if args.type == "intelligence":
        stats = vq.get_intelligence_stats()
        print("🧠 Hybrid Intelligence Analytics:")
        print(json.dumps(stats, indent=2))
    elif args.type == "healing":
        healing = vq.get_healing_analysis()
        print("🔧 Healing Analytics:")
        print(json.dumps(healing, indent=2))
    elif args.type == "governance":
        governance = vq.get_governance_report()
        print("🏢 Governance Report:")
        print(json.dumps(governance, indent=2))


def configure_vibeq(args):
    """Configure VibeQ enterprise settings."""
    from . import VibeQ
    
    print("⚙️ VibeQ Configuration")
    vq = VibeQ(enterprise_mode=True)
    
    config_updates = {}
    if args.ai_mode:
        config_updates["ai_mode"] = args.ai_mode
    if args.max_ai_calls:
        config_updates["max_ai_calls_per_session"] = args.max_ai_calls
    
    if config_updates:
        result = vq.configure_enterprise(**config_updates)
        print(f"⚙️ Configuration updated: {result}")
    else:
        print("ℹ️ No configuration changes specified")


def run_csv_automation(args):
    """Run CSV-based automation."""
    from . import VibeQ
    
    print(f"📄 Processing CSV: {args.file}")
    
    vq = VibeQ(headless=args.headless)
    try:
        vq.start()
        data = vq.read_csv(args.file)
        
        print(f"📊 Loaded {len(data)} rows")
        for i, row in enumerate(data, 1):
            action = row.get('action', '')
            if action:
                print(f"   {i}. Executing: {action}")
                success = vq.do(action)
                print(f"      {'✅' if success else '❌'} {'Success' if success else 'Failed'}")
    finally:
        vq.close()


def run_demo_command(args):
    """Run the interactive VibeQ demo."""
    try:
        from .demo import main as demo_main
        demo_main()
    except ImportError:
        print("❌ Demo module not available")
    except Exception as e:
        print(f"❌ Demo failed: {e}")


def show_examples_command(args):
    """Show available examples or copy one."""
    import os
    from pathlib import Path
    
    if args.copy:
        # Copy example to current directory
        try:
            import pkg_resources
            example_path = pkg_resources.resource_filename('vibeq.examples', f'{args.copy}.py')
            target_path = f"{args.copy}_example.py"
            
            with open(example_path, 'r') as src:
                with open(target_path, 'w') as dst:
                    dst.write(src.read())
            print(f"✅ Copied {args.copy} example to {target_path}")
        except Exception as e:
            print(f"❌ Failed to copy example: {e}")
            print("Available examples: quick_start, complete_ecommerce")
    else:
        print("📚 VIBEQ EXAMPLES")
        print("=" * 60)
        print("Available example scripts:")
        print("")
        print("🚀 quick_start       - Basic VibeQ usage patterns")
        print("🛒 complete_ecommerce - Full e-commerce workflow")
        print("")
        print("To copy an example:")
        print("  vibeq examples --copy quick_start")
        print("  vibeq examples --copy complete_ecommerce")
        print("")
        print("Or run the interactive demo:")
        print("  vibeq demo")


def show_setup_command(args):
    """Show setup guide for new users."""
    import os
    
    print("🚀 VIBEQ SETUP GUIDE")
    print("=" * 60)
    print("")
    
    # Check available AI providers
    print("🤖 AI PROVIDER OPTIONS:")
    print("")
    
    # Check OpenAI
    openai_key = os.getenv('OPENAI_API_KEY')
    print(f"{'✅' if openai_key else '⚪'} OpenAI GPT-4 - Set OPENAI_API_KEY")
    if not openai_key:
        print("   Get key: https://platform.openai.com/api-keys")
    
    # Check Anthropic
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    print(f"{'✅' if anthropic_key else '⚪'} Anthropic Claude - Set ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("   Get key: https://console.anthropic.com/")
    
    # Check Grok
    grok_key = os.getenv('GROK_API_KEY')
    print(f"{'✅' if grok_key else '⚪'} Grok - Set GROK_API_KEY")
    if not grok_key:
        print("   Get key: https://console.x.ai/")
    
    # Check local models
    try:
        from . import VibeQ
        vq_temp = VibeQ()
        has_local = vq_temp._check_local_model()
        print(f"{'✅' if has_local else '⚪'} Local Models - Ollama/LM Studio detected" if has_local else "⚪ Local Models - Install Ollama or LM Studio")
        if not has_local:
            print("   Ollama: https://ollama.ai/")
            print("   LM Studio: https://lmstudio.ai/")
    except:
        print("⚪ Local Models - Install Ollama or LM Studio")
    
    print("")
    
    # Show configuration examples
    if openai_key or anthropic_key or grok_key:
        print("✅ AI Provider configured - you're ready!")
        print("")
        print("📝 USAGE EXAMPLES:")
        print("")
        if openai_key:
            print("vq = VibeQ()  # Auto-detects OpenAI")
            print("vq = VibeQ(ai_provider='openai')")
        if anthropic_key:
            print("vq = VibeQ(ai_provider='anthropic')")
        if grok_key:
            print("vq = VibeQ(ai_provider='grok')")
        
        print("")
        print("🔧 ADVANCED OPTIONS:")
        print("vq = VibeQ(ai_provider='local')  # Use local model")
        print("vq = VibeQ(ai_provider='openai', model='gpt-4')")
        print("vq = VibeQ(ai_provider='custom', ai_endpoint='http://localhost:1234/v1')")
        
    else:
        print("⚠️  No AI providers configured")
        print("")
        print("QUICK SETUP (Choose one):")
        print("")
        print("🔥 OpenAI (Recommended):")
        print("   export OPENAI_API_KEY='your-key-here'")
        print("   # or: echo 'OPENAI_API_KEY=your-key' > .env")
        print("")
        print("🎯 Anthropic Claude:")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        print("")
        print("🚀 Local Models (Free):")
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        print("   ollama run llama3.2")
    
    print("")
    print("QUICK TEST:")
    print("  vibeq demo          # Run interactive demo")
    print("  vibeq examples      # See example scripts")
    print("")
    print("YOUR FIRST SCRIPT:")
    print("  vibeq examples --copy quick_start")
    print("  python quick_start_example.py")
    print("")
    print("DOCUMENTATION:")
    print("  https://github.com/your-org/vibeq")
    print("  Check README.md for complete guides")


if __name__ == "__main__":
    main()
    main()
