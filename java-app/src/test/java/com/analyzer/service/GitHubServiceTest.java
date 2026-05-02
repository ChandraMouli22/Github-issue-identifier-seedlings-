package com.analyzer.service;

import com.analyzer.config.EnvConfig;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
class GitHubServiceTest {

    @Mock
    private EnvConfig envConfig;

    @InjectMocks
    private GitHubService gitHubService;

    @Test
    void parseGitHubUrl_ValidUrl() {
        String[] result = gitHubService.parseGitHubUrl("https://github.com/facebook/react");
        assertEquals("facebook", result[0]);
        assertEquals("react", result[1]);
    }

    @Test
    void parseGitHubUrl_ValidUrlWithTrailingSlash() {
        String[] result = gitHubService.parseGitHubUrl("https://github.com/facebook/react/");
        assertEquals("facebook", result[0]);
        assertEquals("react", result[1]);
    }

    @Test
    void parseGitHubUrl_InvalidUrl_TooFewParts() {
        assertThrows(IllegalArgumentException.class, () -> {
            gitHubService.parseGitHubUrl("https://github.com/onlyowner");
        });
    }

    @Test
    void parseGitHubUrl_InvalidUrl_EmptyPath() {
        assertThrows(IllegalArgumentException.class, () -> {
            gitHubService.parseGitHubUrl("https://github.com/");
        });
    }

    @Test
    void truncateText_ShortText() {
        assertEquals("Hello", gitHubService.truncateText("Hello", 100));
    }

    @Test
    void truncateText_LongText() {
        String longText = "A".repeat(2500);
        String result = gitHubService.truncateText(longText, 2000);
        assertEquals(2003, result.length()); // 2000 + "..."
        assertTrue(result.endsWith("..."));
    }

    @Test
    void truncateText_NullText() {
        assertEquals("", gitHubService.truncateText(null, 100));
    }

    @Test
    void truncateText_EmptyText() {
        assertEquals("", gitHubService.truncateText("", 100));
    }
}
