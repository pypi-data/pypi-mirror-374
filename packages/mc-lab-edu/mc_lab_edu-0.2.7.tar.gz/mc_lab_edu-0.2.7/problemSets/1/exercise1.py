import matplotlib.pyplot as plt
import numpy as np


def simulate_truncated_exp_direct(lam, a, size=1000):
    """
    Most efficient method: X = a + Z where Z ~ Exp(λ)
    """
    return a + np.random.exponential(1 / lam, size)


def simulate_truncated_exp_rejection(lam, a, size=1000):
    """
    Rejection sampling: Keep generating until Y ≥ a
    """
    samples = []
    while len(samples) < size:
        y = np.random.exponential(1 / lam)
        if y >= a:
            samples.append(y)
    return np.array(samples)


def simulate_truncated_exp_inverse_transform(lam, a, size=1000):
    """
    Inverse transform method using CDF F_X(x) = 1 - exp(-λ(x-a))
    """
    u = np.random.uniform(0, 1, size)
    return a - np.log(1 - u) / lam


# Example usage
if __name__ == "__main__":
    # Parameters
    lam = 2.0  # rate parameter
    a = 1.5  # truncation point
    n_samples = 10000

    # Generate samples using all three methods
    samples_direct = simulate_truncated_exp_direct(lam, a, n_samples)
    samples_rejection = simulate_truncated_exp_rejection(lam, a, n_samples)
    samples_inverse = simulate_truncated_exp_inverse_transform(lam, a, n_samples)

    # Verify all samples are ≥ a
    print(f"Direct method - min value: {np.min(samples_direct):.4f}")
    print(f"Rejection method - min value: {np.min(samples_rejection):.4f}")
    print(f"Inverse transform - min value: {np.min(samples_inverse):.4f}")
    print(f"All should be ≥ a = {a}")

    # Compare means (theoretical mean is a + 1/λ)
    theoretical_mean = a + 1 / lam
    print(f"\nTheoretical mean: {theoretical_mean:.4f}")
    print(f"Direct method mean: {np.mean(samples_direct):.4f}")
    print(f"Rejection method mean: {np.mean(samples_rejection):.4f}")
    print(f"Inverse transform mean: {np.mean(samples_inverse):.4f}")

    # Plot histograms to compare
    plt.figure(figsize=(12, 4))

    plt.subplot(1, 3, 1)
    plt.hist(samples_direct, bins=50, density=True, alpha=0.7, color="blue")
    plt.title("Direct Method")
    plt.xlabel("x")
    plt.ylabel("Density")

    plt.subplot(1, 3, 2)
    plt.hist(samples_rejection, bins=50, density=True, alpha=0.7, color="red")
    plt.title("Rejection Sampling")
    plt.xlabel("x")

    plt.subplot(1, 3, 3)
    plt.hist(samples_inverse, bins=50, density=True, alpha=0.7, color="green")
    plt.title("Inverse Transform")
    plt.xlabel("x")

    # Overlay theoretical PDF
    x_range = np.linspace(a, np.max(samples_direct), 1000)
    theoretical_pdf = lam * np.exp(-lam * (x_range - a))

    for i in range(3):
        plt.subplot(1, 3, i + 1)
        plt.plot(x_range, theoretical_pdf, "k--", linewidth=2, label="Theoretical PDF")
        plt.axvline(x=a, color="orange", linestyle=":", linewidth=2, label=f"a = {a}")
        plt.legend()
        plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


# Additional utility function for single sample generation
def sample_truncated_exp(lam, a):
    """Generate a single sample from truncated exponential"""
    return a + np.random.exponential(1 / lam)
