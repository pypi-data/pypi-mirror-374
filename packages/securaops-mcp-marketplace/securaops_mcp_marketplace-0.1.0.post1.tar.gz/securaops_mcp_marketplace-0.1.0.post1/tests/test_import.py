#!/usr/bin/env python3

try:
    from securaops_mcp_marketplace import SlackConnector
    print("✓ Successfully imported SlackConnector")
    print(f"✓ SlackConnector class: {SlackConnector}")
    
    # Test basic functionality
    connector = SlackConnector("test_api_key")
    print("✓ Successfully created connector instance")

except ImportError:
    try:
        # Some build systems might use different names
        from securaops_mcp_marketplace.slack_connector import SlackConnector
        print('✓ Imported from submodule')
    except ImportError:
        try:
            # Check if package installed with different name
            import securaops_mcp_marketplace as pkg
            print(f'✓ Found package: {pkg}')
            print(f'✓ Package content: {dir(pkg)}')
        except ImportError as e:
            print(f'✗ All imports failed: {e}')   
    
#except ImportError as e:
#    print(f"✗ Import failed: {e}")
#    print("\nTroubleshooting steps:")
#    print("1. Run: pip list | grep securaops-mcp-marketplace")
#    print("2. Check package structure")
#    print("3. Verify __init__.py exports")
#except Exception as e:
#    print(f"✗ Other error: {e}")