package com.yeye.icmsjava.controller;

import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import jakarta.annotation.Resource;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;

/**
 * 测试控制器，用于验证 Swagger 功能
 */
@RestController
@RequestMapping("/test")
@Tag(name = "测试接口", description = "提供各类测试接口，用于验证 Swagger 文档生成及接口测试")
public class TestController {

    /**
     * 简单的 GET 接口，用于测试获取数据
     * @param id 路径参数，代表测试数据的唯一标识
     * @return 包含测试数据的响应
     */
    @GetMapping("/{id}")
    @Operation(summary = "获取测试数据接口", description = "根据传入的 ID，获取对应的测试数据")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "成功获取测试数据",
                    content = @Content(schema = @Schema(implementation = Map.class))),
            @ApiResponse(responseCode = "400", description = "参数不合法，ID 格式错误等",
                    content = @Content(schema = @Schema(type = "string", example = "ID 必须为有效数字")))
    })
    public ResponseEntity<Map<String, Object>> getTestData(
            @PathVariable
            @Parameter(description = "测试数据的唯一标识 ID", example = "1")
            Long id) {
        Map<String, Object> data = new HashMap<>();
        data.put("id", id);
        data.put("message", "这是一条测试数据");
        return ResponseEntity.ok(data);
    }

    /**
     * 简单的 POST 接口，用于测试提交数据
     * @param request 包含测试提交数据的请求体
     * @return 提交结果的响应
     */
    @PostMapping("/submit")
    @Operation(summary = "提交测试数据接口", description = "接收测试数据并进行处理，返回提交结果")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "数据提交成功",
                    content = @Content(schema = @Schema(implementation = Map.class))),
            @ApiResponse(responseCode = "400", description = "请求体为空或参数不合法",
                    content = @Content(schema = @Schema(type = "string", example = "请求体不能为空")))
    })
    public ResponseEntity<Map<String, Object>> submitTestData(
            @RequestBody
            @Parameter(
                    name = "testRequest",
                    description = "提交的测试数据，包含 message 字段",
                    content = @Content(
                            schema = @Schema(
                                    implementation = TestRequest.class,
                                    example = "{\"message\":\"测试提交内容\"}"
                            )
                    )
            )
            TestRequest request) {
        Map<String, Object> result = new HashMap<>();
        result.put("status", "success");
        result.put("receivedData", request.getMessage());
        return ResponseEntity.ok(result);
    }

    /**
     * 用于测试 POST 接口的请求体实体类（内部类示例，也可提取为独立类）
     */
    @Schema(description = "测试提交数据的请求体实体类")
    static class TestRequest {
        @Schema(description = "提交的消息内容", example = "测试提交内容")
        private String message;

        public String getMessage() {
            return message;
        }

        public void setMessage(String message) {
            this.message = message;
        }
    }
}