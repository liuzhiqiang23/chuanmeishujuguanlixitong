package com.alvis.media.repository;

import com.alvis.media.domain.ChatFaq;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

/** AI 客服 FAQ 知识库。检索逻辑在 Service 里做（关键词打分），没有特殊 SQL 就不写 XML。 */
@Mapper
public interface ChatFaqMapper extends BaseMapper<ChatFaq> {
}
