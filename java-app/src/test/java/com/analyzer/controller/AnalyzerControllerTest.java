package com.analyzer.controller;

import com.analyzer.model.AnalysisResult;
import com.analyzer.service.CacheService;
import com.analyzer.service.GitHubService;
import com.analyzer.service.LlmService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.ResponseEntity;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.when;

/**
 * Unit tests for AnalyzerController.
 * Uses plain Mockito (no Spring context needed).
 */
@ExtendWith(MockitoExtension.class)
class AnalyzerControllerTest {

    @Mock
    private GitHubService gitHubService;

    @Mock
    private LlmService llmService;

    @Mock
    private CacheService cacheService;

    @InjectMocks
    private AnalyzerController controller;

    @Test
    void healthCheck_ReturnsOk() {
        Map<String, String> result = controller.healthCheck();
        assertEquals("ok", result.get("status"));
    }

    @Test
    void getModels_ReturnsModelList() {
        Map<String, ?> result = controller.getModels();
        assertNotNull(result.get("models"));
        List<?> models = (List<?>) result.get("models");
        assertEquals(6, models.size());
    }

    @Test
    @SuppressWarnings("unchecked")
    void analyzeIssue_Success() {
        Map<String, String> issueData = Map.of(
                "title", "Bug: App crashes",
                "body", "The app crashes on startup",
                "comments", "- user1: Same issue"
        );

        AnalysisResult analysisResult = new AnalysisResult();
        analysisResult.setSummary("Application crashes on startup");
        analysisResult.setType("bug");
        analysisResult.setPriorityScore("4/5 – Blocks users");
        analysisResult.setSuggestedLabels(List.of("bug", "critical"));
        analysisResult.setPotentialImpact("High impact");

        when(cacheService.getCachedAnalysis(anyString(), anyInt(), anyString())).thenReturn(null);
        when(gitHubService.getIssueData(anyString(), anyInt())).thenReturn(issueData);
        when(llmService.analyzeIssue(any(), anyString(), anyString())).thenReturn(analysisResult);

        var request = new com.analyzer.model.AnalyzeRequest("https://github.com/test/repo", 1, "gemini-2.0-flash");
        ResponseEntity<?> response = controller.analyzeIssue(request);

        assertEquals(200, response.getStatusCode().value());
        AnalysisResult body = (AnalysisResult) response.getBody();
        assertNotNull(body);
        assertEquals("Application crashes on startup", body.getSummary());
        assertEquals("bug", body.getType());
    }

    @Test
    @SuppressWarnings("unchecked")
    void analyzeIssue_CacheHit() {
        Map<String, Object> cached = Map.of(
                "summary", "Cached result",
                "type", "bug"
        );

        when(cacheService.getCachedAnalysis(anyString(), anyInt(), anyString())).thenReturn(cached);

        var request = new com.analyzer.model.AnalyzeRequest("https://github.com/test/repo", 1, "gemini-2.0-flash");
        ResponseEntity<?> response = controller.analyzeIssue(request);

        assertEquals(200, response.getStatusCode().value());
        Map<String, Object> body = (Map<String, Object>) response.getBody();
        assertNotNull(body);
        assertEquals("Cached result", body.get("summary"));
    }

    @Test
    @SuppressWarnings("unchecked")
    void analyzeIssue_InvalidUrl_Returns400() {
        when(cacheService.getCachedAnalysis(anyString(), anyInt(), anyString())).thenReturn(null);
        when(gitHubService.getIssueData(anyString(), anyInt()))
                .thenThrow(new IllegalArgumentException("Invalid GitHub URL"));

        var request = new com.analyzer.model.AnalyzeRequest("not-a-url", 1, "gemini-2.0-flash");
        ResponseEntity<?> response = controller.analyzeIssue(request);

        assertEquals(400, response.getStatusCode().value());
        Map<String, String> body = (Map<String, String>) response.getBody();
        assertNotNull(body);
        assertEquals("Invalid GitHub URL", body.get("detail"));
    }

    @Test
    void analyzeIssue_NotFound_Returns404() {
        when(cacheService.getCachedAnalysis(anyString(), anyInt(), anyString())).thenReturn(null);
        when(gitHubService.getIssueData(anyString(), anyInt()))
                .thenThrow(new IllegalArgumentException("Issue #999 not found in test/repo"));

        var request = new com.analyzer.model.AnalyzeRequest("https://github.com/test/repo", 999, "gemini-2.0-flash");
        ResponseEntity<?> response = controller.analyzeIssue(request);

        assertEquals(404, response.getStatusCode().value());
    }
}
