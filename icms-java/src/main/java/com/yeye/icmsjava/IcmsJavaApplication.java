package com.yeye.icmsjava;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.yeye.icmsjava.mapper")
public class IcmsJavaApplication {

    public static void main(String[] args) {
        SpringApplication.run(IcmsJavaApplication.class, args);
    }

}
