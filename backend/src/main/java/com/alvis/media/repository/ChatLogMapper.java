package com.alvis.media.repository;

import com.alvis.media.domain.ChatLog;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;

/** AI 客服对话日志。 */
@Mapper
public interface ChatLogMapper extends BaseMapper<ChatLog> {
}
