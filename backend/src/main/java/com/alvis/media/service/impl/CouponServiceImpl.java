package com.alvis.media.service.impl;

import com.alvis.media.domain.Coupon;
import com.alvis.media.domain.UserCoupon;
import com.alvis.media.repository.CouponMapper;
import com.alvis.media.repository.UserCouponMapper;
import com.alvis.media.service.CouponService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * 优惠券实现。规则：上架 + 有库存才能领；同一模板每人限领 1 张；
 * 核销要校验归属/状态/有效期/门槛；取消订单要把券退回。
 */
@Service
@AllArgsConstructor
public class CouponServiceImpl implements CouponService {

    private final CouponMapper couponMapper;

    private final UserCouponMapper userCouponMapper;

    @Override
    public List<Coupon> available(Integer userId) {
        List<Coupon> templates = couponMapper.selectList(new LambdaQueryWrapper<Coupon>()
                .eq(Coupon::getStatus, 1)
                .orderByAsc(Coupon::getThreshold));
        if (templates.isEmpty()) {
            return templates;
        }
        // 已经领过的模板 id，领过的就不再出现在"可领"列表里
        Set<Integer> received = new HashSet<>();
        for (UserCoupon uc : userCouponMapper.selectList(
                new LambdaQueryWrapper<UserCoupon>().eq(UserCoupon::getUserId, userId))) {
            received.add(uc.getCouponId());
        }
        List<Coupon> result = new ArrayList<>();
        for (Coupon template : templates) {
            if (received.contains(template.getId())) {
                continue;
            }
            // total_count = 0 表示不限量
            if (template.getTotalCount() != null && template.getTotalCount() > 0
                    && template.getReceivedCount() != null
                    && template.getReceivedCount() >= template.getTotalCount()) {
                continue;
            }
            result.add(template);
        }
        return result;
    }

    @Override
    public List<UserCoupon> mine(Integer userId, Integer status) {
        refreshExpired(userId);
        LambdaQueryWrapper<UserCoupon> wrapper = new LambdaQueryWrapper<UserCoupon>()
                .eq(UserCoupon::getUserId, userId)
                .orderByDesc(UserCoupon::getReceiveTime);
        if (status != null) {
            wrapper.eq(UserCoupon::getStatus, status);
        }
        return userCouponMapper.selectList(wrapper);
    }

    /**
     * 过期的券在读取时顺手改状态。省掉一个定时任务，
     * 代价是只有用户来查券时才发现过期——对演示够用了。
     */
    private void refreshExpired(Integer userId) {
        List<UserCoupon> unused = userCouponMapper.selectList(new LambdaQueryWrapper<UserCoupon>()
                .eq(UserCoupon::getUserId, userId)
                .eq(UserCoupon::getStatus, UserCoupon.STATUS_UNUSED));
        Date now = new Date();
        for (UserCoupon uc : unused) {
            if (uc.getExpireTime() != null && uc.getExpireTime().before(now)) {
                uc.setStatus(UserCoupon.STATUS_EXPIRED);
                userCouponMapper.updateById(uc);
            }
        }
    }

    @Override
    public UserCoupon receive(Integer userId, Integer couponId) {
        Coupon template = couponMapper.selectById(couponId);
        if (template == null || template.getStatus() == null || template.getStatus() != 1) {
            throw new IllegalArgumentException("这张券已经下架了");
        }
        if (template.getTotalCount() != null && template.getTotalCount() > 0
                && template.getReceivedCount() != null
                && template.getReceivedCount() >= template.getTotalCount()) {
            throw new IllegalArgumentException("这张券已经被领完了");
        }
        Long own = userCouponMapper.selectCount(new LambdaQueryWrapper<UserCoupon>()
                .eq(UserCoupon::getUserId, userId)
                .eq(UserCoupon::getCouponId, couponId));
        if (own != null && own > 0) {
            throw new IllegalArgumentException("这张券你已经领过了");
        }

        Date now = new Date();
        UserCoupon uc = new UserCoupon();
        uc.setUserId(userId);
        uc.setCouponId(couponId);
        // 抄一份快照：以后后台改券模板不影响用户手里已领的券
        uc.setTitle(template.getTitle());
        uc.setThreshold(template.getThreshold());
        uc.setAmount(template.getAmount());
        uc.setStatus(UserCoupon.STATUS_UNUSED);
        uc.setReceiveTime(now);
        uc.setExpireTime(plusDays(now, template.getValidDays() == null ? 7 : template.getValidDays()));
        userCouponMapper.insert(uc);

        template.setReceivedCount((template.getReceivedCount() == null ? 0 : template.getReceivedCount()) + 1);
        couponMapper.updateById(template);
        return uc;
    }

    @Override
    public List<UserCoupon> usableFor(Integer userId, BigDecimal orderAmount) {
        List<UserCoupon> result = new ArrayList<>();
        if (orderAmount == null) {
            return result;
        }
        for (UserCoupon uc : mine(userId, UserCoupon.STATUS_UNUSED)) {
            BigDecimal threshold = uc.getThreshold() == null ? BigDecimal.ZERO : uc.getThreshold();
            if (orderAmount.compareTo(threshold) >= 0) {
                result.add(uc);
            }
        }
        return result;
    }

    @Override
    public BigDecimal useForOrder(Integer userId, Integer userCouponId, BigDecimal orderAmount, String orderNo) {
        if (userCouponId == null) {
            return BigDecimal.ZERO;
        }
        UserCoupon uc = userCouponMapper.selectById(userCouponId);
        if (uc == null || !userId.equals(uc.getUserId())) {
            throw new IllegalArgumentException("这张券不属于当前用户");
        }
        if (uc.getStatus() == null || uc.getStatus() != UserCoupon.STATUS_UNUSED) {
            throw new IllegalArgumentException("这张券已经用过了");
        }
        if (uc.getExpireTime() != null && uc.getExpireTime().before(new Date())) {
            throw new IllegalArgumentException("这张券已经过期了");
        }
        BigDecimal threshold = uc.getThreshold() == null ? BigDecimal.ZERO : uc.getThreshold();
        if (orderAmount.compareTo(threshold) < 0) {
            throw new IllegalArgumentException("订单金额没到门槛，这张券要满 " + threshold + " 元才能用");
        }
        BigDecimal discount = uc.getAmount() == null ? BigDecimal.ZERO : uc.getAmount();
        if (discount.compareTo(orderAmount) > 0) {
            discount = orderAmount;
        }
        uc.setStatus(UserCoupon.STATUS_USED);
        uc.setUseTime(new Date());
        uc.setOrderNo(orderNo);
        userCouponMapper.updateById(uc);
        return discount;
    }

    @Override
    public void restoreByOrderNo(String orderNo) {
        // updateById 会忽略 null 字段（MP 默认 NOT_NULL 策略），
        // 要把 use_time / order_no 置空必须用 UpdateWrapper 的 set
        userCouponMapper.update(null, new LambdaUpdateWrapper<UserCoupon>()
                .eq(UserCoupon::getOrderNo, orderNo)
                .eq(UserCoupon::getStatus, UserCoupon.STATUS_USED)
                .set(UserCoupon::getStatus, UserCoupon.STATUS_UNUSED)
                .set(UserCoupon::getUseTime, null)
                .set(UserCoupon::getOrderNo, null));
    }

    private Date plusDays(Date base, int days) {
        Calendar calendar = Calendar.getInstance();
        calendar.setTime(base);
        calendar.add(Calendar.DAY_OF_MONTH, days);
        return calendar.getTime();
    }
}
