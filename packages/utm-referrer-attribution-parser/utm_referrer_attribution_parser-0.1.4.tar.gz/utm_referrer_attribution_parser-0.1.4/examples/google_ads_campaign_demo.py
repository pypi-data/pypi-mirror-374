"""
Demonstration of Google Ads campaign ID extraction and modern tracking parameters.

This example shows how the webmetic_referrer library properly extracts:
- Google Ads campaign IDs (gad_campaignid)
- Click IDs with their types (gclid, gbraid, wbraid, fbclid, etc.)
- Priority handling when multiple click IDs are present
"""

from utm_referrer_parser import webmetic_referrer


def main():
    print("=" * 80)
    print("Google Ads Campaign ID and Click Tracking Demo")
    print("=" * 80)
    
    # Example 1: Google Ads with campaign ID
    print("\n1. Google Ads with gad_campaignid:")
    print("-" * 40)
    url1 = "https://example.com/?gad_source=1&gad_campaignid=22633883708&gclid=ABC123"
    result1 = webmetic_referrer(url1)
    print(f"URL: {url1}")
    print(f"Source: {result1['source']}")
    print(f"Medium: {result1['medium']}")
    print(f"Campaign ID: {result1.get('campaign_id')}")
    print(f"Click ID: {result1.get('click_id')}")
    print(f"Click ID Type: {result1.get('click_id_type')}")
    print(f"GAD Source: {result1.get('gad_source')}")
    
    # Example 2: Google Ads with gbraid (app conversions)
    print("\n2. Google Ads with gbraid (app conversions):")
    print("-" * 40)
    url2 = "https://example.com/?gbraid=GB123456&gad_campaignid=789&gad_source=1"
    result2 = webmetic_referrer(url2)
    print(f"URL: {url2}")
    print(f"Source: {result2['source']}")
    print(f"Medium: {result2['medium']}")
    print(f"Campaign ID: {result2.get('campaign_id')}")
    print(f"Click ID: {result2.get('click_id')}")
    print(f"Click ID Type: {result2.get('click_id_type')}")
    
    # Example 3: Multiple click IDs (priority handling)
    print("\n3. Multiple click IDs (gclid has priority):")
    print("-" * 40)
    url3 = "https://example.com/?gclid=GC111&gbraid=GB222&fbclid=FB333&gad_campaignid=999"
    result3 = webmetic_referrer(url3)
    print(f"URL: {url3}")
    print(f"Source: {result3['source']}")
    print(f"Medium: {result3['medium']}")
    print(f"Campaign ID: {result3.get('campaign_id')}")
    print(f"Click ID: {result3.get('click_id')}")
    print(f"Click ID Type: {result3.get('click_id_type')}")
    print("Note: gclid takes priority over other click IDs")
    
    # Example 4: Facebook Ads
    print("\n4. Facebook Ads click tracking:")
    print("-" * 40)
    url4 = "https://example.com/?fbclid=IwAR123456789"
    result4 = webmetic_referrer(url4)
    print(f"URL: {url4}")
    print(f"Source: {result4['source']}")
    print(f"Medium: {result4['medium']}")
    print(f"Click ID: {result4.get('click_id')}")
    print(f"Click ID Type: {result4.get('click_id_type')}")
    
    # Example 5: Microsoft/Bing Ads
    print("\n5. Microsoft/Bing Ads click tracking:")
    print("-" * 40)
    url5 = "https://example.com/?msclkid=MS123456789"
    result5 = webmetic_referrer(url5)
    print(f"URL: {url5}")
    print(f"Source: {result5['source']}")
    print(f"Medium: {result5['medium']}")
    print(f"Click ID: {result5.get('click_id')}")
    print(f"Click ID Type: {result5.get('click_id_type')}")
    
    # Example 6: LinkedIn Ads
    print("\n6. LinkedIn Ads click tracking:")
    print("-" * 40)
    url6 = "https://example.com/?li_fat_id=LI123456789"
    result6 = webmetic_referrer(url6)
    print(f"URL: {url6}")
    print(f"Source: {result6['source']}")
    print(f"Medium: {result6['medium']}")
    print(f"Click ID: {result6.get('click_id')}")
    print(f"Click ID Type: {result6.get('click_id_type')}")
    
    # Example 7: TikTok Ads
    print("\n7. TikTok Ads click tracking:")
    print("-" * 40)
    url7 = "https://example.com/?ttclid=TT123456789"
    result7 = webmetic_referrer(url7)
    print(f"URL: {url7}")
    print(f"Source: {result7['source']}")
    print(f"Medium: {result7['medium']}")
    print(f"Click ID: {result7.get('click_id')}")
    print(f"Click ID Type: {result7.get('click_id_type')}")
    
    # Example 8: UTM override with campaign ID
    print("\n8. UTM parameters override click ID inference (but campaign_id still extracted):")
    print("-" * 40)
    url8 = "https://example.com/?utm_source=newsletter&utm_medium=email&gclid=GC123&gad_campaignid=555"
    result8 = webmetic_referrer(url8)
    print(f"URL: {url8}")
    print(f"Source: {result8['source']}")
    print(f"Medium: {result8['medium']}")
    print(f"Campaign ID: {result8.get('campaign_id')}")
    print(f"Click ID: {result8.get('click_id')}")
    print(f"Click ID Type: {result8.get('click_id_type')}")
    print("Note: UTM parameters override automatic source/medium detection")
    
    # Example 9: Complete Google Ads tracking
    print("\n9. Complete Google Ads tracking with all parameters:")
    print("-" * 40)
    url9 = "https://example.com/?utm_source=google&utm_medium=cpc&utm_campaign=summer_sale&gclid=ABC123&gad_source=1&gad_campaignid=22633883708&gclsrc=aw.ds"
    result9 = webmetic_referrer(url9)
    print(f"URL: {url9}")
    print(f"Source: {result9['source']}")
    print(f"Medium: {result9['medium']}")
    print(f"Campaign: {result9.get('campaign')}")
    print(f"Campaign ID: {result9.get('campaign_id')}")
    print(f"Click ID: {result9.get('click_id')}")
    print(f"Click ID Type: {result9.get('click_id_type')}")
    print(f"GAD Source: {result9.get('gad_source')}")
    print(f"GCL Source: {result9.get('gclsrc')}")
    
    print("\n" + "=" * 80)
    print("Demo complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()