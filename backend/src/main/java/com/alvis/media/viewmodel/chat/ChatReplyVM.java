package com.alvis.media.viewmodel.chat;

import lombok.Data;

import java.util.List;

/** /api/wx/chat 应答 */
@Data
public class ChatReplyVM {

    /** 最终回答文案 */
    private String answer;

    /** glm=模型生成 faq=直接命中知识库 failed=服务暂不可用 */
    private String source;

    /** 引用的资料来源（给前端做「引用了xx条资料」提示） */
    private List<String> refs;

    /** 接口耗时毫秒 */
    private Integer costMs;

    /** 建议的追问（知识库里同分类的其它问法，最多3条；无则空） */
    private List<String> suggestions;
}
