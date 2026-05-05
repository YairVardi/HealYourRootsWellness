package Helpers;

import java.util.Optional;
import java.util.regex.Pattern;

public final class RouteExpectation {
    private final String label;
    private final String path;
    private final Pattern heading;
    private final Pattern urlPattern;
    private final String knownIssue;

    public RouteExpectation(String label, String path, Pattern heading, Pattern urlPattern) {
        this(label, path, heading, urlPattern, null);
    }

    public RouteExpectation(
            String label,
            String path,
            Pattern heading,
            Pattern urlPattern,
            String knownIssue
    ) {
        this.label = label;
        this.path = path;
        this.heading = heading;
        this.urlPattern = urlPattern;
        this.knownIssue = knownIssue;
    }

    public String label() {
        return label;
    }

    public String path() {
        return path;
    }

    public Pattern heading() {
        return heading;
    }

    public Pattern urlPattern() {
        return urlPattern;
    }

    public Optional<String> knownIssue() {
        return Optional.ofNullable(knownIssue);
    }
}
