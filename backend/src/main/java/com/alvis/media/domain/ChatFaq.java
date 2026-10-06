package com.alvis.media.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.util.Date;

/**
 * AI 客服 FAQ 知识库（t_chat_faq）。
 * 私有知识的「运营规则」部分：会员/券/订单等规则条目，命中后作为资料拼进 GLM 的 prompt。
 */
@Data
@EqualsAndHashCode
@TableName("t_chat_faq")
public class ChatFaq implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    /** 命中关键词，竖线分隔 */
    private String keywords;

    /** 标准问法 */
    private String question;

    /** 标准答案 */
    private String answer;

    private String category;

    /** 1 启用 0 停用 */
    private Integer enabled;

    /** 命中次数（观察高频问题用） */
    private Integer hit;

    private Date createdAt;

    private Date updatedAt;
}
