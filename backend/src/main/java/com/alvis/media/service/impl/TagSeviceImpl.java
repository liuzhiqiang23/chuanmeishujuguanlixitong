package com.alvis.media.service.impl;

import com.alvis.media.domain.Tag;
import com.alvis.media.repository.TagMapper;
import com.alvis.media.service.TagService;
import com.baomidou.mybatisplus.spring.service.impl.ServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class TagSeviceImpl extends ServiceImpl<TagMapper, Tag> implements TagService {

    @Autowired
    private TagMapper tagMapper;

        //查询全部
    public List <Tag> queryAll() {
        return tagMapper.selectList(null);
    }
}
