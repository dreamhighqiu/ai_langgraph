package com.deepseek.tests.utils;

import java.util.Arrays;
import java.util.List;

public class TestData {
    public static final String BASE_URL = "https://www.deepseek.com/";
    public static final String ENGLISH_URL = "https://www.deepseek.com/en/";
    public static final String CHAT_URL = "https://chat.deepseek.com";
    public static final String PLATFORM_URL = "https://platform.deepseek.com";
    
    public static final String EXPECTED_TITLE_ZH = "DeepSeek | 深度求索";
    public static final String EXPECTED_TITLE_EN = "DeepSeek";
    
    public static final List<String> SOCIAL_MEDIA_PLATFORMS = Arrays.asList(
        "github.com",
        "twitter.com",
        "zhihu.com",
        "xiaohongshu.com"
    );
    
    public static final List<String> FOOTER_SECTIONS_ZH = Arrays.asList(
        "研究",
        "产品", 
        "法律 & 安全",
        "加入我们"
    );
    
    public static final List<String> FOOTER_SECTIONS_EN = Arrays.asList(
        "Research",
        "Product", 
        "Legal & Safety",
        "Join Us"
    );
    
    public static final List<String> LEGAL_LINKS_ZH = Arrays.asList(
        "隐私政策",
        "用户协议",
        "反馈安全漏洞"
    );
    
    public static final List<String> LEGAL_LINKS_EN = Arrays.asList(
        "Privacy Policy",
        "Terms of Use",
        "Report Vulnerabilities"
    );
    
    public static final List<String> MAIN_BUTTONS_ZH = Arrays.asList(
        "开始对话",
        "API开放平台"
    );
    
    public static final List<String> MAIN_BUTTONS_EN = Arrays.asList(
        "Start Now",
        "Access API"
    );
    
    public static final String COMPANY_COPYRIGHT_ZH = "© 2025 杭州深度求索人工智能基础技术研究有限公司 版权所有";
    public static final String COMPANY_COPYRIGHT_EN = "© 2025 DeepSeek. All rights reserved.";
    
    public static final String ICP_NUMBER = "浙ICP备2023025841号";
    public static final String PUBLIC_SECURITY_NUMBER = "浙公网安备33010502011812号";
    
    public static final String SERVICE_EMAIL = "service@deepseek.com";
    public static final String SECURITY_EMAIL = "security@deepseek.com";
}