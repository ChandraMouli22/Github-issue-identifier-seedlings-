package com.analyzer.controller;

import com.analyzer.model.AnalyzeRequest;
import com.analyzer.model.AnalysisResult;
import com.analyzer.model.ModelInfo;
import com.analyzer.service.CacheService;
import com.analyzer.service.GitHubService;
import com.analyzer.service.LlmService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * REST controller for the GitHub Issue Analyzer API.
 * Equivalent to the FastAPI routes in main.py
 */
@RestController
public class AnalyzerController {

    // Available models configuration (same as Python AVAILABLE_MODELS)
    private static final List<ModelInfo> AVAILABLE_MODELS = List.of(
            // Google Gemini Models
            new ModelInfo("gemini-2.0-flash", "Gemini 2.0 Flash", "Newest generation", "fast", false, "google"),
            new ModelInfo("gemini-2.0-flash-lite", "Gemini 2.0 Flash Lite", "Lightweight & efficient", "fastest", false, "google"),
            new ModelInfo("gemini-flash-lite-latest", "Gemini Flash Lite", "Previous stable generation", "fast", false, "google"),
            // Hugging Face Models
            new ModelInfo("deepseek-ai/DeepSeek-R1", "DeepSeek R1", "Full 671B Base Model", "slow", false, "huggingface"),
            new ModelInfo("deepseek-ai/DeepSeek-R1-Distill-Llama-8B", "DeepSeek R1 Distill", "Powerful reasoning model", "medium", true, "huggingface"),
            new ModelInfo("meta-llama/Meta-Llama-3.1-8B-Instruct", "Llama 3.1 8B", "Meta's latest open model", "fast", false, "huggingface")
    );

    private final GitHubService gitHubService;
    private final LlmService llmService;
    private final CacheService cacheService;

    public AnalyzerController(GitHubService gitHubService, LlmService llmService, CacheService cacheService) {
        this.gitHubService = gitHubService;
        this.llmService = llmService;
        this.cacheService = cacheService;
    }

    @GetMapping("/health")
    public Map<String, String> healthCheck() {
        return Map.of("status", "ok");
    }

    @GetMapping("/api/models")
    public Map<String, List<ModelInfo>> getModels() {
        return Map.of("models", AVAILABLE_MODELS);
    }

    @PostMapping("/api/analyze")
    public ResponseEntity<?> analyzeIssue(@RequestBody AnalyzeRequest request) {
        try {
            System.out.printf("Analyzing: %s #%d with model: %s%n",
                    request.getRepoUrl(), request.getIssueNumber(), request.getModel());

            // Determine provider based on model ID
            String provider = "google";
            for (ModelInfo m : AVAILABLE_MODELS) {
                if (m.getId().equals(request.getModel())) {
                    provider = m.getProvider();
                    break;
                }
            }

            // Check cache first (cache key includes model)
            Map<String, Object> cachedResult = cacheService.getCachedAnalysis(
                    request.getRepoUrl(), request.getIssueNumber(), request.getModel());
            if (cachedResult != null) {
                return ResponseEntity.ok(cachedResult);
            }

            // 1. Fetch from GitHub
            Map<String, String> issueData = gitHubService.getIssueData(
                    request.getRepoUrl(), request.getIssueNumber());

            // 2. Analyze with selected LLM and provider
            AnalysisResult analysis = llmService.analyzeIssue(issueData, request.getModel(), provider);

            // 3. Save to cache for future use (with model in key)
            cacheService.saveToCache(
                    request.getRepoUrl(), request.getIssueNumber(), request.getModel(), analysis);

            return ResponseEntity.ok(analysis);

        } catch (IllegalArgumentException e) {
            // Client errors (400/404)
            String errorMsg = e.getMessage();
            int statusCode = errorMsg.toLowerCase().contains("not found") ? 404 : 400;
            Map<String, String> error = Map.of("detail", errorMsg);
            return ResponseEntity.status(statusCode).body(error);

        } catch (Exception e) {
            // Server errors (500)
            System.out.println("Server Error: " + e.getMessage());
            Map<String, String> error = Map.of("detail", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }
}
