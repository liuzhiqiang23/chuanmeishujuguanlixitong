package com.alvis.media.service;

import com.alvis.media.viewmodel.chat.ChatRequestVM;
import com.alvis.media.viewmodel.chat.ChatReplyVM;

/**
 * 小程序 AI 客服：私有知识检索 + GLM 生成。
 *
 * 路线是 RAG 而不是微调：知识 = t_chat_faq（运营规则）+ t_movie（影片数据），
 * 每次先检索再把资料拼进 prompt，模型只负责组织语言，改知识改表即可、无需重训。
 */
public interface ChatService {

    ChatReplyVM ask(ChatRequestVM req);
}
