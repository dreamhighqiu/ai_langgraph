package com.example.helper;

import com.example.pageobject.DeepSeekChatPage;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.assertions.PlaywrightAssertions;
import static org.junit.jupiter.api.Assertions.*;

/**
 * DeepSeek聊天页面Helper类
 * 封装业务逻辑和复杂操作
 */
public class DeepSeekChatHelper {
    
    private final DeepSeekChatPage deepSeekChatPage;
    private final Page page;
    
    // 常量定义
    private static final int TIMEOUT_SECONDS = 15;
    private static final String TEST_MESSAGE = "你好，请介绍一下你自己";
    private static final String LONG_TEST_MESSAGE = "这是一个测试消息，用于验证系统是否能正确处理较长的文本输入。"
            + "我们需要确保当用户输入大量文本时，系统仍然能够正常工作并给出合理的响应。"
            + "这个测试消息包含了多个句子，模拟真实用户可能输入的内容。"
            + "我们希望验证系统的稳定性和可靠性。";
    
    public DeepSeekChatHelper(Page page) {
        this.page = page;
        this.deepSeekChatPage = new DeepSeekChatPage(page);
    }
    
    /**
     * 打开DeepSeek聊天页面并验证基础功能
     */
    public void openAndVerifyPage() {
        // 导航到页面
        deepSeekChatPage.navigate();
        
        // 等待页面加载
        deepSeekChatPage.waitForPageLoad();
        
        // 验证页面基础元素
        assertTrue(deepSeekChatPage.isPageLoaded(), "页面未正确加载");
        PlaywrightAssertions.assertThat(deepSeekChatPage.getPageTitle())
            .contains("DeepSeek");
    }
    
    /**
     * 执行基础聊天流程测试
     */
    public void testBasicChatFlow() {
        // 输入测试消息
        deepSeekChatPage.typeMessage(TEST_MESSAGE);
        
        // 验证输入框内容
        assertEquals(TEST_MESSAGE, page.getByRole(com.microsoft.playwright.options.AriaRole.TEXTBOX, 
            new Page.GetByRoleOptions().setName("给 DeepSeek 发送消息")).inputValue(),
            "消息输入框内容不正确");
        
        // 发送消息
        deepSeekChatPage.sendMessageByEnter();
        
        // 等待AI回复
        deepSeekChatPage.waitForAiResponse();
        
        // 验证AI回复包含关键词
        String response = deepSeekChatPage.getAiResponseText();
        assertNotNull(response, "AI回复为空");
        assertTrue(response.contains("DeepSeek") || response.contains("AI") || 
                   response.contains("助手"), "AI回复内容不符合预期");
    }
    
    /**
     * 测试新建对话功能
     */
    public void testNewChatFunction() {
        // 记录当前对话状态
        String initialUrl = deepSeekChatPage.getPageUrl();
        
        // 点击新建对话按钮
        deepSeekChatPage.clickNewChat();
        
        // 等待页面更新
        page.waitForURL(url -> !url.equals(initialUrl));
        
        // 验证输入框已清空
        assertTrue(deepSeekChatPage.isMessageInputEmpty(), "新建对话后输入框未清空");
        
        // 验证URL已更新（新对话应有新ID）
        String newUrl = deepSeekChatPage.getPageUrl();
        assertNotEquals(initialUrl, newUrl, "新建对话后URL未更新");
    }
    
    /**
     * 测试深度思考功能
     */
    public void testDeepThinkingFunction() {
        // 初始状态验证
        assertFalse(deepSeekChatPage.isDeepThinkingActive(), "深度思考初始状态应为未激活");
        
        // 激活深度思考
        deepSeekChatPage.toggleDeepThinking();
        
        // 验证按钮状态
        assertTrue(deepSeekChatPage.isDeepThinkingActive(), "深度思考激活后状态不正确");
        
        // 发送测试消息
        deepSeekChatPage.typeMessage("请详细解释一下人工智能");
        deepSeekChatPage.sendMessageByEnter();
        
        // 等待回复
        deepSeekChatPage.waitForAiResponse();
        
        // 验证回复质量（深度思考应有更详细的回复）
        String response = deepSeekChatPage.getAiResponseText();
        assertTrue(response.length() > 100, "深度思考模式下的回复可能不够详细");
        
        // 关闭深度思考
        deepSeekChatPage.toggleDeepThinking();
        assertFalse(deepSeekChatPage.isDeepThinkingActive(), "深度思考关闭后状态不正确");
    }
    
    /**
     * 测试联网搜索功能
     */
    public void testWebSearchFunction() {
        // 初始状态验证
        assertFalse(deepSeekChatPage.isWebSearchActive(), "联网搜索初始状态应为未激活");
        
        // 激活联网搜索
        deepSeekChatPage.toggleWebSearch();
        
        // 验证按钮状态
        assertTrue(deepSeekChatPage.isWebSearchActive(), "联网搜索激活后状态不正确");
        
        // 发送需要实时信息的问题
        deepSeekChatPage.typeMessage("今天北京的天气怎么样？");
        deepSeekChatPage.sendMessageByEnter();
        
        // 等待回复
        deepSeekChatPage.waitForAiResponse();
        
        // 验证回复可能包含网络相关信息
        String response = deepSeekChatPage.getAiResponseText();
        // 注意：实际测试中可能需要根据具体回复内容调整断言
        
        // 关闭联网搜索
        deepSeekChatPage.toggleWebSearch();
        assertFalse(deepSeekChatPage.isWebSearchActive(), "联网搜索关闭后状态不正确");
    }
    
    /**
     * 测试文件上传功能
     */
    public void testFileUploadFunction() {
        // 点击文件上传按钮（会触发文件选择器）
        deepSeekChatPage.clickFileUpload();
        
        // 注意：实际文件上传需要在测试中处理文件选择器
        // 这里主要验证按钮点击功能正常
        // 文件上传的具体测试需要在测试用例中实现
    }
    
    /**
     * 测试消息操作功能（复制、重新生成）
     */
    public void testMessageOperations() {
        // 先进行一次聊天获取AI回复
        deepSeekChatPage.typeMessage("简单的测试问题");
        deepSeekChatPage.sendMessageByEnter();
        deepSeekChatPage.waitForAiResponse();
        
        // 验证复制按钮可见（可能需要鼠标悬停）
        // 实际测试中可能需要先触发hover事件
        
        // 验证重新生成按钮功能
        // 实际测试中需要点击并验证新回复生成
    }
    
    /**
     * 测试边界值 - 超长消息
     */
    public void testLongMessage() {
        // 输入超长消息
        deepSeekChatPage.typeMessage(LONG_TEST_MESSAGE);
        
        // 验证输入成功
        String inputValue = page.getByRole(com.microsoft.playwright.options.AriaRole.TEXTBOX, 
            new Page.GetByRoleOptions().setName("给 DeepSeek 发送消息")).inputValue();
        assertTrue(inputValue.length() >= LONG_TEST_MESSAGE.length(), 
            "超长消息输入不完整");
        
        // 发送消息
        deepSeekChatPage.sendMessageByEnter();
        
        // 等待回复
        deepSeekChatPage.waitForAiResponse();
        
        // 验证收到回复
        String response = deepSeekChatPage.getAiResponseText();
        assertNotNull(response, "超长消息未收到回复");
        assertFalse(response.isEmpty(), "超长消息回复为空");
    }
    
    /**
     * 测试边界值 - 空消息
     */
    public void testEmptyMessage() {
        // 确保输入框为空
        deepSeekChatPage.clearMessageInput();
        
        // 尝试发送空消息
        deepSeekChatPage.sendMessageByEnter();
        
        // 验证输入框仍然为空且保持焦点
        assertTrue(deepSeekChatPage.isMessageInputEmpty(), "空消息发送后输入框状态异常");
        
        // 可以添加延迟验证没有新消息产生
        // 实际测试中可能需要监控网络请求或消息列表
    }
    
    /**
     * 测试特殊字符处理
     */
    public void testSpecialCharacters() {
        String specialMessage = "测试特殊字符：!@#$%^&*()_+-=[]{}|;':\",./<>?`~";
        
        deepSeekChatPage.typeMessage(specialMessage);
        deepSeekChatPage.sendMessageByEnter();
        
        deepSeekChatPage.waitForAiResponse();
        String response = deepSeekChatPage.getAiResponseText();
        assertNotNull(response, "特殊字符消息未收到回复");
    }
    
    /**
     * 测试快速连续发送
     */
    public void testQuickConsecutiveMessages() {
        String[] messages = {
            "第一条消息",
            "第二条消息",
            "第三条消息"
        };
        
        for (String message : messages) {
            deepSeekChatPage.typeMessage(message);
            deepSeekChatPage.sendMessageByEnter();
            
            // 短暂等待，避免请求过于密集
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        
        // 等待最后一个回复
        deepSeekChatPage.waitForAiResponse();
        
        // 验证收到了回复
        String response = deepSeekChatPage.getAiResponseText();
        assertNotNull(response, "连续消息未收到回复");
    }
    
    /**
     * 获取页面对象（供测试类使用）
     */
    public DeepSeekChatPage getPageObject() {
        return deepSeekChatPage;
    }
    
    /**
     * 获取Playwright Page对象
     */
    public Page getPlaywrightPage() {
        return page;
    }
}