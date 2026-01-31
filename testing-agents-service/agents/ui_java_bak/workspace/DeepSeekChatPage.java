package com.example.pageobject;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;

/**
 * DeepSeek聊天页面PageObject类
 * 封装页面元素定位和基础操作
 */
public class DeepSeekChatPage {
    
    private final Page page;
    
    // 页面元素定位器
    private final Locator messageInput;
    private final Locator sendButton;
    private final Locator newChatButton;
    private final Locator deepThinkingButton;
    private final Locator webSearchButton;
    private final Locator fileUploadButton;
    private final Locator voiceInputButton;
    private final Locator chatHistoryList;
    private final Locator aiResponseArea;
    private final Locator copyMessageButton;
    private final Locator regenerateButton;
    
    // 页面常量
    private static final String PAGE_URL = "https://chat.deepseek.com/";
    private static final String PAGE_TITLE = "DeepSeek";
    private static final int TIMEOUT_SECONDS = 15;
    
    public DeepSeekChatPage(Page page) {
        this.page = page;
        
        // 初始化元素定位器
        this.messageInput = page.getByRole(AriaRole.TEXTBOX, 
            new Page.GetByRoleOptions().setName("给 DeepSeek 发送消息"));
        
        this.sendButton = page.locator("button[type='submit']");
        
        this.newChatButton = page.getByText("开启新对话");
        
        this.deepThinkingButton = page.getByRole(AriaRole.BUTTON, 
            new Page.GetByRoleOptions().setName("深度思考"));
        
        this.webSearchButton = page.getByRole(AriaRole.BUTTON, 
            new Page.GetByRoleOptions().setName("联网搜索"));
        
        this.fileUploadButton = page.locator("button").filter(new Locator.FilterOptions()
            .setHas(page.locator("img[alt*='上传']")));
        
        this.voiceInputButton = page.locator("button").filter(new Locator.FilterOptions()
            .setHas(page.locator("img[alt*='语音']")));
        
        this.chatHistoryList = page.locator("[data-testid='chat-history-list']");
        
        this.aiResponseArea = page.locator("[data-testid='ai-response']");
        
        this.copyMessageButton = page.locator("button").filter(new Locator.FilterOptions()
            .setHasText("复制"));
        
        this.regenerateButton = page.locator("button").filter(new Locator.FilterOptions()
            .setHasText("重新生成"));
    }
    
    /**
     * 导航到DeepSeek聊天页面
     */
    public void navigate() {
        page.navigate(PAGE_URL);
        page.waitForLoadState();
    }
    
    /**
     * 验证页面是否成功加载
     */
    public boolean isPageLoaded() {
        return page.title().contains(PAGE_TITLE) && 
               messageInput.isVisible();
    }
    
    /**
     * 输入消息文本
     */
    public void typeMessage(String message) {
        messageInput.fill(message);
    }
    
    /**
     * 发送消息（按Enter键）
     */
    public void sendMessageByEnter() {
        messageInput.press("Enter");
    }
    
    /**
     * 发送消息（点击发送按钮）
     */
    public void sendMessageByButton() {
        sendButton.click();
    }
    
    /**
     * 点击新建对话按钮
     */
    public void clickNewChat() {
        newChatButton.click();
    }
    
    /**
     * 切换深度思考模式
     */
    public void toggleDeepThinking() {
        deepThinkingButton.click();
    }
    
    /**
     * 切换联网搜索模式
     */
    public void toggleWebSearch() {
        webSearchButton.click();
    }
    
    /**
     * 点击文件上传按钮
     */
    public void clickFileUpload() {
        fileUploadButton.click();
    }
    
    /**
     * 点击语音输入按钮
     */
    public void clickVoiceInput() {
        voiceInputButton.click();
    }
    
    /**
     * 获取AI回复文本
     */
    public String getAiResponseText() {
        return aiResponseArea.textContent();
    }
    
    /**
     * 等待AI回复
     */
    public void waitForAiResponse() {
        aiResponseArea.waitFor(new Locator.WaitForOptions()
            .setTimeout(TIMEOUT_SECONDS * 1000));
    }
    
    /**
     * 复制AI回复消息
     */
    public void copyAiResponse() {
        copyMessageButton.click();
    }
    
    /**
     * 重新生成AI回复
     */
    public void regenerateAiResponse() {
        regenerateButton.click();
    }
    
    /**
     * 切换到指定历史对话
     */
    public void switchToHistoryChat(String chatTitle) {
        page.getByRole(AriaRole.LINK, 
            new Page.GetByRoleOptions().setName(chatTitle)).click();
    }
    
    /**
     * 获取当前对话标题
     */
    public String getCurrentChatTitle() {
        return page.locator("[data-testid='chat-title']").textContent();
    }
    
    /**
     * 验证深度思考按钮是否激活
     */
    public boolean isDeepThinkingActive() {
        return deepThinkingButton.getAttribute("aria-pressed") != null &&
               deepThinkingButton.getAttribute("aria-pressed").equals("true");
    }
    
    /**
     * 验证联网搜索按钮是否激活
     */
    public boolean isWebSearchActive() {
        return webSearchButton.getAttribute("aria-pressed") != null &&
               webSearchButton.getAttribute("aria-pressed").equals("true");
    }
    
    /**
     * 验证消息输入框是否为空
     */
    public boolean isMessageInputEmpty() {
        return messageInput.inputValue().isEmpty();
    }
    
    /**
     * 清空消息输入框
     */
    public void clearMessageInput() {
        messageInput.fill("");
    }
    
    /**
     * 获取页面URL
     */
    public String getPageUrl() {
        return page.url();
    }
    
    /**
     * 获取页面标题
     */
    public String getPageTitle() {
        return page.title();
    }
    
    /**
     * 等待页面加载完成
     */
    public void waitForPageLoad() {
        page.waitForURL(url -> url.contains("chat.deepseek.com"));
    }
}