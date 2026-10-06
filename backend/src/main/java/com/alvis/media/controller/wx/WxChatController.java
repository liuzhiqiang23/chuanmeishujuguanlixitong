package com.alvis.media.controller.wx;

import com.alvis.media.base.RestResponse;
import com.alvis.media.service.ChatService;
import com.alvis.media.viewmodel.chat.ChatReplyVM;
import com.alvis.media.viewmodel.chat.ChatRequestVM;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 小程序 AI 客服接口。
 *
 * 约定与其它 wx 接口一致：POST + JSON，返回 {code, message, response}，code === 1 成功。
 * /api/wx/** 在 security-ignore-urls 里，免登录态。
 */
@RestController("WxChatController")
@RequestMapping(value = "/api/wx")
@RequiredArgsConstructor
public class WxChatController {

    private final ChatService chatService;

    @PostMapping("/chat")
    public RestResponse<ChatReplyVM> chat(@RequestBody ChatRequestVM req) {
        if (req == null || req.getQuestion() == null || req.getQuestion().trim().isEmpty()) {
            return RestResponse.fail(400, "问题不能为空");
        }
        if (req.getQuestion().length() > 500) {
            return RestResponse.fail(400, "问题太长了，请控制在 500 字以内");
        }
        return RestResponse.ok(chatService.ask(req));
    }
}
