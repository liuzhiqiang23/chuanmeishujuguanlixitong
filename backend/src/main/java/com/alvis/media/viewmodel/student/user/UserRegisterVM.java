package com.alvis.media.viewmodel.student.user;

import lombok.Data;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

@Data
public class UserRegisterVM {

    @NotBlank
    private String userName;

    @NotBlank
    private String password;

    @NotNull
    private Integer userLevel;
}
