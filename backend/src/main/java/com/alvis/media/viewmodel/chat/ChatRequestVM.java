package com.alvis.media.viewmodel.chat;

import lombok.Data;

/** /api/wx/chat 请求体 */
@Data
public class ChatRequestVM {

    /** 演示版身份：登录接口下发的 userId（与其它 wx 接口同一约定） */
    private Integer userId;

    /** 用户问题，1~500 字 */
    private String question;
}
