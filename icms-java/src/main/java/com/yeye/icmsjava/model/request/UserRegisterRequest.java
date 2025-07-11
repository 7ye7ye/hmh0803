package com.yeye.icmsjava.model.request;

import lombok.Getter;

import java.io.Serial;
import java.io.Serializable;

@Getter
public class UserRegisterRequest implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    private String username;
    private String password;
    private String checkPassword;
    private String faceEmbedding;

    public String getUsername() {
        return username;
    }

    public String getPassword() {
        return password;
    }

    public String getCheckPassword() {
        return checkPassword;
    }

    public String getFaceEmbedding() {
        return faceEmbedding;
    }
}
