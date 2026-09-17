package com.alvis.media.controller.wx;

import com.alvis.media.base.RestResponse;
import com.alvis.media.domain.Coupon;
import com.alvis.media.domain.Member;
import com.alvis.media.domain.Order;
import com.alvis.media.domain.OrderItem;
import com.alvis.media.domain.User;
import com.alvis.media.domain.UserCoupon;
import com.alvis.media.domain.other.MemberPlan;
import com.alvis.media.domain.other.OrderPreview;
import com.alvis.media.domain.other.PageResult;
import com.alvis.media.service.CouponService;
import com.alvis.media.service.MemberService;
import com.alvis.media.service.OrderService;
import com.alvis.media.service.UserService;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Date;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * 微信小程序商城的接口：登录 / 会员 / 优惠券 / 订单。
 *
 * 统一约定（跟项目其它接口一致）：
 *   POST + JSON 请求体，返回 {code, message, response}，**code === 1 才是成功**。
 *
 * 关于身份：演示版让前端把 userId 放在请求体里（登录接口会给）。
 * 正式接入微信时应该改成：登录换到 openid 后发一个 token，
 * 后续请求带 token，服务端从 token 解析用户——不要信客户端传来的 userId。
 */
@RestController("WxShopController")
@RequestMapping(value = "/api/wx")
@AllArgsConstructor
public class WxShopController {

    private final UserService userService;

    private final MemberService memberService;

    private final CouponService couponService;

    private final OrderService orderService;

    // ------------------------------------------------------------------
    // 登录
    // ------------------------------------------------------------------

    /**
     * 微信一键登录：前端 wx.login 拿到 code，调这里换 openid；
     * 第一次来就免注册建号，之后按 openid 认人。
     */
    @PostMapping("/login")
    public RestResponse<Map<String, Object>> login(@RequestBody(required = false) Map<String, Object> body) {
        Map<String, Object> req = body == null ? new HashMap<>() : body;
        String code = strOf(req, "code");
        String nickName = strOf(req, "nickName");

        // 正式流程在这里用 code 调微信 code2session 换 openid（需要小程序 appid + secret）。
        // 演示模式没有 appid，就用 code 派生一个稳定的 openid：
        // 同一个 code 反复登录会落到同一个账号，方便调试。
        String openid = "demo_openid_" + (code == null || code.isEmpty() ? "default" : code);

        User user = userService.selectByWxOpenId(openid);
        if (user == null) {
            user = registerByOpenid(openid, nickName);
        }

        Member member = memberService.getValidMember(user.getId());
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("userId", user.getId());
        data.put("userName", user.getUserName());
        data.put("nickName", user.getRealName());
        data.put("token", "demo-token-" + user.getId() + "-" + UUID.randomUUID().toString().substring(0, 8));
        data.put("isMember", member != null);
        data.put("memberExpireTime", member == null ? null : member.getExpireTime());
        return RestResponse.ok(data);
    }

    /** 免注册建号：只用 openid + 昵称，不设密码 */
    private User registerByOpenid(String openid, String nickName) {
        User user = new User();
        user.setUserUuid(UUID.randomUUID().toString());
        user.setUserName("wx_" + openid);
        user.setRealName(nickName == null || nickName.isEmpty() ? "微信用户" : nickName);
        user.setWxOpenId(openid);
        user.setRole(1);
        user.setStatus(1);
        user.setCreateTime(new Date());
        user.setDeleted(false);
        userService.insertUser(user);
        return user;
    }

    // ------------------------------------------------------------------
    // 会员
    // ------------------------------------------------------------------

    @PostMapping("/member/plans")
    public RestResponse<List<MemberPlan>> memberPlans() {
        return RestResponse.ok(memberService.plans());
    }

    @PostMapping("/member/info")
    public RestResponse<Map<String, Object>> memberInfo(@RequestBody Map<String, Object> body) {
        Integer userId = requireUserId(body);
        Member member = memberService.getValidMember(userId);
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("isMember", member != null);
        data.put("level", member == null ? null : member.getLevel());
        data.put("expireTime", member == null ? null : member.getExpireTime());
        data.put("discountRate", memberService.discountRate());
        data.put("plans", memberService.plans());
        return RestResponse.ok(data);
    }

    /**
     * 开通 / 续费会员。和普通下单一样走订单（可以叠加优惠券），
     * 演示版下单即支付成功，所以返回时会员已经生效。
     */
    @PostMapping("/member/open")
    public RestResponse<Map<String, Object>> memberOpen(@RequestBody Map<String, Object> body) {
        Integer userId = requireUserId(body);
        Integer months = intOf(body, "months");
        Order order = orderService.createMemberOrder(userId, months, intOf(body, "userCouponId"));
        Member member = memberService.getValidMember(userId);
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("orderNo", order.getOrderNo());
        data.put("payAmount", order.getPayAmount());
        data.put("discountAmount", order.getDiscountAmount());
        data.put("expireTime", member == null ? null : member.getExpireTime());
        return RestResponse.ok(data);
    }

    // ------------------------------------------------------------------
    // 优惠券
    // ------------------------------------------------------------------

    /** 可领的券 */
    @PostMapping("/coupon/list")
    public RestResponse<List<Coupon>> couponList(@RequestBody Map<String, Object> body) {
        return RestResponse.ok(couponService.available(requireUserId(body)));
    }

    @PostMapping("/coupon/receive")
    public RestResponse<UserCoupon> couponReceive(@RequestBody Map<String, Object> body) {
        Integer userId = requireUserId(body);
        Integer couponId = intOf(body, "couponId");
        if (couponId == null) {
            throw new IllegalArgumentException("缺少 couponId");
        }
        return RestResponse.ok(couponService.receive(userId, couponId));
    }

    /** 我的券。status 不传 = 全部，0 未使用 1 已使用 2 已过期 */
    @PostMapping("/coupon/mine")
    public RestResponse<List<UserCoupon>> couponMine(@RequestBody Map<String, Object> body) {
        Integer userId = requireUserId(body);
        return RestResponse.ok(couponService.mine(userId, intOf(body, "status")));
    }

    // ------------------------------------------------------------------
    // 订单
    // ------------------------------------------------------------------

    /**
     * 确认订单页：传 videoId 就是买影片观影券，传 months 就是买会员套餐。
     * 返回价格明细（原价/会员折扣/券后价）和这张单能用的券。
     */
    @PostMapping("/order/preview")
    public RestResponse<OrderPreview> orderPreview(@RequestBody Map<String, Object> body) {
        Integer userId = requireUserId(body);
        Integer videoId = intOf(body, "videoId");
        Integer months = intOf(body, "months");
        if (videoId != null) {
            return RestResponse.ok(orderService.previewVideo(userId, videoId));
        }
        if (months != null) {
            return RestResponse.ok(orderService.previewMember(userId, months));
        }
        throw new IllegalArgumentException("要传 videoId（买影片）或 months（买会员）");
    }

    @PostMapping("/order/create")
    public RestResponse<Order> orderCreate(@RequestBody Map<String, Object> body) {
        Integer userId = requireUserId(body);
        Integer userCouponId = intOf(body, "userCouponId");
        Integer videoId = intOf(body, "videoId");
        Integer months = intOf(body, "months");
        if (videoId != null) {
            return RestResponse.ok(orderService.createVideoOrder(userId, videoId, userCouponId));
        }
        if (months != null) {
            return RestResponse.ok(orderService.createMemberOrder(userId, months, userCouponId));
        }
        throw new IllegalArgumentException("要传 videoId（买影片）或 months（买会员）");
    }

    @PostMapping("/order/list")
    public RestResponse<PageResult<Order>> orderList(@RequestBody Map<String, Object> body) {
        Integer userId = requireUserId(body);
        Integer pageIndex = intOf(body, "pageIndex");
        Integer pageSize = intOf(body, "pageSize");
        return RestResponse.ok(orderService.page(userId,
                pageIndex == null ? 1 : pageIndex,
                pageSize == null ? 10 : pageSize));
    }

    @PostMapping("/order/detail")
    public RestResponse<Map<String, Object>> orderDetail(@RequestBody Map<String, Object> body) {
        Integer userId = requireUserId(body);
        String orderNo = strOf(body, "orderNo");
        if (orderNo == null || orderNo.isEmpty()) {
            throw new IllegalArgumentException("缺少 orderNo");
        }
        Order order = orderService.getOwned(userId, orderNo);
        List<OrderItem> items = orderService.itemsOf(orderNo);
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("order", order);
        data.put("items", items);
        return RestResponse.ok(data);
    }

    @PostMapping("/order/cancel")
    public RestResponse<Order> orderCancel(@RequestBody Map<String, Object> body) {
        Integer userId = requireUserId(body);
        String orderNo = strOf(body, "orderNo");
        if (orderNo == null || orderNo.isEmpty()) {
            throw new IllegalArgumentException("缺少 orderNo");
        }
        return RestResponse.ok(orderService.cancel(userId, orderNo));
    }

    // ------------------------------------------------------------------
    // 工具
    // ------------------------------------------------------------------

    /** 业务校验失败统一走 400 + 中文原因，前端直接把 message 弹出来就行 */
    @ExceptionHandler(IllegalArgumentException.class)
    public RestResponse<Void> handleIllegalArgument(IllegalArgumentException e) {
        return RestResponse.fail(400, e.getMessage());
    }

    private Integer requireUserId(Map<String, Object> body) {
        Integer userId = intOf(body, "userId");
        if (userId == null) {
            throw new IllegalArgumentException("缺少 userId，请先调用 /api/wx/login 登录");
        }
        return userId;
    }

    private Integer intOf(Map<String, Object> body, String key) {
        Object value = body == null ? null : body.get(key);
        if (value == null || "".equals(value.toString().trim())) {
            return null;
        }
        return Integer.valueOf(value.toString().trim());
    }

    private String strOf(Map<String, Object> body, String key) {
        Object value = body == null ? null : body.get(key);
        return value == null ? null : value.toString();
    }
}
