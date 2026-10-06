package com.alvis.media.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.util.Date;

/**
 * AI 客服对话日志（t_chat_log）。每轮问答落一条，source 记录回答来源。
 */
@Data
@EqualsAndHashCode
@TableName("t_chat_log")
public class ChatLog implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    private Integer userId;

    private String question;

    private String answer;

    /** glm=模型生成 faq=直接命中兜底 failed=调用失败 */
    private String source;

    /** 引用了哪些资料（faq条目id/影片名），逗号分隔 */
    private String refs;

    /** 接口耗时毫秒 */
    private Integer costMs;

    private Date createdAt;
}
