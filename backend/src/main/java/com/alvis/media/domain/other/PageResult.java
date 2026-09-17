package com.alvis.media.domain.other;

import lombok.Data;

import java.io.Serializable;
import java.util.List;

/**
 * 通用分页结果。没有用 PageHelper：那个是给 XML 里的查询用的，
 * 我这几个列表直接用 MyBatis-Plus 查，自己算 count + limit 更省事，
 * 也避免为分页再注册一个插件。
 */
@Data
public class PageResult<T> implements Serializable {

    private static final long serialVersionUID = 1L;

    private long total;

    private int pageIndex;

    private int pageSize;

    private List<T> list;

    public PageResult(long total, int pageIndex, int pageSize, List<T> list) {
        this.total = total;
        this.pageIndex = pageIndex;
        this.pageSize = pageSize;
        this.list = list;
    }
}
