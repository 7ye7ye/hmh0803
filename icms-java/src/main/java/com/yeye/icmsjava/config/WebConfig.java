package com.yeye.icmsjava.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

//Spring Boot 的自动配置会扫描 @Configuration 注解的类，并加载其中的 Bean 或配置
@Configuration
public class WebConfig implements WebMvcConfigurer {
    //允许跨域
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**") // 匹配所有路径
                .allowedOrigins("http://localhost:8085", "http://121.36.44.77:8090 ","http://121.36.44.77:8085","http://121.36.44.77:8000","http://localhost:8087") // 允许的来源，可以是具体域名或通配符 "*"
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS") // 允许的HTTP方法
                .allowedHeaders("*") // 允许的请求头，"*"表示允许所有
                .allowCredentials(true) // 是否允许发送Cookie（凭证）
                .maxAge(3600); // 预检请求的缓存时间（秒），在此时间内无需再次发送预检请求
    }
}
