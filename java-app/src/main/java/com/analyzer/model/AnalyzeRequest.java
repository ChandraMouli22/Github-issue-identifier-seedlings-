package com.analyzer.model;

/**
 * Request body for the /api/analyze endpoint.
 * Equivalent to the Python Pydantic AnalyzeRequest model.
 */
public class AnalyzeRequest {
    private String repoUrl;
    private int issueNumber;
    private String model = "gemini-2.0-flash";

    public AnalyzeRequest() {}

    public AnalyzeRequest(String repoUrl, int issueNumber, String model) {
        this.repoUrl = repoUrl;
        this.issueNumber = issueNumber;
        this.model = model;
    }

    public String getRepoUrl() { return repoUrl; }
    public void setRepoUrl(String repoUrl) { this.repoUrl = repoUrl; }

    public int getIssueNumber() { return issueNumber; }
    public void setIssueNumber(int issueNumber) { this.issueNumber = issueNumber; }

    public String getModel() { return model; }
    public void setModel(String model) { this.model = model; }
}
