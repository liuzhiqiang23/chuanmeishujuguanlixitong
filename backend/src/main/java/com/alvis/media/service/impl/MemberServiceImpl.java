package com.alvis.media.service.impl;

import com.alvis.media.domain.Member;
import com.alvis.media.domain.other.MemberPlan;
import com.alvis.media.repository.MemberMapper;
import com.alvis.media.service.MemberService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

/**
 * 会员实现。三档套餐写死在代码里（见 MemberPlan 的注释）。
 */
@Service
@AllArgsConstructor
public class MemberServiceImpl implements MemberService {

    /** 会员买影片的折扣率：8 折 */
    private static final BigDecimal DISCOUNT_RATE = new BigDecimal("0.8");

    private static final List<MemberPlan> PLANS = new ArrayList<>();

    static {
        PLANS.add(new MemberPlan(1, "月卡", "15.00", "先试一个月"));
        PLANS.add(new MemberPlan(3, "季卡", "40.00", "折合每月 13.33 元"));
        PLANS.add(new MemberPlan(12, "年卡", "128.00", "折合每月 10.67 元，最划算"));
    }

    private final MemberMapper memberMapper;

    @Override
    public List<MemberPlan> plans() {
        return PLANS;
    }

    @Override
    public MemberPlan planOf(Integer months) {
        if (months == null) {
            return null;
        }
        for (MemberPlan plan : PLANS) {
            if (plan.getMonths().equals(months)) {
                return plan;
            }
        }
        return null;
    }

    @Override
    public boolean isMember(Integer userId) {
        return getValidMember(userId) != null;
    }

    @Override
    public Member getValidMember(Integer userId) {
        if (userId == null) {
            return null;
        }
        Member member = getRaw(userId);
        if (member == null || member.getExpireTime() == null) {
            return null;
        }
        return member.getExpireTime().after(new Date()) ? member : null;
    }

    @Override
    public BigDecimal discountRate() {
        return DISCOUNT_RATE;
    }

    @Override
    public Member openOrRenew(Integer userId, Integer months) {
        MemberPlan plan = planOf(months);
        if (plan == null) {
            throw new IllegalArgumentException("没有这个会员套餐：" + months + " 个月");
        }
        Date now = new Date();
        Member valid = getValidMember(userId);
        // 还有会员就从原到期日往后延，否则从今天算起
        Date base = valid != null ? valid.getExpireTime() : now;
        Date expire = addMonths(base, months);

        if (valid != null) {
            valid.setExpireTime(expire);
            valid.setUpdateTime(now);
            memberMapper.updateById(valid);
            return valid;
        }
        // 过期的老记录要先删掉，否则 t_member 上 user_id 的唯一索引会撞
        Member old = getRaw(userId);
        if (old != null) {
            memberMapper.deleteById(old.getId());
        }
        Member member = new Member();
        member.setUserId(userId);
        member.setLevel(1);
        member.setExpireTime(expire);
        member.setCreateTime(now);
        member.setUpdateTime(now);
        memberMapper.insert(member);
        return member;
    }

    private Member getRaw(Integer userId) {
        return memberMapper.selectOne(new LambdaQueryWrapper<Member>().eq(Member::getUserId, userId));
    }

    private Date addMonths(Date base, int months) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(base);
        calendar.add(Calendar.MONTH, months);
        return calendar.getTime();
    }
}
