package com.analyzer.service;

import com.analyzer.config.EnvConfig;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;

import java.net.URI;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Fetches issue details and comments from the GitHub API.
 * Equivalent to services/github_service.py
 */
@Service
public class GitHubService {

    private final EnvConfig envConfig;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    public GitHubService(EnvConfig envConfig) {
        this.envConfig = envConfig;
        this.restTemplate = new RestTemplate();
        this.objectMapper = new ObjectMapper();
    }

    /**
     * Parses a GitHub repository URL to extract owner and repo name.
     */
    public String[] parseGitHubUrl(String url) {
        try {
            URI uri = new URI(url);
            String path = uri.getPath();
            List<String> parts = Arrays.stream(path.split("/"))
                    .filter(p -> !p.isEmpty())
                    .collect(Collectors.toList());
            if (parts.size() < 2) {
                throw new IllegalArgumentException("Invalid GitHub URL");
            }
            return new String[]{parts.get(0), parts.get(1)};
        } catch (IllegalArgumentException e) {
            throw e;
        } catch (Exception e) {
            throw new IllegalArgumentException("Invalid GitHub URL format");
        }
    }

    /**
     * Truncates text to a maximum length.
     */
    public String truncateText(String text, int maxLength) {
        if (text == null || text.isEmpty()) return "";
        return text.length() > maxLength ? text.substring(0, maxLength) + "..." : text;
    }

    /**
     * Fetches issue details and comments from GitHub.
     */
    public Map<String, String> getIssueData(String repoUrl, int issueNumber) {
        String[] parsed = parseGitHubUrl(repoUrl);
        String owner = parsed[0];
        String repo = parsed[1];

        HttpHeaders headers = new HttpHeaders();
        headers.set("Accept", "application/vnd.github.v3+json");

        // Optional: Use GitHub Token if available
        String githubToken = envConfig.get("GITHUB_TOKEN");
        if (githubToken != null && !githubToken.isEmpty()) {
            headers.set("Authorization", "token " + githubToken);
        }

        HttpEntity<Void> entity = new HttpEntity<>(headers);

        try {
            // 1. Fetch Issue Details
            String issueUrl = String.format(
                    "https://api.github.com/repos/%s/%s/issues/%d", owner, repo, issueNumber);
            ResponseEntity<String> issueResponse = restTemplate.exchange(
                    issueUrl, HttpMethod.GET, entity, String.class);
            JsonNode issueData = objectMapper.readTree(issueResponse.getBody());

            // 2. Fetch Comments
            String commentsUrl = String.format(
                    "https://api.github.com/repos/%s/%s/issues/%d/comments", owner, repo, issueNumber);
            ResponseEntity<String> commentsResponse = restTemplate.exchange(
                    commentsUrl, HttpMethod.GET, entity, String.class);
            JsonNode commentsData = objectMapper.readTree(commentsResponse.getBody());

            // 3. Process Data
            String body = truncateText(
                    issueData.has("body") && !issueData.get("body").isNull()
                            ? issueData.get("body").asText()
                            : "No description provided.",
                    2000
            );

            StringBuilder commentsSummary = new StringBuilder();
            if (commentsData.isArray() && commentsData.size() > 0) {
                for (JsonNode comment : commentsData) {
                    String login = comment.get("user").get("login").asText();
                    String commentBody = truncateText(comment.get("body").asText(), 500);
                    commentsSummary.append("- ").append(login).append(": ").append(commentBody).append("\n");
                }
            } else {
                commentsSummary.append("No comments found.");
            }

            Map<String, String> result = new HashMap<>();
            result.put("title", issueData.get("title").asText());
            result.put("body", body);
            result.put("comments", commentsSummary.toString());
            return result;

        } catch (HttpClientErrorException.NotFound e) {
            throw new IllegalArgumentException(
                    String.format("Issue #%d not found in %s/%s", issueNumber, owner, repo));
        } catch (HttpClientErrorException e) {
            System.out.println("GitHub API Error: " + e.getResponseBodyAsString());
            throw new IllegalArgumentException("GitHub API Error: " + e.getStatusCode().value());
        } catch (IllegalArgumentException e) {
            throw e;
        } catch (Exception e) {
            System.out.println("Error fetching issue: " + e.getMessage());
            throw new RuntimeException(e.getMessage(), e);
        }
    }
}
