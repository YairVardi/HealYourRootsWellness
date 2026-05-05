package Utilities;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilderFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

public final class ConfigReader {
    private static final String DEFAULT_CONFIG_PATH = "Configuration/DataConfig.xml";
    private static final Map<String, String> XML_VALUES = loadXmlValues();

    private ConfigReader() {
    }

    public static String value(String key, String defaultValue) {
        String override = System.getProperty(key);
        if (isNotBlank(override)) {
            return override.trim();
        }
        return XML_VALUES.getOrDefault(key, defaultValue);
    }

    public static boolean booleanValue(String key, boolean defaultValue) {
        String value = value(key, Boolean.toString(defaultValue));
        return Boolean.parseBoolean(value);
    }

    public static int intValue(String key, int defaultValue) {
        String value = value(key, Integer.toString(defaultValue));
        try {
            return Integer.parseInt(value.trim());
        } catch (NumberFormatException ignored) {
            return defaultValue;
        }
    }

    private static Map<String, String> loadXmlValues() {
        Path configPath = Paths.get(System.getProperty("config.file", DEFAULT_CONFIG_PATH));
        if (!Files.exists(configPath)) {
            return Collections.emptyMap();
        }

        try {
            Document document = DocumentBuilderFactory.newInstance()
                    .newDocumentBuilder()
                    .parse(configPath.toFile());
            document.getDocumentElement().normalize();

            Map<String, String> values = new HashMap<>();
            NodeList children = document.getDocumentElement().getChildNodes();
            for (int index = 0; index < children.getLength(); index++) {
                Node node = children.item(index);
                if (node instanceof Element) {
                    Element element = (Element) node;
                    values.put(element.getTagName(), element.getTextContent().trim());
                }
            }
            return Collections.unmodifiableMap(values);
        } catch (Exception exception) {
            throw new IllegalStateException("Failed to read config XML from " + configPath, exception);
        }
    }

    private static boolean isNotBlank(String value) {
        return value != null && !value.trim().isEmpty();
    }
}
