package com.alvis.media.controller.wx;

import com.alvis.media.base.RestResponse;
import com.alvis.media.domain.User;
import com.alvis.media.domain.VideoInfo;
import com.alvis.media.domain.other.PageResult;
import com.alvis.media.service.DiscoverService;
import com.alvis.media.service.UserService;
import lombok.AllArgsConstructor;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 小程序发现页：分类导航 + 搜索 + 影片删除。
 *
 * 分类和搜索是公开数据，不需要登录；删除影片必须管理员（t_user.role == 3），
 * 演示版靠请求体里的 userId 认人，和 WxShopController 一致。
 */
@RestController("WxDiscoverController")
@RequestMapping("/api/wx")
@AllArgsConstructor
public class WxDiscoverController {

    /** t_user.role：1 = 普通用户，3 = 管理员 */
    private static final int ROLE_ADMIN = 3;

    private final DiscoverService discoverService;
    private final UserService userService;

    /** 分类导航：默认取影片数 >= 20 的标签，最多 24 个 */
    @PostMapping("/category/list")
    public RestResponse<List<Map<String, Object>>> categories(@RequestBody(required = false) Map<String, Object> body) {
        Integer minCount = intOf(body, "minCount");
        Integer limit = intOf(body, "limit");
        return RestResponse.ok(discoverService.listCategories(
                minCount == null ? 20 : minCount,
                limit == null ? 24 : limit));
    }

    @PostMapping("/category/videos")
    public RestResponse<PageResult<VideoInfo>> videosByTag(@RequestBody Map<String, Object> body) {
        Integer tagId = intOf(body, "tagId");
        if (tagId == null) {
            throw new IllegalArgumentException("缺少 tagId");
        }
        return RestResponse.ok(discoverService.listVideosByTag(tagId, pageIndex(body), pageSize(body)));
    }

    @PostMapping("/search/videos")
    public RestResponse<PageResult<VideoInfo>> search(@RequestBody Map<String, Object> body) {
        String keyword = strOf(body, "keyword");
        if (keyword == null || keyword.trim().isEmpty()) {
            throw new IllegalArgumentException("请输入搜索关键词");
        }
        return RestResponse.ok(discoverService.search(keyword.trim(), pageIndex(body), pageSize(body)));
    }

    /** 删除影片：只有管理员能调，删完连标签关联一起清掉 */
    @PostMapping("/admin/video/delete")
    public RestResponse<Void> deleteVideo(@RequestBody Map<String, Object> body) {
        Integer userId = requireUserId(body);
        User user = userService.selectById(userId);
        if (user == null || user.getRole() == null || user.getRole() != ROLE_ADMIN) {
            throw new IllegalArgumentException("只有管理员可以删除影片");
        }
        Integer videoId = intOf(body, "videoId");
        if (videoId == null) {
            throw new IllegalArgumentException("缺少 videoId");
        }
        discoverService.deleteVideo(videoId);
        return RestResponse.ok();
    }

    @ExceptionHandler(IllegalArgumentException.class)
    public RestResponse<Void> handleIllegalArgument(IllegalArgumentException e) {
        return RestResponse.fail(400, e.getMessage());
    }

    private int pageIndex(Map<String, Object> body) {
        Integer p = intOf(body, "pageIndex");
        return p == null || p < 1 ? 1 : p;
    }

    private int pageSize(Map<String, Object> body) {
        Integer s = intOf(body, "pageSize");
        return s == null || s < 1 ? 10 : Math.min(s, 50);
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
