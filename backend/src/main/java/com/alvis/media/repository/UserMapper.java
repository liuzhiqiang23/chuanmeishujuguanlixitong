package com.alvis.media.repository;

import com.alvis.media.domain.other.KeyValue;
import com.alvis.media.domain.User;
import com.alvis.media.viewmodel.admin.user.UserPageRequestVM;
import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

/**
 *@author 奇趣
 */

@Mapper
public interface UserMapper extends MediaBaseMapper <User> {


    int deleteByPrimaryKey(Integer id);

    int insert(User record);

    int insertSelective(User record);

    User selectByPrimaryKey(Integer id);

    int updateByPrimaryKeySelective(User record);

    int updateByPrimaryKey(User record);


    /**
     * 带条件查询用户列表
     * @param filter
     * @return
     */
    List<User> selectUserList(User filter );

    /**
     * 获取新增用户数量
     * @param filter
     * @return
     */
     int selectUserCount(User filter);

    /**
     * getAllUser
     *
     * @return List<User>
     */
    List<User> getAllUser();

    /**
     * getUserById
     *
     * @param id id
     * @return User
     */
    User getUserById(Integer id);

    /**
     * getUserByUserName
     *
     * @param username username
     * @return User
     */
    User getUserByUserName(String username);

    /**
     * getUserByUserNamePwd
     *
     * @param username username
     * @param pwd      pwd
     * @return User
     */
    User getUserByUserNamePwd(@Param("username") String username, @Param("pwd") String pwd);

    /**
     * getUserByUuid
     *
     * @param uuid uuid
     * @return User
     */
    User getUserByUuid(String uuid);

    /**
     * userPageList
     *
     * @param map userPageList
     * @return List<User>
     */
    List<User> userPageList(Map<String, Object> map);


    /**
     * userPageCount
     *
     * @param map map
     * @return Integer
     */
    Integer userPageCount(Map<String, Object> map);


    /**
     * @param requestVM requestVM
     * @return List<User>
     */
    List<User> userPage(UserPageRequestVM requestVM);


    /**
     * insertUser
     *
     * @param user user
     */
    void insertUser(User user);

    /**
     * insertUsers
     *
     * @param users users
     */
    void insertUsers(List<User> users);

    /**
     * updateUser
     *
     * @param user user
     */
    void updateUser(User user);

    /**
     * updateUsersAge
     *
     * @param map map
     */
    void updateUsersAge(Map<String, Object> map);

    /**
     * deleteUsersByIds
     *
     * @param ids ids
     */
    void deleteUsersByIds(List<Integer> ids);

    /**
     * insertUserSql
     *
     * @param user user
     */
    void insertUserSql(User user);

    Integer selectAllCount();

    List<KeyValue> selectByUserName(String userName);

    List<User> selectByIds(List<Integer> ids);


    User selectByWxOpenId(@Param("wxOpenId") String wxOpenId);
}
