package Extensions;

import java.util.Collection;
import java.util.Iterator;
import java.util.Map;

public final class JsonUtil {
    private JsonUtil() {
    }

    public static String toJson(Object value) {
        if (value == null) {
            return "null";
        }
        if (value instanceof String) {
            return quote((String) value);
        }
        if (value instanceof Number || value instanceof Boolean) {
            return String.valueOf(value);
        }
        if (value instanceof Map<?, ?>) {
            Map<?, ?> map = (Map<?, ?>) value;
            StringBuilder json = new StringBuilder("{");
            Iterator<? extends Map.Entry<?, ?>> entries = map.entrySet().iterator();
            while (entries.hasNext()) {
                Map.Entry<?, ?> entry = entries.next();
                json.append(quote(String.valueOf(entry.getKey()))).append(':').append(toJson(entry.getValue()));
                if (entries.hasNext()) {
                    json.append(',');
                }
            }
            return json.append('}').toString();
        }
        if (value instanceof Collection<?>) {
            Collection<?> collection = (Collection<?>) value;
            StringBuilder json = new StringBuilder("[");
            Iterator<?> items = collection.iterator();
            while (items.hasNext()) {
                json.append(toJson(items.next()));
                if (items.hasNext()) {
                    json.append(',');
                }
            }
            return json.append(']').toString();
        }

        return quote(String.valueOf(value));
    }

    private static String quote(String value) {
        StringBuilder escaped = new StringBuilder("\"");
        for (int index = 0; index < value.length(); index += 1) {
            char current = value.charAt(index);
            switch (current) {
                case '"':
                    escaped.append("\\\"");
                    break;
                case '\\':
                    escaped.append("\\\\");
                    break;
                case '\b':
                    escaped.append("\\b");
                    break;
                case '\f':
                    escaped.append("\\f");
                    break;
                case '\n':
                    escaped.append("\\n");
                    break;
                case '\r':
                    escaped.append("\\r");
                    break;
                case '\t':
                    escaped.append("\\t");
                    break;
                default:
                    if (current < 0x20) {
                        escaped.append(String.format("\\u%04x", (int) current));
                    } else {
                        escaped.append(current);
                    }
                    break;
            }
        }
        return escaped.append('"').toString();
    }
}
