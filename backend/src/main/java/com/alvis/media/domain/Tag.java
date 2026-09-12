package com.alvis.media.domain;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode
@TableName("t_tag")
public class Tag {

    @TableId(value = "tag_Id", type = IdType.AUTO)
    private Integer tagId;

    private String tagName;


}