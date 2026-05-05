package Utilities;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.List;

public final class AllureEnvironment {
    private static final String DEFAULT_PROJECT_NAME = "HealYourRootsWellness";
    private static final String DEFAULT_FRAMEWORK_NAME = "Java Selenium";
    private static final String DEFAULT_LANGUAGE_NAME = "Java";

    private AllureEnvironment() {
    }

    public static void write() {
        String resultsDirectory = System.getProperty("allure.results.directory", "allure-results");
        Path resultsPath = Paths.get(resultsDirectory);
        if (!resultsPath.isAbsolute()) {
            resultsPath = Paths.get(System.getProperty("user.dir")).resolve(resultsPath);
        }

        List<String> lines = Arrays.asList(
                "Project=" + System.getProperty("project.name", DEFAULT_PROJECT_NAME),
                "BaseURL=" + TestEnvironment.baseUrl(),
                "Framework=" + System.getProperty("framework.name", DEFAULT_FRAMEWORK_NAME),
                "Language=" + System.getProperty("language.name", DEFAULT_LANGUAGE_NAME),
                "BuildTool=Maven",
                "TestRunner=TestNG"
        );

        try {
            Files.createDirectories(resultsPath);
            Files.write(resultsPath.resolve("environment.properties"), lines, StandardCharsets.UTF_8);
        } catch (IOException error) {
            throw new IllegalStateException("Failed to write Allure environment metadata.", error);
        }
    }
}
