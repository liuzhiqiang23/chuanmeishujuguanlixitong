package com.alvis.media.service;

import com.alvis.media.domain.Member;
import com.alvis.media.domain.other.MemberPlan;

import java.math.BigDecimal;
import java.util.List;

/**
 * 会员：套餐、开卡/续费、会员状态。
 */
public interface MemberService {

    /** 三档套餐（写死在实现类里） */
    List<MemberPlan> plans();

    /** 按购买月数取套餐，取不到返回 null */
    MemberPlan planOf(Integer months);

    /** 当前用户是不是有效会员（没开过卡 / 已过期都算不是） */
    boolean isMember(Integer userId);

    /** 取有效会员记录，不是会员返回 null */
    Member getValidMember(Integer userId);

    /** 会员买影片的折扣率，例如 0.8 表示 8 折 */
    BigDecimal discountRate();

    /**
     * 开通或续费。已经是会员就从原到期时间往后延，否则从今天算起。
     *
     * @return 续费后的会员记录
     */
    Member openOrRenew(Integer userId, Integer months);
}
