package com.alvis.media.service.impl;

import com.alvis.media.domain.Order;
import com.alvis.media.domain.OrderItem;
import com.alvis.media.domain.UserCoupon;
import com.alvis.media.domain.VideoInfo;
import com.alvis.media.domain.other.MemberPlan;
import com.alvis.media.domain.other.OrderPreview;
import com.alvis.media.domain.other.PageResult;
import com.alvis.media.repository.OrderItemMapper;
import com.alvis.media.repository.OrderMapper;
import com.alvis.media.service.CouponService;
import com.alvis.media.service.MemberService;
import com.alvis.media.service.OrderService;
import com.alvis.media.service.VideoInfoService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

/**
 * 订单实现。价格规则：
 *   影片单价按评分定档（>=8.5 → 12 元，>=7.5 → 9 元，其余 6 元）；
 *   有效会员买影片打 8 折；买会员套餐本身不再打折（否则套娃）；
 *   券在会员价基础上再抵扣，实付不会小于 0。
 *
 * 演示版「下单即支付成功」（status 直接置为已支付）。
 * 正式接微信支付要拆成：下单落「待支付」→ 调统一下单拿 prepay_id →
 * 支付回调里验签并置「已支付」→ 再走开卡/发券。这两处的注释都标了位置。
 */
@Service
@AllArgsConstructor
public class OrderServiceImpl implements OrderService {

    private final OrderMapper orderMapper;

    private final OrderItemMapper orderItemMapper;

    private final VideoInfoService videoInfoService;

    private final MemberService memberService;

    private final CouponService couponService;

    @Override
    public OrderPreview previewVideo(Integer userId, Integer videoId) {
        VideoInfo video = videoInfoService.selectById(videoId);
        if (video == null) {
            throw new IllegalArgumentException("影片不存在");
        }
        return buildPreview(userId, Order.TYPE_VIDEO, videoId,
                video.getVideoName() + " 观影券", videoPrice(video.getVoteAverage()));
    }

    @Override
    public OrderPreview previewMember(Integer userId, Integer months) {
        MemberPlan plan = memberService.planOf(months);
        if (plan == null) {
            throw new IllegalArgumentException("没有这个会员套餐");
        }
        return buildPreview(userId, Order.TYPE_MEMBER, months, "会员" + plan.getName(), plan.getPrice());
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Order createVideoOrder(Integer userId, Integer videoId, Integer userCouponId) {
        VideoInfo video = videoInfoService.selectById(videoId);
        if (video == null) {
            throw new IllegalArgumentException("影片不存在");
        }
        return doCreate(userId, Order.TYPE_VIDEO, videoId,
                video.getVideoName() + " 观影券", videoPrice(video.getVoteAverage()), userCouponId);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Order createMemberOrder(Integer userId, Integer months, Integer userCouponId) {
        MemberPlan plan = memberService.planOf(months);
        if (plan == null) {
            throw new IllegalArgumentException("没有这个会员套餐");
        }
        Order order = doCreate(userId, Order.TYPE_MEMBER, months,
                "会员" + plan.getName(), plan.getPrice(), userCouponId);
        // 正式接支付时，开卡要挪到支付成功回调里，不能在下单时就开
        memberService.openOrRenew(userId, months);
        return order;
    }

    @Override
    public PageResult<Order> page(Integer userId, Integer pageIndex, Integer pageSize) {
        int index = (pageIndex == null || pageIndex < 1) ? 1 : pageIndex;
        int size = (pageSize == null || pageSize < 1) ? 10 : Math.min(pageSize, 50);
        // 没用 PageHelper：那是给 XML 查询用的，还要注册插件。这里自己算偏移更省事，
        // 注意 limit 拼的是两个已校验过的整数，不接受外部字符串。
        List<Order> list = orderMapper.selectList(new LambdaQueryWrapper<Order>()
                .eq(Order::getUserId, userId)
                .orderByDesc(Order::getCreateTime)
                .last("limit " + ((index - 1) * size) + "," + size));
        Long total = orderMapper.selectCount(new LambdaQueryWrapper<Order>().eq(Order::getUserId, userId));
        return new PageResult<>(total == null ? 0L : total, index, size, list);
    }

    @Override
    public Order getOwned(Integer userId, String orderNo) {
        Order order = orderMapper.selectOne(new LambdaQueryWrapper<Order>().eq(Order::getOrderNo, orderNo));
        if (order == null) {
            throw new IllegalArgumentException("订单不存在");
        }
        if (!userId.equals(order.getUserId())) {
            throw new IllegalArgumentException("这不是你的订单");
        }
        return order;
    }

    @Override
    public List<OrderItem> itemsOf(String orderNo) {
        return orderItemMapper.selectList(new LambdaQueryWrapper<OrderItem>().eq(OrderItem::getOrderNo, orderNo));
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Order cancel(Integer userId, String orderNo) {
        Order order = getOwned(userId, orderNo);
        if (order.getStatus() != null && order.getStatus() == Order.STATUS_CANCELED) {
            throw new IllegalArgumentException("订单已经取消过了");
        }
        if (order.getOrderType() != null && order.getOrderType() == Order.TYPE_MEMBER) {
            // 会员已经生效了，撤销要连带回收会员权益，演示版先不做
            throw new IllegalArgumentException("会员订单不支持取消（会员已生效）");
        }
        order.setStatus(Order.STATUS_CANCELED);
        orderMapper.updateById(order);
        couponService.restoreByOrderNo(orderNo);
        return order;
    }

    private OrderPreview buildPreview(Integer userId, int type, Integer itemId, String itemName, BigDecimal original) {
        OrderPreview preview = new OrderPreview();
        preview.setItemType(type);
        preview.setItemId(itemId);
        preview.setItemName(itemName);
        preview.setOriginalPrice(original);

        boolean member = memberService.isMember(userId);
        preview.setMember(member);
        BigDecimal afterMember = original;
        BigDecimal memberDiscount = BigDecimal.ZERO;
        if (member && type == Order.TYPE_VIDEO) {
            afterMember = applyMemberRate(original);
            memberDiscount = original.subtract(afterMember);
        }
        preview.setMemberDiscount(memberDiscount);
        preview.setPriceAfterMember(afterMember);

        List<UserCoupon> usable = couponService.usableFor(userId, afterMember);
        preview.setUsableCoupons(usable);
        BigDecimal best = BigDecimal.ZERO;
        for (UserCoupon uc : usable) {
            BigDecimal discount = uc.getAmount() == null ? BigDecimal.ZERO : uc.getAmount();
            if (discount.compareTo(afterMember) > 0) {
                discount = afterMember;
            }
            if (discount.compareTo(best) > 0) {
                best = discount;
            }
        }
        preview.setBestCouponDiscount(best);
        return preview;
    }

    private Order doCreate(Integer userId, int type, Integer itemId, String title,
                           BigDecimal original, Integer userCouponId) {
        BigDecimal afterMember = original;
        if (type == Order.TYPE_VIDEO && memberService.isMember(userId)) {
            afterMember = applyMemberRate(original);
        }
        BigDecimal memberDiscount = original.subtract(afterMember);

        String orderNo = nextOrderNo();
        BigDecimal couponDiscount = couponService.useForOrder(userId, userCouponId, afterMember, orderNo);
        BigDecimal payAmount = afterMember.subtract(couponDiscount);
        if (payAmount.compareTo(BigDecimal.ZERO) < 0) {
            payAmount = BigDecimal.ZERO;
        }

        Date now = new Date();
        Order order = new Order();
        order.setOrderNo(orderNo);
        order.setUserId(userId);
        order.setOrderType(type);
        order.setTitle(title);
        order.setTotalAmount(original);
        order.setDiscountAmount(memberDiscount.add(couponDiscount));
        order.setPayAmount(payAmount);
        order.setUserCouponId(userCouponId);
        // ↓↓↓ 演示版：落库即视为支付成功。接微信支付时这里要改成 STATUS_UNPAID
        order.setStatus(Order.STATUS_PAID);
        order.setCreateTime(now);
        order.setPayTime(now);
        orderMapper.insert(order);

        OrderItem item = new OrderItem();
        item.setOrderId(order.getId());
        item.setOrderNo(orderNo);
        item.setItemType(type);
        item.setItemId(itemId);
        item.setItemName(title);
        item.setUnitPrice(original);
        item.setQuantity(1);
        orderItemMapper.insert(item);
        return order;
    }

    /** 影片单价按评分定档 */
    private BigDecimal videoPrice(Double voteAverage) {
        if (voteAverage == null) {
            return new BigDecimal("6.00");
        }
        if (voteAverage >= 8.5) {
            return new BigDecimal("12.00");
        }
        if (voteAverage >= 7.5) {
            return new BigDecimal("9.00");
        }
        return new BigDecimal("6.00");
    }

    private BigDecimal applyMemberRate(BigDecimal price) {
        return price.multiply(memberService.discountRate()).setScale(2, RoundingMode.HALF_UP);
    }

    private String nextOrderNo() {
        String time = new SimpleDateFormat("yyyyMMddHHmmss").format(new Date());
        return "WX" + time + String.format("%04d", ThreadLocalRandom.current().nextInt(10000));
    }
}
