"""Tests for Google Ads campaign ID and modern tracking parameters."""

import pytest
from utm_referrer_parser import webmetic_referrer


class TestGoogleAdsCampaignTracking:
    """Tests for Google Ads campaign ID extraction and tracking parameters."""
    
    def test_gad_campaignid_extraction(self):
        """Test extraction of gad_campaignid as campaign_id."""
        result = webmetic_referrer(
            url="https://example.com/?gad_source=1&gad_campaignid=22633883708&gclid=ABC123"
        )
        
        assert result['source'] == 'google'
        assert result['medium'] == 'cpc'
        assert result['campaign_id'] == '22633883708'
        assert result['click_id'] == 'ABC123'
        assert result['click_id_type'] == 'gclid'
        assert result['gad_source'] == '1'
        assert result['gad_campaignid'] == '22633883708'
    
    def test_gad_parameters_without_gclid(self):
        """Test Google Ads parameters without gclid."""
        result = webmetic_referrer(
            url="https://example.com/?gad_source=1&gad_campaignid=12345"
        )
        
        # Should still recognize as Google traffic
        assert result['source'] == 'google'
        assert result['medium'] == 'cpc'
        assert result['campaign_id'] == '12345'
        assert result['gad_source'] == '1'
        assert result.get('click_id') is None
        assert result.get('click_id_type') is None
    
    def test_gbraid_click_id(self):
        """Test gbraid as click_id with proper type."""
        result = webmetic_referrer(
            url="https://example.com/?gbraid=GB123456&gad_campaignid=789"
        )
        
        assert result['source'] == 'google'
        assert result['medium'] == 'cpc'
        assert result['click_id'] == 'GB123456'
        assert result['click_id_type'] == 'gbraid'
        assert result['campaign_id'] == '789'
    
    def test_wbraid_click_id(self):
        """Test wbraid as click_id with proper type."""
        result = webmetic_referrer(
            url="https://example.com/?wbraid=WB789012"
        )
        
        assert result['source'] == 'google'
        assert result['medium'] == 'cpc'
        assert result['click_id'] == 'WB789012'
        assert result['click_id_type'] == 'wbraid'
    
    def test_click_id_priority_gclid_first(self):
        """Test that gclid has highest priority among Google click IDs."""
        result = webmetic_referrer(
            url="https://example.com/?gclid=GC111&gbraid=GB222&wbraid=WB333"
        )
        
        # gclid should be chosen
        assert result['click_id'] == 'GC111'
        assert result['click_id_type'] == 'gclid'
        assert result['source'] == 'google'
        assert result['medium'] == 'cpc'
    
    def test_click_id_priority_gbraid_over_wbraid(self):
        """Test that gbraid has priority over wbraid when no gclid."""
        result = webmetic_referrer(
            url="https://example.com/?gbraid=GB222&wbraid=WB333"
        )
        
        # gbraid should be chosen
        assert result['click_id'] == 'GB222'
        assert result['click_id_type'] == 'gbraid'
    
    def test_platform_click_id_priority(self):
        """Test priority of platform-specific click IDs."""
        result = webmetic_referrer(
            url="https://example.com/?fbclid=FB111&msclkid=MS222&ttclid=TT333"
        )
        
        # fbclid should be chosen (appears first in priority list)
        assert result['click_id'] == 'FB111'
        assert result['click_id_type'] == 'fbclid'
        # Attribution should be from first click ID found
        assert result['source'] == 'facebook'
        assert result['medium'] == 'cpc'
    
    def test_google_over_platform_priority(self):
        """Test that Google click IDs have priority over other platforms."""
        result = webmetic_referrer(
            url="https://example.com/?gclid=GC111&fbclid=FB222&msclkid=MS333"
        )
        
        # gclid should be chosen
        assert result['click_id'] == 'GC111'
        assert result['click_id_type'] == 'gclid'
        assert result['source'] == 'google'
        assert result['medium'] == 'cpc'
    
    def test_facebook_click_id(self):
        """Test Facebook click ID extraction."""
        result = webmetic_referrer(
            url="https://example.com/?fbclid=IwAR123456789"
        )
        
        assert result['source'] == 'facebook'
        assert result['medium'] == 'cpc'
        assert result['click_id'] == 'IwAR123456789'
        assert result['click_id_type'] == 'fbclid'
    
    def test_microsoft_click_id(self):
        """Test Microsoft/Bing click ID extraction."""
        result = webmetic_referrer(
            url="https://example.com/?msclkid=MS123456789"
        )
        
        assert result['source'] == 'bing'
        assert result['medium'] == 'cpc'
        assert result['click_id'] == 'MS123456789'
        assert result['click_id_type'] == 'msclkid'
    
    def test_tiktok_click_id(self):
        """Test TikTok click ID extraction."""
        result = webmetic_referrer(
            url="https://example.com/?ttclid=TT123456789"
        )
        
        assert result['source'] == 'twitter'  # Note: ttclid maps to twitter in current implementation
        assert result['medium'] == 'cpc'
        assert result['click_id'] == 'TT123456789'
        assert result['click_id_type'] == 'ttclid'
    
    def test_linkedin_click_id(self):
        """Test LinkedIn click ID extraction."""
        result = webmetic_referrer(
            url="https://example.com/?li_fat_id=LI123456789"
        )
        
        assert result['source'] == 'linkedin'
        assert result['medium'] == 'cpc'
        assert result['click_id'] == 'LI123456789'
        assert result['click_id_type'] == 'li_fat_id'
    
    def test_utm_override_with_campaign_id(self):
        """Test that UTM parameters override click ID inference but campaign_id is still extracted."""
        result = webmetic_referrer(
            url="https://example.com/?utm_source=newsletter&utm_medium=email&gclid=GC123&gad_campaignid=999"
        )
        
        # UTM should override attribution
        assert result['source'] == 'newsletter'
        assert result['medium'] == 'email'
        
        # But click ID and campaign ID should still be extracted
        assert result['click_id'] == 'GC123'
        assert result['click_id_type'] == 'gclid'
        assert result['campaign_id'] == '999'
    
    def test_complete_google_ads_tracking(self):
        """Test complete Google Ads tracking with all parameters."""
        result = webmetic_referrer(
            url="https://example.com/?utm_source=google&utm_medium=cpc&utm_campaign=summer_sale&gclid=ABC123&gad_source=1&gad_campaignid=22633883708&gclsrc=aw.ds"
        )
        
        # Core attribution
        assert result['source'] == 'google'
        assert result['medium'] == 'cpc'
        assert result['campaign'] == 'summer_sale'
        assert result['campaign_id'] == '22633883708'
        
        # Click tracking
        assert result['click_id'] == 'ABC123'
        assert result['click_id_type'] == 'gclid'
        
        # All Google Ads parameters
        assert result['gad_source'] == '1'
        assert result['gad_campaignid'] == '22633883708'
        assert result['gclsrc'] == 'aw.ds'
        
        # UTM parameters
        assert result['utm_source'] == 'google'
        assert result['utm_medium'] == 'cpc'
        assert result['utm_campaign'] == 'summer_sale'
    
    def test_backward_compatibility_utm(self):
        """Test backward compatibility with existing UTM extraction."""
        result = webmetic_referrer(
            url="https://example.com/?utm_source=google&utm_medium=organic&utm_campaign=brand"
        )
        
        assert result['source'] == 'google'
        assert result['medium'] == 'organic'
        assert result['campaign'] == 'brand'
        assert result['utm_source'] == 'google'
        assert result['utm_medium'] == 'organic'
        assert result['utm_campaign'] == 'brand'
        
        # No click IDs or campaign_id
        assert result.get('click_id') is None
        assert result.get('click_id_type') is None
        assert result.get('campaign_id') is None
    
    def test_no_campaign_id_when_missing(self):
        """Test that campaign_id is None when gad_campaignid is not present."""
        result = webmetic_referrer(
            url="https://example.com/?utm_source=facebook&fbclid=FB123"
        )
        
        assert result['source'] == 'facebook'
        assert result['click_id'] == 'FB123'
        assert result['click_id_type'] == 'fbclid'
        
        # campaign_id should not be in result when gad_campaignid is missing
        assert 'campaign_id' not in result or result['campaign_id'] is None
    
    def test_mixed_platforms_with_utm(self):
        """Test mixed platform parameters with UTM taking precedence."""
        result = webmetic_referrer(
            url="https://example.com/?utm_source=linkedin&utm_medium=social&fbclid=FB123&gad_campaignid=789"
        )
        
        # UTM should win for attribution
        assert result['source'] == 'linkedin'
        assert result['medium'] == 'social'
        
        # But we should still extract all parameters
        assert result['click_id'] == 'FB123'
        assert result['click_id_type'] == 'fbclid'
        assert result['campaign_id'] == '789'