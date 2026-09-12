package com.alvis.media.viewmodel.student.user;

import lombok.Data;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

@Data
public class UserUpdateVM {

    @NotBlank
    private String realName;

    private String age;

    private Integer sex;

    private String birthDay;

    private String phone;

    @NotNull
    private Integer userLevel;
}
