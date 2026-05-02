package com.analyzer.service;

import com.analyzer.config.EnvConfig;
import com.analyzer.model.AnalysisResult;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;

import java.util.*;
import java.util.regex.Pattern;

/**
 * LLM integration service supporting Google Gemini and Hugging Face models.
 * Equivalent to services/llm_service.py
 */
@Service
public class LlmService {

    private static final String SYSTEM_PROMPT = """
            You are an expert technical project manager and developer.
            Your task is to analyze GitHub issues and output a strictly formatted JSON summary.
            You must NOT output anything other than the JSON object.
            Do not include markdown formatting like ```json or ```.

            Output Schema:
            {
              "summary": "A one-sentence summary of the user's problem or request.",
              "type": "bug" | "feature_request" | "documentation" | "question" | "other",
              "priority_score": "A string containing the score (1-5) followed by a brief justification (e.g., '4/5 – Blocks users...').",
              "suggested_labels": ["Array of exactly 2-3 labels. Prefer standard GitHub labels like 'bug', 'enhancement', 'documentation', 'help wanted', 'ui', 'backend'. Avoid highly specific custom labels."],
              "potential_impact": "Brief impact description."
            }
            """;

    private static final Pattern THINK_PATTERN = Pattern.compile("<think>.*?</think>", Pattern.DOTALL);
    private static final Pattern JSON_BLOCK_PATTERN = Pattern.compile("```json");
    private static final Pattern CODE_BLOCK_PATTERN = Pattern.compile("```");

    private final EnvConfig envConfig;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    public LlmService(EnvConfig envConfig) {
        this.envConfig = envConfig;
        this.restTemplate = new RestTemplate();
        this.objectMapper = new ObjectMapper();
    }

    /**
     * Cleans the LLM response to ensure valid JSON.
     * Removes markdown code blocks and reasoning tags.
     */
    public String cleanJson(String text) {
        // Remove <think> blocks (DeepSeek R1 reasoning)
        String clean = THINK_PATTERN.matcher(text).replaceAll("");
        // Remove markdown code blocks
        clean = JSON_BLOCK_PATTERN.matcher(clean).replaceAll("");
        clean = CODE_BLOCK_PATTERN.matcher(clean).replaceAll("").trim();
        // Extract JSON object between first { and last }
        int firstBrace = clean.indexOf('{');
        int lastBrace = clean.lastIndexOf('}');
        if (firstBrace != -1 && lastBrace != -1) {
            clean = clean.substring(firstBrace, lastBrace + 1);
        }
        return clean;
    }

    /**
     * Dispatcher: routes analysis to the correct LLM provider.
     */
    public AnalysisResult analyzeIssue(Map<String, String> issueData, String modelName, String provider) {
        if ("huggingface".equals(provider)) {
            return analyzeWithHuggingFace(issueData, modelName);
        } else {
            return analyzeWithGemini(issueData, modelName);
        }
    }

    /**
     * Analyzes issue using Google Gemini REST API with retry logic.
     */
    private AnalysisResult analyzeWithGemini(Map<String, String> issueData, String modelName) {
        String apiKey = envConfig.get("LLM_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            throw new IllegalArgumentException("LLM_API_KEY is missing in .env");
        }

        String prompt = buildPrompt(issueData);

        // Retry logic with exponential backoff (same as Python: 3 retries, 5s base)
        int maxRetries = 3;
        int baseDelay = 5;

        for (int attempt = 0; attempt < maxRetries; attempt++) {
            try {
                String url = String.format(
                        "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent?key=%s",
                        modelName, apiKey);

                // Build request body
                Map<String, Object> requestBody = new HashMap<>();

                // Contents
                Map<String, Object> part = Map.of("text", prompt);
                Map<String, Object> content = Map.of("parts", List.of(part));
                requestBody.put("contents", List.of(content));

                // Generation config
                requestBody.put("generationConfig", Map.of("responseMimeType", "application/json"));

                // Safety settings
                List<Map<String, String>> safetySettings = List.of(
                        Map.of("category", "HARM_CATEGORY_HARASSMENT", "threshold", "BLOCK_NONE"),
                        Map.of("category", "HARM_CATEGORY_HATE_SPEECH", "threshold", "BLOCK_NONE"),
                        Map.of("category", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold", "BLOCK_NONE"),
                        Map.of("category", "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold", "BLOCK_NONE")
                );
                requestBody.put("safetySettings", safetySettings);

                HttpHeaders headers = new HttpHeaders();
                headers.setContentType(MediaType.APPLICATION_JSON);
                HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

                ResponseEntity<String> response = restTemplate.postForEntity(url, entity, String.class);
                JsonNode root = objectMapper.readTree(response.getBody());

                // Extract text from response
                String text = root.get("candidates").get(0).get("content").get("parts").get(0).get("text").asText();
                String cleaned = cleanJson(text);

                return objectMapper.readValue(cleaned, AnalysisResult.class);

            } catch (Exception e) {
                String errorMsg = e.getMessage();
                System.out.printf("Gemini API Error (Attempt %d/%d): %s%n", attempt + 1, maxRetries, errorMsg);

                boolean isRateLimit = errorMsg != null && (
                        errorMsg.contains("429") || errorMsg.toLowerCase().contains("quota")
                                || errorMsg.toLowerCase().contains("rate limit")
                                || errorMsg.toLowerCase().contains("resource_exhausted"));

                if (isRateLimit && attempt < maxRetries - 1) {
                    int delay = baseDelay * (int) Math.pow(2, attempt);
                    System.out.printf("⏳ Rate limit hit. Waiting %d seconds before retry...%n", delay);
                    try { Thread.sleep(delay * 1000L); } catch (InterruptedException ie) { Thread.currentThread().interrupt(); }
                    continue;
                }

                if (isRateLimit) {
                    throw new IllegalArgumentException(
                            "Rate limit reached for this model. Please try switching to Gemini Flash Lite or DeepSeek R1 Distill from the dropdown, or wait a minute and retry.");
                }

                throw new IllegalArgumentException("Gemini Error: " + errorMsg);
            }
        }

        throw new IllegalArgumentException("Gemini Error: Max retries exceeded");
    }

    /**
     * Analyzes issue using Hugging Face Inference API.
     */
    private AnalysisResult analyzeWithHuggingFace(Map<String, String> issueData, String modelName) {
        String apiKey = envConfig.get("HF_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            throw new IllegalArgumentException("HF_API_KEY is missing in .env");
        }

        String prompt = buildPrompt(issueData);

        try {
            String url = String.format(
                    "https://api-inference.huggingface.co/models/%s/v1/chat/completions", modelName);

            // Build request body
            Map<String, Object> message = Map.of("role", "user", "content", prompt);
            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("model", modelName);
            requestBody.put("messages", List.of(message));
            requestBody.put("max_tokens", 1024);
            requestBody.put("temperature", 0.1);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.set("Authorization", "Bearer " + apiKey);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            ResponseEntity<String> response = restTemplate.postForEntity(url, entity, String.class);
            JsonNode root = objectMapper.readTree(response.getBody());

            String content = root.get("choices").get(0).get("message").get("content").asText();
            if (content == null || content.isEmpty()) {
                throw new IllegalArgumentException("Empty response from Hugging Face model");
            }

            String cleaned = cleanJson(content);
            return objectMapper.readValue(cleaned, AnalysisResult.class);

        } catch (HttpClientErrorException e) {
            String errorMsg = e.getMessage();
            if (errorMsg != null && (errorMsg.contains("404") || errorMsg.contains("model_not_found"))) {
                throw new IllegalArgumentException(
                        String.format("The model '%s' is not available or access is denied (gated model). "
                                + "Please check if you have access to this model on Hugging Face. "
                                + "If not, consider switching to an open-access model such as DeepSeek or Gemini Flash Lite for best results.",
                                modelName));
            }
            throw new IllegalArgumentException("Hugging Face API Error: " + errorMsg);
        } catch (IllegalArgumentException e) {
            throw e;
        } catch (Exception e) {
            throw new IllegalArgumentException("Hugging Face API Error: " + e.getMessage());
        }
    }

    /**
     * Builds the analysis prompt from issue data.
     */
    private String buildPrompt(Map<String, String> issueData) {
        return String.format("""
                %s

                Analyze the following GitHub Issue:

                Title: %s
                Body: %s
                Comments Summary:
                %s

                Provide the JSON output strictly adhering to the schema.
                """, SYSTEM_PROMPT, issueData.get("title"), issueData.get("body"), issueData.get("comments"));
    }
}
