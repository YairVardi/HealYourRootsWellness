package Extensions;

@FunctionalInterface
public interface ThrowingRunnable {
    void run() throws Exception;
}
