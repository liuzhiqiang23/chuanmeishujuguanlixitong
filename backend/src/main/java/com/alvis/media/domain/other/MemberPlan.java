package com.alvis.media.domain.other;

import lombok.Data;

import java.io.Serializable;
import java.math.BigDecimal;
import java.math.RoundingMode;

/**
 * 会员套餐（不是数据库表，是写死在代码里的三档套餐）。
 * 价格放这里而不是建表，是因为套餐几乎不会变、也不参与库存/上下架逻辑。
 */
@Data
public class MemberPlan implements Serializable {

    private static final long serialVersionUID = 1L;

    /** 月数 */
    private Integer months;

    private String name;

    private BigDecimal price;

    /** 折算到每月的价格，前端展示用 */
    private BigDecimal pricePerMonth;

    private String desc;

    public MemberPlan(Integer months, String name, String price, String desc) {
        this.months = months;
        this.name = name;
        this.price = new BigDecimal(price);
        this.desc = desc;
        this.pricePerMonth = this.price.divide(new BigDecimal(months), 2, RoundingMode.HALF_UP);
    }
}
