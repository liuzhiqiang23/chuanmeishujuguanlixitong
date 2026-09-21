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
import com.alvis.media.utility.WxUtil;
import org.springframework.beans.factory.annotation.Value;
import lombok.RequiredArgsConstructor;
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
@RequiredArgsConstructor
public class WxShopController {

    /** t_user.role：1 = 普通用户，3 = 管理员 */
    private static final int ROLE_ADMIN = 3;

    @Value("${system.wx.appid:}")
    private String wxAppid;

    @Value("${system.wx.secret:}")
    private String wxSecret;

    /** 管理员白名单：这些微信 openid 登录后自动是管理员（逗号分隔） */
    @Value("${system.wx.admin-open-ids:}")
    private String adminOpenIds;

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

        // 配了自己的 appid/secret 就走微信官方 code2session，openid 才稳定；
        // 还是模板作者那套（或没配）就退回演示模式，免得连登录都进不来。
        String openid = resolveOpenId(code);

        User user = userService.selectByWxOpenId(openid);
        if (user == null) {
            user = registerByOpenid(openid, nickName);
        }
        // 白名单里的微信号登录即管理员，不用任何激活码
        if (isWhitelistedAdmin(openid) && (user.getRole() == null || user.getRole() != ROLE_ADMIN)) {
            user.setRole(ROLE_ADMIN);
            userService.updateById(user);
        }

        Member member = memberService.getValidMember(user.getId());
        Map<String, Object> data = new LinkedHashMap<>();
        data.put("userId", user.getId());
        data.put("userName", user.getUserName());
        data.put("nickName", user.getRealName());
        data.put("token", "demo-token-" + user.getId() + "-" + UUID.randomUUID().toString().substring(0, 8));
        data.put("isMember", member != null);
        data.put("memberExpireTime", member == null ? null : member.getExpireTime());
        // 管理员（t_user.role == 3）才能在小程序里删影片，前端按这个标记决定要不要显示删除按钮
        data.put("isAdmin", user.getRole() != null && user.getRole() == ROLE_ADMIN);
        return RestResponse.ok(data);
    }

    /**
     * 把 wx.login 的 code 换成 openid。
     * 配好了自己的 appid/secret 才走微信官方 code2session；否则退回演示模式，
     * 用 code 派生一个假 openid，保证没配凭证时整套流程照样能跑。
     */
    private String resolveOpenId(String code) {
        boolean configured = wxAppid != null && !wxAppid.trim().isEmpty()
                && wxSecret != null && !wxSecret.trim().isEmpty();
        if (!configured) {
            return "demo_openid_" + (code == null || code.isEmpty() ? "default" : code);
        }
        String openid = WxUtil.getOpenId(wxAppid.trim(), wxSecret.trim(), code);
        if (openid == null || openid.isEmpty()) {
            throw new IllegalArgumentException("微信登录失败：code 可能已失效，退出小程序重进一次");
        }
        return openid;
    }

    /** 白名单里的 openid 登录即管理员。配在 wx.admin-open-ids，逗号分隔 */
    private boolean isWhitelistedAdmin(String openid) {
        if (openid == null || adminOpenIds == null || adminOpenIds.trim().isEmpty()) {
            return false;
        }
        for (String item : adminOpenIds.split(",")) {
            if (openid.equals(item.trim())) {
                return true;
            }
        }
        return false;
    }

    /** 免注册建号：只用 openid + 昵称，不设密码 */
    private User registerByOpenid(String openid, String nickName) {        User user = new User();
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

    /**
     * 好友通过分享卡片进来领券：被分享者得一张，分享者也补一张。
     * sharerId 由分享卡片路径上的 shareFrom 带进来，同一对好友只发一次。
     */
    @PostMapping("/coupon/share/receive")
    public RestResponse<Map<String, Object>> couponShareReceive(@RequestBody Map<String, Object> body) {
        Integer userId = requireUserId(body);
        Integer sharerId = intOf(body, "sharerId");
        if (sharerId == null) {
            throw new IllegalArgumentException("缺少 sharerId");
        }
        return RestResponse.ok(couponService.receiveByShare(userId, sharerId));
    }

    /**
     * 分享动作本身的奖励：点「分享得券」把小程序发出去时调，给自己发一张分享奖励券。
     * 每人限 1 张，已领过返回 null（不报错，免得打断分享流程）。
     */
    @PostMapping("/coupon/share/reward")
    public RestResponse<Coupon> couponShareReward(@RequestBody Map<String, Object> body) {
        Integer userId = requireUserId(body);
        return RestResponse.ok(couponService.claimShareReward(userId));
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
