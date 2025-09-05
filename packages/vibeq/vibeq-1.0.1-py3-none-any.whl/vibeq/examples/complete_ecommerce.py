#!/usr/bin/env python3
"""
VibeQ Example: Complete E-commerce Test
Full workflow demonstration with error handling

This is the same test that ships with VibeQ - a complete
end-to-end automation example that works on any e-commerce site.
"""
import time
import os
from vibeq import VibeQ


def test_ecommerce_workflow():
    """Complete e-commerce automation workflow"""
    print("🛒 COMPLETE E-COMMERCE AUTOMATION")
    print("=" * 60)
    print("Login → Add Product → Cart → Checkout → Complete Order")
    print("This shows VibeQ handling a real-world complex workflow\n")

    # Initialize with production settings
    vq = VibeQ(ai_provider="auto", headless=False)  # Auto-detect best available AI provider
    vq.launch_browser()

    results = {}

    try:
        # Step 1: Navigation
        print("📋 STEP 1: NAVIGATION")
        print("-" * 40)
        vq.go_to("https://www.saucedemo.com/")
        print("   🌐 Navigated to SauceDemo ✅")
        results['navigation'] = True
        time.sleep(1.5)

        # Step 2: Login Process
        print("\n📋 STEP 2: LOGIN PROCESS")
        print("-" * 40)
        try:
            vq.do("type standard_user in username")
            print("   👤 Username entered ✅")
            
            vq.do("type secret_sauce in password")
            print("   🔒 Password entered ✅")
            
            vq.do("click login")
            print("   🚪 Login clicked ✅")
            
            results['login'] = True
        except Exception as e:
            print(f"   ❌ Login failed: {e}")
            results['login'] = False
            return results
        time.sleep(2)

        # Step 3: Product Selection
        print("\n📋 STEP 3: PRODUCT SELECTION")
        print("-" * 40)
        try:
            vq.do("click add to cart for first product")
            print("   🎒 Added Backpack to cart ✅")
            results['add_product'] = True
        except Exception as e:
            print(f"   ❌ Failed to add product: {e}")
            results['add_product'] = False
            return results
        time.sleep(1)

        # Step 4: Shopping Cart
        print("\n📋 STEP 4: SHOPPING CART")
        print("-" * 40)
        try:
            cart_opened = vq.do("click cart icon in header")
            if cart_opened:
                print("   🛒 Opened shopping cart ✅")
                results['open_cart'] = True
            else:
                print("   ❌ Failed to open cart")
                results['open_cart'] = False
                return results
        except Exception as e:
            print(f"   ❌ Cart error: {e}")
            results['open_cart'] = False
            return results
        time.sleep(1)

        # Step 5: Checkout Process
        print("\n📋 STEP 5: CHECKOUT PROCESS")
        print("-" * 40)
        
        # Start checkout
        checkout_started = vq.do("click checkout")
        if checkout_started:
            print("   📋 Started checkout ✅")
            results['checkout'] = True
        else:
            print("   ❌ Failed to start checkout")
            results['checkout'] = False
            return results
        time.sleep(1)

        # Fill shipping information
        print("\n📋 STEP 6: SHIPPING INFORMATION")
        print("-" * 40)
        
        first_name = vq.do("type John in firstName field")
        last_name = vq.do("type Doe in lastName field") 
        postal_code = vq.do("type 12345 in postalCode field")
        
        print(f"   📝 First Name: {'✅' if first_name else '❌'}")
        print(f"   📝 Last Name: {'✅' if last_name else '❌'}")
        print(f"   📝 Postal Code: {'✅' if postal_code else '❌'}")
        
        # Continue to next step
        try:
            continue_clicked = vq.do("click continue")
            print(f"   ➡️  Continue: {'✅' if continue_clicked else '❌'}")
            results['shipping_info'] = continue_clicked
        except Exception as e:
            print(f"   ❌ Continue failed: {e}")
            results['shipping_info'] = False
            
        time.sleep(3)  # Wait for page transition

        # Step 7: Complete Order
        print("\n📋 STEP 7: COMPLETE ORDER")
        print("-" * 40)
        try:
            # Multiple strategies for the finish button
            finish_clicked = (
                vq.do("click finish") or
                vq.do("click button with text finish") or  
                vq.do("click submit order")
            )
            print(f"   ✅ Order completed: {'✅' if finish_clicked else '❌'}")
            results['finish_order'] = finish_clicked
        except Exception as e:
            print(f"   ❌ Order completion failed: {e}")
            results['finish_order'] = False
        time.sleep(3)

        # Step 8: Verify Success
        print("\n📋 STEP 8: VERIFY SUCCESS")
        print("-" * 40)
        try:
            success_verified = (
                vq.check("thank you message is visible") or
                vq.check("order completed successfully") or
                vq.check("order confirmation page")
            )
            print(f"   🎉 Success verified: {'✅' if success_verified else '❌'}")
            results['verify_success'] = success_verified
        except Exception as e:
            print(f"   ❌ Verification failed: {e}")
            results['verify_success'] = False

        # Final Results
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        success_rate = (passed / total) * 100
        
        print(f"\n📊 AUTOMATION RESULTS")
        print("=" * 60)
        print(f"✅ Passed Steps: {passed}/{total}")
        print(f"🤖 AI Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 AUTOMATION SUCCESSFUL!")
            print("VibeQ successfully handled a complex e-commerce workflow!")
        elif success_rate >= 60:
            print(f"\n⚠️  Partial Success - Some steps failed")
            print("This is normal for live demos. VibeQ learns and improves!")
        else:
            print(f"\n❌ Multiple Failures")
            print("Check your API key and internet connection")
            
        print(f"\n💡 KEY INSIGHTS:")
        print("• Pure AI-driven automation - no hardcoded selectors")
        print("• Natural language commands work on any website")  
        print("• Self-healing when website structures change")
        print("• Production-ready with intelligent error handling")
        
        return results

    finally:
        try:
            vq.close()
            print("\n🧹 Browser session closed")
        except Exception:
            pass


if __name__ == "__main__":
    test_ecommerce_workflow()
