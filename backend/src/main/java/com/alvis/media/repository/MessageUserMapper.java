package com.alvis.media.repository;

import com.alvis.media.domain.MessageUser;
import com.alvis.media.viewmodel.student.user.MessageRequestVM;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

@Mapper
public interface MessageUserMapper extends MediaBaseMapper <MessageUser> {
    int deleteByPrimaryKey(Integer id);

    int insert(MessageUser record);

    int insertSelective(MessageUser record);

    MessageUser selectByPrimaryKey(Integer id);

    int updateByPrimaryKeySelective(MessageUser record);

    int updateByPrimaryKey(MessageUser record);

    List<MessageUser> selectByMessageIds(List<Integer> ids);

    int inserts(List<MessageUser> list);

    List<MessageUser> studentPage(MessageRequestVM requestVM);

    Integer unReadCount(Integer userId);
}
