package com.alvis.media.util;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

/**
 * Python 算法脚本调度器（后端 ↔ 算法引擎的唯一通道）。
 *
 * 约定（见 docs/04_系统详细设计.md §4.1）：
 *   - 参数逐个传（不做 shell 拼接），stdout 与 stderr 合并后按 UTF-8 读取；
 *   - stdout 最后一行非空文本必须是 JSON：成功 {"ok":true,...}、失败 {"error":"原因"}；
 *   - 超时强制结束进程，避免脚本挂起占死请求线程。
 */
@Component
public class PythonRunner {

    @Value("${system.python.path:python}")
    private String pythonPath;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /** 执行脚本并返回最后一行非空输出（约定是 JSON 文本） */
    public String run(List<String> scriptArgs, long timeoutSeconds) throws Exception {
        List<String> cmd = new ArrayList<>();
        cmd.add(pythonPath);
        cmd.addAll(scriptArgs);

        ProcessBuilder pb = new ProcessBuilder(cmd);
        pb.redirectErrorStream(true);
        Process process = pb.start();

        StringBuilder sb = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                sb.append(line).append('\n');
            }
        }

        boolean finished = process.waitFor(timeoutSeconds, TimeUnit.SECONDS);
        if (!finished) {
            process.destroyForcibly();
            throw new IllegalStateException("算法脚本执行超时（" + timeoutSeconds + " 秒）");
        }
        if (process.exitValue() != 0 && sb.indexOf("{\"error\"") < 0) {
            throw new IllegalStateException("算法脚本异常退出（code " + process.exitValue() + "）：" + sb);
        }

        String lastLine = "";
        for (String line : sb.toString().split("\\r?\\n")) {
            if (!line.trim().isEmpty()) {
                lastLine = line.trim();
            }
        }
        if (lastLine.isEmpty()) {
            throw new IllegalStateException("算法脚本没有输出任何内容");
        }
        return lastLine;
    }

    /** 执行脚本并把最后一行解析为 JSON；带 error 字段时抛出可读异常 */
    public JsonNode runJson(List<String> scriptArgs, long timeoutSeconds) throws Exception {
        String lastLine = run(scriptArgs, timeoutSeconds);
        JsonNode root;
        try {
            root = objectMapper.readTree(lastLine);
        } catch (Exception e) {
            throw new IllegalStateException("算法脚本输出不是合法 JSON：" + lastLine);
        }
        if (root.hasNonNull("error")) {
            throw new IllegalStateException(root.path("error").asText());
        }
        return root;
    }
}
