package Utilities;

import java.net.URI;
import java.util.Locale;
import java.util.regex.Pattern;

public final class TestEnvironment {
    private static final String DEFAULT_BASE_URL = "https://healyourrootswellness.com";

    public static final Pattern ERROR_BOUNDARY_TEXT =
            Pattern.compile("Something went wrong", Pattern.CASE_INSENSITIVE);
    public static final Pattern NOT_FOUND_HEADING =
            Pattern.compile("^404$", Pattern.CASE_INSENSITIVE);

    public static final int DEFAULT_TIMEOUT_MS = parseInt(firstNonBlank(
            System.getProperty("default.timeout.ms"),
            ConfigReader.value("DefaultTimeoutMs", "90000")
    ), 90000);
    public static final int EXPECT_TIMEOUT_MS = parseInt(firstNonBlank(
            System.getProperty("expect.timeout.ms"),
            ConfigReader.value("ExpectTimeoutMs", "10000")
    ), 10000);

    private TestEnvironment() {
    }

    public static String baseUrl() {
        return firstNonBlank(
                System.getProperty("base.url"),
                System.getProperty("url"),
                System.getenv("BASE_URL"),
                ConfigReader.value("url", DEFAULT_BASE_URL),
                DEFAULT_BASE_URL
        );
    }

    public static String apiUrl() {
        return firstNonBlank(
                System.getProperty("url_api"),
                System.getenv("API_URL"),
                ConfigReader.value("url_api", baseUrl()),
                baseUrl()
        );
    }

    public static String platformName() {
        return firstNonBlank(
                System.getProperty("PlatformName"),
                System.getenv("PLATFORM_NAME"),
                ConfigReader.value("PlatformName", "WEB"),
                "WEB"
        );
    }

    public static String browserName() {
        String configuredBrowser = firstNonBlank(
                System.getProperty("browser"),
                System.getProperty("BrowserName"),
                System.getenv("BROWSER"),
                ConfigReader.value("BrowserName", "chromium"),
                "chromium"
        ).toLowerCase(Locale.ROOT);

        switch (configuredBrowser) {
            case "chrome":
                return "chromium";
            case "chromium":
            case "firefox":
            case "webkit":
                return configuredBrowser;
            default:
                throw new IllegalArgumentException(
                        "Unsupported browser '" + configuredBrowser + "'. Use chromium, firefox, or webkit."
                );
        }
    }

    public static boolean headless() {
        if (Boolean.getBoolean("headed")) {
            return false;
        }

        String configuredHeadless = firstNonBlank(
                System.getProperty("headless"),
                System.getProperty("Headless"),
                System.getenv("HEADLESS"),
                ConfigReader.value("Headless", "true"),
                "true"
        );
        return Boolean.parseBoolean(configuredHeadless);
    }

    public static String absoluteUrl(String pathname) {
        return URI.create(baseUrl()).resolve(pathname).toString();
    }

    private static String firstNonBlank(String... values) {
        for (String value : values) {
            if (value != null && !value.trim().isEmpty()) {
                return value.trim();
            }
        }
        return "";
    }

    private static int parseInt(String value, int defaultValue) {
        try {
            return Integer.parseInt(value);
        } catch (NumberFormatException ignored) {
            return defaultValue;
        }
    }
}
